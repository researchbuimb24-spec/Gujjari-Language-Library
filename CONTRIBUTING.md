# Contributing to GojriLang

Thank you for your interest in contributing to **GojriLang**! Gojri (ISO 639-3: `gju`) is spoken by diverse Gujjar and Bakerwal communities across the Himalayas and adjoining regions. Because Gojri has significant dialectal and orthographic variation, community participation and academic rigor are vital.

---

## 1. Core Principles

1. **Evidence-Based Contributions**:
   - Every dictionary entry, grammar rule, or cultural item must cite a verifiable source (published grammar, academic paper, regional dictionary, or identified native speaker consultation).
   - Speculative forms or unverified machine translations are never accepted into the core verified datasets.

2. **Respect for Dialectal & Orthographic Diversity**:
   - Gojri is written in extended Perso-Arabic (Nastaliq), Devanagari, and academic Roman transliteration.
   - Respect regional dialectal forms (e.g., Poonchi/Rajouri, Himachal, Hazara, Swat, Jammu). Do not force one region's pronunciation as the "only correct" form.

3. **Attribution & Licensing**:
   - Maintain author/compiler attribution for traditional proverbs and dictionary items.
   - Do not copy large copyrighted datasets or commercial books without license or permission.

---

## 2. Verification Status Taxonomy

When proposing data entries, assign one of these statuses:
- `verified`: Documented in peer-reviewed academic literature (e.g., CIIL grammars, JKAACL publications, SIL surveys) or vetted by qualified linguists.
- `community_reviewed`: Contributed by native speakers and confirmed by community consensus.
- `provisional`: Under review; awaiting secondary dialect verification.
- `experimental`: Automated diagnostics or heuristic rules under test.

---

## 3. Development Setup

Clone the repository and set up a development virtual environment:

```bash
git clone https://github.com/gojrilang/gojrilang.git
cd gojrilang

# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Or on Linux/macOS:
# source .venv/bin/activate

# Install in editable mode with development dependencies:
python -m pip install -e ".[dev]"

# Run test suite:
pytest
```

---

## 4. Code Standards

- **Type Hints**: All functions must have complete type annotations.
- **Docstrings**: Write clear docstrings for public functions and classes.
- **Tests**: Add unit tests in `tests/` for any new feature or bug fix.
- **Zero Heavy Dependencies**: Keep the core package lightweight, reliable, and runnable without heavy ML frameworks.

---

## 5. Submitting Pull Requests

1. Fork the repo and create your branch: `git checkout -b feature/new-rule-or-words`.
2. Commit your changes with descriptive messages: `git commit -m "Add verified pastoral vocabulary from JKAACL"`.
3. Verify all tests pass: `pytest`.
4. Open a Pull Request detailing sources, dialect relevance, and verification rationale.

