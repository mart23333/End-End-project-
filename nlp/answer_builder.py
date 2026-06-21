#import required modules
import re

# class to build answer data for quiz questions based on detected patterns in sentences, including identification, definition, examples, comparison, cause-effect, chronology, literary analysis, and inference patterns
class AnswerBuilder:
    def __init__(self, pattern_detector):
        self.pattern_detector = pattern_detector
# main function to build answer data based on the detected pattern type in the sentence
    def build(self, sentence, mode, pattern_type):
        if pattern_type == "identification":
            return self._build_identification(sentence, mode)

        if pattern_type == "definition":
            return self._build_definition(sentence, mode)

        if pattern_type == "examples":
            return self._build_examples(sentence, mode)

        if pattern_type == "comparison":
            return self._build_comparison(sentence, mode)

        if pattern_type == "cause_effect":
            return self._build_cause_effect(sentence, mode)

        if pattern_type == "chronology":
            return self._build_chronology(sentence, mode)

        if pattern_type == "literary":
            return self._build_literary(sentence, mode)

        return self._build_inference(sentence, mode)

    
    # function to build answer data for identification pattern, extracting subject area, main name, and alternate name from the sentence, and constructing a correct answer statement based on the identified information
   
    def _build_identification(self, sentence, mode):
        subject_area, main_name, alternate_name = (
            self.pattern_detector.extract_identification_parts(sentence)
        )

        if not main_name or not alternate_name:
            return None

        correct = f"{main_name}, also known as {alternate_name}"

        return {
            "question": self._identification_question(mode),
            "correct": self._make_full_statement(correct),
            "question_type": self._mode_type(mode, "Identification"),
            "pattern": "identification",
            "meta": {
                "subject_area": subject_area,
                "main_name": main_name,
                "alternate_name": alternate_name
            },
            "explanation": (
                f"The passage identifies {main_name} and gives its alternate name as {alternate_name}."
            )
        }

     
    # function to build answer data for definition pattern, extracting subject and explanation from the sentence, and constructing a correct answer statement based on the explanation provided in the passage
    
    def _build_definition(self, sentence, mode):
        subject, explanation = self.pattern_detector.extract_definition_parts(sentence)

        if not subject or not explanation:
            return None

        subject = self._clean(subject)
        explanation = self._clean(explanation)

        if len(subject.split()) > 10:
            return None

        if len(explanation.split()) < 3:
            return None

        correct = self._make_full_statement(explanation)

        return {
            "question": self._definition_question(mode, subject),
            "correct": correct,
            "question_type": self._mode_type(mode, "Concept Understanding"),
            "pattern": "definition",
            "meta": {
                "subject": subject,
                "explanation": explanation
            },
            "explanation": (
                f"The passage explains '{subject}'. The correct answer matches that explanation."
            )
        }

    
    # Builds answer data for example-based questions
    def _build_examples(self, sentence, mode):
        lower = sentence.lower().strip()

        if lower.startswith("for example") or lower.startswith("for instance"):
            cleaned_sentence = re.sub(
                r"^(for example|for instance),?\s*",
                "",
                sentence,
                flags=re.IGNORECASE
            ).strip()

            if len(cleaned_sentence.split()) < 6:
                return None

            return {
                "question": self._application_question(mode),
                "correct": self._make_full_statement(cleaned_sentence),
                "question_type": self._mode_type(mode, "Application"),
                "pattern": "application_example",
                "meta": {
                    "example_sentence": cleaned_sentence
                },
                "explanation": (
                    "The correct answer applies the idea using the example given in the passage."
                )
            }

        concept, examples = self.pattern_detector.extract_example_parts(sentence)

        if not concept or not examples:
            return None

        concept = self._clean(concept)
        examples = self._clean(examples)

        correct = (
            f"The passage gives {examples} as examples or evidence related to {concept}"
        )

        return {
            "question": self._examples_question(mode, concept),
            "correct": self._make_full_statement(correct),
            "question_type": self._mode_type(mode, "Examples and Evidence"),
            "pattern": "examples",
            "meta": {
                "concept": concept,
                "examples": examples
            },
            "explanation": f"The passage gives examples or evidence related to '{concept}'."
        }

    
    # function to build answer data for comparison pattern

    def _build_comparison(self, sentence, mode):
        first_part, second_part, marker = (
            self.pattern_detector.extract_comparison_parts(sentence)
        )

        if not first_part or not second_part:
            return None

        first_part = self._shorten_phrase(first_part, 16)
        second_part = self._shorten_phrase(second_part, 16)

        if marker == "main difference":
            question = f"How does the passage compare {self._extract_main_terms(sentence)}?"
            correct = f"{first_part}, while {second_part}"

        elif marker == "at first/later":
            question = self._change_over_time_question(mode)
            correct = f"It changed from {first_part} to {second_part}"

        else:
            question = self._comparison_question(mode)
            correct = f"The passage contrasts {first_part} with {second_part}"

        return {
            "question": question,
            "correct": self._make_full_statement(correct),
            "question_type": self._mode_type(mode, "Comparison"),
            "pattern": "comparison",
            "meta": {
                "first_part": first_part,
                "second_part": second_part,
                "marker": marker
            },
            "explanation": (
                f"The sentence uses comparison language such as '{marker}' to show a relationship between two ideas."
            )
        }

    
    # function to build answer data for cause-effect pattern
   
    def _build_cause_effect(self, sentence, mode):
        lower = sentence.lower()

        if any(word in lower for word in [
            "effect",
            "effects",
            "impact",
            "influence",
            "influenced",
            "consequence",
            "consequences",
            "continued to"
        ]):
            return self._build_consequence(sentence, mode)

        cause, effect = self.pattern_detector.extract_cause_effect_parts(sentence)

        if not cause or not effect:
            return None

        cause = self._clean(cause)
        effect = self._clean(effect)

        if len(cause.split()) < 2 or len(effect.split()) < 2:
            return None

        if "important" in lower and "because" in lower:
            topic = self._extract_important_topic(sentence)
            reason = self._extract_after_phrase(sentence, "because")

            if topic and reason:
                topic = self._shorten_phrase(topic, 8)
                reason = self._shorten_phrase(reason, 24)

                correct = self._make_reason_answer(reason)

                return {
                    "question": self._why_important_question(mode, topic),
                    "correct": correct,
                    "question_type": self._mode_type(mode, "Cause and Effect"),
                    "pattern": "why_important",
                    "meta": {
                        "topic": topic,
                        "reason": reason
                    },
                    "explanation": (
                        "The correct answer explains why the topic is important according to the passage."
                    )
                }

        cause = self._shorten_phrase(cause, 16)
        effect = self._shorten_phrase(effect, 20)

        correct = f"{cause} leads to {effect}"

        return {
            "question": self._cause_question(mode),
            "correct": self._make_full_statement(correct),
            "question_type": self._mode_type(mode, "Cause and Effect"),
            "pattern": "cause_effect",
            "meta": {
                "cause": cause,
                "effect": effect
            },
            "explanation": (
                "The correct answer identifies the cause-and-effect relationship supported by the passage."
            )
        }
