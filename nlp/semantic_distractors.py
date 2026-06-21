# import required modules
import random
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# class to generate semantically relevant distractor options
class SemanticDistractorGenerator:
    def __init__(self):
        pass
# Main function to generate distractors based on the correct answer, context, and question type
    def generate_distractors(
        self,
        correct_answer,
        context_sentence,
        candidate_pool,
        mode,
        question_type,
        number=3
    ):
        correct_answer = self._clean(correct_answer)
        context_sentence = self._clean(context_sentence)

        semantic_candidates = self._select_semantic_candidates(
            correct_answer=correct_answer,
            context_sentence=context_sentence,
            candidate_pool=candidate_pool,
            number=number
        )

        passage_aware = self._generate_passage_aware_distractors(
            correct_answer=correct_answer,
            context_sentence=context_sentence,
            mode=mode,
            question_type=question_type
        )

        combined = semantic_candidates + passage_aware
        combined = self._unique(combined)

        return combined[:number]
# Selects candidate distractors that are semantically relevant but not too similar to the correct answer
    def _select_semantic_candidates(
        self,
        correct_answer,
        context_sentence,
        candidate_pool,
        number
    ):
        possible = []

        for candidate in candidate_pool:
            candidate = self._clean(candidate)

            if not candidate:
                continue

            if candidate.lower() == correct_answer.lower():
                continue

            if candidate.lower() in correct_answer.lower():
                continue

            if correct_answer.lower() in candidate.lower():
                continue

            if len(candidate.split()) > 14:
                continue

            possible.append(candidate)

        possible = self._unique(possible)

        if len(possible) < 2:
            return []

        texts = [correct_answer + " " + context_sentence] + possible

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(texts)

            scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

            scored_candidates = []

            for score, candidate in zip(scores, possible):
                if 0.05 <= score <= 0.85:
                    scored_candidates.append((score, candidate))

            scored_candidates.sort(reverse=True, key=lambda item: item[0])

            return [candidate for score, candidate in scored_candidates[:number]]

        except Exception:
            random.shuffle(possible)
            return possible[:number]
# Generates distractors that are specifically designed to be plausible based on the passage and question type
    def _generate_passage_aware_distractors(
        self,
        correct_answer,
        context_sentence,
        mode,
        question_type
    ):
        lower_context = context_sentence.lower()

        distractors = []

        if "identification" in question_type.lower():
            distractors.extend([
                self._distort_named_item(correct_answer),
                "An event or idea not identified by the passage.",
                "A detail that is mentioned but not presented as the main answer."
            ])

        elif "consequence" in question_type.lower():
            distractors.extend([
                self._negate_history_statement(correct_answer),
                "The passage suggests the event had no lasting effect.",
                "The passage says the issue was unrelated to later developments."
            ])

        elif "cause" in question_type.lower() or "because" in lower_context:
            distractors.extend([
                "The passage suggests the result happened without the stated cause.",
                "The passage reverses the cause-and-effect relationship.",
                self._negate_general_statement(correct_answer)
            ])

        elif "comparison" in question_type.lower() or "while" in lower_context or "whereas" in lower_context:
            distractors.extend([
                "The passage says both ideas mean exactly the same thing.",
                "The passage reverses the difference explained in the text.",
                "The passage says the two ideas are unrelated."
            ])

        elif "chronology" in question_type.lower():
            distractors.extend([
                "The passage presents the events in the opposite order.",
                "The passage says the events happened at the same time.",
                "The passage gives no clear sequence for the events."
            ])

        elif "example" in question_type.lower():
            distractors.extend([
                "The option includes details not given as examples in the passage.",
                "The option removes the examples that support the idea.",
                "The option gives unrelated examples not supported by the text."
            ])

        elif mode == "Science":
            distractors.extend([
                self._negate_science_statement(correct_answer),
                "The passage suggests the scientific idea has no effect.",
                "The passage gives an explanation that contradicts the scientific relationship."
            ])

        elif mode == "History":
            distractors.extend([
                self._negate_history_statement(correct_answer),
                "The passage suggests the event had no historical consequence.",
                "The passage reverses the historical relationship described."
            ])

        elif mode == "Business":
            distractors.extend([
                self._negate_business_statement(correct_answer),
                "The passage suggests the business decision has no effect on customers or performance.",
                "The passage reverses the business relationship described."
            ])

        elif mode == "Novel / Literature":
            distractors.extend([
                "The passage suggests there is no character conflict, mood, or theme.",
                "The passage removes any emotional or narrative meaning.",
                "The passage is unrelated to character, setting, plot, or theme."
            ])

        else:
            distractors.extend([
                self._negate_general_statement(correct_answer),
                "The passage gives no support for this idea.",
                "The passage presents this detail as unrelated to the main topic."
            ])

        distractors = [self._clean(item) for item in distractors]
        distractors = [
            item for item in distractors
            if item and item.lower() != correct_answer.lower()
        ]

        return self._unique(distractors)
