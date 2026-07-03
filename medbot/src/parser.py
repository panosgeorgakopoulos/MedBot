import re
from typing import Dict, Any
from src.lexicon import canonicalize_greek_noun

def parse_command(command: str) -> Dict[str, Any]:
    command = command.lower().strip()
    
    # 1. Intent Detection
    intent = None
    if re.search(r'\b(φέρε|φέρτε|πάρε|παρέδωσε)\b', command):
        intent = "FETCH"
    elif re.search(r'\b(βάλε|τοποθέτησε|άφησε)\b', command):
        intent = "PLACE"
    elif re.search(r'\b(άνοιξε|ξεκλείδωσε)\b', command):
        intent = "OPEN"
    elif re.search(r'\b(κλείσε|σφράγισε)\b', command):
        intent = "CLOSE"
    elif re.search(r'\b(έλεγξε|τσέκαρε|δες|εξέτασε)\b', command):
        intent = "INSPECT"
    elif re.search(r'\b(δώσε|χορήγησε)\b', command):
        intent = "GIVE"
    elif re.search(r'\b(πόσες|πόσα|πόση|έχω|έχουμε|μένουν|απομένουν|υπάρχουν)\b', command) or re.search(r'\b(how much|how many|is left|do we have)\b', command):
        intent = "CHECK_STOCK"
    elif re.search(r'\b(πού|where|locate)\b', command):
        intent = "LOCATE"
    elif re.search(r'\b(κρατάς|έχεις στα χέρια|κρατάω)\b', command) or re.search(r'\b(holding|hands)\b', command):
        intent = "HOLDING"
        
    # Exclusion tracking
    is_negated = bool(re.search(r'\b(όχι|μην|not|except|but)\b', command))
        
    # 2. Extract Slots
    size = None
    excluded_size = None
    size_match = re.search(r'\b(5x5|10x10|1ml|5ml|10ml|18g|21g|500mg|μικρό|μικρή|μεγάλο|μεγάλη|μεσαίο|μεσαία)\b', command)
    if size_match:
        val = size_match.group(1)
        if val in ['μικρό', 'μικρή']: val = 'μικρό'
        if val in ['μεγάλο', 'μεγάλη']: val = 'μεγάλο'
        if val in ['μεσαίο', 'μεσαία']: val = 'μεσαίο'
        if is_negated:
            excluded_size = val
        else:
            size = val
        
    state = None
    excluded_state = None
    state_match = re.search(r'\b(αποστειρωμένο|αποστειρωμένη|ανοιχτό|ανοιχτή|ληγμένο|ληγμένη|expired)\b', command)
    if state_match:
        val = state_match.group(1)
        if val in ['αποστειρωμένο', 'αποστειρωμένη']: val = 'αποστειρωμένο'
        if val in ['ανοιχτό', 'ανοιχτή']: val = 'ανοιχτό'
        if val in ['ληγμένο', 'ληγμένη', 'expired']: val = 'ληγμένο'
        if is_negated:
            excluded_state = val
        else:
            state = val
        
    location = None
    loc_match = re.search(r'\b(φαρμακείο|μεθ|αποθήκη|θάλαμο|θάλαμος)\b', command)
    if loc_match:
        val = loc_match.group(1)
        if val == 'θάλαμο': val = 'Θάλαμος'
        if val == 'θάλαμος': val = 'Θάλαμος'
        if val == 'φαρμακείο': val = 'Φαρμακείο'
        if val == 'μεθ': val = 'ΜΕΘ'
        if val == 'αποθήκη': val = 'Αποθήκη'
        location = val

    pronoun = None
    if re.search(r'\b(εκείνο|αυτό|το|την|τον|it)\b', command):
        pronoun = True
        
    noun = None
    fallback_noun = None
    nouns_found = re.findall(r'\b(γάζα|γάζες|επίδεσμο|επίδεσμος|σύριγγα|βελόνα|παρακεταμόλη|ιβουπροφένη|αντιβιοτικό|σφυγμόμετρο|οξύμετρο|θερμόμετρο|κουτί)\b', command)
    
    if nouns_found:
        mapping = {
            'γάζ': 'Γάζα',
            'επίδεσμ': 'Επίδεσμος',
            'σύριγγ': 'Σύριγγα',
            'βελόν': 'Βελόνα',
            'παρακεταμόλ': 'Παρακεταμόλη',
            'ιβουπροφέν': 'Ιβουπροφένη',
            'αντιβιοτικό': 'Αντιβιοτικό',
            'σφυγμόμετρ': 'Σφυγμόμετρο',
            'οξύμετρ': 'Οξύμετρο',
            'θερμόμετρ': 'Θερμόμετρο',
            'κουτί': 'Κουτί'
        }
        valid_nouns = []
        for n in nouns_found:
            val = canonicalize_greek_noun(n)
            valid_nouns.append(mapping.get(val, val.capitalize()))
            
        # Deduplicate while preserving order
        seen = set()
        unique_nouns = [x for x in valid_nouns if not (x in seen or seen.add(x))]
        
        if "Κουτί" in unique_nouns and len(unique_nouns) > 1:
            unique_nouns.remove("Κουτί")
            
        noun = unique_nouns[0]
        if len(unique_nouns) > 1:
            fallback_noun = unique_nouns[1]

    return {
        "intent": intent,
        "slots": {
            "size": size,
            "state": state,
            "location": location,
            "noun": noun,
            "fallback_noun": fallback_noun,
            "pronoun": pronoun,
            "excluded_state": excluded_state,
            "excluded_size": excluded_size
        }
    }
