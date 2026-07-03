from src.world import WorldState, MedicalObject, ActionType
from src.context import DialogueContext
from src.audit import write_audit_log
from datetime import datetime

class SafetyError(Exception): pass
class PlanError(Exception): pass
class AuthRequired(Exception): pass

def get_available_batches(obj: MedicalObject, exclude_expired: bool = False, excluded_size: str = None, preferred_zone: str = None):
    now = datetime.now()
    batches = obj.batches
    
    if exclude_expired:
        batches = [b for b in batches if b.expiry_date > now]
        
    if excluded_size and obj.size and excluded_size in obj.size:
        batches = [] # If object itself is excluded by size, no batches available
        
    # Sort by preferred_zone first, then by expiry date (FIFO)
    def sort_key(b):
        return (0 if b.zone == preferred_zone else 1, b.expiry_date)
        
    batches = sorted(batches, key=sort_key)
    return batches

def plan_and_execute(action_req: dict, world: WorldState, context: DialogueContext) -> dict:
    intent = action_req.get("action")
    obj_id = action_req.get("object_id")
    qty = action_req.get("quantity")
    if qty is None:
        qty = 1.0
        
    fallback_id = action_req.get("fallback_object_id")
    exclude_expired = action_req.get("exclude_expired", False)
    auth_provided = action_req.get("auth_provided", False)
    assumed_quantity_msg = action_req.get("assumed_quantity_msg")
    
    excluded_state = action_req.get("excluded_state")
    if excluded_state == "ληγμένο":
        exclude_expired = True
    excluded_size = action_req.get("excluded_size")
    
    agent = world.agents.get("user")
    
    trace = []
    
    if assumed_quantity_msg:
        trace.append(f"({assumed_quantity_msg})")
        
    if qty == 0:
        trace.append("Quantity 0 requested. Action aborted.")
        return {"status": "success", "trace": trace, "color": "yellow"}
    
    if intent == "CHECK_STOCK":
        if not obj_id: return {"status": "error", "trace": ["No object specified for check stock."]}
        obj = world.objects[obj_id]
        total = obj.total_quantity
        trace.append(f"Checked stock for {obj.name}. Total overall: {total}.")
        
        zones_stock = {}
        for b in obj.batches:
            zones_stock[b.zone] = zones_stock.get(b.zone, 0) + b.quantity
            
        for z, count in zones_stock.items():
            if count > 0:
                trace.append(f"- In {z}: {count}")
                
        if total < obj.par_level:
            trace.append(f"WARNING: Stock is below par level ({total} < {obj.par_level})")
        return {"status": "success", "trace": trace, "color": "green"}
        
    if intent == "LOCATE":
        if not obj_id: return {"status": "error", "trace": ["No object specified to locate."]}
        obj = world.objects[obj_id]
        zones = set(b.zone for b in obj.batches if b.quantity > 0)
        if zones:
            trace.append(f"Found {obj.name} in zones: {', '.join(zones)}")
        else:
            trace.append(f"{obj.name} is not found anywhere.")
        return {"status": "success", "trace": trace, "color": "green"}
        
    if intent == "HOLDING":
        if not agent.holding:
            trace.append("Currently holding: nothing.")
        else:
            held_items = []
            for h_id, h_qty in agent.holding.items():
                if h_qty > 0:
                    display_qty = int(h_qty) if float(h_qty).is_integer() else h_qty
                    held_items.append(f"{display_qty}x {world.objects[h_id].name}")
            if held_items:
                trace.append("Currently holding: " + ", ".join(held_items))
            else:
                trace.append("Currently holding: nothing.")
        return {"status": "success", "trace": trace, "color": "green"}

    if intent in ["FETCH", "GIVE"]:
        if not obj_id: return {"status": "error", "trace": ["No object specified."]}
        obj = world.objects[obj_id]
        
        display_qty = int(qty) if float(qty).is_integer() else qty
        if intent == "GIVE":
            # For giving, we should check if we actually have it in holding
            held = agent.holding.get(obj_id, 0)
            if held < qty:
                trace.append(f"Failed: You cannot give {display_qty}x {obj.name} because you are only holding {held}.")
                return {"status": "blocked", "trace": trace, "color": "red"}
                
            agent.holding[obj_id] -= qty
            trace.append(f"GIVE {display_qty}x {obj.name}")
            return {"status": "success", "trace": trace, "color": "green"}
            
        # Check Authorization for controlled substances
        if obj.is_controlled and not auth_provided:
            return {"status": "auth_required", "trace": [f"Authorization required to {intent.lower()} {obj.name} (Controlled Substance)"], "color": "yellow"}
            
        batches = get_available_batches(obj, exclude_expired, excluded_size, agent.location)
        total_avail = sum(b.quantity for b in batches)
        
        if total_avail < qty:
            if fallback_id:
                trace.append(f"Insufficient stock for {obj.name}. Trying substitute...")
                return plan_and_execute({**action_req, "object_id": fallback_id, "fallback_object_id": None, "is_substitution": True}, world, context)
            else:
                trace.append(f"Failed: Insufficient stock for {obj.name}. Need {qty}, have {total_avail}.")
                return {"status": "blocked", "trace": trace, "color": "red"}
                
        # Deduct from batches
        remaining = qty
        used_batches = []
        for b in batches:
            if remaining <= 0: break
            if b.quantity > 0:
                take = min(b.quantity, remaining)
                b.quantity -= take
                remaining -= take
                used_batches.append((b.batch_id, take))
                
        # Update context
        context.update(intent, [obj_id])
        
        # Update agent holding
        agent.holding[obj_id] = agent.holding.get(obj_id, 0) + qty
        
        trace.append(f"{intent} {display_qty}x {obj.name}")
        for b_id, q in used_batches:
            display_q = int(q) if float(q).is_integer() else q
            trace.append(f"- Allocated {display_q} from batch {b_id}")
            write_audit_log(agent.role, intent, obj_id, b_id, q, "SUCCESS")
            
        # Check par level warning after deduction
        if obj.total_quantity < obj.par_level:
            trace.append(f"WARNING: {obj.name} stock dropped below par level ({obj.total_quantity} < {obj.par_level})")
            
        color = "green"
        if action_req.get("is_substitution"):
            trace.insert(0, f"SIMULATED SUGGESTION: Using {obj.name} as substitute. Clinician approval required in real world.")
            color = "yellow"
            
        return {"status": "success", "trace": trace, "color": color}
        
    if intent == "INSPECT":
        obj = world.objects[obj_id]
        trace.append(f"INSPECTED {obj.name}. Stock: {obj.total_quantity}. Expiry: {[b.expiry_date.strftime('%Y-%m-%d') for b in obj.batches if b.quantity > 0]}")
        return {"status": "success", "trace": trace, "color": "green"}
        
    if intent == "OPEN" or intent == "CLOSE":
        obj = world.objects[obj_id]
        if not obj.is_container:
            return {"status": "blocked", "trace": [f"Cannot {intent} {obj.name}, it is not a container."], "color": "red"}
        obj.is_open = (intent == "OPEN")
        trace.append(f"{intent}ED {obj.name}")
        return {"status": "success", "trace": trace, "color": "green"}

    return {"status": "error", "trace": [f"Unknown action: {intent}"], "color": "red"}
