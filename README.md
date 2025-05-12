# Crossword Solver

An AI-assisted crossword solving system that combines semantic clue-answer ranking, constraint satisfaction, and region-based grid solving. This is a personal project and extension/redo of a project from the Northeastern FAI class.

## Structure

- `clue_processing/` – Template and ML-based clue parsers
- `semantic_ranking/` – Fine-tuned BERT models for clue-answer similarity
- `answer_generation/` – Candidate generation and ranking logic
- `grid/` – Crossword grid construction, parsing, and display utilities
- `gui/` – Interactive visualization / solving GUI
- `models/` – Saved ML models, embeddings, and config files
- `data/` – Input crossword puzzle files (CSV/JSON)
- `utils/` – Shared helper utilities
- `scripts/` – CLI tools and experiments
- `tests/` – Unit and integration tests
- `main.py` – Entry point for the solver

## Setup

```bash
pip install -r requirements.txt
