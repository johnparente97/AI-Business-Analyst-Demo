import pandas as pd
import numpy as np
import time
import json
import requests
import streamlit as st

class AIEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, query, df):
        """
        Main entry point for AI analysis.
        Decides whether to use Real AI or Mock AI based on API Key presence.
        """
        if self.api_key and self.api_key.startswith("sk-"):
            try:
                return self._call_openai(query, df)
            except Exception as e:
                st.warning(f"OpenAI API Error: {e}. Falling back to experimental mock engine.")
                return self._generate_mock_response(query, df)
        else:
            return self._generate_mock_response(query, df)

    def _call_openai(self, query, df):
        """
        Calls OpenAI API via requests for browser compatibility (st-lite).
        """
        # Prepare data context (lite version)
        data_preview = df.head(5).to_markdown(index=False)
        columns = ", ".join(df.columns)
        
        system_prompt = f"""
        You are InsightBridge, an expert AI Business Analyst. 
        Your goal is to answer the user's business question based on the provided dataset.
        
        DATA CONTEXT:
        - Columns: {columns}
        - Sample Data:
        {data_preview}
        
        RESPONSE FORMAT:
        Return a valid JSON object with the following structure:
        {{
            "content": "Markdown formatted analysis. Use bullet points for key insights, risks, and recommended actions.",
            "chart_type": "trend" | "bar" | "distribution" | null
        }}
        
        RULES:
        1. Be professional, concise, and executive.
        2. Identify the best chart type to visualize the answer (if applicable).
        3. Do not mention that you are an AI or looking at a sample.
        """
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        content_str = result['choices'][0]['message']['content']
        parsed = json.loads(content_str)
        
        return parsed

    def _generate_mock_response(self, query, df):
        """
        Highly realistic mock engine for demo purposes using keyword heuristics.
        """
        time.sleep(0.6) # Slight branding delay
        
        q = query.lower()
        
        # Dynamic extraction if possible
        row_count = len(df)
        
        response = {
            "content": "",
            "chart_type": None
        }
        
        if "trend" in q or "over time" in q:
            response["chart_type"] = "trend"
            response["content"] = f"""
### 📈 Trend Analysis
**Key Insight:** Analysis of the {row_count} records shows a significant upward trajectory in the primary metrics over the reported period.

*   **Growth:** Consistent month-over-month growth of **~8.5%**.
*   **Seasonality:** Data indicates peak activity during Q3.
*   **Volatility:** Low variance suggests a stable operational baseline.

**Recommendation:** Capitalize on the Q3 momentum by increasing inventory or resource allocation 30 days prior.
            """
            
        elif "risk" in q or "worry" in q or "issue" in q:
            response["chart_type"] = "distribution"
            response["content"] = """
### ⚠️ Risk Assessment
**Critical Finding:** Detected anomalies in the lower quartile of the performance distribution.

*   **Churn Risk:** Engagement metrics for the 'Basic' tier have declined by **5%**.
*   **Cost Efficiency:** Operational overhead has increased slightly faster than revenue in the last cycle.

**Action Required:**
1.  Audit expense reports for the last 30 days.
2.  Launch a retention campaign targeting the 'Basic' cohort immediately.
            """
            
        elif "best" in q or "grow" in q or "opportunity" in q:
            response["chart_type"] = "bar"
            response["content"] = """
### 🌱 Growth Opportunities
**Top Performer:** The 'Enterprise' segment is outperforming all others, contributing **40% of total value** despite being only 15% of volume.

*   **Conversion:** Mobile traffic conversion rate is **2x** higher than desktop.
*   **Untapped Market:** Regional data shows under-penetration in the West Coast market.

**Strategic Move:** Shift ad spend to prioritize mobile-first creatives and double down on Enterprise sales enablement.
            """
            
        else:
            response["content"] = f"""
### 📊 General Analysis
I've analyzed the dataset containing **{row_count} rows** and **{len(df.columns)} columns**.

*   **Data Health:** The data appears consistent with high fill rates.
*   **Correlations:** Strong correlation observed between volume metrics and total value.

To get more specific insights, try asking about **Trends**, **Risks**, or **Top Performers**.
            """
            
        return response

