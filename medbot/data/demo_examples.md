# MedBot Demo Commands Cheat Sheet

Here are several examples of commands you can enter into the MedBot Gradio interface. They showcase the different resolution layers of the **Unified Smart Resolver**.

---

## 1. Greek Commands (Greek Persona / Nurse)
These commands primarily trigger Layer 1 (Rules) or Layer 2 (ML Classifier) and resolve directly.

* **"φέρε τη γάζα 10x10 από την αποθήκη"**
  * *Expected Intent:* `FETCH`
  * *Expected Object:* `Γάζα` (10x10, Αποθήκη)
* **"άνοιξε το κουτί πρώτων βοηθειών"**
  * *Expected Intent:* `OPEN`
  * *Expected Object:* `Κουτί`
* **"δώσε μου μια σύριγγα 5ml"**
  * *Expected Intent:* `GIVE`
  * *Expected Object:* `Σύριγγα` (5ml)
* **"έλεγξε το θερμόμετρο"**
  * *Expected Intent:* `INSPECT`
  * *Expected Object:* `Θερμόμετρο`
* **"κλείσε το βαλιτσάκι"**
  * *Expected Intent:* `CLOSE`
  * *Expected Object:* `Κουτί`

---

## 2. English & Cross-Lingual Commands
These commands show how the system resolves English commands using our alias map (Layer 1 EN) or multilingual embeddings (Layer 3).

* **"bring bandaids"**
  * *Expected Intent:* `FETCH`
  * *Expected Object:* `Γάζα` (mapped via alias)
* **"get a syringe"**
  * *Expected Intent:* `FETCH`
  * *Expected Object:* `Σύριγγα` (mapped via alias)
* **"I need some tylenol"**
  * *Expected Intent:* Falls back to Clarification/Semantic because "I need" is not a fast-matched verb.
  * *Expected Object:* `Παρακεταμόλη` (mapped via alias)
* **"inspect the blood pressure monitor"**
  * *Expected Intent:* `INSPECT`
  * *Expected Object:* `Σφυγμόμετρο` (mapped via alias)
* **"give me the plaster"**
  * *Expected Intent:* `FETCH` / `GIVE`
  * *Expected Object:* `Γάζα`

---

## 3. Typo-Robust & Colloquial Commands (Fuzzy Match)
These test the `rapidfuzz` spelling robustness.

* **"φερε τη γαζα"** (Missing Greek accents)
  * *Expected Intent:* `FETCH`
  * *Expected Object:* `Γάζα`
* **"φέρε τη συρριγα 1ml"** (Double 'ρ' spelling typo)
  * *Expected Intent:* `FETCH`
  * *Expected Object:* `Σύριγγα` (1ml)
* **"δώσε μου τις γαζες"** (Plural inflected noun)
  * *Expected Intent:* `GIVE`
  * *Expected Object:* `Γάζα`

---

## 4. Vague & Out-of-Domain Commands
These demonstrate Layer 3 embeddings match or Layer 4 rejection.

* **"the thing near the window"**
  * *Expected Behavior:* Falls back to Layer 3 Semantic Embeddings and maps to the first aid kit (`first_aid_kit`) or thermometer, depending on context.
* **"what's the weather"**
  * *Expected Behavior:* Triggers **Layer 4 (OOD)** and returns: *"This seems out of scope for my hospital duties. I can only manage medical supplies."*
* **"play some music"**
  * *Expected Behavior:* Triggers **Layer 4 (OOD)**.
