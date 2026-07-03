from typing import List, Optional

class DialogueContext:
    def __init__(self):
        self.last_action: Optional[str] = None
        self.last_mentioned_objects: List[str] = []
        self.last_mentioned_zone: Optional[str] = None
        self.awaiting_clarification: bool = False
        self.clarification_intent: Optional[str] = None
        self.clarification_object: Optional[str] = None
        
    def update(self, action: str, objects: List[str], zone: Optional[str] = None):
        if action:
            self.last_action = action
        if objects:
            self.last_mentioned_objects = objects
        if zone:
            self.last_mentioned_zone = zone
        self.awaiting_clarification = False
        self.clarification_intent = None
        self.clarification_object = None
