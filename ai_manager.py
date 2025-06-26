import json
import pandas as pd
import time
from google import genai
from google.genai import types
from GLOBAL_CONST import GEMINI_API_KEY
from typing import List, Tuple, Dict, Any


class AIManager:
    
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.total_tokens_used = {"prompt_tokens": 0, "completion_tokens": 0}
        self.total_runtime = 0.0

    # ================================ Internal methods ================================

    def _make_ai_request(self, messages: List[Dict[str, str]], max_tokens: int = 100, temperature: float = 0.1, model: str = "gemini-2.5-flash-lite-preview-06-17") -> Tuple[str, int, int, float]:
        start_time = time.time()
        
        try:
            # Convert OpenAI message format to Gemini content format
            contents = []
            for message in messages:
                role = "user" if message["role"] in ["user", "system"] else "model"
                content = types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message["content"])]
                )
                contents.append(content)
            
            # Create configuration
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="text/plain",
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            # Make the request
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config
            )

            result = response.text.strip() if response.text else ""
            
            # Gemini doesn't provide detailed token usage like OpenAI, so we'll estimate
            # Based on rough character count estimation (1 token ≈ 4 characters)
            prompt_text = " ".join([msg["content"] for msg in messages])
            estimated_prompt_tokens = len(prompt_text) // 4
            estimated_completion_tokens = len(result) // 4
            
            # Calculate runtime
            runtime = time.time() - start_time
            
            # Track total usage
            self.total_tokens_used["prompt_tokens"] += estimated_prompt_tokens
            self.total_tokens_used["completion_tokens"] += estimated_completion_tokens
            self.total_runtime += runtime
            
            return result

        except Exception as e:
            runtime = time.time() - start_time
            self.total_runtime += runtime
            print(f"Error making AI request: {str(e)}")
            return "", 0, 0, runtime

    # =================================================================================

    def _clean_json_response(self, response: str) -> str:
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return response.strip()

    # ================================ Public methods ================================
    
    def translate_hebrew_query(self, hebrew_query: str) -> str:
        # Check if query starts with "חפש לי"
        if not hebrew_query.strip().startswith("חפש לי"):
            return ""
        
        # Extract the product name (remove "חפש לי" prefix)
        product_text = hebrew_query.strip()[6:].strip()  # 6 characters for "חפש לי "
        
        if not product_text:
            return ""
        
        # Check if the product text is already in English (basic check for Hebrew characters)
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in product_text)
        
        # If no Hebrew characters found, assume it's already English
        if not has_hebrew:
            return product_text.strip().lower()
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional Hebrew to English translator specializing in product names. Your task is to translate Hebrew product names to their exact English equivalents. Translate ONLY the product name, nothing else. Keep the translation accurate and specific to the actual product being searched for. Do not add extra words or change the meaning."
            },
            {
                "role": "user",
                "content": f"Translate this Hebrew product name to English: {product_text}"
            }
        ]

        result = self._make_ai_request(messages, max_tokens=50, temperature=0.1)
        
        if not result:
            return ""
        
        # Clean up and return the translation
        return result.strip().lower()

    def check_titles_relevance(self, search_query: str, product_titles: List[str]) -> Dict[str, int]:
        titles_text = "\n".join([f"{i}: {title}" for i, title in enumerate(product_titles)])
        
        messages = [
            {
                "role": "system",
                "content": "You are a strict product matching expert. Analyze if each product title is an EXACT match for the search query category. Be very strict: only return 0 (suitable) if the product IS the actual item being searched for, not accessories, parts, or related items. For example: if searching 'wireless headphones', only actual headphones/earbuds should be 0, NOT charging cables, cases, stands, or other accessories. Return ONLY a JSON object with format: {\"0\": 0, \"1\": 1, \"2\": 0, ...} where each key is the title index and each value is: 0 = exact category match, 1 = not exact match."
            },
            {
                "role": "user",
                "content": f"Search query: \"{search_query}\"\n\nProduct titles to analyze:\n{titles_text}\n\nReturn JSON with 0 for relevant titles, 1 for irrelevant titles:"
            }
        ]

        result = self._make_ai_request(messages, max_tokens=2500, temperature=0.1)
        
        if not result:
            print("Error: Empty response from API")
            return {}

        # Clean up the response
        result = self._clean_json_response(result)
        
        try:
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"Failed to parse: '{result}'")
            return {}


    def get_suitable_titles(self, product_name, products_df) -> pd.DataFrame:
        title_list = list(products_df['product_title'])
        
        if not title_list:
            return pd.DataFrame()

        results = self.check_titles_relevance(product_name, title_list)
        if not results:
            return pd.DataFrame()

        suitable_indexes = [int(idx_str) for idx_str, value in results.items() if value == 0]
        top_indices = suitable_indexes[:4]
        
        if not top_indices:
            return pd.DataFrame()
            
        filtered_df = products_df.iloc[top_indices].reset_index(drop=True)
        return filtered_df
    
    # =================================================================================