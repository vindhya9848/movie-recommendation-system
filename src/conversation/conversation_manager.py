# src/conversation_manager.py
from src.llm.give_customized_mood_response import give_customized_mood_response
from src.conversation.state import ConversationState
from src.conversation.interpreter import (
    extract_genre, detect_yes_no, extract_language, extract_plot_text,   extract_runtime)

#from src.predict_mood import predict_mood
class ConversationManager:

    def __init__(self):
        self.state = ConversationState()


    def next_question(self, state):
        step = state.current_step

        if step == "ask_mood":
            return "What's your mood today, I can recommend you geners you might like 🧙‍♂️"
        
        if step == "print_mood_response":
            if  state.selected_genres is None:
              return f"{state.res.response_text}, \n, \n  Enter if any other prefered genre else type no.."
            else:
                state.current_step = 'ask_language'
                return ( f"Gotcha! noted that you are interested in: {','.join(state.selected_genre)}."
                        f"Enter language preference if any else type no"
                )

        # if step == "confirm_genre":
        #     return "Do you have any other prefered genre? (yes/no)"
            # genres = ", ".join(state.suggested_genres)
            # return (
            #     f"Gotcha! Since you are feeling {state.mood}, "
            #     f"I can suggest these genres: {genres}. "
            #     "Do you have any other genre preference? (yes/no)"
            # )
        
        
        if step == "similar_movies":
            return "Please share a similar movie's name or plot description to help me understand your taste better:"
    
        if step == "ask_language":
            return "Please enter prefered language if any else type: 'no'"

        if step == "ask_runtime":
            return "Please enter runtime constraint (e.g. < 2 hours) if any else type: 'no'"

        return None

    def update_state(self, state, user_input):
        text = user_input.lower()

        if not len(text):
            return "Please enter valid input, type 'exit' to quit"

        if state.current_step == "ask_mood":
            # mood_result  = extract_intent_preferences(text)
            genres = extract_genre(text) if  extract_genre(text) else None
            # state.mood =','.join(mood_result['tone'])
            response_generated= give_customized_mood_response(text)
            # print(f"{state.res.response_text}")
            state.suggested_genres = response_generated.genres
            state.selected_genre = genres
            state.current_step = "print_mood_response"
            state.res = response_generated

            # state.suggested_genres = self.mood_to_genres.get(state.mood, [])
            # if  state.mood == "neutral":
            #     print(f"Seems like you are in a {state.mood} mood. Help me understand your genre preference.")
            #     state.current_step = "ask_genre_value"
            return state

        if state.current_step == "print_mood_response":

            yn= detect_yes_no(user_input)
            if yn == "no":
                state.selected_genre = None

            else:
                genre = extract_genre(user_input)
                print("=====selected genre", genre)
                state.current_step 
                state.selected_genres = genre
           
            state.current_step = "ask_language"
            return state



        if state.current_step == "ask_language":
            yn= detect_yes_no(user_input)
            if yn == "no":
                state.language = None
            else:
                language = extract_language(user_input)
                state.language = language
            
            state.current_step = "similar_movies"
            return state
        
        if state.current_step == "similar_movies":
            state.movie_description =extract_plot_text(user_input, state)
            state.current_step = "ask_runtime"
            return state
  

        if state.current_step == "ask_language_value":
          #  language_text= correct_spelling(user_input)
            state.language = extract_language(user_input)
            state.current_step = "ask_runtime"
            return state

        if state.current_step == "ask_runtime":
            yn= detect_yes_no(user_input)
            # print("========yn value for runtime:", yn)
            if yn == "no":
                state.runtime = None
            else:
                runtime = extract_runtime(user_input)
                state.runtime = runtime
            state.current_step ="runtime_done"
            return state



        return state
