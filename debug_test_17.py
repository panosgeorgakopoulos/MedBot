from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
import json

world = setup_initial_world()
resolver = UnifiedResolver(world)
context = DialogueContext()

utt = "if paracetamol is out of stock, bring ibuprofen instead"
res = resolver.resolve_command(utt, context)
print("Result for test 17:")
print(json.dumps(res, indent=2, default=str))
