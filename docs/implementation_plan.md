# Implementation Plan - Investment Advisor Bot

## Goal Description
Create a self-contained, shareable project ("InvestmentAdvisorBot") that acts as an AI-powered investment advisor.
The bot will:
- Focus on investment strategies for budgets of $10-$50/day.
- Use Google Cloud's AI SDK (Gemini) for intelligence.
- Generate structured, strategic reports.
- Feature a premium, "rich aesthetic" web interface.

## User Review Required
> [!IMPORTANT]
> **API Key Handling**: The app will require a Google Cloud/Gemini API key. I will implement a `.env.example` file and also a UI prompt to enter the key if missing, to make it easy for the intern to use.

## Proposed Changes

### Project Structure
Create a new directory: `/Users/anadwi/Documents/Antigravity/InvestmentAdvisorBot`

### Architecture: Streamlit (Python Only)
- **Framework**: Streamlit
- **Key Files**:
    - `app.py`: Main Streamlit application (UI + Logic integration).
    - `advisor_agent.py`: Handles Gemini SDK interactions and prompt engineering.
        - **Update**: Include `country` context in system prompt to recommend local assets (e.g., usage of ISAs in UK, 401k in US).
    - `styles.css`: Custom CSS for "Rich Aesthetics" (Dark mode, glassmorphism).
    - `requirements.txt`: Dependencies (`streamlit`, `google-generativeai`, `python-dotenv`, `watchdog`).

### UI Updates
- **Sidebar**:
    - Add "Select Your Country" dropdown.
    - **Add "Select Model" dropdown**: Options `gemini-2.5-flash` (Default), `gemini-2.5-flash-lite`, `gemma-3-12b`.
- **Logic**:
    - Pass selected country  and **model name** to `AdvisorAgent`.
    - **Optimization**: Implement `tenacity` retry logic.
    - **Advanced Analysis (Real-World Data)**:
        - **Google Search Grounding**: Enable the Google Search tool in Gemini to fetch *live* and *real* data.
        - **No Simulations**: Explicitly forbid hypothetical simulations.
        - **Central Bank & World Bank Outlooks**: Search for and cite the latest reports from the relevant Central Bank (e.g., Fed, ECB, BOE) and World Bank for the target country.
        - **Historical Performance**: Retrieve *actual* historical returns for recommended asset classes (e.g., "S&P 500 annualized return 1923-2023") rather than simulating future paths.


### Packaging
- `start.sh`: A shell script to set up the environment, install dependencies, and run both backend and frontend.
- `README.md`: Instructions for the intern.

## Verification Plan

### Automated Tests
- **Backend Health Check**: Verify `GET /health` returns 200.
- **AI Response Test**: Verify the agent returns a structured response for a sample query like "How to invest $20/day?".

### Manual Verification
1.  **Setup**: Run `./start.sh` in a fresh terminal.
2.  **UI Check**: Verify the "Rich Aesthetics" (animations, dark mode) load correctly.
3.  **Chat Flow**:
    - Enter API Key.
    - Ask: "I have $30/day to invest. What should I do?"
    - Verify the response is a structured "Strategic Report".
4.  **Shareability**: Verify the folder acts as a standalone unit.
