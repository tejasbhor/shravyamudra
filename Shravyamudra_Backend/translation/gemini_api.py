# --- Required Libraries ---
import google.generativeai as genai
import os
import sys
import nltk # Natural Language Toolkit for sentence tokenization

# --- Download NLTK 'punkt' data if not already present ---
try:
    from nltk.tokenize import sent_tokenize
    nltk.data.find('tokenizers/punkt')
except (LookupError, nltk.downloader.DownloadError):
    print("NLTK 'punkt' tokenizer models not found or download needed.")
    print("Attempting to download 'punkt'...")
    try:
        nltk.download('punkt', quiet=True)
        from nltk.tokenize import sent_tokenize # Re-import after download
        print("'punkt' downloaded successfully.")
    except Exception as download_exc:
        print(f"ERROR: Failed to download 'punkt': {download_exc}")
        print("\nPlease ensure you have internet connectivity and appropriate permissions.")
        print("Alternatively, download manually: run 'python', then 'import nltk; nltk.download(\"punkt\")'")
        sys.exit(1)

ISL_PROMPT_TEMPLATE = '''You are an expert in Indian Sign Language (ISL) translation. Translate the following English text into grammatically correct ISL gloss, adhering to natural ISL structure and using standard UPPERCASE gloss. Provide ONLY the ISL gloss translation, with each English sentence translated on a new line:

"""
{input_text}
"""
'''

# --- Function to Call Gemini API (Handles one sentence at a time) ---
def call_gemini_api(api_key: str, input_text: str, model_name: str = "gemini-1.5-flash-latest") -> str:
    """
    Calls the Gemini API using the google-genai SDK with the ISL translation
    prompt template for a SINGLE sentence. Returns the standard uppercase ISL gloss.
    # ... (rest of the function definition is unchanged) ...
    """
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise Exception(f"Failed to configure GenAI SDK: {str(e)}")

    prompt = ISL_PROMPT_TEMPLATE.format(input_text=input_text)

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        if response.parts:
            raw_isl_gloss = response.text.strip()
            if not raw_isl_gloss:
                 raise Exception("Gemini API returned an empty string.")
            return raw_isl_gloss
        elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
             block_reason = response.prompt_feedback.block_reason
             safety_ratings = response.prompt_feedback.safety_ratings
             raise Exception(f"Gemini API request blocked. Reason: {block_reason}. Ratings: {safety_ratings}")
        else:
            candidate_info = response.candidates[0].finish_reason if response.candidates else "No candidates."
            safety_info = response.prompt_feedback if hasattr(response, 'prompt_feedback') else "No feedback available."
            raise Exception(f"Gemini API returned no text content. Finish reason: {candidate_info}. Safety feedback: {safety_info}")

    except Exception as e:
        raise Exception(f"Gemini API call/processing failed for '{input_text[:60]}...': {str(e)}")


# --- Main Execution Block ---
if __name__ == "__main__":
    # --- Get API Key ---
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("---------------------------------------------------------")
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        # ...(Instructions remain the same)...
        print("---------------------------------------------------------")
        sys.exit(1)

    # --- Get User Input ---
    try:
        print("\nEnter the English text to translate into ISL gloss.")
        print("You can enter multiple sentences (e.g., 'Hello Dr. Smith. How are you?'):")
        english_input_block = input("> ")

        if not english_input_block.strip():
             print("\nERROR: Input text cannot be empty.")
             sys.exit(1)

        # --- Split Input into Sentences using NLTK ---
        print("\nTokenizing input into sentences...")
        english_sentences = sent_tokenize(english_input_block)
        english_sentences = [s.strip() for s in english_sentences if s.strip()] # Clean up list

        if not english_sentences:
            print("\nERROR: NLTK could not detect any sentences, or input was empty after stripping.")
            sys.exit(1)

        # --- Call the API for Each Sentence and Print Results ---
        target_model = "gemini-1.5-flash-latest"
        print(f"\nProcessing {len(english_sentences)} sentence(s) using model: {target_model}...\n")

        all_results = []

        for i, sentence in enumerate(english_sentences):
            print(f"--- Sentence {i+1} ---")
            print(f"English:   {sentence}")
            try:
                # Call API for the current single sentence
                isl_translation_upper = call_gemini_api(api_key, sentence, model_name=target_model)
                # *** MODIFICATION HERE: Added " |" at the end ***
                print(f"ISL Gloss: {isl_translation_upper} |")
                all_results.append({"english": sentence, "isl_gloss": isl_translation_upper})
            except Exception as e:
                # Print specific error and add separator for consistency
                print(f"ERROR translating this sentence: {e}")
                # *** MODIFICATION HERE: Added " |" after error placeholder ***
                print(f"ISL Gloss: [TRANSLATION ERROR] |")
                all_results.append({"english": sentence, "isl_gloss": "[TRANSLATION ERROR]"})
            # Print a separator line
            print("-" * (len(f"--- Sentence {i+1} ---") + 5))
            print() # Add a blank line for better readability

        print("="*40)
        print("Translation process finished.")
        print("="*40)

    except FileNotFoundError:
         print("\nERROR: NLTK data path not found. Ensure NLTK is installed and 'punkt' is downloaded.")
         sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected overall error occurred: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)