import requests
import streamlit as st
import time
import json

class AIEngine:
    def __init__(self):
        # Retrieve API Token from Streamlit Secrets
        # User instructions: Add [HF_API_TOKEN] to .streamlit/secrets.toml for deployed apps
        self.api_token = st.secrets.get("HF_API_TOKEN", None)
        # Using a reliable model (Mistral or similar)
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    def generate_executive_summary(self, summary_data):
        """
        Generates a concise executive summary based on the aggregated dataset analysis.
        """
        # Prepare the context for the LLM
        context = self._prepare_context(summary_data)
        
        if self.api_token:
            try:
                return self._call_huggingface(context)
            except Exception as e:
                # Log error (console) but degrade gracefully
                print(f"HF API Error: {e}")
                return self._generate_fallback_summary(summary_data)
        else:
            # No token provided, use deterministic fallback immediately
            return self._generate_fallback_summary(summary_data)

    def _prepare_context(self, data):
        """
        Creates a optimized, compressed prompt string from the aggregated stats.
        """
        # 1. Basic Info
        info_str = f"Dataset: {data['rows']:,} rows, {data['cols']} columns.\n"
        if data['date_range'] != "N/A":
            info_str += f"Date Range: {data['date_range']}.\n"
        
        # 2. Numeric Stats (Top 5 columns to save tokens)
        num_stats = data.get("numeric_stats", {})
        num_str = ""
        for i, (col, stats) in enumerate(num_stats.items()):
            if i >= 5: break
            num_str += f"- {col}: Mean={stats['mean']:.2f}, Max={stats['max']:.2f}\n"

        # 3. Categorical Stats (Top 3 cols, Top 3 values each)
        cat_stats = data.get("categorical_stats", {})
        cat_str = ""
        for i, (col, counter) in enumerate(cat_stats.items()):
            if i >= 3: break
            top_3 = ", ".join([f"{k}({v})" for k,v in counter.most_common(3)])
            cat_str += f"- {col}: {top_3}\n"

        prompt = f"""
[INST] You are a Senior Business Analyst. 
Analyze the following data summary and write an Executive Brief.

CONTEXT:
{info_str}

KEY METRICS:
{num_str}

KEY CATEGORIES:
{cat_str}

INSTRUCTIONS:
1. "Executive Summary": 2 sentences on volume and scope.
2. "Key Insights": 3 bullet points highlighting significant patterns or scale.
3. "Strategic Risks": 2 potential risks based on data quality (missing values) or extreme values.
4. Be professional, concise. Do NOT mention "the provided data" or "AI".
[/INST]
"""
        return prompt

    def _call_huggingface(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 600,
                "temperature": 0.3,
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

    def _generate_fallback_summary(self, data):
        """
        Deterministic template fallback if API fails or no token.
        """
        time.sleep(1) # Simulate complex processing
        
        # Construct dynamic fallback text
        
        # Numeric highlights
        num_insights = []
        for col, stats in list(data.get("numeric_stats", {}).items())[:2]:
            num_insights.append(f"**{col}** averages **{stats['mean']:.1f}** (Max: {stats['max']:.1f}).")
            
        # Missing values check
        total_missing = data.get("total_missing", 0)
        quality_note = "High data quality detected." if total_missing == 0 else f"**{total_missing:,}** missing values detected; data cleaning recommended."
        
        return f"""
### 📊 Automated Executive Brief (Offline Mode)

**Executive Summary**
This dataset contains **{data['rows']:,}** records across **{data['cols']}** variables. The analysis covers the period from **{data['date_range']}**, providing a robust sample for operational review.

**Key Insights**
*   **Volume:** Processed {data['rows']:,} records successfully.
*   **Metric Highlight:** {' '.join(num_insights)}
*   **Data Integrity:** {quality_note}

**Strategic Risks**
*   **Completeness:** Ensure all required fields are populated to improve analysis confidence.
*   **Outliers:** Review maximum values in numeric fields to exclude potential data entry errors.

*(Note: AI interpretation unavailable. Displaying statistical summary.)*
"""
