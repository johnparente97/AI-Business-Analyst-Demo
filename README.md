# InsightBridge AI 🌉

**Scalable. Secure. Strategic.**

InsightBridge AI is an advanced business analytics platform designed to instantly turn raw data into executive-level insights. It bridges the gap between complex datasets and clear, actionable strategy.

## 🚀 Key Capabilities

*   **Large Dataset Support**: Process CSV files up to **200MB** effortlessly. The app uses advanced server-side streaming technology to handle large data without crashing your browser.
*   **Privacy-First AI**: We use a **Safe-Partition Architecture**. Your raw confidential data never leaves the secure processing environment. Only anonymous, high-level statistical summaries are sent to the AI for interpretation.
*   **Instant Diagnostics**: Automatically detects time-series patterns, categorical distributions, and data quality issues (missing values, outliers).
*   **Executive Analysis**: Generates professional strategic briefs highlighting risks, opportunities, and key trends.

## 🛠️ Technology Stack

*   **Engine**: Python (Streamlit)
*   **Data Processing**: Pandas (Chunked Streaming)
*   **Visualization**: Plotly Interactive Charts
*   **Intelligence**: Hugging Face Inference API (Mistral-7B)

## 📋 How to Use

1.  **Upload Data**: Drag and drop any CSV file (up to 200MB).
2.  **View Dashboard**: Instantly see key metrics, interactive trend lines, and category breakdowns.
3.  **Read Strategy**: A comprehensive AI-generated report appears at the bottom, synthesizing the data into business language.

### Configuration (Optional)
To enable the full AI capabilities, you can provide a Hugging Face API Token.
1.  Create a `.streamlit/secrets.toml` file.
2.  Add your token:
    ```toml
    HF_API_TOKEN = "hf_..."
    ```
*Note: Without a token, the app runs in "Offline Mode," providing deterministic statistical summaries.*

## 🔒 Security Note
*   **No Data Retention**: Uploaded files are processed in memory and discarded immediately after analysis.
*   **Sanitized AI Inputs**: The AI model only receives metadata (e.g., "Sales column: Mean=500, Max=1000"), never individual customer records or PII.

---
*Built for the Modern Data Stack.*
