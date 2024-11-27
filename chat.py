import random
import json

import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

def get_suggestions():
    suggestions = []
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            suggestions.append(pattern)
    return suggestions

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# bot_name = "Sam"
# # Dictionary to store context for each user
# context = {}

# def get_response(msg, user_id="default"):
#     global context
#     sentence = tokenize(msg)
#     X = bag_of_words(sentence, all_words)
#     X = X.reshape(1, X.shape[0])
#     X = torch.from_numpy(X).to(device)

#     output = model(X)
#     _, predicted = torch.max(output, dim=1)

#     tag = tags[predicted.item()]

#     probs = torch.softmax(output, dim=1)
#     prob = probs[0][predicted.item()]
#     if prob.item() > 0.75:
#         for intent in intents['intents']:
#             if tag == intent["tag"]:
#                 # Check context filter
#                 if "context_filter" in intent:
#                     if user_id in context and context[user_id] == intent["context_filter"]:
#                         # Update context if needed
#                         if "context_set" in intent:
#                             context[user_id] = intent["context_set"]
#                         else:
#                             context[user_id] = None
#                         return random.choice(intent["responses"])
#                     else:
#                         continue  # Skip if context does not match
#                 else:
#                     # Handle intents without context filtering
#                     if "context_set" in intent:
#                         context[user_id] = intent["context_set"]
#                     else:
#                         context[user_id] = None
#                     return random.choice(intent["responses"])
#     return "I do not understand..."

bot_name = "iSuperPal"
context = {}

def get_response(msg, user_id="default"):
    global context
    sentence = tokenize(msg.lower())

    # Check if there is an active context
    if user_id in context and context[user_id]:
        current_context = context[user_id]
        print(f"Current context for user {user_id}: {current_context}")
        # Filter intents based on context
        applicable_intents = [intent for intent in intents['intents'] if intent.get('tag') and intent.get('context_filter') == current_context]
        # Attempt to match the user's input to patterns in applicable intents
        for intent in applicable_intents:
            for pattern in intent['patterns']:
                pattern_tokens = tokenize(pattern.lower())
                if set(pattern_tokens) == set(sentence):
                    # Match found
                    print(f"Matched intent: {intent['tag']}")
                    if "context_set" in intent:
                        context[user_id] = intent["context_set"]
                    else:
                        context[user_id] = None
                    options = intent.get("options", [])
                    return random.choice(intent["responses"]), options
        # No pattern matched in current context
        print("No pattern matched in current context.")
        return "I do not understand...", []
    else:
        # No active context or context doesn't require special handling
        # Proceed with model prediction
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        print(f"Model predicted tag: {tag} with probability {prob.item()}")
        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    # Check context filter
                    if "context_filter" in intent:
                        if user_id in context and context[user_id] == intent["context_filter"]:
                            # Update context if needed
                            if "context_set" in intent:
                                context[user_id] = intent["context_set"]
                            else:
                                context[user_id] = None
                            options = intent.get("options", [])
                            return random.choice(intent["responses"]), options
                        else:
                            continue  # Skip if context does not match
                    else:
                        # Handle intents without context filtering
                        if "context_set" in intent:
                            context[user_id] = intent["context_set"]
                        else:
                            context[user_id] = None
                        options = intent.get("options", [])
                        return random.choice(intent["responses"]), options
        print("Model confidence too low or no matching intent.")
        return "I do not understand...", []

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    user_id = "user1"  # In real applications, this should be unique per user/session
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence, user_id)
        print(f"{bot_name}: {resp}")