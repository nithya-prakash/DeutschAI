"""Static writing prompt bank — global reference data, seeded via migration.

Each tuple is (cefr_level, prompt_text).
"""

WRITING_PROMPTS: list[tuple[str, str]] = [
    (
        "A1",
        "Stell dich vor: Schreibe 3–4 Sätze über dich. Wie heißt du, wo wohnst du und "
        "was machst du gerne?",
    ),
    (
        "A1",
        "Beschreibe deine Familie in ein paar Sätzen. Wer gehört dazu und was machen "
        "sie beruflich?",
    ),
    (
        "A2",
        "Schreibe eine kurze E-Mail an einen Freund und lade ihn zu deinem "
        "Geburtstag ein. Nenne Datum, Uhrzeit und Ort.",
    ),
    ("A2", "Beschreibe deinen typischen Tagesablauf von morgens bis abends."),
    ("A2", "Du warst im Urlaub. Schreibe eine Postkarte an einen Freund über deine Reise."),
    (
        "B1",
        "Was sind die Vor- und Nachteile des Lebens in einer Großstadt im "
        "Vergleich zu einem Dorf? Schreibe deine Meinung mit Beispielen.",
    ),
    (
        "B1",
        "Sollten Schüler in der Schule eine zweite Fremdsprache lernen müssen? "
        "Begründe deine Meinung.",
    ),
    ("B1", "Schreibe über ein Erlebnis, das dein Deutschlernen verändert oder motiviert hat."),
]
