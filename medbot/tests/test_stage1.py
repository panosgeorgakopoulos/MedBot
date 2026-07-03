import pytest
from src.world import setup_initial_world
from src.context import DialogueContext
from src.parser import parse_command
from src.reference_resolution import resolve_reference, AmbiguityError, NotFoundError
from src.planner import plan_and_execute, SafetyError, PlanError

def test_successful_fetch():
    world = setup_initial_world()
    context = DialogueContext()
    cmd = "Φέρε μου τη σύριγγα 1ml από το φαρμακείο"
    parsed = parse_command(cmd)
    
    assert parsed["intent"] == "FETCH"
    assert parsed["slots"]["size"] == "1ml"
    
    obj_id = resolve_reference(parsed["slots"], world, context)
    assert obj_id == "siringa_1ml"
    
    action_req = {"action": parsed["intent"], "object_id": obj_id, "quantity": 1}
    res = plan_and_execute(action_req, world, context)
    trace = res["trace"]
    assert res["status"] == "success"
    assert any("FETCH 1x Σύριγγα" in t for t in trace)
    assert world.agents["user"].holding.get("siringa_1ml") == 1

def test_ambiguous_reference():
    world = setup_initial_world()
    context = DialogueContext()
    cmd = "Φέρε μου τη σύριγγα"
    parsed = parse_command(cmd)
    
    with pytest.raises(AmbiguityError) as exc:
        resolve_reference(parsed["slots"], world, context)
    assert "(1) Σύριγγα" in exc.value.message
    assert "(2) Σύριγγα" in exc.value.message

def test_ambiguity_resolved_via_recency():
    world = setup_initial_world()
    context = DialogueContext()
    context.last_mentioned_zone = "Αποθήκη"
    
    cmd = "Φέρε μου τη σύριγγα"
    parsed = parse_command(cmd)
    obj_id = resolve_reference(parsed["slots"], world, context)
    assert obj_id == "siringa_10ml"

def test_not_found_object():
    world = setup_initial_world()
    context = DialogueContext()
    cmd = "Φέρε μου το θερμόμετρο από την αποθήκη" # Thermo is in METH and Φαρμακείο
    parsed = parse_command(cmd)
    
    with pytest.raises(NotFoundError):
        resolve_reference(parsed["slots"], world, context)

def test_expired_item_give_blocked():
    world = setup_initial_world()
    context = DialogueContext()
    cmd = "Φέρε το αντιβιοτικό"
    parsed = parse_command(cmd)
    obj_id = resolve_reference(parsed["slots"], world, context)
    
    action_req = {"action": parsed["intent"], "object_id": obj_id, "quantity": 25, "excluded_state": "ληγμένο"}
    res = plan_and_execute(action_req, world, context)
    assert res["status"] == "blocked"
    assert any("Insufficient stock" in t for t in res["trace"])

def test_multistep_fetch_then_inspect():
    world = setup_initial_world()
    context = DialogueContext()
    
    # 1. Fetch thermometer
    cmd1 = "Φέρε το θερμόμετρο"
    parsed1 = parse_command(cmd1)
    obj_id1 = resolve_reference(parsed1["slots"], world, context)
    action_req1 = {"action": parsed1["intent"], "object_id": obj_id1, "quantity": 1}
    res1 = plan_and_execute(action_req1, world, context)
    assert res1["status"] == "success"
    assert world.agents["user"].holding.get("thermo") == 1
    
    # 2. Inspect it
    cmd2 = "Έλεγξε το"
    parsed2 = parse_command(cmd2)
    # uses pronoun resolution
    obj_id2 = resolve_reference(parsed2["slots"], world, context)
    assert obj_id2 == "thermo"
    action_req2 = {"action": parsed2["intent"], "object_id": obj_id2, "quantity": 1}
    res2 = plan_and_execute(action_req2, world, context)
    assert res2["status"] == "success"
    assert any("INSPECTED Θερμόμετρο" in t for t in res2["trace"])
