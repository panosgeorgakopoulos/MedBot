import sys
import copy
from src.world import setup_initial_world
from src.context import DialogueContext
from src.parser import parse_command
from src.reference_resolution import resolve_reference, AmbiguityError, NotFoundError
from src.planner import plan_and_execute, SafetyError, PlanError

def run_examples():
    world = setup_initial_world()
    context = DialogueContext()
    
    examples = [
        "Φέρε μου τη γάζα 10x10 από την αποθήκη",
        "Βάλε τη γάζα",
        "Έλεγξε την", # Pronoun test
        "Άνοιξε το κουτί στη ΜΕΘ",
        "Δώσε το αντιβιοτικό", # Error test
        "Φέρε τη σύριγγα 1ml",
        "Δώσε την", # Multi-step give
        "Φέρε μου την παρακεταμόλη", # Ambiguity test
        "Φέρε το θερμόμετρο από το φαρμακείο", # Not found test
        "Κλείσε το κουτί"
    ]
    
    output = []
    output.append("# Stage 1: Symbolic Baseline Examples\n")
    
    for cmd in examples:
        output.append(f"## Input: `{cmd}`")
        
        parsed = parse_command(cmd)
        output.append(f"**Intent**: {parsed['intent']}")
        output.append(f"**Slots**: {parsed['slots']}")
        
        # Snapshot state
        prev_loc = dict(world.locations)
        prev_holding = world.agents["nurse"].holding
        
        try:
            if not parsed['intent']:
                output.append("**Error**: Δεν βρέθηκε intent.")
                continue
                
            obj_id = resolve_reference(parsed["slots"], world, context)
            output.append(f"**Resolved Object**: `{obj_id}`")
            
            trace = plan_and_execute(parsed["intent"], obj_id, world, context)
            output.append("**Plan Execution Trace**:")
            for t in trace:
                output.append(f"- {t}")
                
            # Diff state
            diffs = []
            if world.agents["nurse"].holding != prev_holding:
                diffs.append(f"Agent holding: {prev_holding} -> {world.agents['nurse'].holding}")
            if world.locations.get(obj_id) != prev_loc.get(obj_id):
                diffs.append(f"Object location: {prev_loc.get(obj_id)} -> {world.locations.get(obj_id)}")
            if parsed['intent'] in ["OPEN", "CLOSE"]:
                diffs.append(f"Object is_open: {world.objects[obj_id].is_open}")
                
            if diffs:
                output.append("**State Diff**:")
                for d in diffs:
                    output.append(f"- {d}")
            else:
                output.append("**State Diff**: No visible changes.")
                
        except (AmbiguityError, NotFoundError, SafetyError, PlanError) as e:
            output.append(f"**Exception**: {type(e).__name__} - {e}")
            
        output.append("\n---\n")

    with open("data/stage1_examples.md", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    run_examples()
