import json
from difflib import get_close_matches
from typing import Optional
from spellchecker import SpellChecker
import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from difflib import SequenceMatcher

nltk.download('stopwords')
nltk.download('punkt')

spell = SpellChecker()
stop_words = set(stopwords.words('english'))

# Context
context = {
    "last_question": None,
    "subject": None
}

def update_context(question: str) -> None:
    tokens = nltk.word_tokenize(question)
    tags = pos_tag(tokens)
    
    # Finding proper nouns
    subjects = [word for word, pos in tags if pos in ['NNP', 'NNPS']]
    if subjects:
        context["last_question"] = question
        context["subject"] = ' '.join(subjects)
    else:
        context["last_question"] = None
        context["subject"] = None

def is_follow_up_question(question: str) -> bool:
    if context["subject"] and context["subject"].lower() in question.lower():
        return True
    return False

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

def correct_spelling(text: str) -> str:
    words = text.split()
    corrected_words = [spell.correction(word) if spell.correction(word) is not None else word for word in words]
    return ' '.join(corrected_words)

def remove_stopwords(text: str) -> str:
    words = nltk.word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def find_best_match(user_question: str, questions: list[str]) -> (Optional[str], float):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.3)
    if matches:
        return matches[0], SequenceMatcher(None, user_question, matches[0]).ratio()
    else:
        return None, 0.0

def get_answer_for_question(question: str, bot_knowledge: dict) -> Optional[str]:
    return bot_knowledge["answers"].get(question)

def find_similar_question(user_question: str, questions: list[str]) -> Optional[str]:
    max_ratio = 0.6
    best_match = None

    for q in questions:
        ratio = SequenceMatcher(None, user_question, q).ratio()
        if ratio > max_ratio:
            max_ratio = ratio
            best_match = q

    return best_match if best_match else None

def chatbot():
    bot_knowledge_file = "bot_knowledge.json"
    bot_knowledge = load_bot_knowledge(bot_knowledge_file)

    # Greeting
    print("=======================================================================================================")
    print("CogniBot: Hello there! 🤖")
    print("CogniBot: I'm CogniBot, your friendly neighborhood AI. Ask me any questions you have!")
    print("CogniBot: If I don't know an answer, you can teach me. Just type 'quit' whenever you want to leave.")
    print("=======================================================================================================")

    while True:
        user_input = input("You: ").strip()

        # Check for context
        if is_follow_up_question(user_input):
            print(f"CogniBot: I'm not sure about {context['subject']}'s current location.")
            continue  # This skips the rest of the loop and waits for the next user input

        if user_input.lower() == "quit":
            print("CogniBot: Goodbye! If you have more questions in the future, you know where to find me. 😊")
            break
        
        # Attempt spelling correction
        user_input_processed = correct_spelling(user_input)
        best_match, confidence = find_best_match(user_input_processed, bot_knowledge["questions"])

        # If there's no match even after correction, try removing stopwords
        if not best_match:
            user_input_processed = remove_stopwords(user_input_processed)
            best_match, confidence = find_best_match(user_input_processed, bot_knowledge["questions"])

        # Decide on response based on confidence
        if best_match and confidence > 0.85:
            answer = get_answer_for_question(best_match, bot_knowledge)
            print(f"CogniBot: {answer}")
        else:
            similar_question = find_similar_question(user_input, bot_knowledge["questions"])
            
            if similar_question:
                print(f"CogniBot: Your question is similar to: '{similar_question}'.")
                print(f"CogniBot: Current answer is: '{bot_knowledge['answers'][similar_question]}'.")
                choice = input("CogniBot: Do you want to update the answer (type 'update'), add as a new question (type 'new'), or skip (type 'skip')? ").strip().lower()
                
                if choice == 'update':
                    new_answer = input("You: ").strip()
                    bot_knowledge["answers"][similar_question] = new_answer
                    save_bot_knowledge(bot_knowledge_file, bot_knowledge)
                    print("CogniBot: Thank you! I updated the response.")
                elif choice == 'new':
                    new_answer = input(f"CogniBot: I don't know the answer to '{user_input}'. Can you teach me? ").strip()
                    bot_knowledge["answers"][user_input.lower()] = new_answer
                    bot_knowledge["questions"].append(user_input.lower())
                    save_bot_knowledge(bot_knowledge_file, bot_knowledge)
                    print("CogniBot: Thank you! I learned a new response.")
                else:
                    print("CogniBot: Okay! Let me know if you have other questions.")
            else:
                new_answer = input(f"CogniBot: I don't know the answer to '{user_input}'. Can you teach me? If not, type 'skip' ").strip()
                if new_answer.lower() != 'skip':
                    bot_knowledge["answers"][user_input.lower()] = new_answer
                    bot_knowledge["questions"].append(user_input.lower())
                    save_bot_knowledge(bot_knowledge_file, bot_knowledge)
                    print("CogniBot: Thank you! I learned a new response.")
                else:
                    print("CogniBot: Okay! Let me know if you have other questions.")
        update_context(user_input)

if __name__ == "__main__":
    chatbot()
