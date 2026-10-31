"""Grammar subsystem for Gojri language linguistic rules and structural diagnostics.

Rules represent verified linguistic evidence published in academic grammars
(e.g., J.C. Sharma 1982, Wayne Losey 2002).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from gojrilang.datasets import load_grammar_rules_raw
from gojrilang.exceptions import RuleNotFoundError
from gojrilang.normalize import detect_script, normalize, normalize_for_search


@dataclass
class GrammarRule:
    """A documented grammatical rule with linguistic provenance."""

    id: str
    category: str
    name: str
    description: str
    dialect: str
    source: str
    verification_status: str
    examples: List[Dict[str, str]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GrammarRule:
        return cls(
            id=data["id"],
            category=data["category"],
            name=data["name"],
            description=data["description"],
            dialect=data.get("dialect", "General Gojri"),
            source=data.get("source", "Unspecified"),
            verification_status=data.get("verification_status", "provisional"),
            examples=data.get("examples", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.id}] ({self.category}) {self.name} [{self.verification_status}]"


class GrammarEngine:
    """Engine for querying Gojri grammar rules and performing evidence-based diagnostics."""

    def __init__(self) -> None:
        raw = load_grammar_rules_raw()
        self._rules: Dict[str, GrammarRule] = {
            r["id"]: GrammarRule.from_dict(r) for r in raw.get("rules", [])
        }

    def list_rules(
        self,
        category: Optional[str] = None,
        dialect: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[GrammarRule]:
        """List documented grammar rules with optional filtering.

        Args:
            category: Filter by category (e.g. 'phonology', 'case_and_postpositions').
            dialect: Filter by dialect.
            status: Filter by verification status (e.g. 'verified').

        Returns:
            List of matching GrammarRule objects.
        """
        results = list(self._rules.values())

        if category:
            cat_clean = category.strip().lower()
            results = [r for r in results if r.category.lower() == cat_clean]

        if dialect:
            dia_clean = dialect.strip().lower()
            results = [
                r for r in results
                if dia_clean in r.dialect.lower() or r.dialect.lower() == "general gojri"
            ]

        if status:
            stat_clean = status.strip().lower()
            results = [r for r in results if r.verification_status.lower() == stat_clean]

        return results

    def get_rule(self, rule_id: str) -> GrammarRule:
        """Retrieve a specific grammar rule by ID.

        Args:
            rule_id: Unique rule identifier (e.g. 'RULE_POSTPOS_01').

        Returns:
            GrammarRule instance.

        Raises:
            RuleNotFoundError: If no rule exists with the given ID.
        """
        rule = self._rules.get(rule_id.strip())
        if not rule:
            # Case-insensitive attempt
            for k, v in self._rules.items():
                if k.lower() == rule_id.strip().lower():
                    return v
            raise RuleNotFoundError(rule_id)
        return rule

    def explain_rule(self, rule_id: str) -> str:
        """Return a formatted educational explanation of a grammar rule with examples and dialect context.

        Args:
            rule_id: Unique rule identifier.

        Returns:
            Human-readable multi-line formatted explanation string.
        """
        rule = self.get_rule(rule_id)
        lines = [
            f"Rule [{rule.id}]: {rule.name}",
            f"Category: {rule.category}",
            f"Dialect: {rule.dialect}",
            f"Verification: {rule.verification_status}",
            f"Source: {rule.source}",
            "",
            "Description:",
            f"  {rule.description}",
        ]
        if rule.examples:
            lines.append("")
            lines.append("Documented Examples:")
            for ex in rule.examples:
                ex_gojri = ex.get("gojri") or ex.get("gojri_perso_arabic") or ex.get("text")
                ex_rom = ex.get("roman") or ex.get("gojri_roman")
                ex_eng = ex.get("translation_en") or ex.get("english") or ex.get("meaning")
                parts = []
                if ex_gojri:
                    parts.append(f"Gojri: {ex_gojri}")
                if ex_rom:
                    parts.append(f"Roman: {ex_rom}")
                if ex_eng:
                    parts.append(f"Meaning: {ex_eng}")
                note = ex.get("note") or ex.get("context")
                if note:
                    parts.append(f"Note: {note}")
                lines.append("  * " + " | ".join(parts))
        return "\n".join(lines)

    def list_categories(self) -> List[str]:
        """Return all available grammar rule categories."""
        return sorted(list({r.category for r in self._rules.values()}))

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze a Gojri sentence for structural and morphological components.

        Note: Sentence analysis diagnostics are experimental and rule-assisted,
        intended for language research rather than automated grading.

        Args:
            sentence: Input sentence string in Perso-Arabic, Devanagari, or Roman.

        Returns:
            Dictionary containing tokens, detected script, identified postpositions,
            pronouns, verbal cues, and diagnostic observations.
        """
        if not sentence or not sentence.strip():
            return {
                "sentence": "",
                "script": "unknown",
                "tokens": [],
                "diagnostics": [],
                "confidence": "experimental",
            }

        normalized = normalize(sentence)
        norm_sent = normalized[0] if isinstance(normalized, tuple) else normalized
        script = detect_script(norm_sent)
        raw_tokens = norm_sent.split()
        clean_tokens = [normalize_for_search(t) for t in raw_tokens if t]

        diagnostics: List[Dict[str, Any]] = []

        # Known functional markers
        known_postpositions = {
            "ne": ("ne", "ergative/agentive marker (split-ergativity rule RULE_POSTPOS_01)"),
            "نے": ("ne", "ergative/agentive marker (split-ergativity rule RULE_POSTPOS_01)"),
            "ने": ("ne", "ergative/agentive marker (split-ergativity rule RULE_POSTPOS_01)"),
            "na": ("nā", "dative/accusative marker (RULE_PRON_01)"),
            "nā": ("nā", "dative/accusative marker (RULE_PRON_01)"),
            "ناں": ("nā", "dative/accusative marker (RULE_PRON_01)"),
            "नाँ": ("nā", "dative/accusative marker (RULE_PRON_01)"),
            "ro": ("ro", "genitive marker masculine concord (RULE_POSTPOS_02)"),
            "رو": ("ro", "genitive marker masculine concord (RULE_POSTPOS_02)"),
            "रो": ("ro", "genitive marker masculine concord (RULE_POSTPOS_02)"),
            "ri": ("rī", "genitive marker feminine concord (RULE_POSTPOS_02)"),
            "rī": ("rī", "genitive marker feminine concord (RULE_POSTPOS_02)"),
            "ری": ("rī", "genitive marker feminine concord (RULE_POSTPOS_02)"),
            "री": ("rī", "genitive marker feminine concord (RULE_POSTPOS_02)"),
            "ma": ("mā̃", "locative marker 'in'"),
            "mā̃": ("mā̃", "locative marker 'in'"),
            "ماں": ("mā̃", "locative marker 'in'"),
            "माँ": ("mā̃", "locative marker 'in'"),
            "par": ("par", "locative marker 'on'"),
            "پر": ("par", "locative marker 'on'"),
            "पर": ("par", "locative marker 'on'"),
        }

        known_pronouns = {
            "hu": "1st person singular ('I')",
            "hū̃": "1st person singular ('I')",
            "ہوں": "1st person singular ('I')",
            "mai": "1st person singular ('I')",
            "میں": "1st person singular ('I')",
            "tu": "2nd person singular informal ('you')",
            "tū̃": "2nd person singular informal ('you')",
            "توں": "2nd person singular informal ('you')",
            "तूँ": "2nd person singular informal ('you')",
            "tusi": "2nd person plural / polite ('you all')",
            "tusī̃": "2nd person plural / polite ('you all')",
            "تسی": "2nd person plural / polite ('you all')",
            "اسی": "1st person plural ('we')",
            "asī̃": "1st person plural ('we')",
            "asi": "1st person plural ('we')",
            "oh": "3rd person distal ('he/she/that')",
            "اوہ": "3rd person distal ('he/she/that')",
            "ओह": "3rd person distal ('he/she/that')",
            "apne": "reflexive genitive ('one's own')",
            "اپنے": "reflexive genitive ('one's own')",
        }

        identified_markers: List[Dict[str, str]] = []
        identified_pronouns: List[Dict[str, str]] = []

        for tok, raw_tok in zip(clean_tokens, raw_tokens):
            if tok in known_postpositions or raw_tok in known_postpositions:
                target_key = tok if tok in known_postpositions else raw_tok
                std_form, desc = known_postpositions[target_key]
                identified_markers.append({
                    "token": raw_tok,
                    "normalized": std_form,
                    "description": desc,
                })

            if tok in known_pronouns or raw_tok in known_pronouns:
                target_key = tok if tok in known_pronouns else raw_tok
                desc = known_pronouns[target_key]
                identified_pronouns.append({
                    "token": raw_tok,
                    "description": desc,
                })

        # Check for ergative construction
        has_ergative = any(m["normalized"] == "ne" for m in identified_markers)
        if has_ergative:
            diagnostics.append({
                "type": "alignment",
                "observation": "Detected agentive marker 'ne'. Indicates past/perfective transitive split-ergative construction (RULE_POSTPOS_01).",
            })

        # Check for terminal verb auxiliary
        terminal_tok = clean_tokens[-1] if clean_tokens else ""
        if terminal_tok in ("hai", "ہے", "है", "hain", "ہیں", "si", "سی", "सी"):
            diagnostics.append({
                "type": "word_order",
                "observation": "Sentence concludes with verbal copula/auxiliary, consistent with canonical Indo-Aryan SOV structure (RULE_SYNTAX_01).",
            })

        return {
            "sentence": sentence,
            "script": script,
            "tokens": raw_tokens,
            "postpositions": identified_markers,
            "pronouns": identified_pronouns,
            "diagnostics": diagnostics,
            "status": "experimental_analysis",
            "notes": "Diagnostic analysis is rule-guided and based on documented morphological patterns.",
        }


_GLOBAL_GRAMMAR_ENGINE: Optional[GrammarEngine] = None


def get_grammar_engine() -> GrammarEngine:
    """Return the singleton instance of the Gojri GrammarEngine."""
    global _GLOBAL_GRAMMAR_ENGINE
    if _GLOBAL_GRAMMAR_ENGINE is None:
        _GLOBAL_GRAMMAR_ENGINE = GrammarEngine()
    return _GLOBAL_GRAMMAR_ENGINE


def grammar_rules(
    category: Optional[str] = None,
    dialect: Optional[str] = None,
    status: Optional[str] = None,
) -> List[GrammarRule]:
    """Query documented Gojri grammar rules with optional filters."""
    return get_grammar_engine().list_rules(category=category, dialect=dialect, status=status)


def explain_rule(rule_id: str) -> str:
    """Return an educational explanation of a rule with examples and dialect notes."""
    return get_grammar_engine().explain_rule(rule_id)


