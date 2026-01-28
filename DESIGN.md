# Design Decisions

## Philosophy
**"Complexity is the enemy of reliability."**
We moved from a multi-modal chat interface to a strict, linear pipeline. This ensures:
1.  **Predictability:** The user always gets the same high-quality output format.
2.  **Speed:** No back-and-forth conversation latency.
3.  **Trust:** Visuals and stats are deterministic; only the narrative is AI-generated.

## Technical Choices

### 1. AI Engine: Hugging Face Inference API
*   **Why?** Allows for free-tier usage with high-quality open-weights models (Mistral-7B).
*   **Security:** API Token is now managed via `st.secrets`, removing the risk of users pasting keys into the frontend or the app hitting rate limits on a shared key exposed in code.
*   **Resilience:** If the API fails (rate limits, downtime), the system silently falls back to a deterministic template. The user never sees a crash.

### 2. User Experience (UX)
*   **Single Flow:** Removed tabs and sidebar settings. The app does one thing: analyzes the uploaded file.
*   **Visual Hierarchy:** 
    1.  **Metrics (Top):** Instant validation that data is loaded correctly.
    2.  **Charts (Middle):** Identify trends/distributions at a glance.
    3.  **Narrative (Bottom):** Executive summary to contextualize the data.
*   **Aesthetics:** Used custom CSS to elevate standard Streamlit metrics into "Material Design" style cards without adding heavy frontend frameworks.

### 3. Code Structure
*   **`utils` separation:** Logic is kept out of `app.py` to allow independent testing of data loading and AI calls.
*   **No Browser-Side Exec:** Removed `st-lite`/Pyodide hacks. The app is designed for standard Python server environments (Streamlit Cloud).
