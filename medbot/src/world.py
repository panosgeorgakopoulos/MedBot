from dataclasses import dataclass, field
from typing import List, Set, Optional, Tuple, Dict
from datetime import datetime, timedelta
import json
import os
from enum import Enum

class ActionType(Enum):
    FETCH = "FETCH"
    PLACE = "PLACE"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    INSPECT = "INSPECT"
    GIVE = "GIVE"
    CHECK_STOCK = "CHECK_STOCK"
    LOCATE = "LOCATE"
    HISTORY = "HISTORY"
    HOLDING = "HOLDING"

@dataclass
class Zone:
    name: str

@dataclass
class Batch:
    batch_id: str
    quantity: int
    expiry_date: datetime
    zone: str

@dataclass
class MedicalObject:
    id: str
    name: str
    category: str
    size: Optional[str] = None
    is_container: bool = False
    is_open: bool = False
    aliases: List[str] = field(default_factory=list)
    
    # Inventory updates
    batches: List[Batch] = field(default_factory=list)
    par_level: int = 0
    is_controlled: bool = False
    requires_refrigeration: bool = False
    substitutes: List[str] = field(default_factory=list) # List of obj IDs
    
    @property
    def total_quantity(self) -> int:
        return sum(b.quantity for b in self.batches)
        
    def get_quantity_in_zone(self, zone: str) -> int:
        return sum(b.quantity for b in self.batches if b.zone == zone)

@dataclass
class Agent:
    name: str
    location: str
    holding: Dict[str, int] = field(default_factory=dict)
    role: str = "nurse" # nurse, pharmacist, doctor

@dataclass
class WorldState:
    zones: Dict[str, Zone] = field(default_factory=dict)
    objects: Dict[str, MedicalObject] = field(default_factory=dict)
    agents: Dict[str, Agent] = field(default_factory=dict)
    
    # Relations
    on_rel: Set[Tuple[str, str]] = field(default_factory=set)
    inside_rel: Set[Tuple[str, str]] = field(default_factory=set)
    next_to_rel: Set[Tuple[str, str]] = field(default_factory=set)

    def on(self, obj_a: str, obj_b: str) -> bool:
        return (obj_a, obj_b) in self.on_rel

    def inside(self, obj_a: str, obj_b: str) -> bool:
        return (obj_a, obj_b) in self.inside_rel

    def next_to(self, obj_a: str, obj_b: str) -> bool:
        return (obj_a, obj_b) in self.next_to_rel

def setup_initial_world() -> WorldState:
    ws = WorldState()
    
    aliases_dict = {}
    alias_path = os.path.join(os.path.dirname(__file__), "..", "data", "aliases.json")
    if os.path.exists(alias_path):
        with open(alias_path, "r", encoding="utf-8") as f:
            aliases_dict = json.load(f)
            
    for z in ["Φαρμακείο", "ΜΕΘ", "Αποθήκη", "Θάλαμος"]:
        ws.zones[z] = Zone(name=z)
        
    ws.agents["user"] = Agent(name="user", location="Φαρμακείο", role="nurse")
    
    now = datetime.now()
    valid_expiry = now + timedelta(days=365)
    expired_expiry = now - timedelta(days=10)
    
    objs = [
        MedicalObject(id="gaza_5x5", name="Γάζα", category="Επιδέσμια", size="5x5", par_level=50,
                      batches=[Batch("B1", 100, valid_expiry, "Αποθήκη"), Batch("B2", 10, valid_expiry, "Φαρμακείο")]),
        MedicalObject(id="gaza_10x10", name="Γάζα", category="Επιδέσμια", size="10x10", par_level=20,
                      batches=[Batch("B3", 50, valid_expiry, "Αποθήκη")]),
        MedicalObject(id="gaza_sterile", name="Γάζα", category="Επιδέσμια", par_level=10, 
                      batches=[Batch("B4", 5, valid_expiry, "ΜΕΘ")]),
        MedicalObject(id="epidesmos_1", name="Επίδεσμος", category="Επιδέσμια", par_level=10,
                      batches=[Batch("B5", 20, valid_expiry, "Φαρμακείο")]),
        
        MedicalObject(id="siringa_1ml", name="Σύριγγα", category="Ένεση", size="1ml", par_level=100,
                      batches=[Batch("B6", 200, valid_expiry, "Φαρμακείο")]),
        MedicalObject(id="siringa_5ml", name="Σύριγγα", category="Ένεση", size="5ml", par_level=50,
                      batches=[Batch("B7", 60, valid_expiry, "Φαρμακείο")]),
        MedicalObject(id="siringa_10ml", name="Σύριγγα", category="Ένεση", size="10ml", par_level=20,
                      batches=[Batch("B8", 10, valid_expiry, "Αποθήκη")]),
        MedicalObject(id="velona_18G", name="Βελόνα", category="Ένεση", size="18G", par_level=50,
                      batches=[Batch("B9", 100, valid_expiry, "Φαρμακείο")]),
        MedicalObject(id="velona_21G", name="Βελόνα", category="Ένεση", size="21G", par_level=50,
                      batches=[Batch("B10", 100, valid_expiry, "Φαρμακείο")]),
        
        MedicalObject(id="paracetamol", name="Παρακεταμόλη", category="Φάρμακα", size="500mg", par_level=30,
                      batches=[Batch("B11", 50, valid_expiry, "Φαρμακείο"), Batch("B12", 5, valid_expiry, "ΜΕΘ")],
                      substitutes=["ibuprofen"]),
        MedicalObject(id="ibuprofen", name="Ιβουπροφένη", category="Φάρμακα", par_level=20,
                      batches=[Batch("B13", 40, valid_expiry, "Φαρμακείο")],
                      substitutes=["paracetamol"]),
        
        MedicalObject(id="antibiotic", name="Αντιβιοτικό", category="Φάρμακα", par_level=10,
                      batches=[Batch("B14", 5, expired_expiry, "Αποθήκη"), Batch("B15", 20, valid_expiry, "Φαρμακείο")],
                      requires_refrigeration=True),
                      
        # Controlled substance
        MedicalObject(id="morphine", name="Μορφίνη", category="Φάρμακα", par_level=5, is_controlled=True,
                      batches=[Batch("B16", 10, valid_expiry, "Φαρμακείο")]),
        
        MedicalObject(id="sphygmo", name="Σφυγμόμετρο", category="Εξοπλισμός", par_level=1,
                      batches=[Batch("EQ1", 1, valid_expiry, "Θάλαμος")]),
        MedicalObject(id="oxy", name="Οξύμετρο", category="Εξοπλισμός", par_level=1,
                      batches=[Batch("EQ2", 1, valid_expiry, "Θάλαμος")]),
        MedicalObject(id="thermo", name="Θερμόμετρο", category="Εξοπλισμός", par_level=2,
                      batches=[Batch("EQ3", 1, valid_expiry, "ΜΕΘ"), Batch("EQ4", 1, valid_expiry, "Φαρμακείο")]),
        MedicalObject(id="first_aid_kit", name="Κουτί", category="Εξοπλισμός", is_container=True, is_open=False,
                      batches=[Batch("EQ5", 1, valid_expiry, "ΜΕΘ")])
    ]
    
    for o in objs:
        if o.name in aliases_dict:
            o.aliases = aliases_dict[o.name]
        ws.objects[o.id] = o
        
    ws.inside_rel.add(("gaza_sterile", "first_aid_kit"))
    ws.on_rel.add(("oxy", "sphygmo"))
    ws.next_to_rel.add(("siringa_5ml", "velona_21G"))

    return ws
