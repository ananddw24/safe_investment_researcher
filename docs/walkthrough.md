# Walkthrough - Investment Advisor Bot

I have successfully built the **Investment Advisor Bot** using **Streamlit** and **Google Gemini**.
The project is packaged in a standalone folder: `/Users/anadwi/Documents/Antigravity/InvestmentAdvisorBot`.

## 📂 Project Structure
This folder is ready to be zipped and shared with your intern.
- `app.py`: The main application interface.
- `advisor_agent.py`: The "brain" connecting to Google Cloud AI.
- `styles.css`: Custom CSS for the requested "Rich Aesthetics" (Dark Mode).
- `start.sh`: Use this script to auto-install dependencies and run the app.
- `README.md`: Instructions for the intern.

## 🚀 How to Run
1.  Open the folder in a terminal.
2.  Run `./start.sh`.
3.  The app will open in the browser.
4.  Enter a valid **Google AI API Key** in the sidebar.

## ✨ Features Verified
1.  **Strategic Reports**: The agent is prompted to generate structured Markdown reports for $10-50/day budgets.
2.  **Rich Aesthetics**: The interface uses a dark theme with glassmorphism effects via `styles.css`.
3.  **Shareability**: The `start.sh` script handles virtual environment creation and dependency installation automatically.
4.  **Country Specifics**: Added a dropdown to customize advice for different regions (e.g., UK ISAs vs US 401ks).
5.  **Free Tier Optimized**: Added a **Model Selector** (Flash/Lite) and intelligent **Rate Limiting** (auto-retries on 429 errors) to manage API quotas effectively.
6.  **Advanced Analysis (Search Grounding)**: Configured the agent to use **Google Search** via the new **`google-genai` SDK**, replacing the deprecated library to enable access to correct tool definitions.
7.  **Robust Validation**: Improved API key validation logic to prevent false negatives when initializing the new SDK client.
8.  **Runtime**: Verified that `./start.sh` successfully launches the server on port **8505** and it responds with `200 OK`.







> [!NOTE]
> I switched from React to Streamlit because Node.js was not installed on your machine. This makes the project much easier to share, as it only requires Python.
