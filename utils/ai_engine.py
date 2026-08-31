"""
InsightBridge AI — AI Analysis Engine
Multi-provider LLM integration with caching, retry resiliency, and robust rule-based fallback.
Supports: OpenAI-compatible APIs, Hugging Face Inference API, and offline mode.
"""
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Attempt to load local .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import streamlit as st
except ImportError:
    st = None

logger = logging.getLogger(__name__)


def _create_resilient_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    """Create and configure a requests.Session with exponential backoff retries."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class AIEngine:
    """
    AI-powered analysis engine for datasets.
    Provides automated domain detection, executive synthesis, and deep-dive analysis.
    Falls back to deterministic rule-based analysis when no LLM API key is configured.
    """

    def __init__(self) -> None:
        """Initialize the AI engine with provider detection, credentials, and network session."""
        self.provider: str = self._detect_provider()
        self.api_token: Optional[str] = None
        self.api_url: Optional[str] = None
        self.model: Optional[str] = None
        self._session: requests.Session = _create_resilient_session()
        self._cache: Dict[str, Any] = {}

        if self.provider == "openai":
            self.api_token = self._get_secret("OPENAI_API_KEY")
            self.api_url = self._get_secret("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model = self._get_secret("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "huggingface":
            self.api_token = self._get_secret("HF_API_TOKEN")
            self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    # ─── Provider Detection ───────────────────────────────────────────────────

    def _detect_provider(self) -> str:
        """
        Auto-detect which LLM provider is configured in environment or Streamlit secrets.

        Returns:
            str: 'openai', 'huggingface', or 'fallback'.
        """
        explicit = (self._get_secret("LLM_PROVIDER") or "").strip().lower()
        if explicit in ("openai", "huggingface"):
            return explicit
        if self._get_secret("OPENAI_API_KEY"):
            return "openai"
        if self._get_secret("HF_API_TOKEN"):
            return "huggingface"
        return "fallback"

    @staticmethod
    def _get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Safely retrieve a secret from Streamlit secrets or environment variables.

        Args:
            key: Secret configuration name.
            default: Default value if key is not found.

        Returns:
            Optional[str]: Retrieved configuration value or default.
        """
        if st is not None:
            try:
                secret_val = st.secrets.get(key, None)
                if secret_val:
                    return str(secret_val)
            except Exception:
                pass
        return os.environ.get(key, default)

    # ─── Caching Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA256 digest for cache keys."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    # ─── Public Analysis Methods ──────────────────────────────────────────────

    def analyze_dataset_context(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1 assessment: Domain classification, synthesis, variable intelligence, and key signals.

        Args:
            summary_data: Dictionary containing statistical summary of the uploaded data.

        Returns:
            Dict[str, Any]: Structured intelligence dictionary with domain, synthesis, and signals.
        """
        if self.provider != "fallback":
            try:
                prompt = self._build_context_prompt(summary_data)
                cache_key = f"ctx_{self._compute_hash(prompt)}"
                if cache_key in self._cache:
                    return self._cache[cache_key]

                raw = self._call_llm(prompt)
                parsed = self._parse_json_response(raw, summary_data)
                if parsed:
                    self._cache[cache_key] = parsed
                    return parsed
            except Exception as e:
                logger.warning("LLM call failed for dataset context: %s. Falling back to rule-based engine.", e)
        return self._generate_fallback_analysis(summary_data)

    def deep_dive_analysis(
        self,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        question: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a deep-dive analysis of the dataset with trends, implications, and anomaly findings.

        Args:
            df: The active pandas DataFrame.
            profile: Profile dictionary generated by generate_full_profile().
            question: Optional specific business question from the user.

        Returns:
            Dict[str, Any]: Structured deep-dive report containing summary, trends, and recommendations.
        """
        context = self._build_deep_dive_context(df, profile)
        if question:
            context += f"\n\nUSER QUESTION: {question}"

        if self.provider != "fallback":
            try:
                prompt = self._build_deep_dive_prompt(context)
                cache_key = f"dd_{self._compute_hash(prompt)}"
                if cache_key in self._cache:
                    return self._cache[cache_key]

                raw = self._call_llm(prompt)
                parsed = self._parse_deep_dive_response(raw)
                if parsed:
                    self._cache[cache_key] = parsed
                    return parsed
            except Exception as e:
                logger.warning("LLM call failed for deep dive: %s. Falling back to rule-based engine.", e)

        return self._generate_fallback_deep_dive(df, profile, question)

    def generate_executive_summary(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        """
        Generate a complete executive summary report formatted in GitHub-Flavored Markdown.

        Args:
            df: The active pandas DataFrame.
            profile: Profile dictionary generated by generate_full_profile().

        Returns:
            str: Markdown-formatted executive summary text.
        """
        context = self._build_deep_dive_context(df, profile)

        if self.provider != "fallback":
            try:
                prompt = self._build_exec_summary_prompt(context)
                cache_key = f"exec_{self._compute_hash(prompt)}"
                if cache_key in self._cache:
                    return self._cache[cache_key]

                raw = self._call_llm(prompt)
                if raw and len(raw) > 50:
                    self._cache[cache_key] = raw
                    return raw
            except Exception as e:
                logger.warning("LLM call failed for executive summary: %s. Falling back to rule-based engine.", e)

        return self._generate_fallback_executive_summary(df, profile)

    def get_provider_status(self) -> Dict[str, str]:
        """
        Return current provider status for UI display.

        Returns:
            Dict[str, str]: Status details with provider, label, and descriptive status.
        """
        return {
            "provider": self.provider,
            "label": {
                "openai": "🟢 OpenAI Connected",
                "huggingface": "🟡 HuggingFace Connected",
                "fallback": "⚪ Offline (Rule-Based Analysis)",
            }.get(self.provider, "⚪ Offline"),
            "description": {
                "openai": f"Full AI analysis powered by OpenAI ({self.model or 'gpt-4o-mini'})",
                "huggingface": "AI analysis via HuggingFace Inference API",
                "fallback": "Statistical analysis without LLM — add an API key for AI insights",
            }.get(self.provider, ""),
        }

    # ─── LLM Call Dispatchers ─────────────────────────────────────────────────

    def _call_llm(self, prompt: str) -> str:
        """
        Route prompt to the active provider API.

        Args:
            prompt: Text prompt to send to the model.

        Returns:
            str: Raw generated text response.
        """
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "huggingface":
            return self._call_huggingface(prompt)
        return ""

    def _call_openai(self, prompt: str) -> str:
        """Call an OpenAI-compatible API endpoint with timeout and error handling."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a Senior Principal Data Analyst. Be precise, factual, and concise. "
                        "Never invent facts. Clearly separate observations from assumptions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }

        resp = self._session.post(
            f"{self.api_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def _call_huggingface(self, prompt: str) -> str:
        """Call the HuggingFace Inference API with timeout and validation."""
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": f"[INST] {prompt} [/INST]",
            "parameters": {"max_new_tokens": 1200, "temperature": 0.2, "return_full_text": False},
        }

        resp = self._session.post(self.api_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        raise ValueError("Unexpected HuggingFace response structure")

    # ─── Prompt Builders ──────────────────────────────────────────────────────

    def _build_context_prompt(self, data: Dict[str, Any]) -> str:
        """Build the dataset context analysis prompt from statistical metadata."""
        info = f"Dataset: {data.get('rows', 0):,} rows, {data.get('cols', 0)} columns.\n"
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
            if hasattr(counter, "most_common"):
                top_items = counter.most_common(3)
            elif isinstance(counter, dict):
                top_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:3]
            else:
                top_items = []
            top_3 = ", ".join([str(k) for k, _ in top_items])
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
  "domain": "String (e.g., Retail, Finance, Healthcare, Operations)",
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

    def _build_deep_dive_context(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        """Build context string from DataFrame and profile dictionary."""
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

    def _parse_json_response(self, text: str, summary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and validate JSON from LLM response text."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "{" in text and "}" in text:
                text = text[text.find("{"):text.rfind("}") + 1]
            return json.loads(text)
        except (json.JSONDecodeError, ValueError, KeyError, IndexError):
            return None

    def _parse_deep_dive_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse and validate deep dive JSON response."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "{" in text and "}" in text:
                text = text[text.find("{"):text.rfind("}") + 1]
            result = json.loads(text)
            required = ["summary", "trends", "business_implications"]
            if any(k in result for k in required):
                return result
            return None
        except (json.JSONDecodeError, ValueError):
            return None

    # ─── Fallback Analysis (Rule-Based) ───────────────────────────────────────

    def _generate_fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive rule-based dataset analysis when no LLM is available."""
        cols = list(data.get("numeric_stats", {}).keys()) + list(data.get("categorical_stats", {}).keys())
        cols_str = " ".join(cols).lower()

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

        var_intel = []
        if data.get("date_col"):
            var_intel.append({
                "column": data["date_col"],
                "role": "Temporal (Time)",
                "description": "Primary timeline for trend analysis.",
            })
        for col in list(data.get("numeric_stats", {}).keys())[:3]:
            var_intel.append({
                "column": col,
                "role": "Metric (KPI)",
                "description": "Key numeric performance indicator.",
            })
        for col in list(data.get("categorical_stats", {}).keys())[:2]:
            var_intel.append({
                "column": col,
                "role": "Segment (Dimension)",
                "description": "Categorical grouping factor.",
            })

        total_cells = max(1, data.get("rows", 1) * max(1, data.get("cols", 1)))
        completeness = max(0.0, min(100.0, 100.0 - (data.get("total_missing", 0) / total_cells * 100)))

        signals = [
            f"Data Volume: {data.get('rows', 0):,} records provide {'strong' if data.get('rows', 0) > 1000 else 'moderate'} statistical reliability.",
            f"Completeness: {completeness:.1f}% of data points are valid.",
            f"Dimensionality: {data.get('cols', 0)} variables enable {'multi-factor' if data.get('cols', 0) > 8 else 'focused'} analysis.",
        ]
        if data.get("date_range", "N/A") != "N/A":
            signals.append(f"Temporal Coverage: {data['date_range']}.")

        return {
            "domain": domain,
            "executive_synthesis": {
                "observation": f"This {domain.lower()} dataset contains {data.get('rows', 0):,} records across {len(cols)} variables, with {completeness:.0f}% data completeness.",
                "implication": (
                    "The data structure supports quantitative analysis. "
                    + ("Time-series dimensions allow for trend identification and forecasting." if data.get("date_col")
                       else "The cross-sectional structure is suited for comparative and distribution analysis.")
                ),
            },
            "variable_intelligence": var_intel,
            "key_signals": signals,
            "recommended_actions": ["Analyze Trends Over Time", "Compare Categories", "Inspect Distributions"],
        }

    def _generate_fallback_deep_dive(
        self,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        question: str = "",
    ) -> Dict[str, Any]:
        """Comprehensive rule-based deep dive analysis."""
        shape = profile.get("shape", {})
        missing = profile.get("missing_summary", {})
        dups = profile.get("duplicates", {})

        trends: List[str] = []
        anomalies: List[str] = []
        implications: List[str] = []

        num_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "numeric"]
        for col in num_cols[:4]:
            stats = profile.get("columns", {}).get(col, {}).get("stats", {})
            outliers = profile.get("columns", {}).get(col, {}).get("outliers", {})

            skew = stats.get("skew", 0)
            if abs(skew) > 1:
                direction = "right-skewed (positive)" if skew > 0 else "left-skewed (negative)"
                trends.append(
                    f"**{col}** is {direction} (skew={skew:.2f}), suggesting "
                    f"{'a few very high values' if skew > 0 else 'a few very low values'} may be pulling the average."
                )

            if outliers.get("count", 0) > 0:
                anomalies.append(
                    f"**{col}** has {outliers['count']} outliers ({outliers['pct']:.1f}% of values) "
                    f"outside the expected range [{outliers.get('lower_bound', 0):.1f}, {outliers.get('upper_bound', 0):.1f}]."
                )

            cv = stats.get("cv", 0)
            if cv > 100:
                implications.append(
                    f"**{col}** shows high variability (CV={cv:.0f}%), indicating significant spread that warrants investigation."
                )

        completeness_pct = missing.get("completeness_pct", 100)
        if completeness_pct < 95:
            implications.append(
                f"Data completeness is {completeness_pct}%, which may introduce bias. Consider imputation or filtering strategies."
            )
        if dups.get("duplicate_rows", 0) > 0:
            implications.append(
                f"Found {dups['duplicate_rows']} duplicate rows ({dups.get('duplicate_pct', 0):.1f}%). These should be investigated and potentially removed."
            )

        if not trends:
            trends = ["No significant statistical skew or anomalies detected in the available numeric data."]
        if not anomalies:
            anomalies = ["No major outliers detected using IQR standard analysis."]
        if not implications:
            implications = ["Data appears well-structured for standard business analytical workflows."]

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

    def _generate_fallback_executive_summary(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        """Generate a rule-based executive summary in Markdown."""
        shape = profile.get("shape", {})
        missing = profile.get("missing_summary", {})
        dups = profile.get("duplicates", {})

        num_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "numeric"]
        cat_cols = [c for c, info in profile.get("columns", {}).items() if info.get("type") == "categorical"]
        dt_cols = profile.get("datetime_columns", [])

        findings = []
        for col in num_cols[:3]:
            stats = profile.get("columns", {}).get(col, {}).get("stats", {})
            findings.append(
                f"**{col}**: Mean = {stats.get('mean', 0):,.2f}, "
                f"Median = {stats.get('median', 0):,.2f}, "
                f"Range = [{stats.get('min', 0):,.2f}, {stats.get('max', 0):,.2f}]"
            )

        for col in cat_cols[:2]:
            stats = profile.get("columns", {}).get(col, {}).get("stats", {})
            mode = stats.get("mode", "N/A")
            unique = stats.get("unique_count", 0)
            findings.append(f"**{col}**: {unique} unique values, most common = \"{mode}\"")

        findings_md = "\n".join(f"- {f}" for f in findings) if findings else "- No significant findings detected."

        outlier_notes = []
        for col in num_cols:
            outliers = profile.get("columns", {}).get(col, {}).get("outliers", {})
            if outliers.get("count", 0) > 0:
                outlier_notes.append(f"- **{col}**: {outliers['count']} outliers ({outliers.get('pct', 0):.1f}%)")
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
