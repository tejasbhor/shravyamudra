import requests
import json
import time
import re
from typing import Optional, List, Dict

# --- ISL Prompt Template (Same as Gemini for consistent results) ---
ISL_PROMPT_TEMPLATE = '''You are an expert in Indian Sign Language (ISL) translation. Your task is to translate English text into grammatically correct ISL gloss, focusing on natural and fluent sign language expression. Follow these ISL grammar principles strictly:

**Rules:**
1.  **Structure:** Topic-Comment. Order: TIME-PLACE-PERSON-OBJECT-VERB.
2.  **Omit:** Articles (a, an, the), linking verbs (is, am, are, was, were), most prepositions.
3.  **Word Order:** Adjectives AFTER noun. Numbers BEFORE noun. Possessor BEFORE item (e.g., MY BOOK).
4.  **Special:** Time expressions FIRST. Question words END. Negation (NOT/NEVER) END.
5.  **Verbs:** Base form (EAT). Past: + FINISH. Continuous: + CONTINUE. Future: WILL at start.
6.  **Format:** ALL CAPS. Space between signs. Compounds: +. Fingerspelled: -.

Examples:

English: "This book is more interesting than the one we read last month."
ISL Gloss: "THIS BOOK INTERESTING MORE COMPARE THAT BOOK WE READ LAST MONTH"

English: "Have you eaten breakfast?"
ISL Gloss: "BREAKFAST EAT FINISH YOU ?"

English: "The red car is fast"
ISL Gloss: "CAR RED FAST"

Now translate the following English text into grammatically correct ISL gloss, applying these rules consistently. Provide ONLY the ISL gloss translation, no explanations:

"""
{input_text}
"""
'''

def get_model_name(model_id: str) -> str:
    """
    Maps the frontend model ID to the actual Ollama model name.
    """
    model_mapping = {
        "gemma": "gemma3:1b",  # Using the correct model name
        "mistral": "mistral",
        "llama2": "llama2",
        "mixtral": "mixtral",
        "neural-chat": "neural-chat"
    }
    return model_mapping.get(model_id, model_id)

def wait_for_ollama(timeout: int = 30) -> bool:
    """
    Wait for Ollama service to be ready.
    Returns True if service is ready, False if timeout reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def check_model_availability(model_name: str, max_retries: int = 3) -> tuple[bool, Optional[str]]:
    """
    Checks if the specified model is available in Ollama.
    Returns (is_available, error_message)
    """
    for _ in range(max_retries):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(model["name"] == model_name for model in models):
                    return True, None
                return False, f"Model '{model_name}' not found. Please run 'ollama pull {model_name}' first."
            return False, f"Ollama returned status code {response.status_code}"
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue
        except Exception as e:
            return False, str(e)
    return False, "Could not connect to Ollama after multiple attempts"

# --- Sentence Splitting Function (Same as in gemini_api.py) ---
def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences based on common punctuation (.?!) followed by space or end of line.
    Handles basic cases but might not be perfect for complex text (e.g., abbreviations).
    """
    # Regex: Looks for sentence-ending punctuation (.?!) followed by whitespace (\s) or end of string ($)
    # The (?<=...) is a lookbehind assertion to keep the punctuation with the sentence.
    sentences = re.split(r'(?<=[.?!])\s+', text)
    # Filter out any empty strings that might result from splitting
    return [s.strip() for s in sentences if s and s.strip()]

def call_ollama_for_sentence(sentence: str, model_name: str, max_retries: int = 3) -> str:
    """
    Calls the Ollama API for a single sentence with the ISL translation prompt template.
    """
    actual_model = get_model_name(model_name)
    prompt = ISL_PROMPT_TEMPLATE.format(input_text=sentence)
    
    # Try to make the API call with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": actual_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,    # Low temperature for consistent output
                        "top_p": 0.7,
                        "top_k": 20,
                        "num_ctx": 1024,
                        "repeat_penalty": 1.2,
                        "stop": ['"""', 'Explanation', 'Note', 'Definition', 'In ISL'],
                        "num_predict": 200     # Increased to allow longer translations
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown error")
                except:
                    pass
                raise Exception(f"Ollama API returned status code {response.status_code}: {error_msg}")
            
            result = response.json()
            raw_translation = result["response"].strip()
            
            # Clean up the response - simpler processing than before
            # Remove explanatory text and keep only the actual translation
            lines = raw_translation.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Skip lines that look like explanations
                if re.match(r'^(Here is|This is|In ISL|Translated)', line, re.IGNORECASE):
                    continue
                # Skip lines with common markers
                if line.startswith('*') or line.startswith('-') or line.startswith('>'):
                    continue
                # Remove markdown formatting
                line = re.sub(r'[*"`\'()]', '', line)
                cleaned_lines.append(line)
            
            joined_text = ' '.join(cleaned_lines)
            
            # Ensure output is in uppercase for consistency with Gemini output
            # If the model didn't provide uppercase, convert it
            if not re.match(r'^[A-Z\s+\-]+$', joined_text):
                joined_text = joined_text.upper()
            
            return joined_text.strip()
                
        except requests.exceptions.ConnectionError:
            last_error = "Connection error"
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            raise Exception(f"Ollama API call failed: {str(e)}")
    
    raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")

def call_ollama_api(input_text: str, model_name: str = "gemma", max_retries: int = 3) -> str:
    """
    Processes text, splits into sentences, and translates each one using Ollama.
    This mirrors the Gemini implementation for consistent results.
    """
    # First ensure Ollama is running
    if not wait_for_ollama():
        raise Exception(
            "Could not connect to Ollama. Please ensure:\n"
            "1. Ollama is installed and running (run 'ollama serve' in a terminal)\n"
            "2. The service is accessible at localhost:11434"
        )
    
    # Then check model availability
    actual_model = get_model_name(model_name)
    model_available, error_msg = check_model_availability(actual_model)
    if not model_available:
        raise Exception(error_msg)
    
    # Split input text into sentences for more accurate translation
    sentences = split_into_sentences(input_text)
    if not sentences:
        return ""  # No valid sentences to translate
    
    # Process each sentence individually
    translations = []
    for sentence in sentences:
        try:
            isl_translation = call_ollama_for_sentence(sentence, model_name, max_retries)
            translations.append(isl_translation)
        except Exception as e:
            # Log the error but continue with other sentences
            print(f"Error translating sentence '{sentence}': {str(e)}")
            translations.append(f"[TRANSLATION ERROR]")
    
    # Join all translations with appropriate separator
    return '\n'.join(translations) 