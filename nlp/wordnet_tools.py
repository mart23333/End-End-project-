# import require module
import re

try:
    from nltk.corpus import wordnet as wn
except Exception:
    wn = None

#  class to provide helper functions for generating word and phrase variations using WordNet, including predefined replacements and synonyms, while ensuring the alternatives are valid and unique
class WordNetHelper:
    def __init__(self):
        self.phrase_replacements = {
            # Science
            "kinetic energy": ["potential energy", "chemical energy", "heat energy"],
            "potential energy": ["kinetic energy", "electrical energy", "light energy"],
            "speed and direction": ["distance and time", "force and motion", "energy and height"],
            "change in position": ["change in speed", "change in direction", "change in energy"],
            "distance travelled": ["direction travelled", "force applied", "energy stored"],

            # Business
            "market research": ["business plan", "marketing strategy", "financial planning"],
            "business plan": ["market research", "advertising campaign", "customer service"],
            "target customers": ["competitors", "investors", "suppliers"],
            "customer needs": ["competitor prices", "investor interest", "brand image"],
            "financial management": ["marketing strategy", "product design", "customer service"],
            "business growth": ["business advertising", "business risk", "business failure"],

            # History
            "political development": ["economic development", "cultural influence", "military expansion"],
            "ethnic diversity": ["economic growth", "regional trade", "religious leadership"],
            "colonial experience": ["modern democracy", "military leadership", "cultural expansion"],
            "struggle for independence": ["growth of trade", "rise of ancient kingdoms", "spread of religion"],
            "ancient civilizations": ["modern states", "nomadic groups", "colonial governments"],
            "government and laws": ["trade and farming", "religion and culture", "war and invasion"],

            # Literature
            "character development": ["setting description", "plot summary", "background detail"],
            "main conflict": ["peaceful setting", "minor event", "background description"],
            "lesson of the story": ["setting of the story", "name of the village", "order of events"],
            "mood of the passage": ["plot of the passage", "location of the passage", "title of the passage"]
        }

        self.word_replacements = {
            # Science
            "motion": ["speed", "force", "energy"],
            "speed": ["velocity", "acceleration", "distance"],
            "velocity": ["speed", "acceleration", "motion"],
            "acceleration": ["velocity", "speed", "distance"],
            "kinetic": ["potential", "chemical", "thermal"],
            "potential": ["kinetic", "chemical", "electrical"],
            "force": ["motion", "energy", "speed"],

            # Business
            "customers": ["competitors", "investors", "suppliers"],
            "market": ["finance", "advertising", "production"],
            "profit": ["revenue", "capital", "demand"],
            "planning": ["promotion", "expansion", "production"],
            "capital": ["profit", "revenue", "sales"],
            "demand": ["supply", "competition", "advertising"],

            # History
            "political": ["economic", "social", "cultural"],
            "economic": ["political", "social", "industrial"],
            "colonial": ["traditional", "democratic", "military"],
            "modern": ["ancient", "colonial", "early"],
            "ethnic": ["regional", "religious", "cultural"],
            "independence": ["colonization", "amalgamation", "military rule"],

            # Literature
            "theme": ["setting", "mood", "conflict"],
            "conflict": ["setting", "dialogue", "description"],
            "courage": ["curiosity", "obedience", "patience"],
            "character": ["setting", "plot", "symbol"],
            "mood": ["theme", "conflict", "setting"]
        }
# function to generate variations of a given text
    def phrase_variations(self, text):
        output = []
        lower = text.lower()

        for phrase, replacements in self.phrase_replacements.items():
            if phrase in lower:
                for replacement in replacements:
                    candidate = re.sub(
                        re.escape(phrase),
                        replacement,
                        text,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    output.append(candidate)

        return output
# function to generate variations of individual words in a given text
    def word_variations(self, text):
        output = []
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text)

        for word in words:
            alternatives = self.alternatives(word)

            for alt in alternatives:
                candidate = re.sub(
                    rf"\b{re.escape(word)}\b",
                    alt,
                    text,
                    count=1,
                    flags=re.IGNORECASE
                )
                output.append(candidate)

        return output
# function to generate alternative words for a given word
    def alternatives(self, word, max_items=5):
        word = word.lower().strip()
        alternatives = []

        if word in self.word_replacements:
            alternatives.extend(self.word_replacements[word])

        if wn is not None:
            try:
                for synset in wn.synsets(word)[:2]:
                    for hypernym in synset.hypernyms():
                        for hyponym in hypernym.hyponyms()[:6]:
                            name = hyponym.lemmas()[0].name()
                            name = name.replace("_", " ").lower()

                            if self._is_valid_alt(word, name):
                                alternatives.append(name)

            except LookupError:
                pass

            except Exception:
                pass

        return self._unique(alternatives)[:max_items]
# function to check if a candidate alternative is valid 
    def _is_valid_alt(self, original, alt):
        if not alt:
            return False

        if alt == original:
            return False

        if len(alt.split()) > 2:
            return False

        if not re.match(r"^[a-zA-Z\s-]+$", alt):
            return False

        return True
# function to ensure that a list of alternatives is unique, ignoring case and extra whitespace, while preserving the original order
    def _unique(self, items):
        seen = set()
        output = []

        for item in items:
            key = item.lower().strip()

            if key in seen:
                continue

            seen.add(key)
            output.append(item)

        return output