"""Gojri traditional folk stories and dastan subsystem.

Preserves documented pastoral folktales, legendary romances, and moral narratives
collected across Jammu, Kashmir, Poonch, Rajouri, Swat, and Himachal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from gojrilang.exceptions import GojriLangError
from gojrilang.normalize import normalize_for_search


class StoryNotFoundError(GojriLangError):
    """Raised when a requested folk story is not found."""

    def __init__(self, story_id: str) -> None:
        super().__init__(f"Folk story '{story_id}' was not found in the Gojri oral narrative archive.")
        self.story_id = story_id


@dataclass
class FolkStorySection:
    """A section, episode, or chapter in a Gojri folktale."""

    section_num: int
    title: str
    text_perso_arabic: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None
    translation_en: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FolkStory:
    """A documented Gojri folktale, dastan, or moral narrative."""

    id: str
    title: str
    title_gojri: str
    genre: str  # dastan, lok_kahani, katha, pastoral_legend
    region: str
    moral_lesson: str
    storyteller: str = "Traditional Gujjar Bards"
    sections: List[FolkStorySection] = field(default_factory=list)
    source: str = "JKAACL Gojri Lok Kahaniyan Series"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_gojri": self.title_gojri,
            "genre": self.genre,
            "region": self.region,
            "moral_lesson": self.moral_lesson,
            "storyteller": self.storyteller,
            "source": self.source,
            "sections": [s.to_dict() for s in self.sections],
        }

    def search(self, query: str) -> bool:
        q_norm = normalize_for_search(query)
        corpus = [
            normalize_for_search(self.title),
            normalize_for_search(self.title_gojri),
            normalize_for_search(self.genre),
            normalize_for_search(self.moral_lesson),
        ]
        for s in self.sections:
            corpus.extend([
                normalize_for_search(s.title),
                normalize_for_search(s.text_perso_arabic),
                normalize_for_search(s.text_devanagari or ""),
                normalize_for_search(s.text_roman or ""),
                normalize_for_search(s.translation_en),
            ])
        return any(q_norm in c for c in corpus if c)


_FOLK_STORIES_CORPUS: List[FolkStory] = [
    FolkStory(
        id="story_sohni_mahiwal",
        title="Dastan-e-Sohni Mahiwal",
        title_gojri="داستان سوہنی ماہیوال",
        genre="dastan",
        region="Chenab Valley / Gujrat / Jammu",
        moral_lesson="Pure love renounces worldly station and braves all barriers.",
        storyteller="Dhadhi Folk Bards",
        source="JKAACL Folklore Documentation",
        sections=[
            FolkStorySection(
                section_num=1,
                title="Izzat Beg ro Charwaho Ban-no (Izzat Beg becomes Mahiwal)",
                text_perso_arabic="عزت بیگ نے سوہنی دے پیار ما اپݨی ساری دولت لٹا دتی تے چناب دے کنڈھے مجھاں چراوݨ لگو۔",
                text_devanagari="इज़्ज़त बेग ने सोहणी दे प्यार मा अपणी सारी दौलत लुटा दिती ते चनाब दे कण्डे मझ्झाँ चरावण लगो।",
                text_roman="Izzat Beg ne Sohnī de pyār mā apṇī sārī daulat luṭā ditī te Chanāb de kaṇḍhe majjhā̃ charāvaṇ lago.",
                translation_en="For love of Sohni, Izzat Beg renounced all his worldly riches and began grazing water buffaloes on the banks of the Chenab.",
            ),
            FolkStorySection(
                section_num=2,
                title="Kachhe Ghaṛe ri Parīksha (Trial of the Unbaked Pitcher)",
                text_perso_arabic="سوہنی کچے گھڑے تے دریا پار کر کے ملدی سی، جد گھڑو گھل گیو، تاں لہر ما ڈُب کے سدا واسطے امر ہو گئی۔",
                text_devanagari="सोहणी कच्चे घड़े ते दरिया पार कर के मिलदी सी, जद घड़ो घुल ग्यो, ताँ लहर मा डुब के सदा वास्ते अमर हो गई।",
                text_roman="Sohnī kachhe ghaṛe te daryā pār kar ke mildī sī, jad ghaṛo ghul gyo, tā̃ lahar mā ḍub ke sadā vāste amar ho gaī.",
                translation_en="Sohni crossed the raging river on an unbaked clay pitcher to meet him; when the pitcher dissolved, she merged into the waves and became immortal.",
            ),
        ],
    ),
    FolkStory(
        id="story_charwaho_te_sher",
        title="Charwaho te Sher (The Shepherd and the Tiger)",
        title_gojri="چرواہو تے شیر",
        genre="lok_kahani",
        region="Pir Panjal / Poonch",
        moral_lesson="Courage, cleverness, and pastoral solidarity overcome brute strength.",
        storyteller="Elders of Surankote",
        source="Gojri Lok Kahaniyan (JKAACL)",
        sections=[
            FolkStorySection(
                section_num=1,
                title="Dhar te Sher ro Awno (Encounter on the Mountain Ridge)",
                text_perso_arabic="اک دہاڑے دھار تے بکریاں چراؤندے ہوئے چرواہے آڈے شیر آ گیو، پر چرواہے نے اپݨے ڈانگ تے کتے نال ہمت دکھائی۔",
                text_devanagari="इक दिहाड़े धार ते बकरियाँ चरावे हुए चरवाहे आड्डे शेर आ ग्यो, पर चरवाहे ने अपणे डांग ते कुत्ते नाल हिम्मत दिखाई।",
                text_roman="Ik dihāṛe dhār te bakriyā̃ charāonde hue charwāhe āḍḍe sher ā gyo, par charwāhe ne apṇe ḍāng te kutte nāl himmat dikhāī.",
                translation_en="One day while grazing goats on the mountain ridge, a tiger confronted the shepherd, but with his shepherd staff and brave pastoral dog he stood his ground.",
            ),
        ],
    ),
    FolkStory(
        id="story_roop_basant",
        title="Kissa Roop Basant",
        title_gojri="قصہ روپ بسنت",
        genre="katha",
        region="General Gojri Belt",
        moral_lesson="Truth and fraternal loyalty endure through exile and false accusations.",
        storyteller="Traditional Gujjar Storytellers",
        source="JKAACL Oral Archives",
        sections=[
            FolkStorySection(
                section_num=1,
                title="Bhrāwā̃ ro Pyār (Brotherly Loyalty)",
                text_perso_arabic="روپ تے بسنت دوویں بھرا ہک دوجے توں جان واردے سن، جنگل دی کٹھن راہواں ما وی ہک دوجے دا ساتھ دِتو۔",
                text_devanagari="रूप ते बसन्त दोवें भरा हिक दूजे तों जान वारदे सन, जंगल दी कठिन राहवाँ मा वी हिक दूजे दा साथ दित्तो।",
                text_roman="Rūp te Basant dovẽ bhrā hik dūje tõ jān vārde san, jangal dī kaṭhin rāhwā̃ mā vī hik dūje dā sāth ditto.",
                translation_en="Roop and Basant were two brothers devoted to each other unto life, standing shoulder to shoulder even along the arduous forest pathways.",
            ),
        ],
    ),
]


def list_stories(genre: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Gojri folktales and oral stories, optionally filtered by genre."""
    results = []
    for s in _FOLK_STORIES_CORPUS:
        if genre and genre.strip().lower() != s.genre.lower():
            continue
        results.append({
            "id": s.id,
            "title": s.title,
            "title_gojri": s.title_gojri,
            "genre": s.genre,
            "region": s.region,
            "moral_lesson": s.moral_lesson,
            "storyteller": s.storyteller,
            "sections_count": len(s.sections),
            "source": s.source,
        })
    return results


def get_story(story_id: str) -> FolkStory:
    """Retrieve a folktale by its ID."""
    clean_id = story_id.strip().lower()
    for s in _FOLK_STORIES_CORPUS:
        if s.id.lower() == clean_id:
            return s
    raise StoryNotFoundError(story_id)


def search_stories(query: str) -> List[Dict[str, Any]]:
    """Search Gojri folktales for keywords, characters, or motifs."""
    results = []
    for s in _FOLK_STORIES_CORPUS:
        if s.search(query):
            results.append({
                "id": s.id,
                "title": s.title,
                "genre": s.genre,
                "region": s.region,
                "moral_lesson": s.moral_lesson,
                "sections_count": len(s.sections),
            })
    return results
