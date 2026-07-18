"""Static A1 grammar quiz bank — one multiple-choice question per grammar
topic, keyed by the same topic name used in `curriculum_reference.py` so the
seed migration can look up each question's `topic_id`. Grading is fully
deterministic (index comparison), so quizzes work with no LLM involved.
"""

# Each entry: (topic_name, question, options, correct_option_index, explanation)
QUIZ_QUESTIONS: list[tuple[str, str, list[str], int, str]] = [
    (
        "Alphabet & pronunciation",
        "How do you write \"für\" if your keyboard has no umlauts?",
        ["fur", "fuer", "fyr", "füer"],
        1,
        "ü is substituted with 'ue' when umlauts aren't available, so 'für' becomes 'fuer'.",
    ),
    (
        "Personal pronouns",
        "Which pronoun should you use with a stranger you're meeting for the first time?",
        ["du", "ihr", "Sie", "es"],
        2,
        "Sie is the formal 'you', the safe default with strangers, officials, and service staff.",
    ),
    (
        "Present tense (regular verbs)",
        "What is the correct 'du' form of 'arbeiten' (to work)?",
        ["du arbeitst", "du arbeitest", "du arbeitet", "du arbeiten"],
        1,
        "Stems ending in -t insert an extra -e- before consonant endings: du arbeitest.",
    ),
    (
        "sein & haben",
        "Which auxiliary verb does 'gehen' (to go) take in the Perfekt tense?",
        ["haben", "sein", "werden", "tun"],
        1,
        "Verbs of motion from one place to another take 'sein': ich bin gegangen.",
    ),
    (
        "Definite articles (der/die/das)",
        "What is the definite article for 'Mädchen' (girl)?",
        ["die", "der", "das", "den"],
        2,
        "Nouns ending in the diminutive suffix -chen are always neuter (das), regardless of meaning.",
    ),
    (
        "Indefinite articles (ein/eine)",
        "Which is correct: '___ Frau' (a woman)?",
        ["ein", "eine", "einen", "einer"],
        1,
        "Feminine nouns take 'eine' in the nominative indefinite article.",
    ),
    (
        "Akkusativ case",
        "Complete: 'Der Mann sieht ___ Hund.' (The man sees the dog.)",
        ["der", "den", "dem", "des"],
        1,
        "The dog is the direct object (accusative), and masculine der becomes den in the accusative.",
    ),
    (
        "Possessive articles",
        "Which possessive is correct: 'Sie hat ___ Tasche.' (She has her bag.)",
        ["sein", "ihre", "seine", "ihr"],
        1,
        "The owner is female (sie), so the possessive is 'ihr-'; Tasche is feminine, so it takes -e: ihre.",
    ),
    (
        "Modal verbs",
        "Where does the infinitive go in 'Ich kann morgen nicht kommen'?",
        [
            "Right after the modal verb, like English",
            "At the very end of the clause",
            "Before the subject",
            "It doesn't appear at all",
        ],
        1,
        "Modal verbs push the governed infinitive to the end of the clause: Ich kann morgen nicht kommen.",
    ),
    (
        "W-questions & yes/no questions",
        "What signals a yes/no question in German (with no question word)?",
        [
            "Rising intonation only, word order stays the same",
            "The verb moves to the very first position",
            "Adding 'do' before the subject",
            "The subject moves to the end",
        ],
        1,
        "Yes/no questions invert to verb-first: 'Wohnst du in Berlin?' with no question word needed.",
    ),
    (
        "Negation (nicht/kein)",
        "How do you negate 'Ich habe Zeit' (I have time)?",
        ["Ich habe nicht Zeit.", "Ich habe keine Zeit.", "Ich nicht habe Zeit.", "Ich habe Zeit nicht."],
        1,
        "Zeit has no article here, so it's negated with kein/keine, not nicht: Ich habe keine Zeit.",
    ),
    (
        "Imperative",
        "What is the correct 'du'-imperative of 'sprechen' (to speak)?",
        ["Sprech!", "Sprichst!", "Sprich!", "Sprechen!"],
        2,
        "Verbs with an e→i stem change in the present tense keep that change "
        "in the du-imperative: Sprich!",
    ),
    (
        "Prepositions",
        "Which case does 'für' (for) always take?",
        ["Nominative", "Accusative", "Dative", "Genitive"],
        1,
        "für is one of the fixed accusative prepositions, along with durch, gegen, ohne, and um.",
    ),
    (
        "Word order (verb-second)",
        "In 'Heute trinke ich Kaffee', why does 'ich' come after the verb?",
        [
            "It's a question",
            "'Heute' took first position, so the verb stays second and the subject moves after it",
            "German always puts pronouns third",
            "This sentence is actually incorrect",
        ],
        1,
        "German main clauses are verb-second: whatever is fronted for emphasis takes slot one, "
        "pushing the subject after the verb.",
    ),
    (
        "Perfekt tense basics",
        "What is the past participle of 'trinken' (to drink)?",
        ["getrinkt", "getrunken", "trinkt", "gedrinkt"],
        1,
        "trinken is a strong (irregular) verb: its past participle is getrunken, "
        "not the regular -t form.",
    ),
    (
        "Numbers, time & dates",
        "What time is 'halb drei'?",
        ["3:30", "2:30", "3:15", "2:15"],
        1,
        "German counts the half hour as 'halfway to' the next hour, "
        "so halb drei means 2:30, not 3:30.",
    ),
]
