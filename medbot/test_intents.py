import pytest
from src.world import setup_initial_world
from src.context import DialogueContext
from src.unified_resolver import UnifiedResolver
from src.planner import plan_and_execute

@pytest.fixture(scope="session")
def global_resolver():
    # Only load the models ONCE for the whole test suite to prevent OOM / hanging
    world = setup_initial_world()
    resolver = UnifiedResolver(world)
    return resolver

@pytest.fixture
def setup(global_resolver):
    # Create a fresh world state and fresh context for each test,
    # but reuse the loaded ML models in the global_resolver
    world = setup_initial_world()
    resolver = global_resolver
    resolver.world = world # point to the fresh world
    context = DialogueContext()
    return world, resolver, context

def test_1_fetch_two_gauze(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("φέρε δύο γάζες", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'FETCH'
    assert req['object_id'].startswith('gaza')
    assert req['quantity'] == 2.0
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 1 Trace: {plan['trace']}")

def test_2_fetch_1_gauze(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("φέρε 1 Γάζα", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['quantity'] == 1.0
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 2 Trace: {plan['trace']}")

def test_3_give_mia_gaza(setup):
    world, resolver, context = setup
    # Give intent requires item in holding first
    world.agents["user"].holding["gaza_5x5"] = 10
    res = resolver.resolve_command("δώσε μία γάζα", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'GIVE'
    assert req['quantity'] == 1.0
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 3 Trace: {plan['trace']}")

def test_4_give_1_gaza(setup):
    world, resolver, context = setup
    world.agents["user"].holding["gaza_5x5"] = 10
    res = resolver.resolve_command("δώσε 1 γάζα", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['quantity'] == 1.0
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 4 Trace: {plan['trace']}")

def test_5_check_stock_gazes(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("πόσες γάζες έχω;", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'CHECK_STOCK'
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 5 Trace: {plan['trace']}")

def test_6_check_stock_menoun(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("πόσες γάζες μένουν;", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'CHECK_STOCK'
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 6 Trace: {plan['trace']}")

def test_7_holding_status(setup):
    world, resolver, context = setup
    world.agents["user"].holding["gaza_5x5"] = 2
    res = resolver.resolve_command("τι κρατάς;", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'HOLDING'
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 7 Trace: {plan['trace']}")

def test_8_fetch_treis_syringes(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("φέρε τρεις σύριγγες", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'FETCH'
    assert req['quantity'] == 3.0
    assert 'siringa' in req['object_id']
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    print(f"Test 8 Trace: {plan['trace']}")

def test_9_place_teseriz_gazes(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("βάλε τέσσερις γάζες στο ράφι", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'PLACE'
    assert req['quantity'] == 4.0

def test_10_miso_kouti(setup):
    world, resolver, context = setup
    world.agents["user"].holding["first_aid_kit"] = 10
    res = resolver.resolve_command("δώσε μισό κουτί γάζες", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['quantity'] == 0.5
    assert 'assumed_quantity_msg' in req
    plan = plan_and_execute(req, world, context)
    print(f"Test 10 Trace: {plan['trace']}")

def test_11_zero_quantity(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("δώσε καμία γάζα", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['quantity'] == 0.0
    plan = plan_and_execute(req, world, context)
    assert plan['status'] == 'success'
    assert "Quantity 0 requested. Action aborted." in plan['trace'][0]
    print(f"Test 11 Trace: {plan['trace']}")

def test_12_stock_zone(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("πόσα σφυγμόμετρα έχουμε στο ΜΕΘ;", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'CHECK_STOCK'
    plan = plan_and_execute(req, world, context)
    print(f"Test 12 Trace: {plan['trace']}")

def test_13_holding_english(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("what do you have in your hands right now", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'HOLDING'
    plan = plan_and_execute(req, world, context)
    print(f"Test 13 Trace: {plan['trace']}")

def test_14_stock_size(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("πόσες σύριγγες 5ml έχουμε;", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'CHECK_STOCK'
    assert req['object_id'] == 'siringa_5ml'
    plan = plan_and_execute(req, world, context)
    print(f"Test 14 Trace: {plan['trace']}")

def test_15_exclusion_greek(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("φέρε γάζα, όχι την ληγμένη", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['excluded_state'] == 'ληγμένο'
    plan = plan_and_execute(req, world, context)
    print(f"Test 15 Trace: {plan['trace']}")

def test_16_exclusion_english(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("bring gauze, not the expired one", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['excluded_state'] == 'ληγμένο'
    plan = plan_and_execute(req, world, context)
    print(f"Test 16 Trace: {plan['trace']}")

def test_17_conditional_english(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("if paracetamol is out of stock, bring ibuprofen instead", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'FETCH'
    assert req['fallback_object_id'] == 'ibuprofen'
    plan = plan_and_execute(req, world, context)
    print(f"Test 17 Trace: {plan['trace']}")

def test_18_conditional_greek(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("αν δεν έχει παρακεταμόλη, φέρε ιβουπροφένη", context)[0]
    assert res['error'] is None, f"Error was: {res['error']}"
    req = res['action_req']
    assert req['action'] == 'FETCH'
    plan = plan_and_execute(req, world, context)
    print(f"Test 18 Trace: {plan['trace']}")

def test_19_multi_turn_ellipsis(setup):
    world, resolver, context = setup
    res1 = resolver.resolve_command("bring the gauze", context)[0]
    req1 = res1['action_req']
    plan_and_execute(req1, world, context)
    
    res2 = resolver.resolve_command("actually make it two", context)[0]
    if res2.get('error'):
        pytest.fail(f"Test 19 Failed: {res2['error']}")
    else:
        req2 = res2['action_req']
        assert req2['quantity'] == 2.0
        plan2 = plan_and_execute(req2, world, context)
        print(f"Test 19 Trace: {plan2['trace']}")

def test_20_ambiguity(setup):
    world, resolver, context = setup
    res = resolver.resolve_command("bring a bandage", context)[0]
    assert res['error'] is not None, "Expected clarification error but got success"
    assert "Found multiple matching items" in res['error']
    print(f"Test 20 Clarification: {res['error']}")

def test_21_multi_holding(setup):
    world, resolver, context = setup
    req1 = resolver.resolve_command("bring 2 syringes", context)[0]['action_req']
    plan_and_execute(req1, world, context)
    
    req2 = resolver.resolve_command("fetch 1 gauze", context)[0]['action_req']
    plan_and_execute(req2, world, context)
    
    req3 = resolver.resolve_command("what are you holding", context)[0]['action_req']
    plan3 = plan_and_execute(req3, world, context)
    print(f"Test 21 Trace: {plan3['trace']}")
    assert any("2.0x Σύριγγα" in t for t in plan3['trace']) or any("2x Σύριγγα" in t for t in plan3['trace'])
    assert any("1.0x Γάζα" in t for t in plan3['trace']) or any("1x Γάζα" in t for t in plan3['trace'])
