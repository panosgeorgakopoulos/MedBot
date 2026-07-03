from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
import json

world = setup_initial_world()
resolver = UnifiedResolver(world)
context = DialogueContext()

utterances = [
    "φέρε δύο γάζες",
    "δώσε μία γάζα",
    "πόσες γάζες έχω;",
    "πόσες γάζες μένουν;",
    "φέρε τρεις σύριγγες",
    "δώσε καμία γάζα",
    "πόσες σύριγγες 5ml έχουμε;",
    "φέρε γάζα, όχι την ληγμένη"
]

for utt in utterances:
    res = resolver.resolve_command(utt, context)
    print(f"Result for '{utt}':")
    # Only print first element of the list, ignore None fields for brevity
    d = {k:v for k,v in res[0].items() if v is not None}
    print(json.dumps(d, indent=2, default=str))
