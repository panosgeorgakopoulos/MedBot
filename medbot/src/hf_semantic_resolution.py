from sentence_transformers import SentenceTransformer, util
import torch

class SemanticResolver:
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        self.candidates = []
        self.candidate_embeddings = None
        self.mapping = []
        
    def fit(self, world_objects):
        self.candidates = list(world_objects.values())
        texts = []
        self.mapping = []
        for i, obj in enumerate(self.candidates):
            desc = f"{obj.name} {obj.category}"
            if obj.size: desc += f" {obj.size}"
            texts.append(desc)
            self.mapping.append(i)
            
            for alias in getattr(obj, "aliases", []):
                texts.append(alias)
                self.mapping.append(i)
                
        self.candidate_embeddings = self.model.encode(texts, convert_to_tensor=True)
        
    def resolve(self, query: str, top_k=1):
        query_emb = self.model.encode([query], convert_to_tensor=True)
        cos_scores = util.cos_sim(query_emb, self.candidate_embeddings)[0]
        
        scores_sorted, indices = torch.sort(cos_scores, descending=True)
        
        results = []
        seen = set()
        for score, idx in zip(scores_sorted, indices):
            obj_idx = self.mapping[idx]
            if obj_idx not in seen:
                seen.add(obj_idx)
                results.append((self.candidates[obj_idx], score.item()))
                if len(results) == top_k:
                    break
                    
        return results

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.world import setup_initial_world
    
    w = setup_initial_world()
    resolver = SemanticResolver()
    resolver.fit(w.objects)
    
    query = "εκείνο το πράγμα που μετράει την πίεση"
    res = resolver.resolve(query, top_k=3)
    print(f"Query: {query}")
    for obj, score in res:
        print(f"{obj.name} (ID: {obj.id}): {score:.4f}")
