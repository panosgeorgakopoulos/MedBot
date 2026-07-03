from typing import List, Dict, Any, Optional
from src.world import WorldState, MedicalObject
from src.context import DialogueContext

class ResolutionError(Exception):
    pass

class AmbiguityError(ResolutionError):
    def __init__(self, candidates: List[MedicalObject], world: WorldState):
        self.candidates = candidates
        names = []
        for i, c in enumerate(candidates):
            locs = ",".join(list(set(b.zone for b in c.batches if b.quantity > 0)))
            names.append(f"({i+1}) {c.name} ({locs})")
        self.message = "Εννοείτε: " + ", ".join(names) + ";"
        super().__init__(self.message)

class NotFoundError(ResolutionError):
    def __init__(self, msg="Δεν βρέθηκε το αντικείμενο."):
        super().__init__(msg)


def resolve_reference(slots: Dict[str, Any], world: WorldState, context: DialogueContext) -> str:
    """
    Returns the resolved object_id.
    Raises AmbiguityError or NotFoundError.
    """
    noun = slots.get('noun')
    size = slots.get('size')
    state = slots.get('state')
    location = slots.get('location')
    pronoun = slots.get('pronoun')
    
    # Pronoun resolution
    if pronoun and not noun:
        if context.last_mentioned_objects:
            return context.last_mentioned_objects[0]
        else:
            raise NotFoundError("Δεν ξέρω σε τι αναφέρεστε (χρήση αντωνυμίας χωρίς προηγούμενο).")
            
    # Filter candidates
    candidates = []
    for obj_id, obj in world.objects.items():
        if noun and obj.name != noun:
            continue
            
        if size:
            if size == "μικρό" and obj.size in ["5x5", "1ml", "21g"]: pass
            elif size == "μεσαίο" and obj.size in ["5ml"]: pass
            elif size == "μεγάλο" and obj.size in ["10x10", "10ml", "18g"]: pass
            elif obj.size == size: pass
            else: continue
            
        if state:
            if state == "αποστειρωμένο" and "sterile" not in obj.id:
                continue
            if state == "ανοιχτό" and not obj.is_open:
                continue
            
        obj_locs = [b.zone for b in obj.batches if b.quantity > 0]
        if location and location not in obj_locs:
            continue
            
        candidates.append(obj)
        
    if len(candidates) == 0:
        raise NotFoundError(f"Δεν βρέθηκε αντικείμενο με τα κριτήρια.")
    elif len(candidates) == 1:
        return candidates[0].id
    else:
        # Ambiguity resolution via recency
        if context.last_mentioned_zone:
            ranked = [c for c in candidates if context.last_mentioned_zone in [b.zone for b in c.batches if b.quantity > 0]]
            if len(ranked) == 1:
                return ranked[0].id
                
        raise AmbiguityError(candidates, world)
