from groq import Groq
import trafilatura
from ftfy import fix_text
import unicodedata
import re 
import os
import sys

# Alternative 1: Using langdetect (Google's language detection library)
try:
    from langdetect import detect, detect_langs, DetectorFactory
    DetectorFactory.seed = 0  # For consistent results
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("langdetect not installed. Install with: pip install langdetect")

# Alternative 2: Using textblob
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("textblob not installed. Install with: pip install textblob")

# Alternative 3: Using spacy-langdetect
try:
    import spacy
    from spacy_langdetect import LanguageDetector
    SPACY_LANGDETECT_AVAILABLE = True
except ImportError:
    SPACY_LANGDETECT_AVAILABLE = False
    print("spacy-langdetect not installed. Install with: pip install spacy spacy-langdetect")

# Alternative 4: Using polyglot (already in your code but can be used standalone)
try:
    from polyglot.detect import Detector
    from collections import Counter
    POLYGLOT_AVAILABLE = True
except ImportError:
    POLYGLOT_AVAILABLE = False
    print("polyglot not installed. Install with: pip install polyglot")

# Alternative 5: Using langid.py
try:
    import langid
    LANGID_AVAILABLE = True
except ImportError:
    LANGID_AVAILABLE = False
    print("langid not installed. Install with: pip install langid")


