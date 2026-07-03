import re

def canonicalize_greek_noun(word: str) -> str:
    word = word.lower().strip()
    suffixes = ['ες', 'ους', 'οι', 'ων', 'α', 'ο', 'ος', 'η', 'ης']
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def extract_quantity_and_assumptions(text: str) -> tuple:
    """Returns (quantity_float, assumption_string)."""
    text = text.lower().strip()
    
    # 1. Check for vague/fractional
    if re.search(r'\b(μισό|μισή|half)\b', text):
        return (0.5, "Assuming you mean 1 unit — let me know if that's wrong")
    if re.search(r'\b(μερικά|μερικές|λίγα|λίγες|few|some)\b', text):
        return (2.0, "Assuming you mean 2 units — let me know if that's wrong")
        
    # 2. Check for zero / none
    if re.search(r'\b(καμία|κανένα|κανέναν|μηδέν|zero|none|no)\b', text):
        return (0.0, None)
        
    # 3. Check for exact matches in Greek/English dictionary
    num_map = {
        'ένα': 1, 'ένας': 1, 'μία': 1, 'μια': 1, 'one': 1,
        'δύο': 2, 'δυο': 2, 'two': 2,
        'τρία': 3, 'τρεις': 3, 'three': 3,
        'τέσσερα': 4, 'τέσσερις': 4, 'four': 4,
        'πέντε': 5, 'five': 5,
        'έξι': 6, 'six': 6,
        'εφτά': 7, 'επτά': 7, 'seven': 7,
        'οκτώ': 8, 'οχτώ': 8, 'eight': 8,
        'εννέα': 9, 'εννιά': 9, 'nine': 9,
        'δέκα': 10, 'ten': 10,
        'έντεκα': 11, 'eleven': 11,
        'δώδεκα': 12, 'twelve': 12,
        'δεκατρία': 13, 'thirteen': 13,
        'δεκατέσσερα': 14, 'fourteen': 14,
        'δεκαπέντε': 15, 'fifteen': 15,
        'δεκαέξι': 16, 'sixteen': 16,
        'δεκαεφτά': 17, 'seventeen': 17,
        'δεκαοκτώ': 18, 'eighteen': 18,
        'δεκαεννέα': 19, 'nineteen': 19,
        'είκοσι': 20, 'twenty': 20,
        'τριάντα': 30, 'thirty': 30,
        'σαράντα': 40, 'forty': 40,
        'πενήντα': 50, 'fifty': 50,
        'εξήντα': 60, 'sixty': 60,
        'εβδομήντα': 70, 'seventy': 70,
        'ογδόντα': 80, 'eighty': 80,
        'ενενήντα': 90, 'ninety': 90,
        'εκατό': 100, 'hundred': 100
    }
    
    # We look for the first number word that appears as an isolated word
    tokens = text.split()
    for token in tokens:
        if token in num_map:
            return (float(num_map[token]), None)
            
    # 4. Fallback to digits
    match = re.search(r'\b(\d+)\b', text)
    if match:
        return (float(match.group(1)), None)
        
    # 5. Check if plural was used without a number
    plurals = ['γάζες', 'επιδέσμους', 'επίδεσμοι', 'σύριγγες', 'βελόνες', 'αντιβιοτικά', 'σφυγμόμετρα', 'οξύμετρα', 'θερμόμετρα', 'κουτιά', 'παρακεταμόλες', 'ιβουπροφένες', 'φάρμακα']
    if any(re.search(r'\b' + p + r'\b', text) for p in plurals):
        return (None, "Plural noun used without explicit quantity")
        
    return (1.0, None) # Default quantity
