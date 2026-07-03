import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [" ".join(d["tokens"]) for d in data]
    labels = [d["intent"] for d in data]
    return texts, labels

def main():
    X_train, y_train = load_data("data/train.json")
    X_val, y_val = load_data("data/val.json")
    X_test, y_test = load_data("data/test.json")
    
    # Train
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1,2)),
        LogisticRegression(max_iter=1000)
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("Intent Classification Test Results:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save
    import os
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/intent_classifier.joblib")
    print("Model saved to models/intent_classifier.joblib")

if __name__ == "__main__":
    main()
