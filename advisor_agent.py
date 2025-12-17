from google import genai
from google.genai import types
import os
from typing import Dict, Generator
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ClientError

class AdvisorAgent:
    def __init__(self, api_key: str, country: str = "United States", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.country = country
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)
        self.chat_session = None
        self._initialize_chat()

    def _initialize_chat(self):
        system_prompt = f"""You are an expert Investment Advisor Agent specialized in micro-investing strategies ($10/day to $50/day) for residents of **{self.country}**.
        
        **Your Goal**: Provide highly strategic, actionable, and formatted investment advice grounded in **REAL-WORLD DATA**.
        
        **CRITICAL INSTRUCTIONS**:
        1.  **NO SIMULATIONS**: Do NOT generate hypothetical "Monte Carlo" simulations or fake future projections.
        2.  **USE SEARCH**: You MUST use your Google Search tool to find:
            *   The latest **Central Bank Interest Rate** and policy outlook (e.g., Fed Minutes, ECB Decisions, RBA Outlook).
            *   Current **Inflation (CPI)** and **GDP Growth** forecasts for {self.country} from the **World Bank** or **IMF**.
            *   **Actual Historical Returns**: Cite real historical performance of recommended assets (e.g., "S&P 500 10-year annualized return: 12.4%").
        3.  **Holistic Verification**: Verify that your advice fits the $10-$50/day budget. Ensure fees (expense ratios, transaction costs) on recommended platforms don't destroy returns.
        
        **Format**: ALWAYS use Markdown with clean headers.
        **Report Structure**:
            *   **Macro Economic Context**: Summary of Central Bank stance & Inflation (cited).
            *   **Strategy Overview**: The "Why" based on the macro context.
            *   **Allocation Breakdown**: Specific tickers/assets.
            *   **Historical Performance**: Real data citation (No predictions).
            *   **Action Plan**: Steps to execute.
            
        **Tone**: Professional, authoritative, citations-focused.
        """
        
        # In new SDK, chats are managed differently, but we can keep state manually or use chats.create()
        # For simplicity and streaming, we'll use chats.create()
        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.7,
            )
        )

    @retry(
        retry=retry_if_exception_type(ClientError), # ClientError covers API errors
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5)
    )
    def ask(self, user_message: str) -> Generator[str, None, None]:
        """
        Sends a message to the agent and yields chunks of the response (streaming).
        Retries automatically on API errors (including 429).
        """
        try:
            # New SDK streaming method
            response = self.chat_session.send_message_stream(user_message)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # Re-raise specific errors for tenacity if needed, or just yield error
            # For 429 specifically we want retry
            if "429" in str(e) or (isinstance(e, ClientError) and e.code == 429):
                 raise ClientError("Quota exceeded", code=429)
            yield f"**Error**: {str(e)}"

    def generate_poster(self, advice_text: str):
        """
        Generates a visual poster summarizing the investment advice using Imagen 3.
        """
        try:
            # Step 1: Create a visual prompt
            prompt_request = f"""
            Based on the following investment advice, create a detailed **text-to-image prompt** for an infographic poster.
            
            **Advice Summary**:
            {advice_text[:2000]}... (truncated)

            **Visual Style**: Minimalist, clean, high-tech fintech aesthetic. Dark mode colors.
            **Content**: A central pie chart or flow chart showing the allocation.
            **Text**: Minimal text, just big numbers (e.g., "60% Equity").
            
            **Output**: Just the prompt string, nothing else.
            """
            
            # Use a separate non-streaming call for the prompt generation
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_request
            )
            visual_prompt = response.text
            print(f"Visual Prompt: {visual_prompt}")

            # Step 2: Generate Image using Imagen 3
            # Note: Imagen 3 model ID is 'imagen-3.0-generate-001'
            image_response = self.client.models.generate_image(
                model='imagen-3.0-generate-001',
                prompt=visual_prompt,
                config=types.GenerateImageConfig(
                    number_of_images=1,
                )
            )
            
            return image_response.generated_images[0].image
            
        except Exception as e:
            print(f"Poster Generation Failed: {e}")
            return None
