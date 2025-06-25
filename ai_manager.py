import json
from openai import OpenAI
from GLOBAL_CONST import API_KEY_OPEN_AI
from typing import List, Tuple, Dict, Any


class AIManager:
    
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY_OPEN_AI)
        self.total_tokens_used = {"prompt_tokens": 0, "completion_tokens": 0}

    # ================================ Internal methods ================================

    def _make_ai_request(self, messages: List[Dict[str, str]], max_tokens: int = 100, temperature: float = 0.1, model: str = "gpt-4o-mini") -> Tuple[str, Dict[str, int]]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            result = response.choices[0].message.content.strip()
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0
            }
            
            # Track total usage
            self.total_tokens_used["prompt_tokens"] += usage["prompt_tokens"]
            self.total_tokens_used["completion_tokens"] += usage["completion_tokens"]
            
            return result, usage

        except Exception as e:
            print(f"Error making AI request: {str(e)}")
            return "", {"prompt_tokens": 0, "completion_tokens": 0}

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
        product_hebrew = hebrew_query.strip()[6:].strip()  # 6 characters for "חפש לי "
        
        if not product_hebrew:
            return ""
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional Hebrew to English translator specializing in product names. Your task is to translate Hebrew product names to their exact English equivalents. Translate ONLY the product name, nothing else. Keep the translation accurate and specific to the actual product being searched for. Do not add extra words or change the meaning."
            },
            {
                "role": "user",
                "content": f"Translate this Hebrew product name to English: {product_hebrew}"
            }
        ]

        result, usage = self._make_ai_request(messages, max_tokens=50, temperature=0.1)
        
        if not result:
            return ""
        
        # Clean up and return the translation
        return result.strip().lower()

    def check_titles_relevance(self, search_query: str, product_titles: List[str]) -> Tuple[Dict[str, int], Dict[str, int]]:
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

        result, usage = self._make_ai_request(messages, max_tokens=1200, temperature=0.1)
        
        if not result:
            print("Error: Empty response from API")
            return {}, {"prompt_tokens": 0, "completion_tokens": 0}

        # Clean up the response
        result = self._clean_json_response(result)
        
        try:
            parsed = json.loads(result)
            return parsed, usage
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"Failed to parse: '{result}'")
            return {}, {"prompt_tokens": 0, "completion_tokens": 0}



    def find_suitable_titles(self, search_query: str, product_titles: List[str]) -> Tuple[List[int], int, int]:
        if not product_titles:
            return [], 0, 0

        results, usage = self.check_titles_relevance(search_query, product_titles)
        if not results:
            return [], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        suitable_indexes = [int(idx_str) for idx_str, value in results.items() if value == 0]
        return suitable_indexes[:4], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)



    def get_token_usage_summary(self) -> str:
        prompt_tokens = self.total_tokens_used["prompt_tokens"]
        completion_tokens = self.total_tokens_used["completion_tokens"]
        total_tokens = prompt_tokens + completion_tokens
        
        # Rough cost calculation (GPT-4o-mini pricing as of 2024)
        prompt_cost = prompt_tokens * 0.00015 / 1000  # $0.15 per 1K prompt tokens
        completion_cost = completion_tokens * 0.0006 / 1000  # $0.60 per 1K completion tokens
        total_cost = prompt_cost + completion_cost
        
        return (
            f"Token Usage Summary:\n"
            f"  Prompt tokens: {prompt_tokens:,}\n"
            f"  Completion tokens: {completion_tokens:,}\n"
            f"  Total tokens: {total_tokens:,}\n"
            f"  Estimated cost: ${total_cost:.4f}"
        )



    def reset_token_usage(self) -> None:
        self.total_tokens_used = {"prompt_tokens": 0, "completion_tokens": 0} 

    # =================================================================================