# function to build answer data for consequence pattern, extracting the consequence and constructing a correct answer statement based on the effect in the text 
    def _build_consequence(self, sentence, mode):
        clean_sentence = self._make_full_statement(
            self._shorten_phrase(sentence, 28)
        )

        return {
            "question": self._consequence_question(mode),
            "correct": clean_sentence,
            "question_type": self._mode_type(mode, "Consequence"),
            "pattern": "consequence",
            "meta": {
                "sentence": sentence
            },
            "explanation": (
                "The correct answer identifies a consequence, result, or lasting effect described in the passage."
            )
        }

    
    # function to build answer data for chronology pattern
     

    def _build_chronology(self, sentence, mode):
        dates = self.pattern_detector.extract_dates(sentence)

        if len(dates) < 2:
            return None

        correct = self._make_full_statement(
            self._shorten_phrase(sentence, 28)
        )

        return {
            "question": self._chronology_question(mode),
            "correct": correct,
            "question_type": self._mode_type(mode, "Chronology"),
            "pattern": "chronology",
            "meta": {
                "dates": dates
            },
            "explanation": (
                "The correct answer follows the time order or sequence suggested by the passage."
            )
        }

    
    # function to build answer data for literary analysis pattern
   
    def _build_literary(self, sentence, mode):
        lower = sentence.lower()

        if any(word in lower for word in ["said", "asked", "whispered", "shouted", "replied"]):
            question = "What might this dialogue reveal in the passage?"
            correct = (
                "It may reveal character emotion, tension, conflict, or relationship"
            )

        elif any(word in lower for word in ["dark", "silent", "empty", "storm", "cloud", "shadow"]):
            question = "What mood is most likely created by this description?"
            correct = (
                "It creates a tense, serious, quiet, or mysterious mood"
            )

        elif any(word in lower for word in ["mirror", "door", "letter", "fire", "river", "symbol"]):
            question = "What might this object or image symbolize in the story?"
            correct = (
                "It may symbolize a deeper idea such as change, conflict, loss, survival, or identity"
            )

        elif any(word in lower for word in ["learned", "lesson", "realized", "understood"]):
            question = "What lesson is most likely developed in this part of the story?"
            correct = (
                "It develops a lesson about character growth, responsibility, courage, or decision-making"
            )

        else:
            question = "What literary idea is most likely developed in this passage?"
            correct = (
                "It may develop character, conflict, mood, theme, setting, or plot"
            )

        return {
            "question": question,
            "correct": self._make_full_statement(correct),
            "question_type": self._mode_type(mode, "Literary Analysis"),
            "pattern": "literary",
            "meta": {
                "sentence": sentence
            },
            "explanation": (
                "The correct answer explains the likely literary function of the passage."
            )
        }

   
    # function to build answer data for inference pattern
    
    def _build_inference(self, sentence, mode):
        clean_sentence = self._make_full_statement(
            self._shorten_phrase(sentence, 28)
        )

        lower = clean_sentence.lower()

        if "indirect rule" in lower:
            question = "What can be inferred about indirect rule in Nigeria?"
        elif "oil" in lower and ("problem" in lower or "corruption" in lower):
            question = "What can be inferred about oil wealth in Nigeria?"
        elif "energy" in lower:
            question = "What can be inferred about energy from the passage?"
        elif "market research" in lower:
            question = "What can be inferred about market research?"
        elif "business" in lower or "entrepreneur" in lower:
            question = "What business idea is best supported by this part of the passage?"
        elif mode == "Novel / Literature":
            question = "What interpretation is best supported by this part of the story?"
        else:
            question = self._inference_question(mode)

        return {
            "question": question,
            "correct": clean_sentence,
            "question_type": self._mode_type(mode, "Inference"),
            "pattern": "inference",
            "meta": {
                "sentence": sentence
            },
            "explanation": (
                "The correct answer is the statement most strongly supported by the passage."
            )
        }

    
    # function to create a well-formed answer statement based on a reason extracted from the passage
   
    def _make_reason_answer(self, reason):
        reason = self._clean(reason)

        if not reason:
            return reason

        if reason.lower().startswith("it "):
            return self._make_full_statement(reason)

        return self._make_full_statement(f"It helps explain {reason}")
