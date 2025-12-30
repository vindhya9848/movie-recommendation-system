
from dotenv import load_dotenv
from src.movie import Movie
from google import genai
import os
from google.genai.errors import APIError

try:
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

def extract_movie_info(text: str):
    if not client:
      print("Gemini client not initialized. Check API key setup.")
      return None
    prompt = f"""
From the USER TEXT, do the following:

1. Identify the movie, web series, or TV show title if mentioned (even partially).
2. If identified, output:
   - official_title
   - themes (3–6 short keywords specifying tone of the movie)
   - plot - a short keyword based plot depicting intent of the movie, webseries or show

Return empty fields if nothing is identified.

USER TEXT: "{text}"
"""
#     system_msg = (
# "You are a movie database expert. Your goal is to identify if the user is mentioning a specific movies, webseries or tv show title (even if partial or slightly incorrect)"
# "1. If a specific movie is identified: Extract the full official title and provide a keyword-based plot summary."
#     )


    
    # prompt = (f"Extract the movie title if present in the USER_TEXT and also generate plot summary of that movie with just important keywords from plot, remove any unnecessary names,  otherwise output None\n\n"
    # f"USER TEXT: \"{text}\""
    # )
    # prompt = f"Identify this movie: {text}"
    # print("=========Validating")
    try:
        # Call the API with the structured output configuration
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[prompt],
            config={
                #    'system_instruction': system_msg,
                   'response_mime_type': 'application/json',
                'response_schema': Movie,
            }
        )
        extracted_movie = Movie.model_validate_json(response.text)
        return extracted_movie
    # except APIError as e:
    #     print(f"Gemini API Error (Check Quota/Rate Limits): {e}")
    #     return None
    except Exception as e:
        print(f"Error generating content: {e}")
        return None


# res = extract_movie_info(" I want something like stranger things dark thriller type")
# # print(res)