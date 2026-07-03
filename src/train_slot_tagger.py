import json
import joblib
import sklearn_crfsuite
from sklearn_crfsuite import metrics

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    X = []
    y = []
    for d in data:
        tokens = d["tokens"]
        tags = d["tags"]
        # Basic features for each token
        features = []
        for i, token in enumerate(tokens):
            feature = {
                'bias': 1.0,
                'word.lower()': token.lower(),
                'word[-3:]': token[-3:],
                'word[-2:]': token[-2:],
                'word.isupper()': token.isupper(),
                'word.istitle()': token.istitle(),
                'word.isdigit()': token.isdigit(),
            }
            if i > 0:
                word1 = tokens[i-1]
                feature.update({
                    '-1:word.lower()': word1.lower(),
                    '-1:word.istitle()': word1.istitle(),
                    '-1:word.isupper()': word1.isupper(),
                })
            else:
                feature['BOS'] = True

            if i < len(tokens)-1:
                word1 = tokens[i+1]
                feature.update({
                    '+1:word.lower()': word1.lower(),
                    '+1:word.istitle()': word1.istitle(),
                    '+1:word.isupper()': word1.isupper(),
                })
            else:
                feature['EOS'] = True
            
            features.append(feature)
            
        X.append(features)
        y.append(tags)
        
    return X, y

def main():
    X_train, y_train = load_data("data/train.json")
    X_test, y_test = load_data("data/test.json")
    
    crf = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    
    crf.fit(X_train, y_train)
    
    y_pred = crf.predict(X_test)
    
    labels = list(crf.classes_)
    if 'O' in labels:
        labels.remove('O')
        
    print("Slot Tagging Test Results:")
    try:
        print(metrics.flat_classification_report(y_test, y_pred, labels=labels, digits=3))
    except Exception as e:
        print("Could not print classification report nicely:", e)
    
    # Save
    import os
    os.makedirs("models", exist_ok=True)
    joblib.dump(crf, "models/slot_tagger.joblib")
    print("Model saved to models/slot_tagger.joblib")

if __name__ == "__main__":
    main()
