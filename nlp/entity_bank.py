# import required modules
import re
from collections import defaultdict

# Builds an entity bank from text using spaCy NLP
class EntityBankBuilder:
    def __init__(self, nlp):
        self.nlp = nlp


 # Processes the text and stores useful entities and concepts    

 # Processes the text and stores useful entities and concepts   
    def build(self, text):
        doc = self.nlp(text)
        bank = defaultdict(list)

        for ent in doc.ents:
            label = self._map_label(ent.label_)

            if label:
                self._add(bank, label, ent.text)

        for chunk in doc.noun_chunks:
            concept = self._clean(chunk.text)

            if self._is_good_concept(concept):
                self._add(bank, "CONCEPT", concept)

        return dict(bank)
# Converts spaCy entity labels into simpler project labels
    def _map_label(self, label):
        mapping = {
            "PERSON": "PERSON",
            "DATE": "DATE",
            "GPE": "PLACE",
            "LOC": "PLACE",
            "ORG": "ORG",
            "NORP": "GROUP",
            "EVENT": "EVENT",
            "FAC": "PLACE"
        }

        return mapping.get(label)
# Adds a cleaned value to the bank if it is valid and not duplicated
    def _add(self, bank, label, value):
        value = self._clean(value)

        if not value:
            return

        if len(value) < 2:
            return

        existing = [item.lower() for item in bank[label]]

        if value.lower() not in existing:
            bank[label].append(value)
 # Checks if a noun phrase is useful enough to be stored as a concept
    def _is_good_concept(self, concept):
        lower = concept.lower()
        words = concept.split()

        if len(words) < 1 or len(words) > 5:
            return False

        bad_values = {
            "it",
            "this",
            "that",
            "they",
            "he",
            "she",
            "we",
            "you",
            "the passage",
            "the article",
            "many people",
            "some people"
        }

        if lower in bad_values:
            return False

        if not any(char.isalpha() for char in concept):
            return False

        return True
# Cleans text by removing extra spaces and punctuation
    def _clean(self, text):
        text = re.sub(r"\s+", " ", str(text))
        text = text.strip()
        text = text.strip(".,;:!?")
        return text
