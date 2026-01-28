# 🌉 InsightBridge AI (Browser-Based)

**A Serverless, Privacy-First Business Analytics Tool.**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Launch%20App-0F52BA?style=for-the-badge)](https://johnparente97.github.io/AI-Business-Analyst-Demo/)

**InsightBridge** runs a full Python Streamlit application **entirely in your web browser** using WebAssembly ([Pyodide](https://pyodide.org/) + [st-lite](https://github.com/whitphx/stlite)).

## ⚠️ Architectural Reality
Unlike standard web apps, **there is no backend server**.
*   **Privacy**: Your CSV data never leaves your device. It is loaded into your browser's RAM.
*   **Security**: API Keys (if used) are sent directly from your browser to OpenAI. They are not stored or proxied.
*   **Performance**: The first load requires downloading the Python runtime (~20-50MB), which may take 10-20 seconds. Subsequent loads are faster due to browser caching.

---

## 🛠 Features vs. Limitations

| Feature | Status | Note |
| :--- | :--- | :--- |
| **Data Analysis** | ✅ Local | Pandas/Numpy run in-browser via WASM. |
| **Interactive Charts** | ✅ Local | Plotly renders client-side. |
| **Demo Intelligence** | ✅ Local | Heuristic engine works offline (Zero cost). |
| **Real AI Intelligence** | ⚠️ Optional | Requires **OpenAI API Key**. Calls are made directly via browser fetch. |
| **History & Saving** | ❌ None | **Refreshing the page wipes all data.** (Transient Memory) |

---

## 🚀 How to Run

### Option 1: Live (GitHub Pages)
1.  Click **[Launch App](https://johnparente97.github.io/AI-Business-Analyst-Demo/)**.
2.  **Wait**: You will see a "Booting Secure Environment" screen. **Do not refresh.**
3.  Once loaded, upload a CSV (Max 5MB).

### Option 2: Local Development
To modify the code, you can run it as a standard Streamlit app:

```bash
# 1. Clone
git clone https://github.com/johnparente97/AI-Business-Analyst-Demo.git
cd AI-Business-Analyst-Demo

# 2. Install (Python 3.9+ recommended)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

*Note: In local mode, standard Python is used, not WebAssembly.*

---

## 🏗️ Technical Stack

*   **Runtime**: Python 3.11 (via Pyodide WASM kernel)
*   **Framework**: Streamlit / st-lite
*   **Hosting**: GitHub Pages (Static HTML/JS)
*   **Networking**: `pyodide-http` patches `requests` for browser context.

### Known Issues
*   **Mobile Mobile**: Heavy WASM usage can crash mobile browser tabs on low-RAM devices. Desktop recommended.
*   **CORS**: OpenAI API calls work because `pyodide-http` proxies requests or the browser handles them, but strict corporate firewalls may block direct API usage.

---

**built by John Parente** | *Architecture > Marketing*
