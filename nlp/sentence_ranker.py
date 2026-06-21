
# imports required modules
import re

# class to rank sentences based on their importance and relevance for quiz question generation
class SentenceRanker:
    def __init__(self, nlp):
        self.nlp = nlp
# function to rank sentences in the input text 
    def rank_sentences(self, text, limit=40):
        doc = self.nlp(text)
        scored_sentences = []

        for sent in doc.sents:
            sentence = self._clean_sentence(sent.text)

            if not self._is_usable_sentence(sentence):
                continue

            score = self._score_sentence(sentence)

            if score > 0:
                scored_sentences.append((score, sentence))

        scored_sentences.sort(reverse=True, key=lambda item: item[0])

        return [sentence for score, sentence in scored_sentences[:limit]]
# function to assign a score to a sentence based on various factors
    def _score_sentence(self, sentence):
        lower = sentence.lower()
        score = 0

        words = sentence.split()

        if 10 <= len(words) <= 45:
            score += 3

        if self._has_definition(lower):
            score += 5

        if self._has_cause_effect(lower):
            score += 5

        if self._has_comparison(lower):
            score += 5

        if self._has_examples(lower):
            score += 4

        if self._has_identification(lower):
            score += 5

        if self._has_dates(sentence):
            score += 4

        if self._has_learning_signal(lower):
            score += 3

        if len(words) > 60:
            score -= 4

        if sentence.count(",") > 5:
            score -= 2

        return score
# function to determine if a sentence is suitable for question generation
    def _is_usable_sentence(self, sentence):
        if not sentence:
            return False

        words = sentence.split()

        if len(words) < 8:
            return False

        if len(words) > 70:
            return False

        bad_fragments = [
            "click here",
            "copyright",
            "all rights reserved",
            "table of contents",
            "www.",
            "http"
        ]

        if any(fragment in sentence.lower() for fragment in bad_fragments):
            return False

        letters = sum(char.isalpha() for char in sentence)
        total = len(sentence)

        if total > 0 and letters / total < 0.55:
            return False

        return True
# function to check if a sentence contains markers that indicate it includes a definition 
    def _has_definition(self, lower):
        markers = [
            " is ",
            " are ",
            " means ",
            " refers to ",
            " can be defined as ",
            " is known as "
        ]

        return any(marker in lower for marker in markers)
# function to check if a sentence contains markers that indicate it includes a cause-effect relationship
    def _has_cause_effect(self, lower):
        markers = [
            "because",
            "therefore",
            "as a result",
            "due to",
            "caused",
            "causes",
            "led to",
            "leads to",
            "resulted in",
            "affects",
            "influences",
            "effect",
            "impact",
            "consequence",
            "continued to"
        ]

        return any(marker in lower for marker in markers)
# function to check if a sentence contains markers that indicate it includes a comparison 
    def _has_comparison(self, lower):
        markers = [
            "while",
            "whereas",
            "unlike",
            "however",
            "but",
            "compared to",
            "in contrast",
            "difference between",
            "different from"
        ]

        return any(marker in lower for marker in markers)
# function to check if a sentence contains markers that indicate it includes examples or elaboration of a concept
    def _has_examples(self, lower):
        markers = [
            "for example",
            "for instance",
            "such as",
            "including",
            "includes",
            "include",
            "examples of"
        ]

        return any(marker in lower for marker in markers)
# function to check if a sentence contains markers that indicate it includes identification of a person, place, or thing
    def _has_identification(self, lower):
        markers = [
            "also known as",
            "known as",
            "called",
            "named"
        ]

        return any(marker in lower for marker in markers)
# function to check if a sentence contains date entities, which can indicate important historical information
    def _has_dates(self, sentence):
        doc = self.nlp(sentence)

        for ent in doc.ents:
            if ent.label_ == "DATE":
                return True

        return False
# function to check if a sentence contains markers that indicate it includes important information
    def _has_learning_signal(self, lower):
        markers = [
            "important",
            "major",
            "main",
            "serious",
            "significant",
            "used to",
            "helps",
            "allows",
            "formed",
            "developed",
            "became",
            "known for"
        ]

        return any(marker in lower for marker in markers)
# function to clean a sentence by removing extra whitespace and ensuring it is properly formatted
    def _clean_sentence(self, sentence):
        sentence = re.sub(r"\s+", " ", sentence)
        return sentence.strip()