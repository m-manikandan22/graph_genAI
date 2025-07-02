import spacy

nlp = spacy.load("en_core_web_md")

ALLOWED_LABELS = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT"}

def extract_entities(text):
    doc = nlp(text)
    seen = set()
    entities = []
    for ent in doc.ents:
        if ent.label_ in ALLOWED_LABELS and ent.text.lower() not in seen:
            seen.add(ent.text.lower())
            entities.append({"text": ent.text, "label": ent.label_})
    return entities
