# import required modules
import random
import re
# import NLP components for question generation
from nlp.text_processor import TextProcessor
from nlp.sentence_ranker import SentenceRanker
from nlp.question_patterns import QuestionPatternDetector
from nlp.answer_builder import AnswerBuilder
from nlp.distractor_builder import DistractorBuilder
from nlp.question_validator import QuestionValidator
from nlp.entity_bank import EntityBankBuilder

# Generates quiz questions from  a given text
class QuestionGenerator:
    def __init__(self):
        self.processor = TextProcessor()
        self.nlp = self.processor.nlp

        self.sentence_ranker = SentenceRanker(self.nlp)
        self.pattern_detector = QuestionPatternDetector(self.nlp)
        self.answer_builder = AnswerBuilder(self.pattern_detector)
        self.distractor_builder = DistractorBuilder()
        self.validator = QuestionValidator()
        self.entity_bank_builder = EntityBankBuilder(self.nlp)
# Main function that cleans text,ranks sentences and generates questions 
    def generate_questions(self, text, number_of_questions=10, mode="General / Article"):
        clean_text = self.processor.clean_text(text)

        entity_bank = self.entity_bank_builder.build(clean_text)

        ranked_sentences = self.sentence_ranker.rank_sentences(
            clean_text,
            limit=number_of_questions * 10
        )

        questions = []
        used_sentences = set()
        used_question_texts = set()
# Builds questions from best ranked sentences
        for index, sentence in enumerate(ranked_sentences):
            if len(questions) >= number_of_questions:
                break

            sentence = self._clean_sentence(sentence)

            if sentence.lower() in used_sentences:
                continue

            question = self._create_question_from_sentence(
                sentence=sentence,
                mode=mode,
                index=index,
                entity_bank=entity_bank
            )

            if not question:
                continue

            question_key = question["question"].lower().strip()

            if question_key in used_question_texts:
                continue

            if not self.validator.validate(question):
                continue

            questions.append(question)
            used_sentences.add(sentence.lower())
            used_question_texts.add(question_key)

        return questions[:number_of_questions]
# Creates either a boolean or multiple choice question from a sentence 
    def _create_question_from_sentence(self, sentence, mode, index, entity_bank):
        if index % 5 == 0:
            boolean_question = self._build_boolean_question(sentence, mode)

            if boolean_question and self.validator.validate(boolean_question):
                return boolean_question

        pattern_type = self.pattern_detector.detect_pattern(sentence, mode)

        answer_data = self.answer_builder.build(
            sentence=sentence,
            mode=mode,
            pattern_type=pattern_type
        )
# Uses inference as a backup if no xlear pattern found 
        if not answer_data:
            answer_data = self.answer_builder.build(
                sentence=sentence,
                mode=mode,
                pattern_type="inference"
            )

        if not answer_data:
            return None

        correct_answer = answer_data["correct"]

        meta = answer_data["meta"]
        meta["question"] = answer_data["question"]

        distractors = self.distractor_builder.build(
            correct=correct_answer,
            sentence=sentence,
            mode=mode,
            pattern=answer_data["pattern"],
            meta=meta,
            entity_bank=entity_bank
        )

        if len(distractors) < 3:
            return None

        options, correct_index = self._make_options(correct_answer, distractors)

        return {
            "question": answer_data["question"],
            "context": sentence,
            "safe_context": "Context hidden until answer is submitted.",
            "options": options,
            "answer": correct_index,
            "type": answer_data["question_type"],
            "mode": mode,
            "explanation": answer_data["explanation"]
        }
# Builds a boolean question by either negating the original sentence
    def _build_boolean_question(self, sentence, mode):
        true_statement = self._make_full_statement(sentence)

        make_false = random.choice([True, False])

        if make_false:
            false_statement = self.distractor_builder._negate_statement(true_statement)

            if false_statement.lower() != true_statement.lower():
                return {
                    "question": f"True or False: {false_statement}",
                    "context": sentence,
                    "safe_context": "Context hidden until answer is submitted.",
                    "options": ["True", "False"],
                    "answer": 1,
                    "type": self._mode_type(mode, "Boolean"),
                    "mode": mode,
                    "explanation": (
                        "The statement is false because it changes an important idea from the passage."
                    )
                }

        return {
            "question": f"True or False: {true_statement}",
            "context": sentence,
            "safe_context": "Context hidden until answer is submitted.",
            "options": ["True", "False"],
            "answer": 0,
            "type": self._mode_type(mode, "Boolean"),
            "mode": mode,
            "explanation": (
                "The statement is true because it matches the information given in the passage."
            )
        }
# Creates the options for a multiple choice question
    def _make_options(self, correct_answer, distractors):
        correct_answer = self._make_full_statement(correct_answer)

        cleaned_distractors = []

        for distractor in distractors:
            distractor = self._make_full_statement(distractor)

            if distractor.lower() == correct_answer.lower():
                continue

            cleaned_distractors.append(distractor)

        options = cleaned_distractors[:3] + [correct_answer]
        random.shuffle(options)

        correct_index = options.index(correct_answer)

        return options, correct_index
# turns text into a complete sentence
    def _make_full_statement(self, text):
        text = self._clean_sentence(text)
        text = text.strip(".,;:!?")

        if not text:
            return text

        text = text[0].upper() + text[1:]

        if not text.endswith("."):
            text += "."

        return text
# removes extra whitespace and ensures the sentence is a clean string
    def _clean_sentence(self, sentence):
        sentence = re.sub(r"\s+", " ", str(sentence))
        return sentence.strip()
# Labels question types based on the mode selected
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