class WebScraperTranslator:
    """Main class for web scraping, language detection, and translation"""
    
    def __init__(self, groq_api_key=None):
        """Initialize the scraper with optional Groq API key"""
        self.groq_client = None
        
        if groq_api_key:
            self.groq_client = Groq(api_key=groq_api_key)
    
    def safe_print(self, text):
        """Safely print text that may contain Unicode characters"""
        try:
            print(text)
        except UnicodeEncodeError:
            # Replace problematic characters with safe alternatives
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            print(safe_text)
    
    def scrape_with_trafilatura(self, url):
        """Scrape content from URL using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            return trafilatura.extract(downloaded)
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None
    
    def remove_emojis(self, text):
        """Remove emojis from text using regex"""
        emoji_pattern = re.compile("["
            u"\U00002700-\U000027BF"  # Dingbats
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U00002600-\U000026FF"  # Miscellaneous Symbols
            u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
        "]+", re.UNICODE)
        return re.sub(emoji_pattern, '', text)
    
    def detect_language_langdetect(self, text, top_n=3):
        """Detect language using langdetect library"""
        if not LANGDETECT_AVAILABLE:
            return None
        
        try:
            # Get multiple language probabilities
            langs = detect_langs(text)
            results = []
            for i, lang in enumerate(langs[:top_n]):
                results.append({
                    "language": lang.lang,
                    "confidence": lang.prob,
                    "method": "langdetect"
                })
            return results
        except Exception as e:
            print(f"Langdetect error: {e}")
            return None
    
    def detect_language_textblob(self, text):
        """Detect language using TextBlob"""
        if not TEXTBLOB_AVAILABLE:
            return None
        
        try:
            blob = TextBlob(text)
            detected_lang = blob.detect_language()
            return [{
                "language": detected_lang,
                "confidence": 1.0,  # TextBlob doesn't provide confidence scores
                "method": "textblob"
            }]
        except Exception as e:
            print(f"TextBlob error: {e}")
            return None
    
    def detect_language_polyglot(self, text, top_n=3):
        """Detect top languages using Polyglot"""
        if not POLYGLOT_AVAILABLE:
            return None
        
        try:
            detector = Detector(text, quiet=True)
            lang_spans = [(segment.language.code, len(segment.text)) for segment in detector]
            lang_counter = Counter()

            total_chars = sum(length for _, length in lang_spans)
            for lang, length in lang_spans:
                lang_counter[lang] += length

            top_langs = lang_counter.most_common(top_n)
            return [
                {"language": lang, "confidence": length / total_chars, "method": "polyglot"}
                for lang, length in top_langs
            ]
        except Exception as e:
            print(f"Polyglot error: {e}")
            return None
    
    def detect_language_langid(self, text):
        """Detect language using langid.py"""
        if not LANGID_AVAILABLE:
            return None
        
        try:
            lang, confidence = langid.classify(text)
            return [{
                "language": lang,
                "confidence": confidence,
                "method": "langid"
            }]
        except Exception as e:
            print(f"Langid error: {e}")
            return None
    
    def detect_language_spacy(self, text):
        """Detect language using spacy-langdetect"""
        if not SPACY_LANGDETECT_AVAILABLE:
            return None
        
        try:
            # Load a basic spacy model (you might need to download it first)
            # python -m spacy download en_core_web_sm
            nlp = spacy.load("en_core_web_sm")
            nlp.add_pipe('language_detector', last=True)
            
            doc = nlp(text)
            return [{
                "language": doc._.language['language'],
                "confidence": doc._.language['score'],
                "method": "spacy-langdetect"
            }]
        except Exception as e:
            print(f"Spacy-langdetect error: {e}")
            return None
    
    def detect_language_multiple_methods(self, text):
        """Try multiple language detection methods and return results"""
        results = {}
        
        # Method 1: langdetect (most reliable and lightweight)
        langdetect_result = self.detect_language_langdetect(text)
        if langdetect_result:
            results['langdetect'] = langdetect_result
        
        # Method 2: langid.py (very fast and lightweight)
        langid_result = self.detect_language_langid(text)
        if langid_result:
            results['langid'] = langid_result
        
        # Method 3: TextBlob (simple but less accurate)
        textblob_result = self.detect_language_textblob(text)
        if textblob_result:
            results['textblob'] = textblob_result
        
        # Method 4: Polyglot (good for mixed languages)
        polyglot_result = self.detect_language_polyglot(text)
        if polyglot_result:
            results['polyglot'] = polyglot_result
        
        return results
    
    def get_best_language_detection(self, text):
        """Get the best language detection result using available methods"""
        # Priority order: langdetect > langid > polyglot > textblob
        
        # Try langdetect first (most reliable)
        result = self.detect_language_langdetect(text)
        if result:
            return result
        
        # Try langid as fallback
        result = self.detect_language_langid(text)
        if result:
            return result
        
        # Try polyglot as second fallback
        result = self.detect_language_polyglot(text)
        if result:
            return result
        
        # Try textblob as last resort
        result = self.detect_language_textblob(text)
        if result:
            return result
        
        # If all fail
        return [{"language": "unknown", "confidence": 0.0, "method": "none"}]
    
    def translate_with_groq(self, text):
        """Translate text to English using Groq LLaMA model"""
        if not self.groq_client:
            print("Error: Groq API key not provided")
            return None
        
        content = (
            "You are a professional translator. "
            "Translate the following text, which may contain multiple languages including Arabic and French, into clear and natural English. "
            "Do not omit, summarize, or change any ideas, details, or cultural nuances. "
            "Maintain the tone, style, and meaning as faithfully as possible. "
            "Preserve all sentences and their order exactly. "
            "Here is the text:\n\n"
            f"{text}"
        )

        try:
            chat_completion = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "user", "content": content}],
                temperature=0.0,
                seed=2025
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Translation error: {e}")
            return None
    
    def process_url(self, url, groq_api_key=None, display_full_text=True, use_multiple_methods=False):
        """Main method to process a URL: scrape, clean, detect language, and translate if needed"""
        print("Downloading article...\n")
        
        # Scrape content
        article_text = self.scrape_with_trafilatura(url)
        if not article_text:
            print("Failed to scrape article.")
            return None
        
        print(f"Article length: {len(article_text)} characters")
        
        # Display text conditionally
        if len(article_text) > 10000 and not display_full_text:
            view = input("Text is very long. Do you want to display it? (y/n): ")
            if view.lower() == "y":
                self.safe_print(f"\n--- Full Text ---\n{article_text}\n")
        else:
            self.safe_print(f"\n--- Full Text ---\n{article_text}\n")
        
        # Clean text
        article_text_no_emojis = self.remove_emojis(article_text)
        corrected_text = fix_text(article_text_no_emojis)
        print("Text after cleaning and encoding correction:")
        self.safe_print(corrected_text)
        
        # Language detection
        if use_multiple_methods:
            all_results = self.detect_language_multiple_methods(corrected_text)
            print("\n--- Language Detection Results (All Methods) ---")
            for method, results in all_results.items():
                print(f"\n{method.upper()}:")
                for i, result in enumerate(results, start=1):
                    lang = result["language"]
                    confidence = result["confidence"]
                    print(f"  {i}. Language: {lang} | Confidence: {confidence:.2%}")
            
            # Use the best result for translation decision
            language_results = self.get_best_language_detection(corrected_text)
        else:
            language_results = self.get_best_language_detection(corrected_text)
            print("\n--- Detected Languages ---")
            for i, result in enumerate(language_results, start=1):
                lang = result["language"]
                confidence = result["confidence"]
                method = result["method"]
                print(f"{i}. Language: {lang} | Confidence: {confidence:.2%} | Method: {method}")
        
        # Translation if needed
        if all(result["language"] == "en" for result in language_results):
            print("\n✅ Text is already entirely in English. No translation needed.")
            return corrected_text
        else:
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                translated_text = self.translate_with_groq(corrected_text)
                if translated_text:
                    print("\n=== Translated Text ===")
                    self.safe_print(translated_text)
                    return translated_text
                else:
                    print("Translation failed.")
                    return corrected_text
            else:
                print("No Groq API key provided. Cannot translate.")
                return corrected_text


# Example usage
if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    url = "https://www.bac.org.tn/%D9%86%D8%B5%D8%A7%D8%A6%D8%AD-%D8%B3%D8%B1%D9%8A%D8%B9%D8%A9-%D9%85%D8%B9-%D8%A5%D9%82%D8%AA%D8%B1%D8%A7%D8%A8-%D8%A5%D9%85%D8%AA%D8%AD%D8%A7%D9%86%D8%A7%D8%AA-%D8%A7%D9%84%D8%A8%D8%A7%D9%83%D8%A7/"
    groq_api_key = os.getenv("groq_api_key") 

    scraper = WebScraperTranslator()
    
    result = scraper.process_url(url, groq_api_key, use_multiple_methods=False)
    
    # Or process with multiple methods for comparison
    # result = scraper.process_url(url, groq_api_key, use_multiple_methods=True)

    if result:
        print("\n--- Processing completed successfully ---")
    else:
        print("\n--- Processing failed ---")