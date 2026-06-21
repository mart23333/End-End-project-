
#import required modules
import re
import spacy

# class to process text for quiz generation, including cleaning, sentence splitting, key sentence extraction, and keyword extraction using spaCy for natural language processing
class TextProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model not found. Run this command: "
                "python -m spacy download en_core_web_sm"
            )
# function to clean the input text by removing extra whitespace and newlines, returning a cleaned version of the text
    def clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ")
        return text.strip()
# function to split the input text into sentences using spaCy
    def split_sentences(self, text):
        cleaned_text = self.clean_text(text)
        doc = self.nlp(cleaned_text)

        sentences = []

        for sent in doc.sents:
            sentence = sent.text.strip()

            if len(sentence.split()) >= 10:
                sentences.append(sentence)

        return sentences
# function to extract key sentences from the input text by scoring them based on entity count, noun and verb count, length, and presence of reasoning keywords
    def extract_key_sentences(self, text, limit=30):
        sentences = self.split_sentences(text)
        scored_sentences = []

        for sentence in sentences:
            doc = self.nlp(sentence)

            entity_count = len(doc.ents)
            noun_count = len([
                token for token in doc
                if token.pos_ in ["NOUN", "PROPN"]
            ])
            verb_count = len([
                token for token in doc
                if token.pos_ == "VERB"
            ])

            length_score = min(len(sentence.split()) / 25, 2)

            reasoning_keywords = [
                "because",
                "therefore",
                "however",
                "although",
                "despite",
                "consequently",
                "result",
                "impact",
                "influence",
                "caused",
                "led",
                "created",
                "suggests",
                "indicates",
                "reveals",
                "shows",
                "implies",
                "conflict",
                "theme",
                "motivation"
            ]

            keyword_score = 0

            for keyword in reasoning_keywords:
                if keyword.lower() in sentence.lower():
                    keyword_score += 2

            score = (
                entity_count
                + noun_count
                + verb_count
                + length_score
                + keyword_score
            )

            scored_sentences.append((sentence, score))

        scored_sentences.sort(key=lambda item: item[1], reverse=True)

        return [sentence for sentence, score in scored_sentences[:limit]]
# function to extract keywords from the input text by identifying noun chunks and named entities using spaCy
    def extract_keywords(self, text, limit=50):
        cleaned_text = self.clean_text(text)
        doc = self.nlp(cleaned_text)

        keywords = []

        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip()

            if 2 <= len(phrase.split()) <= 5:
                keywords.append(phrase)

        for ent in doc.ents:
            keywords.append(ent.text.strip())

        unique_keywords = []

        for keyword in keywords:
            already_exists = False

            for item in unique_keywords:
                if keyword.lower() == item.lower():
                    already_exists = True
                    break

            if not already_exists:
                unique_keywords.append(keyword)

        return unique_keywords[:limit]