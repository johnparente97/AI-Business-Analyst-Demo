# AI Business Analyst Demo (InsightBridge)

**[🚀 Launch App Now (Live Demo)](https://johnparente97.github.io/insightbridge-ai/)**  
*(Serverless AI Analytics running entirely in your browser)*

---

## 💡 How to Use
Once you click the link above:
1.  **Upload**: Drag & drop any CSV file (Sales, Financials, etc.).
2.  **Chat**: Ask questions like *"What are the risks?"* or click **Surprise Me**.
3.  **Report**: Click **Generate Executive Summary** for a board-ready view.

---

## 🤖 What does this app do?
**InsightBridge AI** acts as an on-demand business data analyst. Instead of writing SQL queries or building complex dashboards, you simply upload your raw data and have a conversation with it.

It automatically:
*   **Analyzes Trends**: Detects growth patterns, seasonality, and anomalies.
*   **Identifies Risks**: Highlights potential issues like churn or cost spikes.
*   **Visualizes Answers**: Generates interactive charts instantly to back up its insights.
*   **Drafts Reports**: Creates professional executive summaries in seconds.

## ⚙️ How does it work?
This application is unique because it is **Serverless & Secure**.
*   **Client-Side Execution**: It uses `st-lite` (WebAssembly) to run Python, Pandas, and Plotly entirely inside your web browser. Your data **never leaves your computer**.
*   **AI Simulation**: For this demo, it uses a mock inference engine that simulates the structure of advanced LLM reasoning, ensuring zero latency and zero cost while demonstrating the UX patterns of a real AI product.
*   **Dynamic UI**: The interface is built with Streamlit but heavily customized with CSS to provide a premium "SaaS" feel.

## 🏗️ Host It Yourself (GitHub Pages)
Want your own copy?
1.  **Fork** this repository.
2.  Go to **Settings > Pages**.
3.  Select Source: **`main` / `root`**.
4.  Wait 3 minutes. Your app is live!

### Troubleshooting
- **404 Error?** Ensure repo is **Public** and contains the `.nojekyll` file.

## 🛠️ Local Development
```bash
git clone https://github.com/johnparente97/insightbridge-ai.git
pip install -r requirements.txt
streamlit run app.py
```
