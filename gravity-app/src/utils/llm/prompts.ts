import type { FieldStat } from '../analyze'
import type { DataRecord } from '../../types/data'
import { formatNumPrecise } from '../format'

export function buildSystemPrompt(
  source: string,
  fieldStats: FieldStat[],
  records: DataRecord[]
): string {
  const count = records.length

  const numericSummary = fieldStats
    .filter(s => s.type === 'numeric')
    .map(s =>
      `  - ${s.key}: min=${formatNumPrecise(s.min)}, max=${formatNumPrecise(s.max)}, avg=${formatNumPrecise(s.avg)}, sum=${formatNumPrecise(s.sum)}` +
      (s.maxLabel ? ` | Highest: "${s.maxLabel}"` : '') +
      (s.minLabel ? ` | Lowest: "${s.minLabel}"` : '')
    ).join('\n')

  const categorySummary = fieldStats
    .filter(s => s.type === 'categorical' && s.topValues?.length)
    .map(s =>
      `  - ${s.key}: ${s.topValues!.slice(0, 6).map(v => `"${v.value}" ${v.pct}% (n=${v.count})`).join(', ')}`
    ).join('\n')

  const sampleRows = records.slice(0, 8)
    .map((r, i) =>
      `  [${i + 1}] ${Object.entries(r.fields).slice(0, 8).map(([k, v]) => `${k}="${v}"`).join(' | ')}`
    ).join('\n')

  return `You are DataInsight AI — a world-class data analyst embedded in an analytics platform. You have deep expertise in statistics, data science, and business intelligence.

You are analyzing this specific dataset:
DATASET: ${source}
RECORDS: ${count}
FIELDS (${fieldStats.length}): ${fieldStats.map(s => `${s.key} [${s.type}]`).join(', ')}

NUMERIC STATISTICS:
${numericSummary || '  (no numeric fields)'}

CATEGORY DISTRIBUTIONS:
${categorySummary || '  (no categorical fields)'}

SAMPLE DATA (first ${Math.min(8, count)} of ${count} records):
${sampleRows}

GUIDELINES:
- Always cite specific values, counts, and percentages from the data
- When asked to rank or compare, be precise and complete
- Identify outliers, anomalies, and patterns proactively
- Suggest follow-up analyses the user should consider
- If a question cannot be answered from available data, say so clearly and explain what data would be needed
- Keep responses focused and structured — use bullet points for lists, numbers for rankings
- You can see ALL ${count} records through the statistics above — reason about the full dataset, not just samples`
}

export function buildInitialAnalysisPrompt(): string {
  return `Please analyze this dataset comprehensively. Structure your response as follows:

## Executive Summary
2–3 sentences: what this dataset captures, its scope, and the single most important finding.

## Key Findings
8–10 specific, quantified bullet points. Reference exact values. Go beyond the obvious — find surprising or non-obvious insights.

## Patterns & Distributions
How is the data distributed? Any skew, clustering, or concentration? What does the spread tell us?

## Outliers & Anomalies
3–5 specific records or values that are extreme or unexpected. Name them precisely.

## Field Intelligence
For each important field: what it measures, its range/quality, and what it reveals.

## What To Explore Next
3–4 specific analytical next steps. What statistical tests, cross-references, or visualizations would unlock the most value?`
}
