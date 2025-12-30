from src.conversation.conversation_manager import ConversationManager
from src.conversation.state import ConversationState
from typing import Union

class ChatbotService():

    def __init__(self):

        self.waiting_for_answer = False
        self.state = ConversationState()
        self.manager = ConversationManager()
        

    def run_chatbot(self):
        print("\nHowdy! I am your movie assistant Nova!\n")

        self.state = ConversationState()
        self.manager = ConversationManager()

        while self.state.current_step != "runtime_done":
            question = self.manager.next_question(self.state)
            if question:
                  print("\nNova:", question)
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "q", "bye"]:
               print("Exiting the conversation. Goodbye!")
               break
            elif user_input.strip() == "":
               print("Please provide a valid response.")
               continue
            else:
              self.state = self.manager.update_state(self.state, user_input)

        print("\n--- Conversation Complete ---")
        print("Final state to feed recommender:\n")
        return self.state


    def handle_user_message(self, user_input: Union[str, None]):
        """
        Handles exactly ONE turn.
        Ensures question → answer → state transition order.
        exited: bool
        """

        # ---------------------------------------------
        # Case 1: conversation just started OR
        #         last turn completed an answer
        # ---------------------------------------------
        if not self.waiting_for_answer:
            question = self.manager.next_question(self.state)
            self.waiting_for_answer = True
            return question, False, self.state, False

        # ---------------------------------------------
        # Case 2: we are waiting for user's answer
        # ---------------------------------------------
        if user_input is None or not user_input.strip():
            return "Please provide a valid response.", False, self.state, False

        if user_input.lower() in ["exit", "quit", "q", "bye"]:
            self.state = ConversationState()
            self.manager = ConversationManager()
            self.waiting_for_answer = False
            return "Goodbye! 👋", False, self.state, True

        # 🔹 Update state based on answer
        self.state = self.manager.update_state(self.state, user_input)
        self.waiting_for_answer = False

        # ---------------------------------------------
        # Check completion
        # ---------------------------------------------
        if self.state.current_step == "runtime_done":
            return (
                "🎬 Got it! Let me find some great movies for you.",
                True,
                self.state, False
            )

        # ---------------------------------------------
        # Otherwise, next turn will ask a question
        # ---------------------------------------------
        question = self.manager.next_question(self.state)
        self.waiting_for_answer = True
        return question, False, self.state, False