# Distorts a named item (like a person, place, or concept) to create a plausible but incorrect option
    def _distort_named_item(self, statement):
        statement = self._clean(statement)

        if "also known as" in statement.lower():
            return re.sub(
                r"also known as",
                "not known as",
                statement,
                count=1,
                flags=re.IGNORECASE
            )

        return f"The passage does not identify {statement} as the main detail."
# Negates a scientific statement by replacing key terms with their opposites or by adding negation to the main verb
    def _negate_science_statement(self, statement):
        replacements = {
            "can": "cannot",
            "helps": "does not help",
            "allows": "does not allow",
            "causes": "does not cause",
            "affects": "does not affect",
            "increases": "decreases",
            "decreases": "increases",
            "is": "is not",
            "are": "are not"
        }

        return self._replace_first_match(statement, replacements)
# Negates a historical statement by replacing key terms with their opposites
    def _negate_history_statement(self, statement):
        replacements = {
            "continued": "stopped",
            "influenced": "had no influence on",
            "influence": "have no influence on",
            "caused": "did not cause",
            "led to": "did not lead to",
            "remained": "did not remain",
            "changed": "did not change",
            "was": "was not",
            "were": "were not",
            "is": "is not"
        }

        return self._replace_first_match(statement, replacements)
# Negates a business statement by replacing key terms with their opposites 
    def _negate_business_statement(self, statement):
        replacements = {
            "increase": "decrease",
            "increases": "decreases",
            "improve": "weaken",
            "improves": "weakens",
            "reduce": "increase",
            "reduces": "increases",
            "helps": "does not help",
            "can": "cannot",
            "is": "is not",
            "are": "are not"
        }

        return self._replace_first_match(statement, replacements)
# Negates a general statement by replacing key terms with their opposites 
    def _negate_general_statement(self, statement):
        replacements = {
            "can": "cannot",
            "helps": "does not help",
            "shows": "does not show",
            "suggests": "does not suggest",
            "supports": "does not support",
            "is": "is not",
            "are": "are not"
        }

        return self._replace_first_match(statement, replacements)
# function to replace the first occurrence of a key term in the statement with its opposite based on the provided replacements dictionary
    def _replace_first_match(self, statement, replacements):
        statement = self._clean(statement)

        for old, new in replacements.items():
            pattern = r"\b" + re.escape(old) + r"\b"

            if re.search(pattern, statement, flags=re.IGNORECASE):
                return re.sub(
                    pattern,
                    new,
                    statement,
                    count=1,
                    flags=re.IGNORECASE
                )

        return f"The passage does not support the idea that {statement}"
# Cleans the input text by removing extra whitespace, punctuation, and ensuring it's a clean string
    def _clean(self, text):
        text = str(text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        text = text.strip(".,;:!?")
        return text
# Removes duplicate items from a list 
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