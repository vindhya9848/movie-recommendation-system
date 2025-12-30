
from dotenv import load_dotenv
from src.mood_genre import MovieGenre
from google import genai
import os
# from google.genai.errors import APIError



try:
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

def give_customized_mood_response(text: str):
    if not client:
      print("Gemini client not initialized. Check API key setup.")
      return None
    
    if len(text)==0:
        return None
    prompt = (f"Based on the user text analyze the mood he is in and suggest movie genres he might like. The response_text must contain customized response something like: Since you are in a mood to watch so and so"
            f"I want you to output a json with response_text as string and standardised genres as a list of strings in lowercase do not output none values, output empty string if no genre or no response_text \n\Mood: \"{text}\"")
    # system_msg = (
    #  "You are free to modify the output with no grammar errors, Your job is to give customized response_text and list of genres if Mood text is empty output empty string"
    # )
    # print("=========Validating")
    try:
        # Call the API with the structured output configuration
        response = client.models.generate_content(
            model="gemini-2.5-flash",

            contents=[prompt],
            config={
                   'response_mime_type': 'application/json',
                'response_schema': MovieGenre,
            }
        )
        extracted_response = MovieGenre.model_validate_json(response.text)
        return extracted_response

    except Exception as e:
        print(f"Error generating content: {e}")
        return None
    

    # except APIError as e:
    #     print(f"Gemini API Error (Check Quota/Rate Limits): {e}")
    #     return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    

# res = give_customized_mood_response("light, uplifting")
# print(f"{res.response_text} {','.join(res.genres)}")