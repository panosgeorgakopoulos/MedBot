import json
import torch
from sentence_transformers import SentenceTransformer, util

class FewShotIntentClassifier:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        self.centroids = {}
        self.intents = []
        
    def fit(self, data_path="data/train.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        intent_texts = {}
        for d in data:
            intent = d["intent"]
            text = " ".join(d["tokens"])
            if intent not in intent_texts:
                intent_texts[intent] = []
            intent_texts[intent].append(text)
            
        self.intents = list(intent_texts.keys())
        
        for intent in self.intents:
            embeddings = self.model.encode(intent_texts[intent], convert_to_tensor=True)
            centroid = torch.mean(embeddings, dim=0)
            self.centroids[intent] = centroid
            
    def predict(self, texts):
        query_embs = self.model.encode(texts, convert_to_tensor=True)
        centroid_tensor = torch.stack([self.centroids[i] for i in self.intents])
        cos_scores = util.cos_sim(query_embs, centroid_tensor)
        
        predictions = []
        for scores in cos_scores:
            best_idx = torch.argmax(scores).item()
            predictions.append(self.intents[best_idx])
            
        return predictions

    def predict_with_scores(self, texts):
        query_embs = self.model.encode(texts, convert_to_tensor=True)
        centroid_tensor = torch.stack([self.centroids[i] for i in self.intents])
        cos_scores = util.cos_sim(query_embs, centroid_tensor)
        
        predictions = []
        for scores in cos_scores:
            best_idx = torch.argmax(scores).item()
            predictions.append((self.intents[best_idx], scores[best_idx].item()))
            
        return predictions

if __name__ == "__main__":
    import os
    if os.path.exists("data/train.json"):
        clf = FewShotIntentClassifier()
        clf.fit()
        queries = ["πιάσε μου τη γάζα", "άνοιξε το κουτί", "τι είναι αυτό το κουτί", "πάρε τα χάπια"]
        preds = clf.predict(queries)
        for q, p in zip(queries, preds):
            print(f"{q} => {p}")
