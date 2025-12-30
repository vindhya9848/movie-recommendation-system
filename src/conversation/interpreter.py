# src/interpreter.py

import re
import requests
import nltk
# from spellchecker import SpellChecker
from rapidfuzz import fuzz
from thefuzz import process
import pycountry
import spacy
import re
from typing import Optional, Dict, Any
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from src.config.settings import genres,YES_WORDS,NO_WORDS, LANGUAGES
from src.llm.extract_movie_info import extract_movie_info

# spell = SpellChecker()


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: Model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
    exit()


try:
    stopwords.words('english')
except LookupError as e:
    print("Downloading NLTK stopwords...", e)


# Define the stop words set globally for maximum efficiency
STOP_WORDS_SET = set(stopwords.words('english'))


def extract_plot_text(text: str, state) -> str:
    if not text:
        return text

    enriched = extract_movie_info(text)
    if not enriched:
        return text
    
    if enriched:
        text = str(enriched.plot).strip()+ ', '.join([str(t) for t in enriched.themes]) if len(enriched.plot) or len(enriched.themes) else text
        return text

    return text

   

def remove_stopwords(text: str) -> str:
   word_tokens = word_tokenize(text.lower()) # Convert to lowercase first
   
   filtered_sentence = [w for w in word_tokens if w.isalnum() and w not in STOP_WORDS_SET]
 #  print(filtered_sentence)
   return ' '.join(filtered_sentence)


def detect_yes_no(text: str):
 text = text.lower().strip() if text is not None else ''

    # 1. IMMEDIATE CHECK: Exact Match
    # If the user types a perfect match, we return immediately.
 if text in YES_WORDS:
     return "yes"
 if text in NO_WORDS:
        return "no"
 best_yes_score = 0
 for w in YES_WORDS:
        score = fuzz.ratio(w, text)
        if score > best_yes_score:
            best_yes_score = score
            
    # Check against NO words
 best_no_score = 0
 for w in NO_WORDS:
        score = fuzz.ratio(w, text)
        if score > best_no_score:   
            best_no_score = score

    # Decision Logic: Check if the best score meets the threshold
    # and is significantly better than the opposing category.
    
 if best_yes_score >= 80 and best_yes_score > best_no_score:
        return "yes"
    
 if best_no_score >= 80 and best_no_score > best_yes_score:
        return "no"

 return None


# -------------------------------
# Genre extraction
# -------------------------------
def extract_genre(text: str):
    CORRECT_GENRES = [ g.lower() for g in genres]
    lowercased_text=text.lower()
    cleaned_text=remove_stopwords(lowercased_text)

    candidates = re.split(r'[,\s-]+', cleaned_text)
    best_matches = [process.extractOne(c, CORRECT_GENRES) for c in candidates]
   # candidates = [word for word in text.lower().split() if len(word) > 2]
    # Extract the corrected name if the score is above the threshold (85)
    # print(best_matches)
    corrected_genres = [match[0] for match in best_matches if match[1] > 80]
    
    # Return unique, correctly spelled genres

    if len(corrected_genres) ==0:
        return None
    return list(set(corrected_genres))


def extract_language(text: str):
    result = detect_yes_no(text)

    if result =='no':
        return None
    CORRECT_LANG = [ l.lower() for l in LANGUAGES]
  #  candidates = [word for word in text.lower().split() if len(word) > 2]
    lowercased_text=text.lower() if text is not None else ''
    cleaned_text=remove_stopwords(lowercased_text)
    candidates = re.split(r'[,\s-]+', cleaned_text)
    best_matches = [process.extractOne(c, CORRECT_LANG) for c in candidates]
    
    # Extract the corrected name if the score is above the threshold (85)
    corrected_languages = [match[0] for match in best_matches if match[1] > 75]
    if len(corrected_languages) ==0:
        return None
    
    # Return unique, correctly spelled genres
    return list(set(corrected_languages))



all_language_names = [language.name for language in pycountry.languages]


# -------------------------------
# Runtime extraction
# Examples:
# "< 2 hours", "under 90 mins", "not more than 1 hour"
# -------------------------------


def extract_runtime(text: str) -> Optional[Dict[str, Any]]:
    text= text if text is not None else None
    t = text.lower().strip()

    # ---------------------------------
    # 1) Detect constraint type (symbols first)
    # ---------------------------------

    result = detect_yes_no(t)

    if result == 'no':
        return None
    
    if re.search(r"(<=|<)", t):
        ctype = "max"
    elif re.search(r"(>=|>)", t):
        ctype = "min"
    elif re.search(r"(under|below|less\s+than|at\s+most|within|no\s+more\s+than)", t):
        ctype = "max"
    elif re.search(r"(over|greater\s+than|more\s+than|at\s+least|minimum|min\.?)", t):
        ctype = "min"
    else:
        ctype = "exact"

    # ---------------------------------
    # 2) Parse runtime and convert to minutes
    # ---------------------------------
    minutes = None

    # handles: "1h 30m", "1 hr 20 min", "2h", "45m"
    hm = re.search(
        r"(?:(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours))?\s*"
        r"(?:(\d+(?:\.\d+)?)\s*(m|min|mins|minute|minutes))?",
        t
    )
    if hm and (hm.group(1) or hm.group(3)):
        hours = float(hm.group(1)) if hm.group(1) else 0
        mins = float(hm.group(3)) if hm.group(3) else 0
        minutes = int(round(hours * 60 + mins))

    # handles: "< 30 mins", "> 2 hours", "less than 90 minutes"
    if minutes is None:
        m = re.search(
            r"(<=|>=|<|>|under|greater\s+than|below|less\s+than|over|more\s+than|at\s+least|at\s+most)?\s*"
            r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)\b",
            t
        )
        if m:
            val = float(m.group(2))
            unit = m.group(3)
            minutes = int(round(val * 60)) if unit.startswith("h") else int(round(val))

    if minutes is None:
        return None

    return {"type": ctype, "minutes": minutes}