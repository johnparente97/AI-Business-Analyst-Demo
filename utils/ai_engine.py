import requests
import streamlit as st
import time
import json
import random

class AIEngine:
    def __init__(self):
        # Retrieve API Token from Streamlit Secrets
        self.api_token = st.secrets.get("HF_API_TOKEN", None)
        # Using a reliable model (Mistral or similar instruct model)
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    def analyze_dataset_context(self, summary_data):
        """
        Performs the Phase 1 assessment: Domain, Purpose, Signals.
        Returns a structured dictionary.
        """
        # Prepare the context for the LLM
        context = self._prepare_context(summary_data)
        
        if self.api_token:
            try:
                raw_response = self._call_huggingface(context)
                return self._parse_json_response(raw_response, summary_data)
            except Exception as e:
                print(f"HF API Error: {e}")
                return self._generate_fallback_analysis(summary_data)
        else:
            return self._generate_fallback_analysis(summary_data)

    def _prepare_context(self, data):
        """
        Creates a prompt requesting JSON output.
        """
        # 1. Basic Info
        info_str = f"Dataset: {data['rows']:,} rows, {data['cols']} columns.\n"
        if data['date_range'] != "N/A":
            info_str += f"Date Range: {data['date_range']}.\n"
        
        # 2. Numeric Stats
        num_stats = data.get("numeric_stats", {})
        num_str = ""
        for i, (col, stats) in enumerate(num_stats.items()):
            if i >= 5: break
            num_str += f"- {col}: Mean={stats['mean']:.2f}, Max={stats['max']:.2f}\n"

        # 3. Categorical Stats
        cat_stats = data.get("categorical_stats", {})
        cat_str = ""
        for i, (col, counter) in enumerate(cat_stats.items()):
            if i >= 5: break
            top_3 = ", ".join([f"{k}" for k,v in counter.most_common(3)])
            cat_str += f"- {col}: {top_3}\n"

        # 4. Sample Columns (Names)
        all_cols = ", ".join(list(num_stats.keys()) + list(cat_stats.keys()))

        prompt = f"""
[INST] You are an Expert Data Analyst. 
Analyze the metadata below and provide a structured JSON assessment.

DATASET METADATA:
{info_str}
COLUMNS: {all_cols}

KEY STATS:
{num_str}

KEY CATEGORIES:
{cat_str}

TASK:
Return a valid JSON object with these keys:
- "domain": String (e.g., "Retail", "Healthcare", "Finance", "Logistics", "Other")
- "purpose": String (1 sentence on what this data likely tracks)
- "summary": String (3 sentence executive summary of the data scope and volume)
- "key_signals": List of Strings (3 bullet points on data characteristics)
- "recommended_actions": List of Strings (3 short click-to-explore questions, e.g., "Analyze Sales Trends", "Compare Region Performance")

Omit markdown formatting. Return raw JSON.
[/INST]
"""
        return prompt

    def _call_huggingface(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        # Lower temp for strict JSON
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.1, 
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        
        # Parse output
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').strip()
        else:
            raise ValueError("Unexpected API response structure")

    def _parse_json_response(self, text, summary_data):
        """
        Robustly parses JSON from LLM output.
        """
        try:
            # Try to find JSON block if wrapped in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "{" in text:
                text = text[text.find("{"):text.rfind("}")+1]
            
            data = json.loads(text)
            return data
        except:
             # Fallback if JSON is malformed
            return self._generate_fallback_analysis(summary_data)

    def _generate_fallback_analysis(self, data):
        """
        Deterministic expert fallback.
        """
        time.sleep(1) # Simulate thinking
        
        # Heuristic Domain Detection
        cols = (list(data.get("numeric_stats", {}).keys()) + list(data.get("categorical_stats", {}).keys()))
        cols_str = " ".join(cols).lower()
        
        domain = "General Operations"
        if any(x in cols_str for x in ['sales', 'revenue', 'price', 'cost']):
            domain = "Financial / Retail"
        elif any(x in cols_str for x in ['patient', 'diagnosis', 'drug', 'treatment']):
            domain = "Healthcare"
        elif any(x in cols_str for x in ['log', 'error', 'status', 'ip', 'server']):
            domain = "IT / System Logs"
            
        purpose = f"This dataset appears to track {domain.lower()} metrics, containing {data['rows']:,} records."
        
        actions = []
        if data.get("date_col"):
            actions.append("Analyze Trends Over Time")
        if data.get("categorical_stats"):
            actions.append("Compare Categories")
        if data.get("numeric_stats"):
            actions.append("Inspect Numeric Distributions")
            
        return {
            "domain": domain,
            "purpose": purpose,
            "summary": f"The dataset contains {data['rows']:,} records and {data['cols']} variables. It covers the period {data['date_range']}.",
            "key_signals": [
                f"Volume: {data['rows']:,} records processed.",
                f"Completeness: {data['total_missing']:,} missing values detected.",
                f"Complexity: {len(cols)} core variables identified."
            ],
            "recommended_actions": actions
        }
