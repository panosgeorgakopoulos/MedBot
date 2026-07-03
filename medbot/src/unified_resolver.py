import unicodedata
from rapidfuzz import fuzz
import joblib
import os
import re

from src.parser import parse_command
from src.hf_semantic_resolution import SemanticResolver
from src.hf_intent_fewshot import FewShotIntentClassifier
from src.world import WorldState
from src.context import DialogueContext
from src.decomposer import CommandDecomposer
from src.lexicon import extract_quantity_and_assumptions

class UnifiedResolver:
    def __init__(self, world: WorldState):
        self.world = world
        
        self.decomposer = CommandDecomposer()
        
        clf_path = os.path.join(os.path.dirname(__file__), "..", "models", "intent_classifier.joblib")
        if os.path.exists(clf_path):
            self.intent_clf = joblib.load(clf_path)
        else:
            self.intent_clf = None
            
        self.semantic_resolver = SemanticResolver()
        self.semantic_resolver.fit(world.objects)
        
        self.hf_intent_clf = FewShotIntentClassifier()
        train_path = os.path.join(os.path.dirname(__file__), "..", "data", "train.json")
        if os.path.exists(train_path):
            self.hf_intent_clf.fit(train_path)
            
    def strip_accents(self, text):
        if not text: return ""
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

    def _fallback_intent_heuristics(self, utterance: str):
        utt = utterance.lower()
        if re.search(r'\b(fetch|get|bring|give me|φέρε|πάρε|make|κάνε)\b', utt): return "FETCH"
        if re.search(r'\b(place|put|drop|βάλε)\b', utt): return "PLACE"
        if re.search(r'\b(open|unlock|άνοιξε)\b', utt): return "OPEN"
        if re.search(r'\b(close|shut|κλείσε)\b', utt): return "CLOSE"
        if re.search(r'\b(inspect|check|look|έλεγξε)\b', utt): return "INSPECT"
        if re.search(r'\b(give|hand|δώσε)\b', utt): return "GIVE"
        if re.search(r'\b(stock|how much|πόση|έχουμε|απόθεμα|πόσες|πόσα|μένουν|απομένουν)\b', utt): return "CHECK_STOCK"
        if re.search(r'\b(where|locate|πού)\b', utt): return "LOCATE"
        if re.search(r'\b(κρατάς|έχεις στα χέρια|κρατάω|holding|hands)\b', utt): return "HOLDING"
        return None

    def resolve_atomic(self, action_dict: dict, context: DialogueContext):
        utterance = str(action_dict.get("object_query") or action_dict.get("action") or "")
        full_utterance = action_dict.get("raw_utterance", utterance)
        
        lexicon_qty, assumed_msg = extract_quantity_and_assumptions(full_utterance)
        
        utt_clean = self.strip_accents(utterance)
        
        intent = action_dict.get("action")
        obj_id = None
        layer = None
        confidence = 0.0
        
        ood_keywords = ["weather", "time", "joke", "sports", "news", "music", "play", "καιρός", "ωρα", "αστείο"]
        if any(f" {k} " in f" {utt_clean} " or utt_clean == k for k in ood_keywords):
            return {"intent": None, "object_id": None, "layer": "Layer 4 (OOD)", "confidence": 0.0, "error": "This seems out of scope for my hospital duties. I can only manage medical supplies."}
        
        parsed = parse_command(full_utterance)
        parsed_noun = parsed.get("slots", {}).get("noun")
        parsed_fallback = parsed.get("slots", {}).get("fallback_noun")
        
        valid_intents = ["FETCH", "PLACE", "OPEN", "CLOSE", "INSPECT", "GIVE", "CHECK_STOCK", "LOCATE", "HOLDING"]
        if not intent or intent not in valid_intents:
            if parsed.get("intent"):
                intent = parsed.get("intent")
            else:
                intent = self._fallback_intent_heuristics(utterance)
                
            if not intent and self.intent_clf:
                try:
                    probs = self.intent_clf.predict_proba([utterance])[0]
                    idx = probs.argmax()
                    score = probs[idx]
                    if score > 0.65:
                        intent = self.intent_clf.classes_[idx]
                except:
                    pass
                    
        if intent == "HOLDING":
            return {"intent": intent, "object_id": None, "layer": "Parser/Heuristics", "confidence": 1.0, "error": None, "action_req": {"action": intent}}
        
        excluded_size = parsed.get("slots", {}).get("excluded_size")
        excluded_state = parsed.get("slots", {}).get("excluded_state")
        req_size = parsed.get("slots", {}).get("size")
        req_state = parsed.get("slots", {}).get("state")
        
        match_targets = [utt_clean]
        if parsed_noun:
            match_targets.append(self.strip_accents(parsed_noun))
        
        candidates = []
        best_score = 0
        for o_id, obj in self.world.objects.items():
            if excluded_size and obj.size and excluded_size in obj.size:
                continue
            if excluded_state == "αποστειρωμένο" and "sterile" in obj.id:
                continue
            if req_size and (not obj.size or req_size not in obj.size):
                continue
            if req_state == "αποστειρωμένο" and "sterile" not in obj.id:
                continue
                
            choices = [self.strip_accents(a) for a in obj.aliases] + [self.strip_accents(obj.name)]
            for choice in choices:
                score = max(fuzz.partial_ratio(choice, t) for t in match_targets)
                if any(f" {choice} " in f" {t} " or choice == t for t in match_targets):
                    score = 100
                if score > best_score:
                    best_score = score
                    candidates = [obj]
                elif score == best_score and score > 0:
                    if obj not in candidates:
                        candidates.append(obj)
                        
        action_req = dict(action_dict)
        
        if best_score >= 85: 
            if len(candidates) > 1:
                # Handle conditionals / multiple objects parsed
                if parsed_fallback:
                    c1 = next((c for c in candidates if c.name == parsed_noun), None)
                    c2 = next((c for c in candidates if c.name == parsed_fallback), None)
                    if c1 and c2:
                        action_req["fallback_object_id"] = c2.id
                        obj_id = c1.id
                        layer = "Layer 1 (Alias/Fuzzy Conditional)"
                        confidence = 1.0
                elif parsed_noun:
                    c_primary = [c for c in candidates if c.name == parsed_noun]
                    if c_primary:
                        candidates = c_primary
                
                if not obj_id:
                    names = ", ".join(set(c.name for c in candidates))
                    if len(set(c.name for c in candidates)) > 1:
                        fbq = action_req.get("fallback_query")
                        if fbq and str(fbq).lower() not in ("none", "null"):
                            fb_obj, _ = self._resolve_object_only(fbq)
                            if fb_obj:
                                filtered_candidates = [c for c in candidates if c.id != fb_obj]
                                if len(set(c.name for c in filtered_candidates)) == 1:
                                    obj_id = filtered_candidates[0].id
                                    action_req["fallback_object_id"] = fb_obj
                                    
                        if not obj_id:
                            return {"intent": intent, "object_id": None, "layer": "Layer 4 (Clarification)", "confidence": best_score / 100.0, "error": f"Found multiple matching items ({names}). Please specify which one."}
                    else:
                        obj_id = candidates[0].id
                        layer = "Layer 1 (Alias/Fuzzy)"
                        confidence = best_score / 100.0
            else:
                if len(candidates) == 1:
                    obj_id = candidates[0].id
                    layer = "Layer 1 (Alias/Fuzzy)"
                    confidence = best_score / 100.0
        else:
            results = self.semantic_resolver.resolve(utterance, top_k=1)
            if results:
                top_obj, top_score = results[0]
                if top_score > 0.45:
                    obj_id = top_obj.id
                    layer = "Layer 3 (Semantic Embeddings)"
                    confidence = top_score
                    
        # Context Recency fallback for pronouns
        if not obj_id and re.search(r'\b(it|this|that|αυτό|την|το|εκείνο|two|ένα|δύο|τρεις|three)\b', utt_clean):
            if context.last_mentioned_objects:
                obj_id = context.last_mentioned_objects[0]
                layer = "Layer 1 (Context Recency)"
                confidence = 1.0

        if not intent or not obj_id:
            if not intent and not obj_id:
                 return {"intent": None, "object_id": None, "layer": "Layer 4 (OOD)", "confidence": 0.0, "error": "This seems out of scope for my hospital duties."}
            return {"intent": intent, "object_id": obj_id, "layer": "Layer 4 (Clarification)", "confidence": 0.0, "error": "Δεν είμαι σίγουρος/η. Παρακαλώ διευκρινίστε την εντολή ή το αντικείμενο. (I am not sure, please clarify)."}
            
        action_req["action"] = intent
        action_req["object_id"] = obj_id
        action_req["quantity"] = lexicon_qty
        
        if assumed_msg:
            action_req["assumed_quantity_msg"] = assumed_msg
            
        if parsed.get("slots"):
            action_req["excluded_state"] = parsed["slots"].get("excluded_state")
            action_req["excluded_size"] = parsed["slots"].get("excluded_size")
        
        fallback_query = action_req.get("fallback_query")
        if fallback_query and str(fallback_query).lower() not in ("none", "null") and "fallback_object_id" not in action_req:
            fallback_obj, _ = self._resolve_object_only(fallback_query)
            action_req["fallback_object_id"] = fallback_obj
            
        return {"intent": intent, "object_id": obj_id, "layer": layer, "confidence": confidence, "error": None, "action_req": action_req}

    def _resolve_object_only(self, query):
        utt_clean = self.strip_accents(str(query))
        parsed = parse_command(str(query))
        parsed_noun = parsed.get("slots", {}).get("noun")
        match_targets = [utt_clean]
        if parsed_noun:
            match_targets.append(self.strip_accents(parsed_noun))
            
        best_obj = None
        best_score = 0
        for o_id, obj in self.world.objects.items():
            choices = [self.strip_accents(a) for a in obj.aliases] + [self.strip_accents(obj.name)]
            for choice in choices:
                score = max(fuzz.partial_ratio(choice, t) for t in match_targets)
                if any(f" {choice} " in f" {t} " or choice == t for t in match_targets):
                    score = 100
                if score > best_score:
                    best_score = score
                    best_obj = obj
        if best_score >= 85: return best_obj.id, best_score
        
        results = self.semantic_resolver.resolve(query, top_k=1)
        if results and results[0][1] > 0.45:
            return results[0][0].id, results[0][1]
        return None, 0.0

    def resolve_command(self, utterance: str, context: DialogueContext):
        # Layer 0: Decompose
        atomic_actions = self.decomposer.decompose(utterance, context)
        
        if not atomic_actions or (len(atomic_actions) == 1 and str(atomic_actions[0]).strip() in ("", "None", "null", "[]")):
            atomic_actions = [{"action": None, "object_query": utterance, "quantity": 1, "fallback_query": None}]
        
        results = []
        for action_dict in atomic_actions:
            if isinstance(action_dict, str):
                action_dict = {"action": None, "object_query": action_dict, "quantity": 1, "fallback_query": None}
            
            if action_dict.get("action") and len(str(action_dict["action"]).split()) > 2:
                action_dict["object_query"] = str(action_dict["action"]) + " " + str(action_dict.get("object_query") or "")
                action_dict["action"] = None
                
            action_dict["raw_utterance"] = utterance
            res = self.resolve_atomic(action_dict, context)
            res["raw_atomic"] = action_dict
            results.append(res)
            
        return results
