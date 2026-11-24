"""Gojri classical and modern poetry subsystem.

Covers documented poetic forms: Bait, Si-Harfi, Kafi, Ghazal, Dohra, and Nazm,
featuring classical masters such as Hazrat Mian Nizam-ud-Din Larvi, Khuda Bakhsh Zaar,
and Sain Qadir Bakhsh.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from gojrilang.exceptions import GojriLangError
from gojrilang.normalize import normalize_for_search


class PoemNotFoundError(GojriLangError):
    """Raised when a requested poem is not found."""

    def __init__(self, poem_id: str) -> None:
        super().__init__(f"Poem '{poem_id}' was not found in the Gojri poetry collection.")
        self.poem_id = poem_id


@dataclass
class PoemVerse:
    """A single verse, couplet, or stanza in a Gojri poem."""

    line_num: int
    text_perso_arabic: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None
    translation_en: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Poem:
    """A Gojri poem or verse collection."""

    id: str
    title: str
    title_gojri: str
    poet: str
    poetic_form: str  # bait, si_harfi, kafi, ghazal, dohra, nazm
    year: Optional[int] = None
    theme: str = "spiritual"
    verses: List[PoemVerse] = field(default_factory=list)
    notes: Optional[str] = None
    source: str = "JKAACL Classical Series"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_gojri": self.title_gojri,
            "poet": self.poet,
            "poetic_form": self.poetic_form,
            "year": self.year,
            "theme": self.theme,
            "notes": self.notes,
            "source": self.source,
            "verses": [v.to_dict() for v in self.verses],
        }

    def search(self, query: str) -> bool:
        q_norm = normalize_for_search(query)
        fields = [
            normalize_for_search(self.title),
            normalize_for_search(self.title_gojri),
            normalize_for_search(self.poet),
            normalize_for_search(self.theme),
        ]
        for v in self.verses:
            fields.extend([
                normalize_for_search(v.text_perso_arabic),
                normalize_for_search(v.text_devanagari or ""),
                normalize_for_search(v.text_roman or ""),
                normalize_for_search(v.translation_en),
            ])
        return any(q_norm in f for f in fields if f)


_POETRY_CORPUS: List[Poem] = [
    Poem(
        id="poem_larvi_tauheed",
        title="Bait-e-Tauheed (Hymn of Divine Unity)",
        title_gojri="بیت توحید",
        poet="Hazrat Mian Nizam-ud-Din Larvi (1863–1926)",
        poetic_form="bait",
        year=1910,
        theme="mystical devotion & nature",
        notes="Composed at Baba Nagri, Wangat; classic synthesis of Sufi metaphysics and Himalayan landscape.",
        source="Kalam-e-Nizam (JKAACL 1974)",
        verses=[
            PoemVerse(
                line_num=1,
                text_perso_arabic="اوّل نام اللہ دا لیجے، جو مالک کل جہاناں دا۔",
                text_devanagari="अव्वल नाम अल्लाह दा लीजे, जो मालिक कुल जहानाँ दा।",
                text_roman="Avval nām Allāh dā līje, jo mālik kul jahānā̃ dā.",
                translation_en="First invoke the name of God, the sovereign Lord of all the worlds.",
            ),
            PoemVerse(
                line_num=2,
                text_perso_arabic="پہاڑ تے جنگل سبھ اوہدی شان، کی انت مھارے بیاں دا!",
                text_devanagari="पहाड़ ते जंगल सभ ओहदी शान, की अन्त म्हारे बयाँ दा!",
                text_roman="Pahāṛ te jangal sabh ohdī shān, kī ant mhāre bayā̃ dā!",
                translation_en="Mountains and woodlands are all His splendor; what limit is there to our feeble speech!",
            ),
        ],
    ),
    Poem(
        id="poem_sain_qadir_dohra",
        title="Dohra: Ethical Detachment",
        title_gojri="دوہرا اخلاق",
        poet="Sain Qadir Bakhsh",
        poetic_form="dohra",
        year=1930,
        theme="ethics & pastoral humility",
        notes="Memorized across Gujjar shepherd gatherings in Poonch and Rajouri.",
        source="Gojri Lok Adab (JKAACL)",
        verses=[
            PoemVerse(
                line_num=1,
                text_perso_arabic="کبر غرور نہ کر بندیا، مٹی ما مل جاؤنگا!",
                text_devanagari="किब्र ग़रूर न कर बन्देया, मिट्टी मा मिल जावंगा!",
                text_roman="Kibr-ġhurūr na kar bandyā, miṭṭī mā mil jāvangā!",
                translation_en="Do not indulge in arrogance, O mortal, for into earth thou shalt return!",
            ),
            PoemVerse(
                line_num=2,
                text_perso_arabic="نیکی دی کر کمائی، سدا نام کماؤنگا!",
                text_devanagari="नेकी दी कर कमाई, सदा नाम कमावंगा!",
                text_roman="Nekī dī kar kamāī, sadā nām kamāvangā!",
                translation_en="Earn the wealth of virtue, and thou shalt earn an everlasting name!",
            ),
        ],
    ),
    Poem(
        id="poem_zaar_bahak",
        title="Nazm: Bahak ro Nazaro (High Alpine Meadow)",
        title_gojri="نظم: باہک رو نظارو",
        poet="Khuda Bakhsh Zaar",
        poetic_form="nazm",
        year=1955,
        theme="pastoral transhumance & beauty",
        notes="Depicts the tranquil beauty of the high Pir Panjal summer huts.",
        source="Kulyat-e-Zaar (JKAACL)",
        verses=[
            PoemVerse(
                line_num=1,
                text_perso_arabic="اُچی باہک تے ٹھنڈی ہواواں، پھلاں بھری بہار!",
                text_devanagari="उस बाहक ते ठण्डी हवावाँ, फुल्लाँ भरी बहार!",
                text_roman="Uchī bāhak te ṭhaṇḍī hawāwā̃, phullā̃ bharī bahār!",
                translation_en="On the high meadow hut cool breezes blow, amid a flower-laden spring!",
            ),
            PoemVerse(
                line_num=2,
                text_perso_arabic="گجر مجھاں چراوے مستی نال، رب رو شکر گزار!",
                text_devanagari="गुज्जर मझ्झाँ चरावे मस्ती नाल, रब रो शुक्र गुज़ार!",
                text_roman="Gujjar majjhā̃ charāve mastī nāl, Rab ro shukr-guzār!",
                translation_en="The Gujjar grazes his buffaloes in joy, ever thankful to the Creator!",
            ),
        ],
    ),
]


def list_poems(
    form: Optional[str] = None,
    poet: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List Gojri poems filtered by poetic form or poet."""
    results = []
    for p in _POETRY_CORPUS:
        if form and form.strip().lower() != p.poetic_form.lower():
            continue
        if poet and poet.strip().lower() not in p.poet.lower():
            continue
        results.append({
            "id": p.id,
            "title": p.title,
            "title_gojri": p.title_gojri,
            "poet": p.poet,
            "poetic_form": p.poetic_form,
            "year": p.year,
            "theme": p.theme,
            "verses_count": len(p.verses),
            "source": p.source,
        })
    return results


def get_poem(poem_id: str) -> Poem:
    """Retrieve a poem by its identifier."""
    clean_id = poem_id.strip().lower()
    for p in _POETRY_CORPUS:
        if p.id.lower() == clean_id:
            return p
    raise PoemNotFoundError(poem_id)


def search_poetry(query: str) -> List[Dict[str, Any]]:
    """Search across Gojri poems for keywords or themes."""
    results = []
    for p in _POETRY_CORPUS:
        if p.search(query):
            results.append({
                "id": p.id,
                "title": p.title,
                "poet": p.poet,
                "poetic_form": p.poetic_form,
                "theme": p.theme,
                "verses_count": len(p.verses),
            })
    return results


def list_poetic_forms() -> List[str]:
    """Return all documented Gojri poetic forms."""
    return sorted(list({p.poetic_form for p in _POETRY_CORPUS}))
