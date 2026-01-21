import pandas as pd
import numpy as np
import time

def generate_insight(query, df):
    """
    Mock AI engine that generates structured responses based on the query.
    In a real app, this would call OpenAI API.
    """
    # Simulate network latency for realism
    time.sleep(1.5)
    
    query_lower = query.lower()
    
    # RESPONSE TEMPLATES
    
    if "trend" in query_lower:
        return {
            "title": "Trend Analysis",
            "content": """
**💡 Key Insights**
- Overall revenue has increased by **12%** over the selected period.
- A significant spike was observed in **Q3**, correlated with the marketing campaign.

**⚠️ Risks**
- Customer retention dipped slightly in the last month (-2%).
- Seasonality suggests a potential dip in the upcoming weeks.

**🌱 Opportunities**
- Capitalize on the Q3 momentum by extending successful promotional offers.
- Focus on re-engagement campaigns for at-risk user segments.

**🚀 Recommended Actions**
1. Launch a "Win-Back" email sequence for inactive users.
2. Allocate additional budget to the high-performing Q3 channels.
            """,
            "chart_type": "trend"
        }
        
    elif "worry" in query_lower or "risk" in query_lower:
        return {
            "title": "Risk Assessment",
            "content": """
**💡 Key Insights**
- Operational costs have risen by **8%**, outpacing revenue growth in the last month.
- Inventory turnover has slowed, leading to higher holding costs.

**⚠️ Risks**
- Cash flow could be tight next quarter if the trend continues.
- Potential overstocking issues for seasonal items.

**🌱 Opportunities**
- Negotiate better terms with top suppliers to reduce COGS.
- Implement a "Flash Sale" to clear excess inventory quickly.

**🚀 Recommended Actions**
1. Audit top expense categories immediately.
2. Pause low-ROI ad spend until margins improve.
            """,
            "chart_type": "bar"
        }
        
    elif "grow" in query_lower or "best" in query_lower:
        return {
            "title": "Growth Opportunities",
            "content": """
**💡 Key Insights**
- **Mobile users** are converting at 2x the rate of desktop users.
- The **Premium Plan** segment grew by 25% YoY.

**⚠️ Risks**
- Desktop experience is lagging and may be driving users away.
- High dependence on a single acquisition channel.

**🌱 Opportunities**
- Double down on mobile-first ad creatives.
- 50% of Basic users match the upgrade profile for Premium.

**🚀 Recommended Actions**
1. Optimize the desktop checkout flow to reduce friction.
2. Create an in-app upgrade prompt for eligible Basic users.
            """,
            "chart_type": "distribution"
        }
        
    else:
        # Generic Response
        return {
            "title": "General Analysis",
            "content": f"""
**💡 Key Insights**
- Analyzed **{len(df)} rows** of data.
- Found strong correlations between key performance metrics.
- Data quality is generally high, with few missing values.

**⚠️ Risks**
- Some outliers detected in the upper percentiles of the dataset.
- Ensure data freshness; current dataset ends on {df.iloc[-1].get('date', 'recent date')}.

**🌱 Opportunities**
- deeper segmentation could reveal hidden high-value cohorts.
- Automating this report could save 5 hours/week.

**🚀 Recommended Actions**
1. Drill down into specific regions for more granular insights.
2. Set up automated alerts for anomaly detection.
            """,
            "chart_type": None
        }

