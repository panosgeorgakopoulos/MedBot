from src.context import DialogueContext
from src.decomposer import CommandDecomposer
import json

decomposer = CommandDecomposer()
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
    res = decomposer.decompose(utt, context)
    print(f"Decomposer output for '{utt}':")
    print(json.dumps(res, indent=2, default=str))
