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
        Returns a structured dictionary with DEEP intelligence.
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

        # 4. Column Names for role classification
        all_cols_list = list(num_stats.keys()) + list(cat_stats.keys())
        all_cols = ", ".join(all_cols_list)

        prompt = f"""
[INST] You are a Senior Principal Analyst.
Interpret the metadata below to provide a "Data Story".

DATASET METADATA:
{info_str}
COLUMNS: {all_cols}

KEY STATS:
{num_str}

KEY CATEGORIES:
{cat_str}

TASK:
Return a valid JSON object with the following structure:
{{
  "domain": "String (e.g., Retail, Finance)",
  "executive_synthesis": {{
    "observation": "2 sentences describing what the data represents structurally.",
    "implication": "2 sentences explaining the strategic value or potential risk in this data."
  }},
  "variable_intelligence": [
     {{ "column": "ColName", "role": "Metric (KPI)" or "Segment (Dimension)" or "Temporal (Time)" or "Identifier" or "Noise", "description": "Short explanation" }}
     // Categorize the top 5 most important columns only
  ],
  "key_signals": [ "String 1", "String 2", "String 3"],
  "recommended_actions": [ "String 1", "String 2", "String 3"]
}}

Be decisive. Classify variables based on their likely use in business intelligence (e.g. Sales is a Metric, Region is a Segment).
Omit markdown formatting. Return raw JSON.
[/INST]
"""
        return prompt

    def _call_huggingface(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.2, 
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
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "{" in text:
                text = text[text.find("{"):text.rfind("}")+1]
            return json.loads(text)
        except:
            return self._generate_fallback_analysis(summary_data)

    def _generate_fallback_analysis(self, data):
        """
        Deterministic expert fallback.
        """
        time.sleep(1) 
        
        # Heuristic Domain Detection
        cols = (list(data.get("numeric_stats", {}).keys()) + list(data.get("categorical_stats", {}).keys()))
        cols_str = " ".join(cols).lower()
        
        domain = "General Operations"
        if any(x in cols_str for x in ['sales', 'revenue', 'price', 'cost']):
            domain = "Financial / Retail"
        elif any(x in cols_str for x in ['patient', 'diagnosis', 'drug']):
            domain = "Healthcare"
            
        # Variable Intelligence Heuristics
        var_intel = []
        if data.get("date_col"):
            var_intel.append({"column": data['date_col'], "role": "Temporal (Time)", "description": "Primary timeline for trend analysis."})
        
        for col in list(data.get("numeric_stats", {}).keys())[:2]:
            var_intel.append({"column": col, "role": "Metric (KPI)", "description": "Key numeric performance indicator."})
            
        for col in list(data.get("categorical_stats", {}).keys())[:2]:
            var_intel.append({"column": col, "role": "Segment (Dimension)", "description": "Categorical grouping factor."})

        return {
            "domain": domain,
            "executive_synthesis": {
                "observation": f"The dataset tracks {len(cols)} variables across {data['rows']:,} records, primarily focused on {domain.lower()} metrics.",
                "implication": "The presence of both time-series and categorical dimensions suggests strong potential for identifying performance drivers and seasonal trends."
            },
            "variable_intelligence": var_intel,
            "key_signals": [
                f"Data Volume: High reliability with {data['rows']:,} samples.",
                f"Completeness: {100 - (data['total_missing']/(max(1,data['rows']*data['cols']))*100):.1f}% valid data points.",
                f"Temporal Coverage: {data['date_range']}."
            ],
            "recommended_actions": ["Analyze Trends Over Time", "Compare Categories", "Inspect Distributions"]
        }
