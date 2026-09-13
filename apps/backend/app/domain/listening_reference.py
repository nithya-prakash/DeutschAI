"""Static listening comprehension bank — global reference data (like
reading_reference.py), seeded via migration. `script_text` is what gets
synthesized to audio (see scripts/synthesize_listening_audio.py); it is never
sent to the frontend.

Each tuple is (cefr_level, script_text, question, options,
correct_option_index, explanation).
"""

LISTENING_SCRIPTS: list[tuple[str, str, str, list[str], int, str]] = [
    (
        "A1",
        "Guten Tag! Ich heiße Sofia und ich komme aus Spanien. Ich lerne seit drei "
        "Monaten Deutsch. Am liebsten höre ich deutsche Musik.",
        "Wie lange lernt Sofia schon Deutsch?",
        ["Drei Wochen", "Drei Monate", "Drei Jahre", "Drei Tage"],
        1,
        "Sofia sagt: 'Ich lerne seit drei Monaten Deutsch.'",
    ),
    (
        "A1",
        "Das Wetter heute ist schlecht. Es regnet den ganzen Tag und es ist "
        "windig. Morgen soll aber die Sonne scheinen.",
        "Wie ist das Wetter morgen laut der Vorhersage?",
        ["Es regnet weiter", "Es schneit", "Die Sonne scheint", "Es ist windig"],
        2,
        "Der Text sagt: 'Morgen soll aber die Sonne scheinen.'",
    ),
    (
        "A1",
        "Ich stehe jeden Morgen um sechs Uhr auf. Zuerst dusche ich, dann "
        "frühstücke ich und trinke einen Tee. Um sieben Uhr verlasse ich das Haus.",
        "Was trinkt die Person zum Frühstück?",
        ["Kaffee", "Wasser", "Tee", "Saft"],
        2,
        "Der Text sagt direkt: 'trinke einen Tee.'",
    ),
    (
        "A2",
        "Herr Braun fährt jeden Tag mit dem Zug zur Arbeit. Der Zug fährt um "
        "sieben Uhr fünfzehn ab und die Fahrt dauert vierzig Minuten.",
        "Wie lange dauert die Zugfahrt von Herrn Braun?",
        ["Fünfzehn Minuten", "Vierzig Minuten", "Eine Stunde", "Zwei Stunden"],
        1,
        "Der Text sagt: 'die Fahrt dauert vierzig Minuten.'",
    ),
    (
        "A2",
        "Am Samstag gehen Lisa und ihre Freundin ins Kino. Zuerst essen sie in "
        "einem Restaurant und danach schauen sie sich einen neuen Film an.",
        "Was machen Lisa und ihre Freundin zuerst?",
        [
            "Sie schauen einen Film",
            "Sie essen in einem Restaurant",
            "Sie gehen einkaufen",
            "Sie fahren nach Hause",
        ],
        1,
        "Der Text sagt: 'Zuerst essen sie in einem Restaurant.'",
    ),
    (
        "A2",
        "Der kleine Tim feiert nächste Woche seinen Geburtstag. Seine Mutter "
        "plant eine Party mit vielen Kindern, einem großen Kuchen und "
        "Luftballons im Garten.",
        "Wo findet die Geburtstagsparty statt?",
        ["Im Garten", "Im Restaurant", "In der Schule", "Im Schwimmbad"],
        0,
        "Der Text sagt: 'im Garten.'",
    ),
    (
        "B1",
        "In den letzten Jahren ist Fahrradfahren in deutschen Städten viel "
        "beliebter geworden. Viele Städte bauen deshalb neue Fahrradwege, damit "
        "Radfahrer sicherer unterwegs sind.",
        "Warum bauen die Städte neue Fahrradwege?",
        [
            "Um mehr Parkplätze zu schaffen",
            "Damit Radfahrer sicherer fahren können",
            "Weil Autos verboten werden",
            "Um Touristen anzulocken",
        ],
        1,
        "Der Text sagt: 'damit Radfahrer sicherer unterwegs sind.'",
    ),
    (
        "B1",
        "Peter überlegt, ob er nach dem Studium im Ausland arbeiten soll. Er hat "
        "ein Jobangebot aus Kanada bekommen, zögert aber, weil er seine Familie "
        "in Deutschland nicht so oft sehen würde.",
        "Warum zögert Peter bei dem Jobangebot?",
        [
            "Das Gehalt ist zu niedrig",
            "Er möchte seine Familie öfter sehen",
            "Er spricht kein Englisch",
            "Die Stelle gefällt ihm nicht",
        ],
        1,
        "Der Text nennt den Grund: 'weil er seine Familie... nicht so oft sehen würde.'",
    ),
]
