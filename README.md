# 🌉 InsightBridge AI
**The Executive AI Business Analyst.**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Launch%20App-0F52BA?style=for-the-badge)](https://johnparente97.github.io/AI-Business-Analyst-Demo/)

**InsightBridge** is a serverless, privacy-first AI analytics tool that turns raw CSV data into board-ready strategic insights. It runs entirely in your browser using WebAssembly (`st-lite`), ensuring your sensitive financial data never leaves your device unless you explicitly connect your own AI model.

---

## 🎯 Key Capabilities

*   **🔒 Privacy-First Architecture**: Powered by `st-lite`, the Python backend runs inside your browser. Your data is processed locally in memory.
*   **🤖 Hybrid AI Engine**:
    *   **Demo Mode (Default)**: Uses a sophisticated heuristic engine to simulate AI insights for zero-cost testing.
    *   **Real AI Mode**: Connect your own **OpenAI API Key** to unlock GPT-4o powered analysis on your live data. keys are ephemeral and never stored.
*   **📊 Dynamic Visualization**: Automatically detects trends, distributions, and comparisons to generate interactive Plotly charts.
*   **📋 Executive Reporting**: One-click generation of "Board Ready" summaries, highlighting risks, opportunities, and strategic 30-60-90 day plans.
*   **💬 Natural Language Interface**: Chat with your data as if you were speaking to a Senior Analyst.

---

## 🚀 Quick Start

### Option 1: Live Browser Demo (Recommended)
1.  Click the **[Live Demo](https://johnparente97.github.io/AI-Business-Analyst-Demo/)** button.
2.  Wait ~30s for the WebAssembly environment to boot (subsequent loads are instant).
3.  Upload any standard CSV (e.g., Sales Data, Financial Assessment, User Growth).
4.  *Optional*: Enter your OpenAI API Key in the sidebar for real intelligence.

### Option 2: Local Development
If you want to modify the code or run it locally:

```bash
# 1. Clone the repository
git clone https://github.com/johnparente97/AI-Business-Analyst-Demo.git
cd AI-Business-Analyst-Demo

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## 🏗️ Architecture & Security

InsightBridge leverages a modern "Serverless AI" architecture:

```mermaid
graph TD
    User[User Browser]
    WASM[WebAssembly Runtime (Pyodide)]
    App[Streamlit App]
    Data[Local CSV Data]
    OpenAI[OpenAI API (Optional)]

    User -->|Loads App| WASM
    WASM -->|Runs| App
    App -->|Processes| Data
    
    subgraph Browser Sandbox
        WASM
        App
        Data
    end
    
    App -->|Requests (Only if Key provided)| OpenAI
```

*   **Zero-Data Retention**: Data loaded into the app exists only in your browser's RAM (volatile memory). Refreshing the page wipes the data.
*   **Client-Side Processing**: All filtering, aggregation, and chart generation happens locally.
*   **API Security**: If you provide an OpenAI Key, it is used strictly for making direct requests to OpenAI endpoints from your browser. It is not managed, saved, or logged by any middleman server.

---

## 🔧 Troubleshooting

**"App is stuck on 'Initializing'..."**
*   This usually requires a **Hard Refresh** (`Cmd+Shift+R` or `Ctrl+F5`) to clear old cache.
*   Ensure you are using a modern browser (Chrome, Edge, Firefox, Safari).

**"API Key Invalid"**
*   Ensure your OpenAI key has active credits and permissions for `gpt-4o-mini`.

---

## ⚖️ Ethical AI & Disclaimer
This tool uses Large Language Models (LLMs) to generate insights. While powerful, LLMs can occasionally hallucinate or misinterpret numerical data. Always verify critical financial figures against the raw data preview provided in the dashboard.

---

**Built with ❤️ by John Parente**
*Optimized for Performance & Design.* app.py
