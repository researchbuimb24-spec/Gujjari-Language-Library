"""Traditional Gojri music and song archive.

Provides rich documentation, multiscript lyrics, musical instruments, rhythm notes,
and cultural provenance for traditional Gojri musical genres:
Chhaint, Mahya, Singran Ka Geet, Bait, Lori, Dholak De Geet, Baranmah,
pastoral calls (Gwali), wedding, harvest, devotional, and migration songs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from gojrilang.exceptions import GojriLangError
from gojrilang.normalize import normalize_for_search


class SongNotFoundError(GojriLangError):
    """Raised when a requested song record is not found."""

    def __init__(self, song_id: str) -> None:
        super().__init__(f"Song record '{song_id}' was not found in the Gojri music archive.")
        self.song_id = song_id


@dataclass
class SongLyricVerse:
    """A verse or couplet in a Gojri song."""

    verse_num: int
    text_perso_arabic: str
    text_devanagari: Optional[str] = None
    text_roman: Optional[str] = None
    translation_en: str = ""
    translation_hi: Optional[str] = None
    translation_ur: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_text(self, script: str = "perso-arabic") -> str:
        s_clean = script.lower().strip()
        if "perso" in s_clean or "arabic" in s_clean or "urdu" in s_clean:
            return self.text_perso_arabic
        if "devanagari" in s_clean or "hindi" in s_clean:
            return self.text_devanagari or self.text_perso_arabic
        if "roman" in s_clean or "latin" in s_clean:
            return self.text_roman or self.text_perso_arabic
        return self.text_perso_arabic


@dataclass
class SongRecord:
    """A documented Gojri traditional song with lyrics, musicology, and cultural provenance."""

    id: str
    title: str
    title_gojri: str
    category: str  # chhaint, mahya, singran_geet, bait, lori, dholak, baranmah, wedding, pastoral, harvest, devotional, migration
    dialect: str
    traditional_origin: str
    cultural_significance: str
    verses: List[SongLyricVerse] = field(default_factory=list)
    musical_instruments: List[str] = field(default_factory=list)
    rhythm_notes: str = ""
    regional_variations: Optional[str] = None
    performer: Optional[str] = None
    audio_ref: Optional[str] = None
    video_ref: Optional[str] = None
    source: str = "JKAACL Gojri Lok Geet"
    verification_status: str = "verified"
    license: str = "Public Documentation Open Access"

    @property
    def region(self) -> str:
        return self.dialect or self.traditional_origin

    @property
    def singer_informant(self) -> str:
        return self.performer or "Traditional Informants"

    @property
    def theme(self) -> str:
        return self.cultural_significance

    @property
    def musical_metadata(self) -> Dict[str, Any]:
        return {
            "raga_association": "Folk Pastoral",
            "tempo": self.rhythm_notes or "Traditional",
            "instruments": self.musical_instruments,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SongRecord:
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            title_gojri=data.get("title_gojri", ""),
            category=data.get("category", "general"),
            dialect=data.get("dialect", "General Gojri"),
            traditional_origin=data.get("traditional_origin", ""),
            cultural_significance=data.get("cultural_significance", ""),
            verses=[SongLyricVerse(**v) for v in data.get("verses", [])],
            musical_instruments=data.get("musical_instruments", []),
            rhythm_notes=data.get("rhythm_notes", ""),
            regional_variations=data.get("regional_variations"),
            performer=data.get("performer"),
            audio_ref=data.get("audio_ref"),
            video_ref=data.get("video_ref"),
            source=data.get("source", "JKAACL Gojri Lok Geet"),
            verification_status=data.get("verification_status", "verified"),
            license=data.get("license", "Public Documentation Open Access"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_gojri": self.title_gojri,
            "category": self.category,
            "dialect": self.dialect,
            "traditional_origin": self.traditional_origin,
            "cultural_significance": self.cultural_significance,
            "musical_instruments": self.musical_instruments,
            "rhythm_notes": self.rhythm_notes,
            "regional_variations": self.regional_variations,
            "performer": self.performer,
            "audio_ref": self.audio_ref,
            "video_ref": self.video_ref,
            "source": self.source,
            "verification_status": self.verification_status,
            "license": self.license,
            "verses": [v.to_dict() for v in self.verses],
        }

    def search(self, query: str) -> bool:
        q_norm = normalize_for_search(query)
        corpus = [
            normalize_for_search(self.title),
            normalize_for_search(self.title_gojri),
            normalize_for_search(self.category),
            normalize_for_search(self.cultural_significance),
            normalize_for_search(" ".join(self.musical_instruments)),
            normalize_for_search(self.traditional_origin),
        ]
        for v in self.verses:
            corpus.extend([
                normalize_for_search(v.text_perso_arabic),
                normalize_for_search(v.text_devanagari or ""),
                normalize_for_search(v.text_roman or ""),
                normalize_for_search(v.translation_en),
                normalize_for_search(v.translation_hi or ""),
                normalize_for_search(v.translation_ur or ""),
            ])
        return any(q_norm in c for c in corpus if c)


_SONGS_REGISTRY: List[SongRecord] = [
    SongRecord(
        id="SONG_CHHAINT_01",
        title="Chhaint: Pir Panjal Heroic Pastoral Ballad",
        title_gojri="چھینٹ: پیر پنجال رو رزمیہ لوک گیت",
        category="chhaint",
        dialect="Pir Panjal & Poonchi Gojri",
        traditional_origin="Pir Panjal Highlands, Jammu & Kashmir",
        cultural_significance="Epic heroic narrative sung by hereditary bards (Dhadhis) commemorating community valor and alpine endurance.",
        musical_instruments=["alghoza", "sarangi", "dholak"],
        rhythm_notes="Traditional 6/8 pastoral folk cadence in fast tempo",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="پیر پنجال دیاں اُچیاں دھاراں، برفا پئی جھما جھم ہو! سُوگندھ مھاری مٹی دی، گوجر سر نہ جھکاوے ہو!",
                text_devanagari="पीर पंजाल दियाँ उस धाराँ, बर्फा पई झमा झम हो! सोगंध म्हारी मिट्टी दी, गूज्जर सिर न झुकावे हो!",
                text_roman="Pīr Panjāl diyā̃ uchīyā̃ dhārā̃, barfā paī jhamā-jham ho! Sūgandh mhārī miṭṭī dī, Gūjjar sir na jhukāve ho!",
                translation_en="On the high ridges of the Pir Panjal, snow falls steadily! By the sacred bond of our soil, the Gujjar never bows his head!",
                translation_hi="पीर पंजाल की ऊँची चोटियों पर, बर्फ़ झमाझम गिर रही है! हमारी मिट्टी की सौगंध, गुज्जर कभी सिर नहीं झुकाता!",
                translation_ur="پیر پنجال کی اونچی دھاروں پر برف جھما جھم پڑ رہی ہے! ہماری مٹی کی قسم، گوجر کبھی سر نہیں جھکاتا!",
            ),
            SongLyricVerse(
                verse_num=2,
                text_perso_arabic="الڳوزہ وجے، سارنگی گائے، ویر جواناں دی شان ہو!",
                text_devanagari="अलगोज़ा वजे, सारंगी गाए, वीर जवानाँ दी शान हो!",
                text_roman="Alġhozah vaje, sārangī gāye, vīr jawānā̃ dī shān ho!",
                translation_en="The double-flute sounds, the sarangi sings, exalting the glory of brave youths!",
                translation_hi="अलगोज़ा बज रहा है, सारंगी गा रही है, वीर जवानों की शान है!",
                translation_ur="الگوزہ بجتا ہے، سارنگی گاتی ہے، بہادر جوانوں کی شان ہے!",
            ),
        ],
    ),
    SongRecord(
        id="SONG_MAHYA_01",
        title="Mahya: Alpine Meadow Solitude Melody",
        title_gojri="ماہیا: باہکاں رو فراقی گیت",
        category="mahya",
        dialect="Poonch / Rajouri Gojri",
        traditional_origin="Alpine grazing meadows (Bahaks) of Poonch and Rajouri",
        cultural_significance="Beloved two-line lyrical verse form sung across mountain pastures expressing longing, love, and seasonal separation.",
        musical_instruments=["bansuri", "sarangi"],
        rhythm_notes="Lyrical rubato cadence, unmetered alpine vocal call",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="دو پتّر اناراں دے! باہکاں تے بہہ کے روواں، دکھڑے پردیساں دے!",
                text_devanagari="दो पत्तर अनाराँ दे! बाहकाँ ते बह के रोवाँ, दुखड़े परदेसाँ दे!",
                text_roman="Do pattar anārā̃ de! Bāhakā̃ te bah ke rowā̃, dukhṛe pardesā̃ de!",
                translation_en="Two leaves of the pomegranate tree! Sitting in high alpine huts, I weep over the sorrows of distant exile!",
                translation_hi="अनार के दो पत्ते! ऊँचे चरागाह की झोपड़ी में बैठकर परदेस के दुखों पर रोता हूँ!",
                translation_ur="انار کے دو پتے! بلند چراگاہ کی باہک پر بیٹھ کر پردیس کے دکھوں پر روتا ہوں!",
            ),
            SongLyricVerse(
                verse_num=2,
                text_perso_arabic="ہک پھل گلاب رو ہے! تیری مٹھی بولی سُݨ کے، سارا دُکھ لَہہ جاوے ہے!",
                text_devanagari="हिक फल गुलाब रो है! तेरी मिट्ठी बोली सुण के, सारा दुख लह जावे है!",
                text_roman="Hik phul gulāb ro hai! Terī miṭṭhī bolī suṇ ke, sārā dukh lah jāve hai!",
                translation_en="A single rose blossom blooms! Hearing your sweet voice, all grief melts away!",
                translation_hi="गुलाब का एक फूल है! तुम्हारी मीठी बोली सुनकर सारा दुख दूर हो जाता है!",
                translation_ur="ایک پھول گلاب کا ہے! تیری میٹھی بولی سن کر سارا دکھ دور ہو جاتا ہے!",
            ),
        ],
    ),
    SongRecord(
        id="SONG_SINGRAN_01",
        title="Singran Ka Geet: Nomadic Caravan Migration Chant",
        title_gojri="سنگراں کا گیت (ٹانڈو ری روانگی)",
        category="singran_geet",
        dialect="Pir Panjal & Central Gojri",
        traditional_origin="Annual transhumant mountain passes",
        cultural_significance="Communal march chant sung as pastoral families pack baggage onto pack-horses and drive livestock up mountain passes.",
        musical_instruments=["alghoza", "chimta", "dholak"],
        rhythm_notes="Rhythmic march cadence matching footsteps of pack-horses",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="چلو نِی سنگیو! باہکاں نا چلیے، گرمی دی رُت آئی ہے۔ گھوڑیاں تے لاہڈو کٹھا کیتو، تاںڈو ٹر پیا اے۔",
                text_devanagari="चलो नी संगियो! बाहकाँ ना चल्ये, गर्मी दी रुत आई है। घोड़ियाँ ते लाहडो कठो कीतो, ताँडो टुर प्या ए।",
                text_roman="Chalo nī sangiyo! Bāhakā̃ nā chalye, garmī dī rut āī hai. Ghoṛyā̃ te lāhḍo kaṭho kīto, tā̃ḍo ṭur pyā e.",
                translation_en="Come along, companions! Let us move to the high alpine pastures, for the summer season has arrived. Loading baggage on horses, the caravan has set out.",
                translation_hi="चलो साथियो, ऊँचे चरागाहों की ओर चलें, गर्मी की रुत आई है। घोड़ों पर सामान बाँध लिया है और क़ाफ़िला चल पड़ा है।",
                translation_ur="چلو ساتھیو چراگاہوں کی طرف چلیں، گرمی کی رت آئی ہے۔ گھوڑوں پر سامان لاد دیا ہے اور قافلہ چل پڑا ہے۔",
            ),
        ],
    ),
    SongRecord(
        id="SONG_BAIT_01",
        title="Bait: Ethical and Spiritual Quatrain of Sain Qadir Bakhsh",
        title_gojri="بیت: سائیں قادر بخش رو پند نامو",
        category="bait",
        dialect="Jammu / Poonch Gojri",
        traditional_origin="Spiritual gatherings and pastoral night vigils",
        cultural_significance="Philosophical four-line verse form celebrating moral uprightness, humility, and eternity.",
        musical_instruments=["chimta", "dholak", "sarangi"],
        rhythm_notes="Contemplative medium tempo",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="کبر غرور نہ کر بندیا، مٹی ما مل جاؤنگا! نیکی دی کر کمائی، سدا نام کماؤنگا!",
                text_devanagari="किब्र ग़रूर न कर बन्देया, मिट्टी मा मिल जावंगा! नेकी दी कर कमाई, सदा नाम कमावंगा!",
                text_roman="Kibr-ġhurūr na kar bandyā, miṭṭī mā mil jāvangā! Nekī dī kar kamāī, sadā nām kamāvangā!",
                translation_en="Do not indulge in pride and conceit, O mortal, for into dust you shall return! Strive for the earnings of good deeds, and you shall earn an enduring name!",
                translation_hi="घमण्ड और अहंकार मत कर ओ इंसान, मिट्टी में मिल जाओगे! भलाई और नेकी कमाओ, सदा नाम कमाओगे!",
                translation_ur="تکبر اور غرور مت کر اے انسان، مٹی میں مل جائے گا! نیکی کی کمائی کر، ہمیشہ کا نام پائے گا۔",
            ),
        ],
    ),
    SongRecord(
        id="SONG_LORI_01",
        title="Gojri Lori: Traditional Gujjar Cradle Lullaby",
        title_gojri="گوجری لوری",
        category="lori",
        dialect="General Gojri",
        traditional_origin="Pastoral kothas and mountain dwellings",
        cultural_significance="Gentle lullaby sung by mothers to soothe infants to sleep in mountain stone cottages and seasonal tents.",
        musical_instruments=[],
        rhythm_notes="Gentle rocking 3/4 lullaby rhythm",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="سون جا میرے لعل، چن مھارے سون جا! جنگلاں ما ٹھنڈی ہوا لگی، مٹھے سپنے ویکھ سون جا!",
                text_devanagari="सौं जा मेरे लाल, चन म्हारे सौं जा! जंगलाँ मा ठण्डी हवा लगी, मिट्ठे सपने वेख सौं जा!",
                text_roman="Sõ jā mere lāl, chan mhāre sõ jā! Janglā̃ mā ṭhaṇḍī hawā lagī, miṭṭhe sapne vekh sõ jā!",
                translation_en="Sleep, my darling child, sleep my moon! Cool breezes rustle through the mountain forests; dream sweet dreams and sleep!",
                translation_hi="सो जा मेरे लाल, मेरे चाँद सो जा! जंगलों में ठंडी हवा चल रही है, मीठे सपने देखकर सो जा!",
                translation_ur="سو جا میرے لعل، میرے چاند سو جا! جنگلوں میں ٹھنڈی ہوا چل رہی ہے، میٹھے خواب دیکھ کر سو جا!",
            ),
        ],
    ),
    SongRecord(
        id="SONG_DHOLAK_01",
        title="Dholak De Geet: Gujjar Wedding Celebration Melody",
        title_gojri="ڈھولک دے گیت (سہرے تے مہندی)",
        category="dholak",
        dialect="Jammu & Punjab Hills Gojri",
        traditional_origin="Gujjar marriage ceremonies and festive gatherings",
        cultural_significance="Festive celebratory songs sung by Gujjar women to the beat of the dholak drum during wedding rituals and henna ceremonies.",
        musical_instruments=["dholak", "ghunghroo", "chimta"],
        rhythm_notes="Kaharva 8 beats in vibrant celebratory tempo",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="مہندی لاؤ نی گجری دی، پھلاں بھری بہار آئی! ڈھولک وجے، گھنگھرو چھنکن، سارا جگ خوشیاں منائی!",
                text_devanagari="मेहन्दी लाओ नी गूजरी दी, फुल्लाँ भरी बहार आई! ढोलक वजे, घुँघरू छनकन, सारा जग खुशियाँ मनाई!",
                text_roman="Mehndī lāo nī Gūjrī dī, phullā̃ bharī bahār āī! Ḍholak vaje, ghunghrū chhankan, sārā jag khushyā̃ manāī!",
                translation_en="Apply the bridal henna to the Gujjar maiden, for a flower-laden spring has arrived! The dholak beats, ankle-bells chime, and the whole world rejoices!",
                translation_hi="गूजरी को मेंहदी लगाओ, फूलों भरी बहार आई है! ढोलक बज रही है, घुँघरू छनक रहे हैं, सारा संसार ख़ुशियाँ मना रहा है!",
                translation_ur="گوجری کو مہندی لگاؤ، پھولوں بھری بہار آئی ہے! ڈھولک بجتی ہے، گھنگھرو چھنکتے ہیں، سارا جہاں خوشیاں مناتا ہے!",
            ),
        ],
    ),
    SongRecord(
        id="SONG_BARANMAH_01",
        title="Baranmah Song: Sawan (Monsoon in the High Meadows)",
        title_gojri="بارہ ماہ گیت: ساون ری رُت",
        category="baranmah",
        dialect="Pir Panjal Gojri",
        traditional_origin="Annual transhumance poetry of the Pir Panjal",
        cultural_significance="Celebration of monsoon bounty, overflowing milk yields, and butter churning at high-altitude summer huts.",
        musical_instruments=["alghoza", "bansuri"],
        rhythm_notes="Rhythmic pastoral melody",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="ساوݨ برسیو رم جھم، مھاری باہک ہری ہوئی! کجلی بدلیاں گرجن، مکھݨ دی خوشبو پھیلی!",
                text_devanagari="सावण बर्स्यो रिम झिम, म्हारी बाहक हरी होई! कजली बदलियाँ गर्जन, मक्खण दी खुशबू फैली!",
                text_roman="Sāwaṇ barsyo rim-jhim, mhārī bāhak harī hoī! Kajlī badliyā̃ garjan, makkhaṇ dī khushbū phailī!",
                translation_en="Sawan has rained down in gentle showers; our high alpine meadow has turned vibrant green! Dark clouds thunder softly, and the fragrance of fresh churned butter fills the air!",
                translation_hi="सावन रिमझिम बरसा है, हमारा चरागाह हरा-भरा हो गया है! काले बादल गरज रहे हैं और ताज़े मक्खन की सुगंध फैल रही है!",
                translation_ur="ساون رم جھم برسا ہے، ہماری چراگاہ ہری بھری ہو گئی ہے! سیاہ بادل گرجتے ہیں اور تازہ مکھن کی خوشبو پھیل گئی ہے!",
            ),
        ],
    ),
    SongRecord(
        id="SONG_PASTORAL_GWALI_01",
        title="Gwali: Highland Shepherd Pasture Call",
        title_gojri="گوالی: چرواہے ری پکار",
        category="pastoral",
        dialect="Poonch & Rajouri",
        traditional_origin="Alpine ravines and grazing ridges",
        cultural_significance="Authentic high-pitched vocal call and melody used by mountain herders to guide flocks across misty alpine ridges.",
        musical_instruments=["bansuri"],
        rhythm_notes="Unmetered vocal echo resonance",
        verses=[
            SongLyricVerse(
                verse_num=1,
                text_perso_arabic="او ہو بھیڈاں والیو! دھاراں تے ہری گھاہ آئی ہے، مجھاں نا ہانک کے باہک تے لے آؤ!",
                text_devanagari="ओ हो भीडाँ वाल्यो! धाराँ ते हरी घाह आई है, मझ्झाँ ना हांक के बाहक ते ले आवो!",
                text_roman="O ho bhīḍā̃ vālyo! Dhārā̃ te harī ghāh āī hai, majjhā̃ nā hāṅk ke bāhak te le āo!",
                translation_en="O shepherds of the sheep! Fresh green grass has covered the mountain ridges; drive the water buffaloes and bring them up to the meadow hut!",
                translation_hi="ओ भेड़ों के चरवाहो! चोटियों पर हरी घास उग आई है, भैंसों को हाँककर चरागाह की झोपड़ी पर ले आओ!",
                translation_ur="او بھیڑوں کے چرواہو! دھاروں پر ہری گھاس اگ آئی ہے، بھینسوں کو ہانک کر باہک پر لے آؤ!",
            ),
        ],
    ),
]


def list_songs(
    category: Optional[str] = None,
    dialect: Optional[str] = None,
) -> List[SongRecord]:
    """List traditional Gojri songs, optionally filtered by category or dialect."""
    results = []
    for s in _SONGS_REGISTRY:
        if category and category.strip().lower() != s.category.lower():
            continue
        if dialect and dialect.strip().lower() not in s.dialect.lower():
            continue
        results.append(s)
    return results


def get_song(song_id: str) -> SongRecord:
    """Retrieve a traditional song record by its identifier."""
    clean_id = song_id.strip().lower()
    for s in _SONGS_REGISTRY:
        if s.id.lower() == clean_id:
            return s
    raise SongNotFoundError(song_id)


def search_songs(query: str, category: Optional[str] = None) -> List[SongRecord]:
    """Search across traditional Gojri songs, lyrics, and cultural notes."""
    results = []
    for s in _SONGS_REGISTRY:
        if category and category.strip().lower() != s.category.lower():
            continue
        if s.search(query):
            results.append(s)
    return results


def list_song_categories() -> List[str]:
    """List all categories of traditional Gojri songs available in the archive."""
    return sorted(list({s.category for s in _SONGS_REGISTRY}))


def get_song_lyrics(song_id: str, script: str = "perso-arabic") -> List[str]:
    """Extract lyrics line-by-line in the requested script for a specific song."""
    song = get_song(song_id)
    return [v.get_text(script) for v in song.verses]
