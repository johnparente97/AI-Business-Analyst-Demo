# InsightBridge AI 🌉

> **Free, open-source–powered executive analytics.**

InsightBridge is a streamlined business intelligence tool that turns raw CSV data into executive-style summaries, visual trends, and strategic insights—instantly.

**[Try the Demo](https://insightbridge.streamlit.app)** _(Replace with your actual link)_

---

## 🚀 Features

*   **Instant Analysis**: strict "No Setup" flow. Just drag and drop your CSV.
*   **Executive Focus**: Generates high-level summaries, risks, and strategic opportunities.
*   **Secure & Private**: Runs entirely in the cloud (or locally). No data persists after the session.
*   **Visual Intelligence**: Auto-detects time-series and categorical data to generate Plotly charts.
*   **Open Source AI**: Powered by Hugging Face Inference API (Mistral-7B / Llama-3).

## 🛠️ How to Run

### 1. Cloud (Recommended)
Deploy directly to **Streamlit Community Cloud**:
1.  Fork this repository.
2.  Connect to Streamlit Cloud.
3.  Add your Hugging Face Token to **Secrets**:
    ```toml
    # .streamlit/secrets.toml
    HF_API_TOKEN = "hf_..."
    ```
4.  Deploy!

### 2. Local Development
```bash
# Clone
git clone https://github.com/johnparente97/AI-Business-Analyst-Demo.git
cd AI-Business-Analyst-Demo

# Install Dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

## 🔒 Configuration

The app requires a **Hugging Face Access Token** for the AI generation to work securely.
If no token is provided, the app gracefully degrades to **Deterministic Mode**, providing heuristic-based templates instead of live LLM generation.

1.  Get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2.  Set it in `.streamlit/secrets.toml` (locally) or Streamlit Cloud Secrets (deployed).

## 📦 Project Structure

*   `app.py`: Main application entry point. Single-flow logic.
*   `utils/`:
    *   `data_loader.py`: Safe CSV handling and statistical profiling.
    *   `ai_engine.py`: Handles Hugging Face API calls and prompt engineering.
    *   `chart_generator.py`: Plotly visualization logic.
*   `requirements.txt`: Minimal dependency set.

---

**Designed for Simplicity, Reliability, and Speed.**
