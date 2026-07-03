from src.context import DialogueContext
from src.decomposer import CommandDecomposer
import json

decomposer = CommandDecomposer()
context = DialogueContext()
utt = "if paracetamol is out of stock, bring ibuprofen instead"
res = decomposer.decompose(utt, context)
print("Decomposer output for test 17:")
print(json.dumps(res, indent=2))
