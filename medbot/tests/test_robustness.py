import pytest
from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver

@pytest.fixture(scope="module")
def resolver():
    world = setup_initial_world()
    return UnifiedResolver(world)

@pytest.fixture
def context():
    return DialogueContext()

def test_robustness(resolver, context):
    tests = [
        ("bring bandaids", ["gaza_5x5", "gaza_10x10", "gaza_sterile", "epidesmos_1"]), 
        ("get a syringe", ["siringa_1ml", "siringa_5ml", "siringa_10ml"]),
        ("fetch tylenol", ["paracetamol"]),
        ("γαζα", ["gaza_5x5", "gaza_10x10", "gaza_sterile"]),
        ("the thing near the window", []), # Vague English reference, might hit layer 4 or 3
        ("what's the weather", None) # Should trigger OOD
    ]
    
    for text, valid_ids in tests:
        res = resolver.resolve_command(text, context)[0]
        print(f"Test: '{text}' -> Intent: {res['intent']}, Obj: {res['object_id']}, Layer: {res['layer']}")
        if valid_ids is not None:
            if valid_ids:
                # We expect it to either find a valid ID, or fall back to Clarification
                assert res["object_id"] in valid_ids or res["layer"] == "Layer 4 (Clarification)"
        else:
            assert res["layer"] == "Layer 4 (OOD)"

