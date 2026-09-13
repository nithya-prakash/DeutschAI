"""Static reading comprehension bank — global reference data (like
quiz_reference.py), seeded via migration.

Each tuple is (cefr_level, passage_text, question, options,
correct_option_index, explanation).
"""

READING_PASSAGES: list[tuple[str, str, str, list[str], int, str]] = [
    (
        "A1",
        "Anna wohnt in Berlin. Sie arbeitet in einem Café in der Nähe von ihrer "
        "Wohnung. Jeden Morgen trinkt sie einen Kaffee, bevor sie zur Arbeit geht.",
        "Wo arbeitet Anna?",
        ["In einer Schule", "In einem Café", "In einem Krankenhaus", "In einem Supermarkt"],
        1,
        "Der Text sagt direkt: 'Sie arbeitet in einem Café.'",
    ),
    (
        "A1",
        "Das ist meine Familie. Mein Vater heißt Peter und meine Mutter heißt Julia. "
        "Ich habe eine Schwester. Sie heißt Lena und ist zehn Jahre alt.",
        "Wie heißt die Schwester?",
        ["Julia", "Peter", "Lena", "Anna"],
        2,
        "Der Text nennt die Schwester namentlich: 'Sie heißt Lena.'",
    ),
    (
        "A1",
        "Herr Meyer hat einen Hund. Der Hund heißt Bello und ist drei Jahre alt. "
        "Jeden Tag geht Herr Meyer mit Bello im Park spazieren.",
        "Wie alt ist der Hund?",
        ["Ein Jahr", "Zwei Jahre", "Drei Jahre", "Vier Jahre"],
        2,
        "Der Text sagt: 'Der Hund heißt Bello und ist drei Jahre alt.'",
    ),
    (
        "A2",
        "Am Wochenende fährt Familie Schmidt oft aufs Land. Sie haben ein kleines "
        "Ferienhaus am See, wo sie schwimmen und grillen.",
        "Was macht die Familie am See?",
        [
            "Sie geht einkaufen",
            "Sie schwimmt und grillt",
            "Sie besucht ein Museum",
            "Sie arbeitet im Garten",
        ],
        1,
        "Der Text nennt die Aktivitäten direkt: 'wo sie schwimmen und grillen.'",
    ),
    (
        "A2",
        "Markus hat sich letzte Woche das Bein gebrochen, als er Fahrrad gefahren "
        "ist. Jetzt muss er für sechs Wochen einen Gips tragen und kann nicht zur "
        "Arbeit gehen.",
        "Warum kann Markus nicht arbeiten?",
        [
            "Er ist im Urlaub",
            "Er hat sich das Bein gebrochen",
            "Er hat gekündigt",
            "Er ist krank mit Grippe",
        ],
        1,
        "Der Text erklärt: 'Markus hat sich letzte Woche das Bein gebrochen.'",
    ),
    (
        "A2",
        "Frau Klein kocht jeden Sonntag für ihre ganze Familie. Diese Woche macht "
        "sie Schnitzel mit Kartoffelsalat, weil das ihr Enkelkind am liebsten isst.",
        "Was kocht Frau Klein diese Woche?",
        ["Nudeln mit Tomatensoße", "Schnitzel mit Kartoffelsalat", "Suppe", "Fisch mit Reis"],
        1,
        "Der Text sagt direkt: 'macht sie Schnitzel mit Kartoffelsalat.'",
    ),
    (
        "B1",
        "Immer mehr Menschen in Deutschland entscheiden sich für ein Leben ohne "
        "Auto, besonders in großen Städten. Sie nutzen stattdessen öffentliche "
        "Verkehrsmittel, Fahrräder oder Carsharing-Angebote, um Kosten zu sparen "
        "und die Umwelt zu schonen.",
        "Warum verzichten viele Menschen auf ein eigenes Auto?",
        [
            "Weil Autos verboten sind",
            "Um Geld zu sparen und die Umwelt zu schützen",
            "Weil sie keinen Führerschein haben",
            "Weil es keine Straßen gibt",
        ],
        1,
        "Der Text nennt die Gründe: 'um Kosten zu sparen und die Umwelt zu schonen.'",
    ),
    (
        "B1",
        "Die Digitalisierung verändert die Arbeitswelt stark. Viele Angestellte "
        "arbeiten heute von zu Hause aus und müssen sich nicht mehr täglich ins "
        "Büro fahren. Das spart Zeit, kann aber auch dazu führen, dass sich "
        "Kollegen seltener persönlich treffen.",
        "Welcher Nachteil des Homeoffice wird im Text genannt?",
        [
            "Es kostet mehr Geld",
            "Kollegen treffen sich seltener persönlich",
            "Man muss länger arbeiten",
            "Es gibt keine Pausen",
        ],
        1,
        "Der Text nennt genau diesen Nachteil: 'Kollegen seltener persönlich treffen.'",
    ),
]
