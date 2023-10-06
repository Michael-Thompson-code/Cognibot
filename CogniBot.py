import json
from difflib import get_close_matches
from typing import Optional

def load_bot_knowledge(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"questions": [], "answers": {}}

def save_bot_knowledge(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> Optional[str]:
    matches = get_close_matches(user_question.lower(), questions, n=1, cutoff=0.3)
    return matches[0] if matches else None

def get_answer_for_question(question: str, bot_knowledge: dict) -> Optional[str]:
    return bot_knowledge["answers"].get(question)

def chatbot():
    bot_knowledge_file = "bot_knowledge.json"
    bot_knowledge = load_bot_knowledge(bot_knowledge_file)
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        
        best_match = find_best_match(user_input, bot_knowledge["questions"])

        # New logic to improve interaction
        if best_match and best_match.lower() == user_input.lower():
            # It's an exact or very close match
            answer = get_answer_for_question(best_match, bot_knowledge)
            print(f"CogniBot: {answer}")
        else:
            # Either no match or not a good enough match
            print(f"CogniBot: I don't know the answer to '{user_input}'. Can you teach me? if not type skip")
            new_answer = input("You: ").strip()
            if new_answer.lower() != "skip":
                bot_knowledge["answers"][user_input.lower()] = new_answer
                bot_knowledge["questions"].append(user_input.lower())
                save_bot_knowledge(bot_knowledge_file, bot_knowledge)
                print("CogniBot: Thank you! I learned a new response.")
            else:
                print("CogniBot: Okay! Let me know if you have other questions.")

if __name__ == "__main__":
    chatbot()
