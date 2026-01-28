import pandas as pd
import requests
import streamlit as st
import time

class AIEngine:
    def __init__(self):
        # Retrieve API Token from Streamlit Secrets
        # User instructions: Add [HF_API_TOKEN] to .streamlit/secrets.toml for deployed apps
        self.api_token = st.secrets.get("HF_API_TOKEN", None)
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    def generate_executive_summary(self, df, summary_stats):
        """
        Generates a concise executive summary based on the dataset.
        """
        # Prepare the context for the LLM
        context = self._prepare_context(df, summary_stats)
        
        if self.api_token:
            try:
                return self._call_huggingface(context)
            except Exception as e:
                # Log error (console) but degrade gracefully
                print(f"HF API Error: {e}")
                return self._generate_fallback_summary(summary_stats)
        else:
            # No token provided, use deterministic fallback immediately
            return self._generate_fallback_summary(summary_stats)

    def _prepare_context(self, df, summary_stats):
        """
        Creates a prompt string from the dataframe stats.
        """
        columns = ", ".join(df.columns[:10]) # Limit columns for context window
        numeric_desc = df.describe().to_markdown() if not df.empty else "No numeric data"
        
        prompt = f"""
        [INST] You are a Senior Business Analyst. 
        Analyze the following dataset summary and write a short, executive-style report.
        
        DATA CONTEXT:
        - Columns: {columns}
        - Total Rows: {summary_stats['rows']}
        - Date Range: {summary_stats['date_range']}
        - Key Statistics:
        {numeric_desc}

        INSTRUCTIONS:
        1. Write a 3-bullet point "Key Insights" section.
        2. Write a 2-bullet point "Risks & Opportunities" section.
        3. Be professional, concise, and direct. 
        4. Do NOT mention you are an AI or looking at a summary.
        [/INST]
        """
        return prompt

    def _call_huggingface(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        
        # Parse output
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').strip()
        else:
            raise ValueError("Unexpected API response structure")

    def _generate_fallback_summary(self, summary_stats):
        """
        Deterministic template fallback if API fails or no token.
        """
        time.sleep(1) # Simulate thinking
        
        return f"""
        ### 📊 Automated Executive Summary
        
        **Key Insights**
        *   **Volume:** The dataset contains **{summary_stats['rows']}** records, providing a substantial sample for analysis.
        *   **Structure:** There are **{summary_stats['cols']}** variables tracked, indicating a multi-dimensional dataset.
        *   **Data Quality:** We detected **{summary_stats['missing_values']}** missing values that may require attention during detailed auditing.
        
        **Risks & Recommendations**
        *   **Completeness:** Ensure all key fields are popularized to maximize analysis accuracy.
        *   **Next Steps:** We recommend drilling down into specific time periods (currently covering {summary_stats['date_range']}) to identify seasonal trends.
        """

