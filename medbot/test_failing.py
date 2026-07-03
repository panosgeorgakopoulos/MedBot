from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
from src.planner import plan_and_execute
import json

def run_trace():
    world = setup_initial_world()
    resolver = UnifiedResolver(world)
    context = DialogueContext()
    
    tests = [
        "φέρε δύο γάζες",
        "φέρε 1 Γάζα",
        "δώσε μία γάζα",
        "δώσε 1 γάζα",
        "πόσες γάζες έχω;",
        "πόσες γάζες μένουν;",
        "τι κρατάς;"
    ]
    
    for t in tests:
        print(f"\nINPUT: {t}")
        results = resolver.resolve_command(t, context)
        for res in results:
            print(f"Decomposer JSON: {res.get('raw_atomic')}")
            if res.get('error'):
                print(f"Blocked at {res.get('layer')}: {res['error']}")
                continue
            action_req = res["action_req"]
            plan_res = plan_and_execute(action_req, world, context)
            print(f"Status: {plan_res['status']}")
            for trace_line in plan_res["trace"]:
                print(f"  -> {trace_line}")

if __name__ == "__main__":
    run_trace()