# function to turn text into a complete sentence by cleaning it, capitalizing the first letter, and ensuring it ends with a period
    def _make_full_statement(self, text):
        text = self._clean(text)

        if not text:
            return text

        text = text[0].upper() + text[1:]

        if not text.endswith("."):
            text += "."

        return text
# function to clean text 
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
# function to shorten a phrase to a maximum number of words without ending on weak connector words
    def _shorten_phrase(self, text, max_words):
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
# function to extract the part of a sentence that comes after a specific phrase, cleaning the result
    def _extract_after_phrase(self, sentence, phrase):
        pattern = rf"{re.escape(phrase)}\s+(.+)"
        match = re.search(pattern, sentence, flags=re.IGNORECASE)

        if match:
            return self._clean(match.group(1))

        return None
# function to extract the topic that is described as important in the sentence, looking for patterns that indicate importance and cleaning the result
    def _extract_important_topic(self, sentence):
        patterns = [
            r"(.+?)\s+is important\b",
            r"(.+?)\s+are important\b",
            r"(.+?)\s+was important\b",
            r"(.+?)\s+were important\b"
        ]

        for pattern in patterns:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)

            if match:
                return self._clean(match.group(1))

        return None
# function to extract the main terms being compared in a sentence that indicates a main difference, looking for a specific pattern and cleaning the results
    def _extract_main_terms(self, sentence):
        match = re.search(
            r"the main difference between\s+(.+?)\s+and\s+(.+?)\s+is that",
            sentence,
            flags=re.IGNORECASE
        )

        if match:
            first = self._clean(match.group(1))
            second = self._clean(match.group(2))
            return f"{first} and {second}"

        return "these ideas"

   
    # function to generate a question about applying the idea in the passage
   
    def _application_question(self, mode):
        if mode == "Science":
            return "Which option correctly applies the scientific idea in the passage?"

        if mode == "Business":
            return "Which option correctly applies the business idea in the passage?"

        if mode == "History":
            return "Which option correctly applies the historical idea in the passage?"

        if mode == "Novel / Literature":
            return "Which option correctly applies the literary idea in the passage?"

        return "Which option correctly applies the idea in the passage?"
# function to generate a question about why a topic is important according to the passage
    def _why_important_question(self, mode, topic):
        if mode == "Novel / Literature":
            return f"Why is {topic} important in the passage?"

        if mode == "General / Article":
            return f"Why is {topic} important according to the article?"

        return f"Why is {topic} important according to the passage?"
