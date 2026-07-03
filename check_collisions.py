import json
import os
import sys

def canonicalize_greek_noun(word: str) -> str:
    word = word.lower()
    # Remove common suffixes for plural and accusative to get a base stem
    suffixes = ['ες', 'ους', 'οι', 'ων', 'α', 'ο', 'ος', 'η', 'ης']
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

aliases_dict = {}
alias_path = os.path.join(os.path.dirname(__file__), "data", "aliases.json")
if os.path.exists(alias_path):
    with open(alias_path, "r", encoding="utf-8") as f:
        aliases_dict = json.load(f)
else:
    print("No aliases.json found.")

objects = [
    "Γάζα", "Επίδεσμος", "Σύριγγα", "Βελόνα", "Παρακεταμόλη", 
    "Ιβουπροφένη", "Αντιβιοτικό", "Μορφίνη", "Σφυγμόμετρο", 
    "Οξύμετρο", "Θερμόμετρο", "Κουτί"
]

all_words = []
for obj in objects:
    all_words.append((obj, obj))
    if obj in aliases_dict:
        for alias in aliases_dict[obj]:
            all_words.append((obj, alias))

stems = {}
collisions = []
for obj_name, word in all_words:
    stem = canonicalize_greek_noun(word)
    if stem in stems and stems[stem] != obj_name:
        collisions.append((stem, word, obj_name, stems[stem]))
    else:
        stems[stem] = obj_name

print("Stems:")
for s, o in stems.items():
    print(f"  {s} -> {o}")

print("\nCollisions:")
if not collisions:
    print("  None")
else:
    for c in collisions:
        print(f"  Stem '{c[0]}' from word '{c[1]}' (object: {c[2]}) collides with object {c[3]}")
