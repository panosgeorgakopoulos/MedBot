from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
import json

world = setup_initial_world()
resolver = UnifiedResolver(world)
context = DialogueContext()

utterance = "φέρε δύο γάζες"
action_dict = {"action": "FETCH", "object_query": utterance}
res = resolver.resolve_atomic(action_dict, context)
print("Result for 'φέρε δύο γάζες':")
print(json.dumps(res, indent=2, default=str))

parsed = __import__("src.parser", fromlist=["parse_command"]).parse_command(utterance)
print("Parsed:", parsed)

utt_clean = resolver.strip_accents(utterance)
parsed_noun = parsed.get("slots", {}).get("noun")
match_targets = [utt_clean]
if parsed_noun:
    match_targets.append(resolver.strip_accents(parsed_noun))

print("Match targets:", match_targets)

for o_id, obj in world.objects.items():
    if "gaza" in o_id:
        choices = [resolver.strip_accents(a) for a in obj.aliases] + [resolver.strip_accents(obj.name)]
        print("Choices for", o_id, ":", choices)
