
#import required modules
import re

# cleans and normalizes answer options
class OptionNormalizer:
    def normalize(self, question, correct, distractors, limit=3):
        correct = self._fit_question_shape(question, correct)
        correct = self._make_full_statement(correct)

        target_words = len(correct.split())
        max_words = max(12, min(28, target_words + 6))

        cleaned = []

        for distractor in distractors:
            distractor = self._fit_question_shape(question, distractor)
            distractor = self._limit_length(distractor, max_words)
            distractor = self._make_full_statement(distractor)

            if distractor.lower() == correct.lower():
                continue

            cleaned.append(distractor)

        return self._unique(cleaned)[:limit]
# Adjusts an option  based on the type of question
    def _fit_question_shape(self, question, option):
        question_lower = question.lower().strip()
        option = self._clean(option)

        if question_lower.startswith("why"):
            option = self._remove_repeated_why_answer(option)

        return option
# removes repeated  wording from "why" answers 
    def _remove_repeated_why_answer(self, option):
        lower = option.lower()

        if " is important because " in lower:
            parts = re.split(
                r"\bis important because\b",
                option,
                flags=re.IGNORECASE
            )

            if len(parts) >= 2:
                reason = self._clean(parts[1])

                if reason.lower().startswith("it "):
                    return reason

                return f"It {reason}"

        return option
# shortens long options  without ending on weak connector words 
    def _limit_length(self, text, max_words):
        text = self._clean(text)
        words = text.split()

        if len(words) <= max_words:
            return text

        cut_words = words[:max_words]

        while cut_words and cut_words[-1].lower() in {
            "and", "or", "but", "because", "with", "of", "to"
        }:
            cut_words.pop()

        return " ".join(cut_words)
# turns text into a complete sentence 
    def _make_full_statement(self, text):
        text = self._clean(text)

        if not text:
            return text

        text = text[0].upper() + text[1:]

        if not text.endswith("."):
            text += "."

        return text
# cleans spacinng, punctuation, annd unnecessary introductory words
    def _clean(self, text):
        text = re.sub(r"\s+", " ", str(text))
        text = text.strip()
        text = text.strip(".,;:!?")

        intro_words = [
            "however",
            "therefore",
            "also",
            "although",
            "in conclusion",
            "for example",
            "for instance"
        ]

        for word in intro_words:
            text = re.sub(rf"^{word},?\s+", "", text, flags=re.IGNORECASE)

        return text
# Removes repeated options while keeping the original order
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