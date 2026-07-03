# MedBot: SHRDLU-Inspired Grounded Language System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MedBot is a natural language understanding system designed for a Greek hospital microworld. Inspired by Winograd's (1972) SHRDLU, MedBot provides a highly robust, context-aware NLU interface for medical inventory management, utilizing a constrained universe with explicit rules, state mutations, and a focus on grounding language directly to physical hospital objects and actions.

## 🌟 Features

- **Multi-layered NLU Routing:**
  - **Layer 1 (Symbolic Baseline):** Fast, deterministic rule-based parser utilizing regex templates and alias matching.
  - **Layer 2 (Classical ML):** Logistic Regression classifier and Conditional Random Field (CRF) tagger to handle noisy or elliptical inputs via learned n-grams.
  - **Layer 3 (Semantic Embeddings):** Hugging Face Transformer model (`paraphrase-multilingual-MiniLM-L12-v2`) for complex semantic matching and out-of-vocabulary terms.
- **Strict Clinical Constraints:** Deterministic planner execution checks expiration dates, inventory levels, and role-based access before mutating state.
- **Context-Aware Dialogue:** Context recency enables seamless pronoun resolution across conversation turns.
- **Privacy-First:** Redaction of Patient Health Information (PHI) via `anonymize_log.py` to ensure GDPR compliance.
- **Interactive UI:** Built-in Gradio dashboard for live simulation and audit logging.

## 🛠 Prerequisites

- Python 3.10 or higher
- `pip` or `uv` package manager

## 🚀 Installation & Setup

1. **Clone the repository and set up a virtual environment:**
   ```bash
   git clone https://github.com/panosgeorgakopoulos/MedBot.git
   cd MedBot
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🧪 Testing & Model Training

MedBot's classical machine learning models must be trained before launching the full application.

1. **Run the Unit Tests:**
   Validate the core baseline logic and planner mechanics.
   ```bash
   PYTHONPATH=. pytest tests/
   ```

2. **Generate the Dataset & Train Models:**
   Generate the combinatorial clinical datasets and train the Stage 2 Intent Classifier and Slot Tagger.
   ```bash
   PYTHONPATH=. python3 src/generate_dataset.py
   PYTHONPATH=. python3 src/train_intent_classifier.py
   PYTHONPATH=. python3 src/train_slot_tagger.py
   ```

3. **Evaluate the System (Optional):**
   Compare the Stage 1 Rule-based metrics against the Stage 2 Sequence models.
   ```bash
   PYTHONPATH=. python3 src/evaluate.py
   ```

## 💻 Usage (Interactive Dashboard)

To interact with MedBot through the visual web interface, launch the Gradio application:

```bash
PYTHONPATH=. python3 gradio_app.py
```
*Navigate to `http://localhost:7860` in your web browser to access the dashboard.*

## 📂 Project Structure

```text
MedBot/
├── src/                        # Core application logic
│   ├── parser.py               # Layer 1 symbolic parser
│   ├── world.py                # Hospital microworld state and dataclasses
│   ├── planner.py              # Action validation and execution engine
│   ├── reference_resolution.py # Entity resolution and grounding
│   └── *                       # Various ML and dataset generation scripts
├── tests/                      # Pytest unit tests for Stage 1 mechanics
├── data/                       # Generated datasets and aliases
├── models/                     # Serialized ML models (.joblib)
├── gradio_app.py               # Interactive web UI launch script
└── report.md                   # Final academic report answering rubric questions
```

## 👥 Authors
- **Georgakopoulos Panagiotis Sergios** - P23024
- **Dimitriou Konstantinos** - P23040
