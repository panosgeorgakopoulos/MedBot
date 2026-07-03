# Stage 1: Symbolic Baseline Examples

## Input: `Φέρε μου τη γάζα 10x10 από την αποθήκη`
**Intent**: FETCH
**Slots**: {'size': '10x10', 'state': None, 'location': 'Αποθήκη', 'noun': 'Γάζα', 'pronoun': True}
**Resolved Object**: `gaza_10x10`
**Plan Execution Trace**:
- Moving to Αποθήκη to fetch Γάζα
- FETCHED Γάζα (gaza_10x10)
**State Diff**:
- Agent holding: None -> gaza_10x10
- Object location: Αποθήκη -> nurse

---

## Input: `Βάλε τη γάζα`
**Intent**: PLACE
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': 'Γάζα', 'pronoun': None}
**Resolved Object**: `gaza_5x5`
**Plan Execution Trace**:
- Need to fetch Γάζα first.
- PLACED Γάζα at Αποθήκη
**State Diff**:
- Agent holding: gaza_10x10 -> None

---

## Input: `Έλεγξε την`
**Intent**: INSPECT
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': None, 'pronoun': True}
**Resolved Object**: `gaza_5x5`
**Plan Execution Trace**:
- INSPECTED Γάζα. Κατάσταση: None, Μέγεθος: 5x5
**State Diff**: No visible changes.

---

## Input: `Άνοιξε το κουτί στη ΜΕΘ`
**Intent**: OPEN
**Slots**: {'size': None, 'state': None, 'location': 'ΜΕΘ', 'noun': 'Κουτί', 'pronoun': True}
**Resolved Object**: `first_aid_kit`
**Plan Execution Trace**:
- OPENED Κουτί
**State Diff**:
- Object is_open: True

---

## Input: `Δώσε το αντιβιοτικό`
**Intent**: GIVE
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': 'Αντιβιοτικό', 'pronoun': True}
**Resolved Object**: `antibiotic`
**Exception**: SafetyError - ΠΡΟΣΟΧΗ: Το Αντιβιοτικό είναι ληγμένο! Προτείνω να χρησιμοποιήσετε ένα άλλο σε απόθεμα.

---

## Input: `Φέρε τη σύριγγα 1ml`
**Intent**: FETCH
**Slots**: {'size': '1ml', 'state': None, 'location': None, 'noun': 'Σύριγγα', 'pronoun': None}
**Resolved Object**: `siringa_1ml`
**Plan Execution Trace**:
- Moving to Φαρμακείο to fetch Σύριγγα
- FETCHED Σύριγγα (siringa_1ml)
**State Diff**:
- Agent holding: None -> siringa_1ml
- Object location: Φαρμακείο -> nurse

---

## Input: `Δώσε την`
**Intent**: GIVE
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': None, 'pronoun': True}
**Resolved Object**: `siringa_1ml`
**Plan Execution Trace**:
- GIVEN Σύριγγα to patient.
**State Diff**:
- Agent holding: siringa_1ml -> None
- Object location: nurse -> patient

---

## Input: `Φέρε μου την παρακεταμόλη`
**Intent**: FETCH
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': 'Παρακεταμόλη', 'pronoun': True}
**Resolved Object**: `paracetamol_pharmacy`
**Plan Execution Trace**:
- Moving to Φαρμακείο to fetch Παρακεταμόλη
- FETCHED Παρακεταμόλη (paracetamol_pharmacy)
**State Diff**:
- Agent holding: None -> paracetamol_pharmacy
- Object location: Φαρμακείο -> nurse

---

## Input: `Φέρε το θερμόμετρο από το φαρμακείο`
**Intent**: FETCH
**Slots**: {'size': None, 'state': None, 'location': 'Φαρμακείο', 'noun': 'Θερμόμετρο', 'pronoun': True}
**Exception**: NotFoundError - Δεν βρέθηκε αντικείμενο με τα κριτήρια.

---

## Input: `Κλείσε το κουτί`
**Intent**: CLOSE
**Slots**: {'size': None, 'state': None, 'location': None, 'noun': 'Κουτί', 'pronoun': True}
**Resolved Object**: `first_aid_kit`
**Plan Execution Trace**:
- CLOSED Κουτί
**State Diff**:
- Object is_open: False

---
