from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import re
import ast

class CommandDecomposer:
    def __init__(self, model_name="google/flan-t5-base"):
        print(f"Loading decomposer model {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
    def decompose(self, utterance: str, context: list = None) -> list:
        prompt = f"""Decompose the medical command into a list of Python dictionaries.
Fields: action, object_query, quantity, fallback_query.
Actions allowed: FETCH, PLACE, OPEN, CLOSE, INSPECT, GIVE, CHECK_STOCK, LOCATE.
Example: "bring me two 5ml syringes and check if the antibiotic is expired"
Result: [{{"action": "FETCH", "object_query": "5ml syringe", "quantity": 2, "fallback_query": "null"}}, {{"action": "INSPECT", "object_query": "antibiotic", "quantity": 1, "fallback_query": "null"}}]
Example: "if paracetamol is out of stock bring ibuprofen"
Result: [{{"action": "FETCH", "object_query": "paracetamol", "quantity": 1, "fallback_query": "ibuprofen"}}]
Example: "πόση παρακεταμόλη έχουμε;"
Result: [{{"action": "CHECK_STOCK", "object_query": "παρακεταμόλη", "quantity": 1, "fallback_query": "null"}}]
Command: "{utterance}"
Result:"""

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=150)
        out = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        try:
            start = out.find('[')
            end = out.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = out[start:end]
                try:
                    json_str_fixed = json_str.replace("None", "null").replace("False", "false").replace("True", "true").replace("'", '"')
                    parsed = json.loads(json_str_fixed)
                except:
                    parsed = ast.literal_eval(json_str)
                    
                if isinstance(parsed, list):
                    return parsed
        except Exception as e:
            pass # Fall back to regex
            
        # Robust regex fallback for FLAN-T5 malformed JSON (e.g. flat lists without braces)
        actions = re.findall(r'"action":\s*"([^"]+)"', out)
        objects = re.findall(r'"object_query":\s*"([^"]+)"', out)
        quantities = re.findall(r'"quantity":\s*([0-9]+|null)', out)
        fallbacks = re.findall(r'"fallback_query":\s*"([^"]+)"', out)
        
        results = []
        for i in range(len(actions)):
            action = actions[i] if i < len(actions) else None
            obj = objects[i] if i < len(objects) else None
            qty = quantities[i] if i < len(quantities) else 1
            if qty == "null" or qty is None: qty = 1
            else: qty = int(qty)
            fb = fallbacks[i] if i < len(fallbacks) else None
            if fb == "null": fb = None
            results.append({"action": action, "object_query": obj, "quantity": qty, "fallback_query": fb})
            
        if results:
            return results
            
        return [{"action": None, "object_query": utterance, "quantity": 1, "fallback_query": None}]

if __name__ == "__main__":
    d = CommandDecomposer()
    print(d.decompose("bring two 5ml syringes and check if the antibiotic in the ICU cart is expired"))
