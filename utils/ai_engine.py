"""
InsightBridge AI — AI Analysis Engine
Multi-provider LLM integration with strong rule-based fallback.
Supports: HuggingFace, OpenAI-compatible APIs, and offline mode.
"""
import requests
import streamlit as st
import json
import numpy as np
import pandas as pd


class AIEngine:
    """
    AI-powered analysis engine for datasets.
    Falls back to comprehensive rule-based analysis when no API key is available.
    """

    def __init__(self):
        self.provider = self._detect_provider()
        self.api_token = None
        self.api_url = None

        if self.provider == "openai":
            self.api_token = self._get_secret("OPENAI_API_KEY")
            self.api_url = self._get_secret("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model = self._get_secret("OPENAI_MODEL", "gpt-3.5-turbo")
        elif self.provider == "huggingface":
            self.api_token = self._get_secret("HF_API_TOKEN")
            self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    # ─── Provider Detection ───────────────────────────────────────────────────

    def _detect_provider(self) -> str:
        """Auto-detect which LLM provider is configured."""
        explicit = self._get_secret("LLM_PROVIDER", "").lower()
        if explicit in ("openai", "huggingface"):
            return explicit
        if self._get_secret("OPENAI_API_KEY"):
            return "openai"
        if self._get_secret("HF_API_TOKEN"):
            return "huggingface"
        return "fallback"

    @staticmethod
    def _get_secret(key: str, default: str = None):
        """Safely retrieve a secret from Streamlit secrets or environment."""
        import os
        try:
            return st.secrets.get(key, None) or os.environ.get(key, default)
        except Exception:
            import os
            return os.environ.get(key, default)

    # ─── Public Analysis Methods ──────────────────────────────────────────────

    def analyze_dataset_context(self, summary_data: dict) -> dict:
        """
        Phase 1 assessment: Domain, synthesis, variable intelligence, signals.
        Compatible with the legacy data loader summary format.
        """
        if self.provider != "fallback":
            try:
                prompt = self._build_context_prompt(summary_data)
                raw = self._call_llm(prompt)
                parsed = self._parse_json_response(raw, summary_data)
                if parsed:
                    return parsed
            except Exception as e:
                print(f"LLM Error (analyze_dataset_context): {e}")
        return self._generate_fallback_analysis(summary_data)

    def deep_dive_analysis(self, df: pd.DataFrame, profile: dict, question: str = "") -> dict:
        """
        Generate a deep-dive analysis of the dataset.
        Returns a dict with: summary, trends, implications, limitations, questions, sources.
        """
        context = self._build_deep_dive_context(df, profile)

        if question:
            context += f"\n\nUSER QUESTION: {question}"

        if self.provider != "fallback":
            try:
                prompt = self._build_deep_dive_prompt(context)
                raw = self._call_llm(prompt)
                parsed = self._parse_deep_dive_response(raw)
                if parsed:
                    return parsed
            except Exception as e:
                print(f"LLM Error (deep_dive): {e}")

        return self._generate_fallback_deep_dive(df, profile, question)

    def generate_executive_summary(self, df: pd.DataFrame, profile: dict) -> str:
        """Generate a complete executive summary as Markdown text."""
        context = self._build_deep_dive_context(df, profile)

        if self.provider != "fallback":
            try:
                prompt = self._build_exec_summary_prompt(context)
                raw = self._call_llm(prompt)
                if raw and len(raw) > 50:
                    return raw
            except Exception as e:
                print(f"LLM Error (exec_summary): {e}")

        return self._generate_fallback_executive_summary(df, profile)

    def get_provider_status(self) -> dict:
        """Return current provider status for UI display."""
        return {
            "provider": self.provider,
            "label": {
                "openai": "🟢 OpenAI Connected",
                "huggingface": "🟡 HuggingFace Connected",
                "fallback": "⚪ Offline (Rule-Based Analysis)",
            }.get(self.provider, "⚪ Offline"),
            "description": {
                "openai": "Full AI analysis powered by OpenAI",
                "huggingface": "AI analysis via HuggingFace Inference API",
                "fallback": "Statistical analysis without LLM — add an API key for AI insights",
            }.get(self.provider, ""),
        }

    # ─── LLM Call Dispatchers ─────────────────────────────────────────────────

    def _call_llm(self, prompt: str) -> str:
        """Route to the correct API based on provider."""
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "huggingface":
            return self._call_huggingface(prompt)
        return ""

    def _call_openai(self, prompt: str) -> str:
        """Call an OpenAI-compatible API."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a Senior Principal Data Analyst. Be precise, factual, and concise. Never invent facts. Clearly separate observations from assumptions."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
        }

        resp = requests.post(
            f"{self.api_url}/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def _call_huggingface(self, prompt: str) -> str:
        """Call the HuggingFace Inference API."""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": f"[INST] {prompt} [/INST]",
            "parameters": {"max_new_tokens": 1200, "temperature": 0.2, "return_full_text": False},
        }

        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        raise ValueError("Unexpected HuggingFace response structure")

    # ─── Prompt Builders ──────────────────────────────────────────────────────

    def _build_context_prompt(self, data: dict) -> str:
        """Build the dataset context analysis prompt."""
        info = f"Dataset: {data['rows']:,} rows, {data['cols']} columns.\n"
        if data.get("date_range", "N/A") != "N/A":
            info += f"Date Range: {data['date_range']}.\n"

        num_str = ""
        for i, (col, stats) in enumerate(data.get("numeric_stats", {}).items()):
            if i >= 5:
                break
            num_str += f"- {col}: Mean={stats.get('mean', 0):.2f}, Max={stats.get('max', 0):.2f}\n"

        cat_str = ""
        for i, (col, counter) in enumerate(data.get("categorical_stats", {}).items()):
            if i >= 5:
                break
            top_3 = ", ".join([str(k) for k, v in counter.most_common(3)])
            cat_str += f"- {col}: {top_3}\n"

        all_cols = list(data.get("numeric_stats", {}).keys()) + list(data.get("categorical_stats", {}).keys())

        return f"""Interpret the metadata below to provide a Data Story.

DATASET METADATA:
{info}
COLUMNS: {', '.join(all_cols)}

KEY STATS:
{num_str}

KEY CATEGORIES:
{cat_str}

Return a valid JSON object with this structure:
{{
  "domain": "String (e.g., Retail, Finance)",
  "executive_synthesis": {{
    "observation": "2 sentences describing what the data represents structurally.",
    "implication": "2 sentences explaining the strategic value or potential risk."
  }},
  "variable_intelligence": [
     {{ "column": "ColName", "role": "Metric (KPI)" or "Segment (Dimension)" or "Temporal (Time)" or "Identifier" or "Noise", "description": "Short explanation" }}
  ],
  "key_signals": [ "String 1", "String 2", "String 3"],
  "recommended_actions": [ "String 1", "String 2", "String 3"]
}}

Be decisive. Classify variables by their likely business use. Return raw JSON only."""

    def _build_deep_dive_context(self, df: pd.DataFrame, profile: dict) -> str:
        """Build context string from DataFrame and profile."""
        shape = profile.get("shape", {})
        missing = profile.get("missing_summary", {})
        dups = profile.get("duplicates", {})

        context = f"Dataset: {shape.get('rows', 0):,} rows × {shape.get('columns', 0)} columns\n"
        context += f"Data Completeness: {missing.get('completeness_pct', 0)}%\n"
        context += f"Duplicate Rows: {dups.get('duplicate_rows', 0)}\n\n"

        # Numeric column stats
        num_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "numeric"]
        if num_cols:
            context += "NUMERIC COLUMNS:\n"
            for col in num_cols[:6]:
                stats = profile["columns"][col].get("stats", {})
                outliers = profile["columns"][col].get("outliers", {})
                context += f"- {col}: Mean={stats.get('mean', 0):.2f}, Median={stats.get('median', 0):.2f}, "
                context += f"Std={stats.get('std', 0):.2f}, Skew={stats.get('skew', 0):.2f}, "
                context += f"Outliers={outliers.get('count', 0)} ({outliers.get('pct', 0):.1f}%)\n"

        # Categorical column stats
        cat_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "categorical"]
        if cat_cols:
            context += "\nCATEGORICAL COLUMNS:\n"
            for col in cat_cols[:5]:
                stats = profile["columns"][col].get("stats", {})
                top = list(stats.get("top_values", {}).keys())[:3]
                context += f"- {col}: Top values = {', '.join(str(t) for t in top)}\n"

        # Datetime columns
        dt_cols = profile.get("datetime_columns", [])
        if dt_cols:
            context += f"\nTIME COLUMNS: {', '.join(dt_cols)}\n"
            for col in dt_cols:
                stats = profile.get("columns", {}).get(col, {}).get("stats", {})
                if stats:
                    context += f"  Range: {stats.get('min_date', 'N/A')} to {stats.get('max_date', 'N/A')}\n"

        return context

    def _build_deep_dive_prompt(self, context: str) -> str:
        """Build the deep dive analysis prompt."""
        return f"""Analyze this dataset and provide actionable insights.

{context}

Return a JSON object with these keys:
{{
  "summary": "2-3 sentence overview of what the data shows",
  "trends": ["trend 1", "trend 2", "trend 3"],
  "outliers_and_anomalies": ["finding 1", "finding 2"],
  "business_implications": ["implication 1", "implication 2", "implication 3"],
  "limitations": ["limitation 1", "limitation 2"],
  "follow_up_questions": ["question 1", "question 2", "question 3"],
  "recommended_data_sources": ["source 1", "source 2"]
}}

RULES:
- Clearly separate observations from assumptions
- Do not give medical, legal, or financial advice
- Say when more data is needed
- Base analysis only on the statistics provided
Return raw JSON only."""

    def _build_exec_summary_prompt(self, context: str) -> str:
        """Build executive summary prompt."""
        return f"""Write a professional executive summary report in Markdown format for the following dataset.

{context}

Include these sections:
## Executive Summary
Brief 2-3 sentence overview.

## Key Findings
Bulleted list of the most important discoveries.

## Data Quality Assessment
Completeness, duplicates, outlier summary.

## Trends & Patterns
Identified trends with supporting statistics.

## Recommendations
Actionable next steps based on the data.

## Limitations & Disclaimers
What the data cannot tell us. Note that this is automated analysis and should be verified.

RULES:
- Be concise and professional
- Use specific numbers from the data
- Clearly separate observations from assumptions
- Do not give medical, legal, or financial advice
- Mention that this is an automated analysis"""

    # ─── Response Parsers ─────────────────────────────────────────────────────

    def _parse_json_response(self, text: str, summary_data: dict) -> dict:
        """Parse JSON from LLM response text."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "{" in text:
                text = text[text.find("{"):text.rfind("}") + 1]
            return json.loads(text)
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            return None

    def _parse_deep_dive_response(self, text: str) -> dict:
        """Parse deep dive JSON response."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "{" in text:
                text = text[text.find("{"):text.rfind("}") + 1]
            result = json.loads(text)
            # Validate expected keys
            required = ["summary", "trends", "business_implications"]
            if any(k in result for k in required):
                return result
            return None
        except (json.JSONDecodeError, ValueError):
            return None

    # ─── Fallback Analysis (Rule-Based) ───────────────────────────────────────

    def _generate_fallback_analysis(self, data: dict) -> dict:
        """Comprehensive rule-based dataset analysis when no LLM is available."""
        cols = list(data.get("numeric_stats", {}).keys()) + list(data.get("categorical_stats", {}).keys())
        cols_str = " ".join(cols).lower()

        # Domain detection heuristics
        domain = "General Operations"
        if any(x in cols_str for x in ["sales", "revenue", "price", "cost", "profit", "margin"]):
            domain = "Financial / Retail"
        elif any(x in cols_str for x in ["patient", "diagnosis", "drug", "health", "disease", "mortality"]):
            domain = "Healthcare"
        elif any(x in cols_str for x in ["gdp", "population", "inflation", "unemployment", "income"]):
            domain = "Economic / Demographic"
        elif any(x in cols_str for x in ["student", "grade", "enrollment", "school"]):
            domain = "Education"
        elif any(x in cols_str for x in ["click", "impression", "conversion", "campaign"]):
            domain = "Marketing / Advertising"

        # Variable intelligence
        var_intel = []
        if data.get("date_col"):
            var_intel.append({"column": data["date_col"], "role": "Temporal (Time)", "description": "Primary timeline for trend analysis."})
        for col in list(data.get("numeric_stats", {}).keys())[:3]:
            var_intel.append({"column": col, "role": "Metric (KPI)", "description": "Key numeric performance indicator."})
        for col in list(data.get("categorical_stats", {}).keys())[:2]:
            var_intel.append({"column": col, "role": "Segment (Dimension)", "description": "Categorical grouping factor."})

        completeness = 100 - (data["total_missing"] / max(1, data["rows"] * data["cols"]) * 100)

        # Key signals based on data characteristics
        signals = [
            f"Data Volume: {data['rows']:,} records provide {'strong' if data['rows'] > 1000 else 'moderate'} statistical reliability.",
            f"Completeness: {completeness:.1f}% of data points are valid.",
            f"Dimensionality: {data['cols']} variables enable {'multi-factor' if data['cols'] > 8 else 'focused'} analysis.",
        ]
        if data.get("date_range", "N/A") != "N/A":
            signals.append(f"Temporal Coverage: {data['date_range']}.")

        return {
            "domain": domain,
            "executive_synthesis": {
                "observation": f"This {domain.lower()} dataset contains {data['rows']:,} records across {len(cols)} variables, with {completeness:.0f}% data completeness.",
                "implication": "The data structure supports quantitative analysis. " + (
                    "Time-series dimensions allow for trend identification and forecasting." if data.get("date_col")
                    else "The cross-sectional structure is suited for comparative and distribution analysis."
                ),
            },
            "variable_intelligence": var_intel,
            "key_signals": signals,
            "recommended_actions": ["Analyze Trends Over Time", "Compare Categories", "Inspect Distributions"],
        }

    def _generate_fallback_deep_dive(self, df: pd.DataFrame, profile: dict, question: str = "") -> dict:
        """Comprehensive rule-based deep dive analysis."""
        shape = profile.get("shape", {})
        missing = profile.get("missing_summary", {})
        dups = profile.get("duplicates", {})

        # Analyze numeric columns
        trends = []
        anomalies = []
        implications = []

        num_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "numeric"]
        for col in num_cols[:4]:
            stats = profile["columns"][col].get("stats", {})
            outliers = profile["columns"][col].get("outliers", {})

            skew = stats.get("skew", 0)
            if abs(skew) > 1:
                direction = "right-skewed (positive)" if skew > 0 else "left-skewed (negative)"
                trends.append(f"**{col}** is {direction} (skew={skew:.2f}), suggesting {'a few very high values' if skew > 0 else 'a few very low values'} may be pulling the average.")

            if outliers.get("count", 0) > 0:
                anomalies.append(f"**{col}** has {outliers['count']} outliers ({outliers['pct']:.1f}% of values) outside the expected range [{outliers['lower_bound']:.1f}, {outliers['upper_bound']:.1f}].")

            cv = stats.get("cv", 0)
            if cv > 100:
                implications.append(f"**{col}** shows high variability (CV={cv:.0f}%), indicating significant spread in the data that warrants investigation.")

        # Data quality implications
        completeness_pct = missing.get("completeness_pct", 100)
        if completeness_pct < 95:
            implications.append(f"Data completeness is {completeness_pct}%, which may introduce bias in analysis. Consider imputation or filtering strategies.")
        if dups.get("duplicate_rows", 0) > 0:
            implications.append(f"Found {dups['duplicate_rows']} duplicate rows ({dups['duplicate_pct']:.1f}%). These should be investigated and potentially removed.")

        if not trends:
            trends = ["No significant statistical trends detected in the available numeric data."]
        if not anomalies:
            anomalies = ["No major outliers or anomalies detected using IQR analysis."]
        if not implications:
            implications = ["Data appears well-structured for standard analytical workflows."]

        summary = (
            f"This dataset contains {shape.get('rows', 0):,} records across {shape.get('columns', 0)} variables. "
            f"Data completeness is {completeness_pct}%. "
            f"{'Time-series analysis is possible with detected date columns.' if profile.get('datetime_columns') else 'No temporal dimensions detected; analysis is cross-sectional.'}"
        )

        return {
            "summary": summary,
            "trends": trends,
            "outliers_and_anomalies": anomalies,
            "business_implications": implications,
            "limitations": [
                "This is automated statistical analysis and should be validated by domain experts.",
                "Correlation does not imply causation — additional investigation is needed for causal claims.",
                "Analysis is based on the provided dataset and may not reflect broader population trends.",
            ],
            "follow_up_questions": [
                "What business decisions depend on this data?",
                "Are there external factors that could explain the patterns observed?",
                "What additional data sources would provide useful context?",
            ],
            "recommended_data_sources": [
                "World Bank Open Data — for macroeconomic context",
                "U.S. Census Bureau — for demographic baselines",
                "Industry-specific benchmarking reports",
            ],
        }

    def _generate_fallback_executive_summary(self, df: pd.DataFrame, profile: dict) -> str:
        """Generate a rule-based executive summary in Markdown."""
        shape = profile.get("shape", {})
        missing = profile.get("missing_summary", {})
        dups = profile.get("duplicates", {})

        num_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "numeric"]
        cat_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "categorical"]
        dt_cols = profile.get("datetime_columns", [])

        # Key findings
        findings = []
        for col in num_cols[:3]:
            stats = profile["columns"][col].get("stats", {})
            findings.append(
                f"**{col}**: Mean = {stats.get('mean', 0):,.2f}, "
                f"Median = {stats.get('median', 0):,.2f}, "
                f"Range = [{stats.get('min', 0):,.2f}, {stats.get('max', 0):,.2f}]"
            )

        for col in cat_cols[:2]:
            stats = profile["columns"][col].get("stats", {})
            mode = stats.get("mode", "N/A")
            unique = stats.get("unique_count", 0)
            findings.append(f"**{col}**: {unique} unique values, most common = \"{mode}\"")

        findings_md = "\n".join(f"- {f}" for f in findings) if findings else "- No significant findings detected."

        # Outlier summary
        outlier_notes = []
        for col in num_cols:
            outliers = profile.get("columns", {}).get(col, {}).get("outliers", {})
            if outliers.get("count", 0) > 0:
                outlier_notes.append(f"- **{col}**: {outliers['count']} outliers ({outliers['pct']:.1f}%)")
        outlier_md = "\n".join(outlier_notes) if outlier_notes else "- No significant outliers detected."

        return f"""## Executive Summary

This dataset contains **{shape.get('rows', 0):,} records** across **{shape.get('columns', 0)} variables**, including {len(num_cols)} numeric, {len(cat_cols)} categorical, and {len(dt_cols)} temporal columns.

## Key Findings

{findings_md}

## Data Quality Assessment

- **Completeness**: {missing.get('completeness_pct', 100)}% of all data points are valid
- **Duplicate Rows**: {dups.get('duplicate_rows', 0)} ({dups.get('duplicate_pct', 0):.1f}%)
- **Columns with Missing Data**: {len(missing.get('columns_with_missing', {}))}

## Outlier Analysis

{outlier_md}

## Recommendations

1. {'Investigate and clean duplicate records before analysis.' if dups.get('duplicate_rows', 0) > 0 else 'No duplicate cleaning needed.'}
2. {'Address missing values in columns with >10% missing data.' if missing.get('completeness_pct', 100) < 90 else 'Data completeness is strong.'}
3. Validate outliers to determine if they represent genuine extreme values or data entry errors.
4. {'Use time-series analysis to identify seasonal patterns and trends.' if dt_cols else 'Consider adding temporal dimensions for trend analysis.'}

## Limitations & Disclaimers

- This is an **automated statistical analysis** and should be reviewed by domain experts.
- Correlation does not imply causation.
- This report does not constitute medical, legal, or financial advice.
- Analysis reflects only the data provided and may not be representative of broader trends.

---
*Generated by InsightBridge AI • Automated Analysis Report*
"""
