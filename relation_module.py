import spacy
import requests

# Load spaCy for entity detection and sentence parsing
nlp = spacy.load("en_core_web_sm")

# Hugging Face Inference API setup
API_URL = "https://api-inference.huggingface.co/models/Babelscape/rebel-large"
headers = {"Authorization": f"Bearer "}

def query_rebel_api(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def extract_relations(text):
    doc = nlp(text)
    relations = []

    # ----- spaCy rule-based relation extraction -----
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ("dobj", "attr") and token.head.pos_ == "VERB":
                subject = [w for w in token.head.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                if subject:
                    relations.append({
                        "source": subject[0].text,
                        "target": token.text,
                        "relation": token.head.lemma_,
                        "confidence": 0.85,
                        "source_type": "spacy"
                    })

    # ----- REBEL API-based relation extraction -----
    api_output = query_rebel_api(text)

    # Safely parse the output
    decoded = ""
    if isinstance(api_output, str):
        decoded = api_output
    elif isinstance(api_output, dict) and "generated_text" in api_output:
        decoded = api_output["generated_text"]
    elif isinstance(api_output, list) and len(api_output) > 0 and "generated_text" in api_output[0]:
        decoded = api_output[0]["generated_text"]
    else:
        print("Warning: No valid REBEL output received.")
        decoded = ""


    # Parse generated triples
    for triple in decoded.split("<triplet>")[1:]:
        try:
            sub = triple.split("<subj>")[1].split("<obj>")[0].strip()
            obj = triple.split("<obj>")[1].split("<rel>")[0].strip()
            rel = triple.split("<rel>")[1].strip()

            if sub and obj:
                relations.append({
                    "source": sub,
                    "target": obj,
                    "relation": rel,
                    "confidence": 0.90,
                    "source_type": "rebel"
                })
        except:
            continue

    return relations