# function to generate a question about identifying a key detail in the passage based on the subject area or mode
    def _identification_question(self, mode):
        if mode == "History":
            return "What historical event or idea is identified in the passage?"

        if mode == "Science":
            return "What scientific concept or item is identified in the passage?"

        if mode == "Business":
            return "What business concept or item is identified in the passage?"

        if mode == "Novel / Literature":
            return "What character, object, or idea is identified in the passage?"

        return "What important detail is identified in the passage?"
# function to generate a question about understanding a concept or idea explained in the passage based on the subject area or mode
    def _definition_question(self, mode, subject):
        if mode == "Science":
            return f"According to the passage, what is {subject}?"

        if mode == "History":
            return f"What does the passage explain about {subject}?"

        if mode == "Business":
            return f"What business idea is explained by {subject}?"

        if mode == "Novel / Literature":
            return f"What does the passage suggest about {subject}?"

        return f"According to the article, what is explained about {subject}?"
# function to generate a question about identifying 
    def _examples_question(self, mode, concept):
        if mode == "Science":
            return f"Which option correctly identifies examples or evidence related to {concept}?"

        if mode == "History":
            return f"Which option correctly identifies examples or evidence related to {concept}?"

        if mode == "Business":
            return f"Which option correctly identifies business examples or evidence related to {concept}?"

        if mode == "Novel / Literature":
            return f"Which detail best supports the literary idea of {concept}?"

        return "Which option correctly identifies examples or evidence from the article?"
# function to generate a question about comparing or contrasting ideas in the passage based on the subject area or mode
    def _comparison_question(self, mode):
        if mode == "Science":
            return "How does the passage compare or contrast these scientific ideas?"

        if mode == "History":
            return "How does the passage compare or contrast these historical ideas?"

        if mode == "Business":
            return "How does the passage compare or contrast these business ideas?"

        if mode == "Novel / Literature":
            return "How does the passage contrast characters, ideas, or situations?"

        return "How does the passage compare or contrast these ideas?"
# function to generate a question about how a situation, process
    def _change_over_time_question(self, mode):
        if mode == "History":
            return "How did the situation change over time according to the passage?"

        if mode == "Science":
            return "How did the process change according to the passage?"

        if mode == "Business":
            return "How did the business situation change according to the passage?"

        if mode == "Novel / Literature":
            return "How did the situation change in the story?"

        return "How did the situation change according to the passage?"
# function to generate a question about identifying a cause-and-effect relationship in the passage based on the subject area or mode
    def _cause_question(self, mode):
        if mode == "Science":
            return "What scientific cause-and-effect relationship is explained in the passage?"

        if mode == "History":
            return "What historical cause-and-effect relationship is suggested by the passage?"

        if mode == "Business":
            return "What business cause-and-effect relationship is suggested by the passage?"

        if mode == "Novel / Literature":
            return "What relationship between actions or events is suggested in the passage?"

        return "What relationship is suggested by this part of the article?"
# function to generate a question about identifying a consequence, result
    def _consequence_question(self, mode):
        if mode == "History":
            return "What lasting consequence is described in this historical passage?"

        if mode == "Science":
            return "What effect or result is described in the science passage?"

        if mode == "Business":
            return "What business consequence is described in the passage?"

        if mode == "Novel / Literature":
            return "What consequence or effect is suggested in the passage?"

        return "What consequence or effect is described in this part of the article?"
# function to generate a question about identifying the order of events, steps
    def _chronology_question(self, mode):
        if mode == "History":
            return "Which statement best reflects the historical sequence in the passage?"

        if mode == "Science":
            return "Which statement best reflects the order of the scientific process?"

        if mode == "Business":
            return "Which statement best reflects the order of the business process?"

        if mode == "Novel / Literature":
            return "Which statement best reflects the order of events in the story?"

        return "Which statement best reflects the time relationship in the passage?"
# function to generate a question about interpreting the literary function of a passage based on the subject area or mode
    def _inference_question(self, mode):
        if mode == "Science":
            return "Which scientific conclusion is best supported by the passage?"

        if mode == "History":
            return "Which historical conclusion is best supported by the passage?"

        if mode == "Business":
            return "Which business conclusion is best supported by the passage?"

        if mode == "Novel / Literature":
            return "Which interpretation is best supported by the passage?"

        return "What can be reasonably inferred from this part of the article?"
# function to generate a question type string based on the subject area or mode and the type of question being asked
    def _mode_type(self, mode, question_type):
        if mode == "Science":
            return f"Scientific {question_type}"

        if mode == "History":
            return f"Historical {question_type}"

        if mode == "Business":
            return f"Business {question_type}"

        if mode == "Novel / Literature":
            return f"Literary {question_type}"

        return f"Article {question_type}"