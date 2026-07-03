import time
import json
import joblib
from sklearn.metrics import accuracy_score
from src.parser import parse_command

def build_stress_test():
    return [
        {"text": "φέρτε μου παρακαλώ πολύ εκείνη την μικρή γάζα", "intent": "FETCH", "slots": ["O", "O", "O", "O", "O", "O", "B-SIZE", "B-TYPE"]},
        {"text": "βάλε", "intent": "PLACE", "slots": ["O"]},
        {"text": "θα ήθελα να ξεκλειδώσεις το κουτί", "intent": "OPEN", "slots": ["O", "O", "O", "O", "O", "B-TYPE"]},
        {"text": "δώσε μου το ληγμένο αντιβιοτικό", "intent": "GIVE", "slots": ["O", "O", "O", "B-STATE", "B-TYPE"]},
        {"text": "παρακεταμόλη", "intent": "FETCH", "slots": ["B-TYPE"]},
        {"text": "έλεγξε το κουτί", "intent": "INSPECT", "slots": ["O", "O", "B-TYPE"]}
    ]

def evaluate_stage1(stress_data):
    results = []
    start = time.time()
    for item in stress_data:
        parsed = parse_command(item["text"])
        pred_intent = parsed["intent"]
        results.append(pred_intent == item["intent"])
    end = time.time()
    acc = sum(results) / len(results) if results else 0
    latency = (end - start) / len(stress_data) if stress_data else 0
    return acc, latency

def evaluate_stage2(stress_data):
    intent_model = joblib.load("models/intent_classifier.joblib")
    
    texts = [item["text"] for item in stress_data]
    y_true_intents = [item["intent"] for item in stress_data]
    
    start = time.time()
    y_pred_intents = intent_model.predict(texts)
    end = time.time()
    
    acc = accuracy_score(y_true_intents, y_pred_intents)
    latency = (end - start) / len(stress_data) if stress_data else 0
    
    return acc, latency

def main():
    stress_data = build_stress_test()
    acc1, lat1 = evaluate_stage1(stress_data)
    acc2, lat2 = evaluate_stage2(stress_data)
    
    print("=== Evaluation Results ===")
    print("| System | Intent Accuracy | Latency (s/query) |")
    print("|--------|-----------------|-------------------|")
    print(f"| Stage 1 (Rules)       | {acc1:.2f}            | {lat1:.5f}           |")
    print(f"| Stage 2 (Classical)   | {acc2:.2f}            | {lat2:.5f}           |")

if __name__ == "__main__":
    main()
