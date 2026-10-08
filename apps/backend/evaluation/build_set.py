"""Generates tutor_eval_set.json. Facts are taken from the knowledge-base notes in
app/ai/rag/knowledge_base; `must` is a list of fact groups, each a list of regex
alternatives, and an answer is correct only if every group matches."""
import json

T = {1: "Alphabet & pronunciation", 2: "Personal pronouns", 3: "Present tense (regular verbs)",
     4: "sein & haben", 5: "Definite articles (der/die/das)", 6: "Indefinite articles (ein/eine)",
     7: "Akkusativ case", 8: "Possessive articles", 9: "Modal verbs", 10: "W-questions & yes/no questions",
     11: "Negation (nicht/kein)", 12: "Imperative", 13: "Prepositions", 14: "Word order (verb-second)",
     15: "Perfekt tense basics", 16: "Numbers, time & dates"}

IN = [  # (topic id, question, must)
 (1, "How do I pronounce the German letter w?", [[r"\bv\b", r"vater|\"v\"|like (an? )?(english )?v"]]),
 (1, "What do I write if my keyboard has no ß or umlauts?", [[r"\bss\b"], [r"\bae\b|\boe\b|\bue\b"]]),
 (2, "When should I use Sie instead of du?", [[r"formal|polite"], [r"stranger|official|older|service"]]),
 (2, "Why is a table called er in German?", [[r"gender"], [r"der tisch|masculine"]]),
 (3, "How do I conjugate machen for du?", [[r"machst"]]),
 (3, "Why is it du arbeitest and not du arbeitst?", [[r"arbeitest"], [r"\be\b|extra|pronounc"]]),
 (4, "What is the conjugation of sein?", [[r"\bbin\b"], [r"\bbist\b"], [r"\bist\b"], [r"\bsind\b"], [r"\bseid\b"]]),
 (4, "How do I say I am 20 years old in German?", [[r"ich bin 20|ich bin zwanzig"], [r"not .{0,20}haben|bin"]]),
 (5, "Which article does Mädchen take and why?", [[r"das"], [r"-?chen|neuter|diminutive"]]),
 (5, "Which article do I use for nouns ending in -ung?", [[r"\bdie\b"], [r"feminine"]]),
 (6, "How do I say some men without an article?", [[r"männer"], [r"no (plural )?(indefinite )?article|without|einige"]]),
 (6, "What is the indefinite article for a feminine noun?", [[r"\beine\b"]]),
 (7, "What happens to der in the accusative?", [[r"\bden\b"], [r"masculine"]]),
 (7, "How do I find the accusative object in a sentence?", [[r"wen|was"], [r"object"]]),
 (8, "What is the difference between sein and ihr as his and her?", [[r"owner"], [r"male|man|he|his"], [r"female|woman|she|her"]]),
 (8, "How do I say my mother?", [[r"meine mutter"], [r"\be\b|ending|feminine"]]),
 (9, "Where does the second verb go with a modal verb?", [[r"end"], [r"infinitive"]]),
 (9, "What is the ich form of können?", [[r"\bkann\b"]]),
 (10, "How do I form a yes/no question in German?", [[r"first|beginning|start"], [r"verb"]]),
 (10, "Is it Wo wohnst du or Wo du wohnst?", [[r"wo wohnst du"], [r"second|verb"]]),
 (11, "When do I use kein instead of nicht?", [[r"\bkein"], [r"noun"], [r"\bnicht\b"]]),
 (11, "Where does nicht go when I negate the whole sentence?", [[r"end"], [r"komme heute nicht|clause|sentence"]]),
 (12, "What is the du imperative of kommen?", [[r"\bkomm\b"]]),
 (12, "How do I form a polite Sie command?", [[r"kommen sie|verb.{0,15}(first|before)|invert"], [r"sie"]]),
 (13, "Which prepositions always take the accusative?", [[r"\bdurch\b"], [r"\bfür\b|fuer"], [r"\bohne\b|\bgegen\b|\bum\b"]]),
 (13, "When do two-way prepositions like in take accusative versus dative?", [[r"motion|wohin|direction|toward"], [r"static|location|\bwo\b"]]),
 (14, "Why is it Heute trinke ich Kaffee?", [[r"second"], [r"verb"]]),
 (14, "Where does the verb go after weil?", [[r"end"], [r"subordinate|weil"]]),
 (15, "How do I form the Perfekt?", [[r"haben|sein"], [r"participle"]]),
 (15, "Which verbs take sein in the Perfekt?", [[r"motion|movement|gehen|fahren"], [r"change of state|change"]]),
 (16, "What does halb drei mean?", [[r"2:30|half past two|2\.30|14:30"], [r"not|instead|rather"]]),
 (16, "How do I write 47 in German?", [[r"siebenundvierzig"]]),
]
OUT = [  # out-of-scope: KB has no note; a good answer flags that
 "How do I use the Genitiv case?",
 "How do I form the Konjunktiv II?",
 "How does the German passive voice work?",
 "How do relative clauses with der, die and das work?",
 "What are the adjective endings after a definite article?",
 "How do I form the Plusquamperfekt?",
 "What is the capital of Australia?",
 "Write a Python function that sorts a list.",
]
cases = []
for i, (t, q, must) in enumerate(IN, 1):
    cases.append({"id": f"in-{i:02d}", "kind": "in_scope", "question": q, "cefr_level": "A1",
                  "topic": T[t], "must": must})
for i, q in enumerate(OUT, 1):
    cases.append({"id": f"out-{i:02d}", "kind": "out_of_scope", "question": q, "cefr_level": "A1",
                  "topic": None, "must": []})
json.dump({"version": 1, "cases": cases}, open("tutor_eval_set.json", "w"), ensure_ascii=False, indent=1)
print(len(cases), "cases")
