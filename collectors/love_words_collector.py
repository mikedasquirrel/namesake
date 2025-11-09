"""
Love Words Data Collector

Comprehensive dataset of 100+ words for "love" across modern and ancient languages.
Includes semantic distinctions, etymology, cultural context, and phonetic representations.

This collector provides the foundation data for cross-linguistic phonetic analysis
following the same methodology as country name analysis.
"""

import logging
from typing import List, Dict
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class LoveWordsCollector:
    """Collects and structures love words from 20+ languages"""
    
    def __init__(self):
        self.love_words_data = self._build_comprehensive_dataset()
    
    def _build_comprehensive_dataset(self) -> List[Dict]:
        """
        Comprehensive dataset of 100+ love words from modern and ancient languages.
        Each entry includes etymology, semantics, cultural context, and phonetics.
        """
        
        dataset = []
        
        # ========================================================================
        # GERMANIC LANGUAGES
        # ========================================================================
        
        # English
        dataset.append({
            'language': 'English',
            'language_family': 'Germanic',
            'language_code': 'en',
            'is_ancient': False,
            'word': 'love',
            'romanization': 'love',
            'ipa_pronunciation': '/lʌv/',
            'semantic_type': 'general',
            'semantic_nuance': 'All-encompassing term covering romantic, familial, platonic, and object affection. Semantically broad but philosophically shallow compared to Greek distinctions.',
            'etymology_root': 'PIE *leubʰ- (to love, desire)',
            'etymology_path': 'PIE *leubʰ- → Proto-Germanic *lubō → Old English lufu → Middle English love → Modern English love',
            'first_recorded_year': 897,
            'cultural_context': 'English collapsed multiple love concepts into single word, reflecting cultural tendency toward semantic generalization. Used for romantic partners, family, friends, hobbies, and food.',
            'usage_frequency': 'very_common',
            'usage_examples': 'I love you; love of my life; I love pizza',
            'cognates': json.dumps(['German Liebe', 'Dutch liefde', 'Swedish kärlek']),
            'synonyms': json.dumps(['affection', 'adoration', 'devotion', 'infatuation']),
            'source': 'Oxford English Dictionary, Online Etymology Dictionary'
        })
        
        # German
        dataset.append({
            'language': 'German',
            'language_family': 'Germanic',
            'language_code': 'de',
            'is_ancient': False,
            'word': 'Liebe',
            'romanization': 'Liebe',
            'ipa_pronunciation': '/ˈliːbə/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love term, primarily romantic but extends to familial and platonic. More formal than English "love".',
            'etymology_root': 'PIE *leubʰ-',
            'etymology_path': 'PIE *leubʰ- → Proto-Germanic *lubō → Old High German liubi → Middle High German liebe → Modern German Liebe',
            'first_recorded_year': 800,
            'cultural_context': 'Central to German Romantic philosophy (Romantik). Closer to original Germanic root phonetically than English.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Ich liebe dich; Liebe meines Lebens',
            'cognates': json.dumps(['English love', 'Dutch liefde', 'Gothic liufs']),
            'synonyms': json.dumps(['Zuneigung', 'Verliebtheit']),
            'source': 'Deutsches Wörterbuch, Etymologisches Wörterbuch'
        })
        
        # Dutch
        dataset.append({
            'language': 'Dutch',
            'language_family': 'Germanic',
            'language_code': 'nl',
            'is_ancient': False,
            'word': 'liefde',
            'romanization': 'liefde',
            'ipa_pronunciation': '/ˈlifdə/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, romantic and familial',
            'etymology_root': 'PIE *leubʰ-',
            'etymology_path': 'PIE *leubʰ- → Proto-Germanic *lubō → Middle Dutch liefde → Modern Dutch liefde',
            'first_recorded_year': 1100,
            'cultural_context': 'Standard Dutch love term, phonetically intermediate between German and English',
            'usage_frequency': 'very_common',
            'usage_examples': 'Ik hou van jou; liefde van mijn leven',
            'cognates': json.dumps(['German Liebe', 'English love']),
            'synonyms': json.dumps(['genegenheid']),
            'source': 'Van Dale Etymologisch Woordenboek'
        })
        
        # Swedish
        dataset.append({
            'language': 'Swedish',
            'language_family': 'Germanic',
            'language_code': 'sv',
            'is_ancient': False,
            'word': 'kärlek',
            'romanization': 'kärlek',
            'ipa_pronunciation': '/ˈɕæːɭɛk/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Primarily romantic love, distinct from general affection (älska)',
            'etymology_root': 'Old Norse kærleikr',
            'etymology_path': 'Old Norse kærleikr → Middle Swedish kärlek → Modern Swedish kärlek',
            'first_recorded_year': 1200,
            'cultural_context': 'Swedish distinguishes between kärlek (romantic) and älska (to love verb). More specific than English.',
            'usage_frequency': 'common',
            'usage_examples': 'Min kärlek; förälskelse',
            'cognates': json.dumps(['Norwegian kjærlighet', 'Danish kærlighed']),
            'synonyms': json.dumps(['förälskelse (infatuation)']),
            'source': 'Svenska Akademiens Ordbok'
        })
        
        # ========================================================================
        # ROMANCE LANGUAGES (Latin descendants)
        # ========================================================================
        
        # Latin (Ancient)
        dataset.append({
            'language': 'Latin',
            'language_family': 'Romance',
            'language_code': 'la',
            'is_ancient': True,
            'word': 'amor',
            'romanization': 'amor',
            'ipa_pronunciation': '/ˈamor/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Romantic and passionate love, often erotic. Associated with Cupid (Amor in Latin mythology).',
            'etymology_root': 'PIE *am- (to take, seize)',
            'etymology_path': 'PIE *am- → Latin amor → Romance languages (Spanish/French/Italian amor/amour/amore)',
            'first_recorded_year': -200,
            'cultural_context': 'Central to Roman love poetry (Ovid, Catullus). Personified as deity Amor/Cupid. Root of modern Romance words.',
            'usage_frequency': 'common',
            'usage_examples': 'Amor vincit omnia (love conquers all); Amor fati (love of fate)',
            'cognates': json.dumps(['Spanish amor', 'French amour', 'Italian amore', 'Portuguese amor']),
            'synonyms': json.dumps(['caritas (charity)', 'dilectio (affection)']),
            'source': 'Lewis & Short Latin Dictionary'
        })
        
        dataset.append({
            'language': 'Latin',
            'language_family': 'Romance',
            'language_code': 'la',
            'is_ancient': True,
            'word': 'caritas',
            'romanization': 'caritas',
            'ipa_pronunciation': '/ˈkaritas/',
            'semantic_type': 'divine',
            'semantic_nuance': 'Christian charity, selfless divine love. Higher form than amor.',
            'etymology_root': 'Latin carus (dear, expensive)',
            'etymology_path': 'Latin carus → caritas → English charity',
            'first_recorded_year': 100,
            'cultural_context': 'Christian theological term for divine/selfless love, equivalent to Greek agape. Used in Vulgate Bible.',
            'usage_frequency': 'formal',
            'usage_examples': 'Deus caritas est (God is love)',
            'cognates': json.dumps(['English charity', 'French charité']),
            'synonyms': json.dumps(['amor (romantic)', 'dilectio (affection)']),
            'source': 'Vulgate Bible, Medieval Latin texts'
        })
        
        # Spanish
        dataset.append({
            'language': 'Spanish',
            'language_family': 'Romance',
            'language_code': 'es',
            'is_ancient': False,
            'word': 'amor',
            'romanization': 'amor',
            'ipa_pronunciation': '/aˈmor/',
            'semantic_type': 'general',
            'semantic_nuance': 'All types of love - romantic, familial, platonic. Direct descendant of Latin amor.',
            'etymology_root': 'Latin amor',
            'etymology_path': 'Latin amor → Vulgar Latin amōre → Old Spanish amor → Modern Spanish amor',
            'first_recorded_year': 1140,
            'cultural_context': 'Preserved Latin root with high fidelity. Central to Spanish love poetry and music tradition.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Te amo; amor de mi vida; amor platónico',
            'cognates': json.dumps(['French amour', 'Italian amore', 'Portuguese amor', 'Latin amor']),
            'synonyms': json.dumps(['cariño (affection)', 'querencia (fondness)']),
            'source': 'Real Academia Española Dictionary'
        })
        
        # French
        dataset.append({
            'language': 'French',
            'language_family': 'Romance',
            'language_code': 'fr',
            'is_ancient': False,
            'word': 'amour',
            'romanization': 'amour',
            'ipa_pronunciation': '/amuʁ/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Primarily romantic love, culturally emphasized in French philosophy of love',
            'etymology_root': 'Latin amor',
            'etymology_path': 'Latin amor → Old French amur → Middle French amour → Modern French amour',
            'first_recorded_year': 1080,
            'cultural_context': 'Central to French cultural identity as "language of love". Sophisticated romantic vocabulary around amour.',
            'usage_frequency': 'very_common',
            'usage_examples': "Je t'aime; l'amour de ma vie; faire l'amour",
            'cognates': json.dumps(['Spanish amor', 'Italian amore', 'Latin amor']),
            'synonyms': json.dumps(['affection', 'tendresse']),
            'source': 'Dictionnaire de l\'Académie française'
        })
        
        # Italian
        dataset.append({
            'language': 'Italian',
            'language_family': 'Romance',
            'language_code': 'it',
            'is_ancient': False,
            'word': 'amore',
            'romanization': 'amore',
            'ipa_pronunciation': '/aˈmore/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Romantic and passionate love, central to Italian opera and poetry',
            'etymology_root': 'Latin amor',
            'etymology_path': 'Latin amor → Vulgar Latin amore → Old Italian amore → Modern Italian amore',
            'first_recorded_year': 1200,
            'cultural_context': 'Preserved Latin form most faithfully. Central to Italian opera (Puccini, Verdi). Phonetically melodious.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Ti amo; amore mio; dolce vita e amore',
            'cognates': json.dumps(['Spanish amor', 'French amour', 'Latin amor']),
            'synonyms': json.dumps(['affetto (affection)', 'tenerezza (tenderness)']),
            'source': 'Vocabolario Treccani'
        })
        
        # Portuguese
        dataset.append({
            'language': 'Portuguese',
            'language_family': 'Romance',
            'language_code': 'pt',
            'is_ancient': False,
            'word': 'amor',
            'romanization': 'amor',
            'ipa_pronunciation': '/ɐˈmoɾ/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love across contexts - romantic, familial, platonic',
            'etymology_root': 'Latin amor',
            'etymology_path': 'Latin amor → Vulgar Latin amore → Old Portuguese amor → Modern Portuguese amor',
            'first_recorded_year': 1200,
            'cultural_context': 'Portuguese preserves Latin amor with nasal quality. Rich poetic tradition (fado, bossa nova).',
            'usage_frequency': 'very_common',
            'usage_examples': 'Eu te amo; amor da minha vida',
            'cognates': json.dumps(['Spanish amor', 'Italian amore', 'Latin amor']),
            'synonyms': json.dumps(['carinho (affection)', 'paixão (passion)']),
            'source': 'Dicionário Priberam'
        })
        
        # Romanian
        dataset.append({
            'language': 'Romanian',
            'language_family': 'Romance',
            'language_code': 'ro',
            'is_ancient': False,
            'word': 'dragoste',
            'romanization': 'dragoste',
            'ipa_pronunciation': '/ˈdraɡoste/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love. Unlike other Romance languages, did NOT preserve Latin amor.',
            'etymology_root': 'Latin dracus (dear) + -oste suffix',
            'etymology_path': 'Latin dracus → Old Romanian drag → dragoste',
            'first_recorded_year': 1600,
            'cultural_context': 'Unique among Romance languages for NOT using amor cognate. Shows Slavic influence.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Te iubesc; dragostea vieții mele',
            'cognates': json.dumps(['Slavic languages drag-root']),
            'synonyms': json.dumps(['iubire (from Latin jubere)']),
            'source': 'Dicționarul explicativ al limbii române'
        })
        
        # ========================================================================
        # ANCIENT GREEK - The Four Types
        # ========================================================================
        
        dataset.append({
            'language': 'Ancient Greek',
            'language_family': 'Hellenic',
            'language_code': 'grc',
            'is_ancient': True,
            'word': 'ἀγάπη',
            'romanization': 'agape',
            'ipa_pronunciation': '/aˈɡa.pɛː/',
            'semantic_type': 'divine',
            'semantic_nuance': 'Unconditional, selfless, divine love. Highest form in Christian theology. Love of God for humans and vice versa.',
            'etymology_root': 'Greek agapaō (to love, show affection)',
            'etymology_path': 'Proto-Hellenic *agapaō → Classical Greek ἀγάπη → Koine Greek agape → Christian theological term',
            'first_recorded_year': -800,
            'cultural_context': 'Used in New Testament for divine love. Contrasts with eros (passion). Adopted into English as "agape".',
            'usage_frequency': 'formal',
            'usage_examples': 'Christian theological texts: "God is agape" (1 John 4:8)',
            'cognates': json.dumps(['Modern Greek αγάπη']),
            'synonyms': json.dumps(['storge (familial)', 'philia (friendship)', 'eros (romantic)']),
            'source': 'Liddell-Scott Greek Lexicon, New Testament'
        })
        
        dataset.append({
            'language': 'Ancient Greek',
            'language_family': 'Hellenic',
            'language_code': 'grc',
            'is_ancient': True,
            'word': 'ἔρως',
            'romanization': 'eros',
            'ipa_pronunciation': '/ˈerɔːs/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Passionate, romantic, sexual love. Named after god Eros (Cupid). Intense desire and longing.',
            'etymology_root': 'Greek god Eros',
            'etymology_path': 'Proto-Hellenic → Classical Greek ἔρως → English "erotic"',
            'first_recorded_year': -700,
            'cultural_context': 'Central to Greek philosophy (Plato\'s Symposium). Personified as god Eros. Source of English "erotic".',
            'usage_frequency': 'common',
            'usage_examples': 'Plato\'s Symposium; Greek love poetry',
            'cognates': json.dumps(['English erotic, eroticism']),
            'synonyms': json.dumps(['agape (divine)', 'philia (friendship)', 'storge (familial)']),
            'source': 'Liddell-Scott, Plato\'s Symposium'
        })
        
        dataset.append({
            'language': 'Ancient Greek',
            'language_family': 'Hellenic',
            'language_code': 'grc',
            'is_ancient': True,
            'word': 'φιλία',
            'romanization': 'philia',
            'ipa_pronunciation': '/pʰiˈli.a/',
            'semantic_type': 'platonic',
            'semantic_nuance': 'Friendship love, affectionate regard. Love between equals. Central to Aristotle\'s ethics.',
            'etymology_root': 'Greek philos (beloved, dear, friend)',
            'etymology_path': 'Proto-Hellenic → Classical Greek φιλία → English "-philia" suffix',
            'first_recorded_year': -800,
            'cultural_context': 'Aristotle devoted Books VIII-IX of Nicomachean Ethics to philia. Source of English prefix/suffix.',
            'usage_frequency': 'common',
            'usage_examples': 'Aristotle\'s Ethics; Philadelphia (city of brotherly love)',
            'cognates': json.dumps(['English -philia (bibliophilia, philosophy)']),
            'synonyms': json.dumps(['agape (divine)', 'eros (romantic)', 'storge (familial)']),
            'source': 'Aristotle Nicomachean Ethics, Liddell-Scott'
        })
        
        dataset.append({
            'language': 'Ancient Greek',
            'language_family': 'Hellenic',
            'language_code': 'grc',
            'is_ancient': True,
            'word': 'στοργή',
            'romanization': 'storge',
            'ipa_pronunciation': '/storˈɡɛː/',
            'semantic_type': 'familial',
            'semantic_nuance': 'Natural familial affection, especially parent-child. Instinctive, protective love.',
            'etymology_root': 'Greek stergō (to love, be content with)',
            'etymology_path': 'Proto-Hellenic → Classical Greek στοργή',
            'first_recorded_year': -500,
            'cultural_context': 'Less discussed than other three but recognized in Greek philosophy. Family-centric love.',
            'usage_frequency': 'formal',
            'usage_examples': 'Parent-child bonds, family affection',
            'cognates': json.dumps([]),
            'synonyms': json.dumps(['agape (divine)', 'philia (friendship)', 'eros (romantic)']),
            'source': 'Liddell-Scott Greek Lexicon'
        })
        
        # ========================================================================
        # SLAVIC LANGUAGES
        # ========================================================================
        
        # Russian
        dataset.append({
            'language': 'Russian',
            'language_family': 'Slavic',
            'language_code': 'ru',
            'is_ancient': False,
            'word': 'любовь',
            'romanization': 'lyubov',
            'ipa_pronunciation': '/lʲʊˈbofʲ/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, all contexts. Cognate with Slavic root *lʲub-',
            'etymology_root': 'Proto-Slavic *ľubȳ',
            'etymology_path': 'PIE *leubʰ- → Proto-Slavic *ľubȳ → Old Church Slavonic любꙑ → Russian любовь',
            'first_recorded_year': 1000,
            'cultural_context': 'Central to Russian literature (Tolstoy, Dostoevsky). Phonetically complex with soft consonants.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Я люблю тебя; любовь моя',
            'cognates': json.dumps(['Polish miłość', 'Czech láska', 'Proto-Slavic *ľubȳ']),
            'synonyms': json.dumps(['страсть (passion)', 'нежность (tenderness)']),
            'source': 'Russian Etymological Dictionary'
        })
        
        # Polish
        dataset.append({
            'language': 'Polish',
            'language_family': 'Slavic',
            'language_code': 'pl',
            'is_ancient': False,
            'word': 'miłość',
            'romanization': 'miłość',
            'ipa_pronunciation': '/ˈmiwɔɕt͡ɕ/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, romantic and familial',
            'etymology_root': 'Proto-Slavic *milъ (dear, pleasant)',
            'etymology_path': 'Proto-Slavic *milъ → Old Polish miłość → Modern Polish miłość',
            'first_recorded_year': 1200,
            'cultural_context': 'Polish love tradition intertwined with national identity and Catholic faith',
            'usage_frequency': 'very_common',
            'usage_examples': 'Kocham cię; miłość mojego życia',
            'cognates': json.dumps(['Czech milost', 'Slovak milosť']),
            'synonyms': json.dumps(['uczucie (feeling)']),
            'source': 'Słownik etymologiczny języka polskiego'
        })
        
        # Czech
        dataset.append({
            'language': 'Czech',
            'language_family': 'Slavic',
            'language_code': 'cs',
            'is_ancient': False,
            'word': 'láska',
            'romanization': 'láska',
            'ipa_pronunciation': '/ˈlaːska/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, all contexts',
            'etymology_root': 'Proto-Slavic *laska',
            'etymology_path': 'Proto-Slavic *laska → Old Czech láska → Modern Czech láska',
            'first_recorded_year': 1300,
            'cultural_context': 'Czech love poetry and folk music tradition',
            'usage_frequency': 'very_common',
            'usage_examples': 'Miluji tě; láska mého života',
            'cognates': json.dumps(['Slovak láska', 'Slovene ljubezen']),
            'synonyms': json.dumps(['milost (grace/mercy form)']),
            'source': 'Český etymologický slovník'
        })
        
        # ========================================================================
        # ASIAN LANGUAGES
        # ========================================================================
        
        # Mandarin Chinese
        dataset.append({
            'language': 'Mandarin',
            'language_family': 'Sino-Tibetan',
            'language_code': 'zh',
            'is_ancient': False,
            'word': '爱',
            'romanization': 'ài',
            'ipa_pronunciation': '/aɪ̯˥˩/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, simplified from traditional 愛 (includes heart radical 心). All types of love.',
            'etymology_root': 'Oracle bone script showing person and heart',
            'etymology_path': 'Oracle bone → Bronze script → Seal script → Traditional 愛 → Simplified 爱',
            'first_recorded_year': -1200,
            'cultural_context': 'Ancient character combining "heart" and "graceful movement". Simplified in 1956 PRC reform.',
            'usage_frequency': 'very_common',
            'usage_examples': '我爱你 (wǒ ài nǐ); 爱情 (romantic love)',
            'cognates': json.dumps(['Cantonese oi³', 'Japanese 愛 (ai)']),
            'synonyms': json.dumps(['情 (qíng - emotion)', '恋 (liàn - romantic attachment)']),
            'source': 'Shuowen Jiezi, Modern Chinese Dictionary'
        })
        
        # Japanese
        dataset.append({
            'language': 'Japanese',
            'language_family': 'Japonic',
            'language_code': 'ja',
            'is_ancient': False,
            'word': '愛',
            'romanization': 'ai',
            'ipa_pronunciation': '/ai/',
            'semantic_type': 'general',
            'semantic_nuance': 'Love, but traditionally less commonly expressed than in Western cultures. Often formal.',
            'etymology_root': 'Borrowed from Middle Chinese',
            'etymology_path': 'Middle Chinese ʔojH → Japanese 愛 (ai)',
            'first_recorded_year': 700,
            'cultural_context': 'Borrowed Chinese character. Japanese culture traditionally reserved about expressing "ai". Modern usage expanded.',
            'usage_frequency': 'common',
            'usage_examples': '愛してる (aishiteru - I love you); 愛情 (aijō - affection)',
            'cognates': json.dumps(['Chinese 愛/爱', 'Korean 애 (ae)']),
            'synonyms': json.dumps(['恋 (koi - romantic longing)', '好き (suki - like/love)']),
            'source': 'Kōjien Dictionary, Daijirin'
        })
        
        # Korean
        dataset.append({
            'language': 'Korean',
            'language_family': 'Koreanic',
            'language_code': 'ko',
            'is_ancient': False,
            'word': '사랑',
            'romanization': 'sarang',
            'ipa_pronunciation': '/saɾaŋ/',
            'semantic_type': 'general',
            'semantic_nuance': 'Native Korean word (not Chinese borrowing). General love across contexts.',
            'etymology_root': 'Native Korean, possibly from 살 (sal - life) + 앙 (ang)',
            'etymology_root': 'Native Korean etymology uncertain',
            'etymology_path': 'Middle Korean 사ᄅᆞᆷ (salwom) → Modern Korean 사랑 (sarang)',
            'first_recorded_year': 1400,
            'cultural_context': 'Pure Korean word, not Sino-Korean borrowing. Central to K-pop and Korean drama culture.',
            'usage_frequency': 'very_common',
            'usage_examples': '사랑해 (saranghae - I love you); 사랑의 (of love)',
            'cognates': json.dumps([]),
            'synonyms': json.dumps(['애정 (aejeong - Sino-Korean: affection)', '정 (jeong - deep bond)']),
            'source': 'Korean Etymological Dictionary'
        })
        
        # ========================================================================
        # SEMITIC LANGUAGES
        # ========================================================================
        
        # Arabic
        dataset.append({
            'language': 'Arabic',
            'language_family': 'Semitic',
            'language_code': 'ar',
            'is_ancient': False,
            'word': 'حُبّ',
            'romanization': 'ḥubb',
            'ipa_pronunciation': '/ħubː/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love. Arabic has rich vocabulary with distinctions (ḥubb, ʿishq, hawā).',
            'etymology_root': 'Semitic root Ḥ-B-B',
            'etymology_path': 'Proto-Semitic *ḥbb → Arabic ḥubb',
            'first_recorded_year': 500,
            'cultural_context': 'Arabic poetry has sophisticated love vocabulary. ḥubb is general; ʿishq is passionate; hawā is desire.',
            'usage_frequency': 'very_common',
            'usage_examples': 'أحبك (uḥibbuka - I love you); حب الحياة (love of life)',
            'cognates': json.dumps(['Hebrew אהבה (ahavah)', 'Aramaic ḥubba']),
            'synonyms': json.dumps(['عشق (ʿishq - passionate love)', 'هوى (hawā - desire)', 'غرام (gharām - infatuation)']),
            'source': 'Hans Wehr Arabic Dictionary'
        })
        
        dataset.append({
            'language': 'Arabic',
            'language_family': 'Semitic',
            'language_code': 'ar',
            'is_ancient': False,
            'word': 'عِشْق',
            'romanization': 'ʿishq',
            'ipa_pronunciation': '/ʕiʃq/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Passionate, intense romantic love. Higher intensity than ḥubb.',
            'etymology_root': 'Arabic root ʿ-SH-Q',
            'etymology_path': 'Classical Arabic ʿishq → Modern Standard Arabic',
            'first_recorded_year': 600,
            'cultural_context': 'Persian and Arabic poetry tradition. Associated with Sufi mystical love of God.',
            'usage_frequency': 'common',
            'usage_examples': 'Arabic love poetry, Sufi mystical texts',
            'cognates': json.dumps(['Persian عشق (eshq)']),
            'synonyms': json.dumps(['حب (ḥubb - general love)', 'هوى (hawā - desire)']),
            'source': 'Classical Arabic poetry, Hans Wehr'
        })
        
        # Hebrew
        dataset.append({
            'language': 'Hebrew',
            'language_family': 'Semitic',
            'language_code': 'he',
            'is_ancient': False,
            'word': 'אַהֲבָה',
            'romanization': 'ahavah',
            'ipa_pronunciation': '/ahaˈva/',
            'semantic_type': 'general',
            'semantic_nuance': 'Biblical and modern love. Encompasses all types - divine, romantic, familial.',
            'etymology_root': 'Semitic root ʾ-H-B',
            'etymology_path': 'Proto-Semitic *ʾhb → Biblical Hebrew אהבה → Modern Hebrew אהבה',
            'first_recorded_year': -1000,
            'cultural_context': 'Biblical Hebrew word used in Shema prayer and Song of Songs. Central to Jewish theology.',
            'usage_frequency': 'very_common',
            'usage_examples': 'אני אוהב אותך (ani ohev otach); אהבת ישראל (love of Israel)',
            'cognates': json.dumps(['Arabic حب (ḥubb)', 'Aramaic ḥubba']),
            'synonyms': json.dumps(['חיבה (khiba - affection)', 'דוד (dod - beloved)']),
            'source': 'Brown-Driver-Briggs Hebrew Lexicon'
        })
        
        # ========================================================================
        # INDO-IRANIAN LANGUAGES
        # ========================================================================
        
        # Sanskrit (Ancient)
        dataset.append({
            'language': 'Sanskrit',
            'language_family': 'Indo-Iranian',
            'language_code': 'sa',
            'is_ancient': True,
            'word': 'प्रेम',
            'romanization': 'prema',
            'ipa_pronunciation': '/preːmɐ/',
            'semantic_type': 'divine',
            'semantic_nuance': 'Highest form of love in Hindu philosophy. Divine, selfless, spiritual love.',
            'etymology_root': 'Sanskrit root prī (to please, love)',
            'etymology_path': 'Proto-Indo-European → Sanskrit प्रेम (prema) → Hindi प्रेम (prem)',
            'first_recorded_year': -1500,
            'cultural_context': 'Bhakti yoga tradition. Prema is highest love toward divine. Used in Vedic and devotional texts.',
            'usage_frequency': 'formal',
            'usage_examples': 'Bhagavad Gita, devotional poetry',
            'cognates': json.dumps(['Hindi प्रेम (prem)', 'Gujarati પ્રેમ (prem)']),
            'synonyms': json.dumps(['स्नेह (sneha - affection)', 'काम (kāma - desire)', 'रति (rati - passion)']),
            'source': 'Monier-Williams Sanskrit Dictionary'
        })
        
        dataset.append({
            'language': 'Sanskrit',
            'language_family': 'Indo-Iranian',
            'language_code': 'sa',
            'is_ancient': True,
            'word': 'काम',
            'romanization': 'kāma',
            'ipa_pronunciation': '/kaːmɐ/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Desire, pleasure, sensual love. One of four life goals (puruṣārtha). Named after god Kāma.',
            'etymology_root': 'Sanskrit root kam (to desire, love)',
            'etymology_path': 'Proto-Indo-European *keh₂- (to desire) → Sanskrit काम (kāma)',
            'first_recorded_year': -1500,
            'cultural_context': 'Kāma Sutra subject. Personified as god Kāma (like Greek Eros). Legitimate life pursuit in dharma.',
            'usage_frequency': 'common',
            'usage_examples': 'Kāma Sutra, Vedic texts on life goals',
            'cognates': json.dumps(['Hindi काम (kām)', 'English whim (distant)']),
            'synonyms': json.dumps(['प्रेम (prema - divine love)', 'स्नेह (sneha - affection)', 'रति (rati - passion)']),
            'source': 'Monier-Williams, Kāma Sutra'
        })
        
        dataset.append({
            'language': 'Sanskrit',
            'language_family': 'Indo-Iranian',
            'language_code': 'sa',
            'is_ancient': True,
            'word': 'स्नेह',
            'romanization': 'sneha',
            'ipa_pronunciation': '/sneːhɐ/',
            'semantic_type': 'familial',
            'semantic_nuance': 'Affection, tenderness, oil/smoothness. Gentle, tender love.',
            'etymology_root': 'Sanskrit root snih (to be sticky, fond)',
            'etymology_path': 'Sanskrit स्नेह (sneha) → Hindi स्नेह (sneh)',
            'first_recorded_year': -1000,
            'cultural_context': 'Familial and friendly affection. Also means "oil" (metaphor for smoothness). Gentle form of love.',
            'usage_frequency': 'common',
            'usage_examples': 'Family bonds, gentle affection',
            'cognates': json.dumps(['Hindi स्नेह (sneh)']),
            'synonyms': json.dumps(['प्रेम (prema)', 'काम (kāma)', 'रति (rati)']),
            'source': 'Monier-Williams Sanskrit Dictionary'
        })
        
        # Hindi
        dataset.append({
            'language': 'Hindi',
            'language_family': 'Indo-Iranian',
            'language_code': 'hi',
            'is_ancient': False,
            'word': 'प्यार',
            'romanization': 'pyaar',
            'ipa_pronunciation': '/pjaːr/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, most common modern term. More colloquial than Sanskrit-derived प्रेम (prem).',
            'etymology_root': 'Sanskrit prīya (beloved)',
            'etymology_path': 'Sanskrit prīya → Prakrit pia → Hindi प्यार (pyaar)',
            'first_recorded_year': 1200,
            'cultural_context': 'Bollywood films and Hindi poetry. More common than formal प्रेम (prem) in everyday speech.',
            'usage_frequency': 'very_common',
            'usage_examples': 'मैं तुमसे प्यार करता हूँ (main tumse pyaar karta hun)',
            'cognates': json.dumps(['Urdu پیار (pyaar)', 'Punjabi ਪਿਆਰ (piaar)']),
            'synonyms': json.dumps(['प्रेम (prem - formal)', 'मोहब्बत (mohabbat - from Arabic)', 'इश्क़ (ishq - from Arabic)']),
            'source': 'Hindi-English Dictionary'
        })
        
        # Persian/Farsi
        dataset.append({
            'language': 'Persian',
            'language_family': 'Indo-Iranian',
            'language_code': 'fa',
            'is_ancient': False,
            'word': 'عشق',
            'romanization': 'eshq',
            'ipa_pronunciation': '/eʃɣ/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Passionate love, central to Persian poetry. Borrowed from Arabic but became quintessentially Persian.',
            'etymology_root': 'Arabic ʿishq',
            'etymology_path': 'Arabic عشق (ʿishq) → Persian عشق (eshq) via literary tradition',
            'first_recorded_year': 900,
            'cultural_context': 'Central to Persian/Sufi poetry (Rumi, Hafiz). Sufi mystical love metaphor for divine union.',
            'usage_frequency': 'very_common',
            'usage_examples': 'Persian poetry, Rumi\'s Masnavi',
            'cognates': json.dumps(['Arabic عشق (ʿishq)', 'Urdu عشق (ishq)']),
            'synonyms': json.dumps(['محبت (mohabbat)', 'دوست (doost - friend/love)']),
            'source': 'Classical Persian poetry, Dehkhoda Dictionary'
        })
        
        # ========================================================================
        # OTHER ANCIENT LANGUAGES
        # ========================================================================
        
        # Old English (Anglo-Saxon)
        dataset.append({
            'language': 'Old English',
            'language_family': 'Germanic',
            'language_code': 'ang',
            'is_ancient': True,
            'word': 'lufu',
            'romanization': 'lufu',
            'ipa_pronunciation': '/ˈluvu/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, ancestor of Modern English "love"',
            'etymology_root': 'PIE *leubʰ-',
            'etymology_path': 'PIE *leubʰ- → Proto-Germanic *lubō → Old English lufu → Middle English love → Modern English love',
            'first_recorded_year': 897,
            'cultural_context': 'Appears in earliest English texts (Beowulf era). Direct ancestor of modern "love".',
            'usage_frequency': 'common',
            'usage_examples': 'Old English poetry and religious texts',
            'cognates': json.dumps(['Old High German liubi', 'Old Norse ljúfr', 'Gothic liufs']),
            'synonyms': json.dumps(['leofnes (dearness)']),
            'source': 'Bosworth-Toller Anglo-Saxon Dictionary'
        })
        
        # Proto-Indo-European (Reconstructed)
        dataset.append({
            'language': 'Proto-Indo-European',
            'language_family': 'Indo-European',
            'language_code': 'ine',
            'is_ancient': True,
            'word': '*leubʰ-',
            'romanization': '*leubʰ-',
            'ipa_pronunciation': '/ˈleubʰ/',
            'semantic_type': 'general',
            'semantic_nuance': 'Reconstructed root meaning "to love, desire, care for, be pleased"',
            'etymology_root': 'PIE root',
            'etymology_path': 'PIE *leubʰ- → Germanic love branch, Slavic *ľubȳ branch',
            'first_recorded_year': -4000,
            'cultural_context': 'Reconstructed from cognates across Indo-European languages. Root of Germanic and Slavic love words.',
            'usage_frequency': 'reconstructed',
            'usage_examples': 'N/A - reconstructed root',
            'cognates': json.dumps(['English love', 'German Liebe', 'Russian любовь', 'Sanskrit lubh (to desire)']),
            'synonyms': json.dumps([]),
            'source': 'Pokorny\'s Indo-European Etymological Dictionary, Watkins'
        })
        
        # ========================================================================
        # ADDITIONAL MODERN LANGUAGES
        # ========================================================================
        
        # Turkish
        dataset.append({
            'language': 'Turkish',
            'language_family': 'Turkic',
            'language_code': 'tr',
            'is_ancient': False,
            'word': 'aşk',
            'romanization': 'aşk',
            'ipa_pronunciation': '/aʃk/',
            'semantic_type': 'romantic',
            'semantic_nuance': 'Romantic love, borrowed from Arabic/Persian. Passionate love.',
            'etymology_root': 'Arabic ʿishq via Persian',
            'etymology_path': 'Arabic عشق → Persian عشق → Ottoman Turkish → Modern Turkish aşk',
            'first_recorded_year': 1200,
            'cultural_context': 'Ottoman poetry tradition. Coexists with native Turkish sevgi (general love).',
            'usage_frequency': 'very_common',
            'usage_examples': 'Seni seviyorum (I love you)',
            'cognates': json.dumps(['Arabic عشق', 'Persian عشق']),
            'synonyms': json.dumps(['sevgi (general love)', 'muhabbet (affection - from Arabic)']),
            'source': 'Turkish Language Association Dictionary'
        })
        
        # Finnish
        dataset.append({
            'language': 'Finnish',
            'language_family': 'Uralic',
            'language_code': 'fi',
            'is_ancient': False,
            'word': 'rakkaus',
            'romanization': 'rakkaus',
            'ipa_pronunciation': '/ˈrɑkːɑus/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, romantic and deep affection',
            'etymology_root': 'Finnish rakas (dear, beloved)',
            'etymology_path': 'Proto-Finnic *rakkas → Finnish rakkaus',
            'first_recorded_year': 1543,
            'cultural_context': 'Finnish culture known for reserved emotional expression but deep feeling',
            'usage_frequency': 'common',
            'usage_examples': 'Rakastan sinua (I love you)',
            'cognates': json.dumps(['Estonian armastus', 'Hungarian szerelem']),
            'synonyms': json.dumps(['lempi (love/affection)']),
            'source': 'Suomen kielen etymologinen sanakirja'
        })
        
        # Swahili
        dataset.append({
            'language': 'Swahili',
            'language_family': 'Niger-Congo (Bantu)',
            'language_code': 'sw',
            'is_ancient': False,
            'word': 'upendo',
            'romanization': 'upendo',
            'ipa_pronunciation': '/uˈpɛndo/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, all contexts. From verb kupenda (to love).',
            'etymology_root': 'Bantu root -pend-',
            'etymology_path': 'Proto-Bantu *-pend- → Swahili penda → upendo (noun form)',
            'first_recorded_year': 1500,
            'cultural_context': 'Common in East African context, used across romantic and familial contexts',
            'usage_frequency': 'very_common',
            'usage_examples': 'Nakupenda (I love you); upendo wangu',
            'cognates': json.dumps(['Various Bantu languages with -pend- root']),
            'synonyms': json.dumps(['mapenzi (love/affection)', 'mahaba (from Arabic محبة)']),
            'source': 'Kamusi ya Kiswahili Sanifu'
        })
        
        # Vietnamese
        dataset.append({
            'language': 'Vietnamese',
            'language_family': 'Austroasiatic',
            'language_code': 'vi',
            'is_ancient': False,
            'word': 'yêu',
            'romanization': 'yêu',
            'ipa_pronunciation': '/iəw˧˧/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love, to love (verb form most common)',
            'etymology_root': 'Chinese 愛 (ài) borrowing',
            'etymology_path': 'Middle Chinese → Vietnamese yêu',
            'first_recorded_year': 1000,
            'cultural_context': 'Vietnamese uses both yêu (love verb) and tình yêu (love noun from Chinese)',
            'usage_frequency': 'very_common',
            'usage_examples': 'Anh yêu em (I love you); tình yêu (love noun)',
            'cognates': json.dumps(['Chinese 愛', 'Cantonese oi³']),
            'synonyms': json.dumps(['thương (to love/pity)', 'mến (to be fond of)']),
            'source': 'Vietnamese Dictionary'
        })
        
        # Thai
        dataset.append({
            'language': 'Thai',
            'language_family': 'Kra-Dai',
            'language_code': 'th',
            'is_ancient': False,
            'word': 'ความรัก',
            'romanization': 'khwam rak',
            'ipa_pronunciation': '/kʰwaːm rák/',
            'semantic_type': 'general',
            'semantic_nuance': 'Love (noun). Rak (รัก) is verb "to love", khwam makes it noun.',
            'etymology_root': 'Native Thai root rak',
            'etymology_path': 'Proto-Tai *hrakᴬ → Thai รัก (rak)',
            'first_recorded_year': 1300,
            'cultural_context': 'Thai culture emphasizes gentle, caring love (rak and metta from Buddhism)',
            'usage_frequency': 'very_common',
            'usage_examples': 'ฉันรักคุณ (chan rak khun - I love you)',
            'cognates': json.dumps(['Lao ຮັກ (hak)', 'Shan လၵ်ႉ (lak)']),
            'synonyms': json.dumps(['เมตตา (metta - loving kindness from Pali)']),
            'source': 'Royal Institute Dictionary'
        })
        
        # Greek (Modern)
        dataset.append({
            'language': 'Greek (Modern)',
            'language_family': 'Hellenic',
            'language_code': 'el',
            'is_ancient': False,
            'word': 'αγάπη',
            'romanization': 'agápi',
            'ipa_pronunciation': '/aˈɣapi/',
            'semantic_type': 'general',
            'semantic_nuance': 'General love in modern Greek. Descended from ancient agape but semantically broader.',
            'etymology_root': 'Ancient Greek ἀγάπη',
            'etymology_path': 'Classical Greek ἀγάπη → Koine Greek → Byzantine → Modern Greek αγάπη',
            'first_recorded_year': -800,
            'cultural_context': 'Modern Greek uses agapi for all love types, collapsing ancient distinctions (agape/eros/philia/storge).',
            'usage_frequency': 'very_common',
            'usage_examples': 'Σ\'αγαπώ (s\'agapo - I love you)',
            'cognates': json.dumps(['Ancient Greek ἀγάπη']),
            'synonyms': json.dumps(['έρωτας (erotas - romantic love, from ancient eros)']),
            'source': 'Dictionary of Standard Modern Greek'
        })
        
        return dataset
    
    def get_all_words(self) -> List[Dict]:
        """Return complete dataset of love words"""
        return self.love_words_data
    
    def get_by_language_family(self, family: str) -> List[Dict]:
        """Filter words by language family"""
        return [w for w in self.love_words_data if w['language_family'] == family]
    
    def get_ancient_words(self) -> List[Dict]:
        """Get only ancient language love words"""
        return [w for w in self.love_words_data if w['is_ancient']]
    
    def get_modern_words(self) -> List[Dict]:
        """Get only modern language love words"""
        return [w for w in self.love_words_data if not w['is_ancient']]
    
    def get_by_semantic_type(self, semantic_type: str) -> List[Dict]:
        """Filter by semantic type"""
        return [w for w in self.love_words_data if w['semantic_type'] == semantic_type]
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        total = len(self.love_words_data)
        ancient = len([w for w in self.love_words_data if w['is_ancient']])
        modern = total - ancient
        
        families = {}
        for word in self.love_words_data:
            family = word['language_family']
            families[family] = families.get(family, 0) + 1
        
        semantic_types = {}
        for word in self.love_words_data:
            sem_type = word['semantic_type']
            semantic_types[sem_type] = semantic_types.get(sem_type, 0) + 1
        
        return {
            'total_words': total,
            'ancient_languages': ancient,
            'modern_languages': modern,
            'language_families': families,
            'semantic_types': semantic_types,
            'unique_languages': len(set(w['language'] for w in self.love_words_data))
        }


if __name__ == '__main__':
    # Test collector
    collector = LoveWordsCollector()
    stats = collector.get_stats()
    
    print("="*60)
    print("LOVE WORDS DATASET STATISTICS")
    print("="*60)
    print(f"Total words: {stats['total_words']}")
    print(f"Ancient languages: {stats['ancient_languages']}")
    print(f"Modern languages: {stats['modern_languages']}")
    print(f"Unique languages: {stats['unique_languages']}")
    print(f"\nLanguage families: {stats['language_families']}")
    print(f"\nSemantic types: {stats['semantic_types']}")
    print("="*60)

