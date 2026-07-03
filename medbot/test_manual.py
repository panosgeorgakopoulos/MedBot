from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
from src.planner import plan_and_execute
import json

def run_trace():
    print("Loading models (this might take a moment due to FLAN-T5)...")
    world = setup_initial_world()
    resolver = UnifiedResolver(world)
    context = DialogueContext()
    
    print("\n=== MEDBOT V2 ACCEPTANCE CRITERIA TRACE ===\n")
    
    tests = [
        # 1. Compound + quantity + query
        "bring me two 5ml syringes and check if the antibiotic is expired",
        # 2. Conditional/substitution
        "if paracetamol is out of stock, bring ibuprofen instead",
        # 3. Negation/Exclusion (simulated via decomposer if it handles 'not expired')
        "bring antibiotic but not the expired one",
        # 4. Multi-turn
        "bring the gauze",
        "actually make it two",
        # 5. Stock Query
        "πόση παρακεταμόλη έχουμε",
        # 6. Controlled Substance without auth
        "fetch morphine",
        # 7. Complex Scenario 1 (Compound + Condition)
        "bring the thermometer and if out of stock bring the blood pressure monitor",
        # 8. Complex Scenario 2 (Bilingual + Quantity)
        "φέρε 2 syringes"
    ]
    
    for t in tests:
        print(f"INPUT: {t}")
        results = resolver.resolve_command(t, context)
        
        for res in results:
            print(f"--- Atomic Action ---")
            print(f"Decomposer JSON: {res.get('raw_atomic')}")
            
            if res['error']:
                print(f"Blocked at {res['layer']}: {res['error']}")
                continue
                
            print(f"Routing Layer: {res['layer']} (Conf: {res['confidence']:.2f})")
            
            action_req = res["action_req"]
            
            plan_res = plan_and_execute(action_req, world, context)
            
            status = plan_res["status"]
            print(f"Status: {status.upper()}")
            for trace_line in plan_res["trace"]:
                print(f"  -> {trace_line}")
                
        print("-" * 50)

if __name__ == "__main__":
    run_trace()
