# MedBot Dataset Description

This dataset consists of 600 Greek commands for a hospital microworld.
- **Generation Method**: 
  - ~75% generated using combinatorial templates (intent verbs + slots).
  - ~25% hand-authored minimal/elliptical commands mimicking the nurse persona.
- **Labels**:
  - `intent`: One of [FETCH, PLACE, OPEN, CLOSE, INSPECT, GIVE]
  - `tags`: BIO format tags for slots: B-TYPE, B-SIZE, B-STATE, B-ZONE.
- **Splits**: 70% Train, 15% Validation, 15% Test.
- **Seed**: Fixed at 42 for reproducibility.
