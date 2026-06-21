#Import required libraries
import random

# class to generate distractor options for multiple choice questions
class DistractorGenerator:
    def __init__(self):
        pass

    def generate_distractors(self, correct_answer, keywords, number=3):
        distractors = []

        for keyword in keywords:
            if keyword.lower() != correct_answer.lower():
                if keyword not in distractors:
                    distractors.append(keyword)

        random.shuffle(distractors)

        selected = distractors[:number]

        while len(selected) < number:
            fallback = self._fallback_distractor(correct_answer)

            if fallback not in selected and fallback.lower() != correct_answer.lower():
                selected.append(fallback)

        return selected
# helper function to provide generic distractor candidates when specific keywords are not available
    def _fallback_distractor(self, correct_answer):
        generic_distractors = [
            "A minor detail that is not central to the text",
            "An unrelated event with little connection to the passage",
            "A simple factual point rather than a deeper explanation",
            "A temporary situation with no long-term importance",
            "An unsupported interpretation of the passage",
            "A conclusion based only on personal opinion",
            "A weak explanation that ignores the main idea"
        ]

        return random.choice(generic_distractors)