"""The static A1 curriculum topic lists.

Single source of truth for the Goethe-Zertifikat A1 grammar syllabus and
Sprechen topic list — imported by the Alembic seed migration and by the test
suite, so both stay in sync with exactly one place to edit when the
curriculum changes.
"""

GRAMMAR_TOPICS: list[str] = [
    "Alphabet & pronunciation",
    "Personal pronouns",
    "Present tense (regular verbs)",
    "sein & haben",
    "Definite articles (der/die/das)",
    "Indefinite articles (ein/eine)",
    "Akkusativ case",
    "Possessive articles",
    "Modal verbs",
    "W-questions & yes/no questions",
    "Negation (nicht/kein)",
    "Imperative",
    "Prepositions",
    "Word order (verb-second)",
    "Perfekt tense basics",
    "Numbers, time & dates",
]

EVERYDAY_TOPICS: list[str] = [
    "Introducing yourself",
    "Family and friends",
    "Hobbies and interests",
    "Daily routine",
    "Shopping",
    "Food and drinks",
    "Work and studies",
    "Travel and transportation",
    "Weather",
    "Appointments and schedules",
]
