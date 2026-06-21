# import required modules
import re

from nlp.wordnet_tools import WordNetHelper
from nlp.similarity_filter import SimilarityFilter
from nlp.option_normalizer import OptionNormalizer

# class to build distractor options for multiple-choice questions by generating candidates based on entity swapping, keyword variations, and question pattern
class DistractorBuilder:
    def __init__(self):
        self.wordnet = WordNetHelper()
        self.similarity_filter = SimilarityFilter()
        self.normalizer = OptionNormalizer()
# main function to build distractor options by generating candidates from various methods and filtering them based on similarity to the correct answer, then normalizing the final options
    def build(self, correct, sentence, mode, pattern, meta, entity_bank=None):
        entity_bank = entity_bank or {}

        correct = self._clean(correct)
        sentence = self._clean(sentence)

        candidates = []

        candidates.extend(self._entity_swap_distractors(correct, entity_bank))
        candidates.extend(self._keyword_swap_distractors(correct))
        candidates.extend(self._pattern_distractors(correct, sentence, mode, pattern, meta))
        candidates.extend(self._mode_fallbacks(mode, pattern, meta))

        candidates = self._unique([
            candidate
            for candidate in candidates
            if candidate and candidate.lower().strip() != correct.lower().strip()
        ])

        candidates = self.similarity_filter.filter_distractors(
            correct=correct,
            candidates=candidates,
            limit=8
        )

        question_text = meta.get("question", "")

        distractors = self.normalizer.normalize(
            question=question_text,
            correct=correct,
            distractors=candidates,
            limit=3
        )

        if len(distractors) < 3:
            extra = self.normalizer.normalize(
                question=question_text,
                correct=correct,
                distractors=self._mode_fallbacks(mode, pattern, meta),
                limit=3
            )

            for item in extra:
                if item.lower() not in [d.lower() for d in distractors]:
                    distractors.append(item)

                if len(distractors) == 3:
                    break

        return distractors[:3]
# function to generate distractor candidates by swapping named entities in the correct answer with other entities 
    def _entity_swap_distractors(self, correct, entity_bank):
        candidates = []

        labels = [
            "PERSON",
            "DATE",
            "PLACE",
            "ORG",
            "GROUP",
            "EVENT"
        ]

        for label in labels:
            entities = entity_bank.get(label, [])

            for entity in entities:
                if not self._contains_word(correct, entity):
                    continue

                for replacement in entities:
                    if replacement.lower() == entity.lower():
                        continue

                    candidate = self._replace_once(correct, entity, replacement)
                    candidates.append(candidate)

        return candidates
# function to generate distractor candidates by finding variations of keywords in the correct answer using WordNet
    def _keyword_swap_distractors(self, correct):
        candidates = []

        candidates.extend(self.wordnet.phrase_variations(correct))
        candidates.extend(self.wordnet.word_variations(correct))

        return candidates
# function to generate distractor candidates based on the question pattern and subject area by calling specific methods for each pattern type
    def _pattern_distractors(self, correct, sentence, mode, pattern, meta):
        if pattern == "definition":
            return self._definition_distractors(correct, sentence, mode, meta)

        if pattern == "examples":
            return self._example_distractors(correct, sentence, mode, meta)

        if pattern == "application_example":
            return self._application_distractors(correct, sentence, mode, meta)

        if pattern == "comparison":
            return self._comparison_distractors(correct, sentence, mode, meta)

        if pattern == "cause_effect":
            return self._cause_effect_distractors(correct, sentence, mode, meta)

        if pattern == "why_important":
            return self._importance_distractors(correct, sentence, mode, meta)

        if pattern == "consequence":
            return self._consequence_distractors(correct, sentence, mode, meta)

        if pattern == "chronology":
            return self._chronology_distractors(correct, sentence, mode, meta)

        if pattern == "literary":
            return self._literary_distractors(correct, sentence, mode, meta)

        return self._inference_distractors(correct, sentence, mode, meta)
# function to generate distractor candidates for definition questions 
    def _definition_distractors(self, correct, sentence, mode, meta):
        subject = self._clean(meta.get("subject", "the concept"))
        text = f"{subject} {correct} {sentence}".lower()

        concept_bank = {
            "motion": [
                "The distance an object travels without considering time",
                "The energy stored in an object because of its position",
                "The force that keeps an object from changing position"
            ],
            "reference point": [
                "The rate at which velocity changes over time",
                "The energy an object has because it is moving",
                "The direction in which an object travels"
            ],
            "speed": [
                "The rate at which velocity changes with time",
                "Motion that includes both distance and direction",
                "The energy an object has because it is moving"
            ],
            "velocity": [
                "The distance travelled per unit time without direction",
                "The stored energy an object has before it moves",
                "The force that moves an object through a distance"
            ],
            "acceleration": [
                "The total distance covered by an object per unit time",
                "The change in position of an object over time",
                "The energy possessed by a moving object"
            ],
            "kinetic energy": [
                "Energy stored because of position or condition",
                "Energy possessed by an object before it begins moving",
                "Energy produced only by heat, light, or electricity"
            ],
            "potential energy": [
                "Energy possessed because an object is already moving",
                "Energy that disappears when an object is lifted",
                "Energy caused only by speed and direction"
            ],
            "entrepreneurship": [
                "The process of working inside an existing business without taking risk",
                "The activity of selling products without organizing a business",
                "The process of advertising products after business failure"
            ],
            "market research": [
                "A written document that explains business goals and finances",
                "Money used to start, operate, and grow a business",
                "The promotion of products through branding and advertising"
            ],
            "business plan": [
                "The process of gathering information about customers and demand",
                "Money used by entrepreneurs to pay for business activities",
                "The method used to attract customers through promotion"
            ],
            "capital": [
                "The customers a business hopes to sell products to",
                "The written document that explains how a business operates",
                "The process of studying competitors, prices, and demand"
            ],
            "ancient civilizations": [
                "Small groups that moved constantly without permanent settlements",
                "Modern countries that developed only after industrial technology",
                "Communities with no organized government, trade, writing, or culture"
            ],
            "indirect rule": [
                "A system where colonial officials replaced all traditional rulers",
                "A system where local people governed without British supervision",
                "A system created after independence to replace colonial administration"
            ]
        }

        for key, options in concept_bank.items():
            if key in text:
                return options

        return self._mode_fallbacks(mode, "definition", meta)
# function to generate distractor candidates for example questions 
    def _example_distractors(self, correct, sentence, mode, meta):
        concept = self._clean(meta.get("concept", "the idea"))

        if mode == "Science":
            return [
                f"The examples involve the same topic but apply a different scientific principle from {concept}",
                f"The examples describe physical objects but do not show the exact concept of {concept}",
                f"The examples use related scientific details but connect them to the wrong process"
            ]

        if mode == "Business":
            return [
                f"The examples describe business activity but focus more on selling than {concept}",
                f"The examples are connected to business but apply to a different decision",
                f"The examples show a business situation but not the specific idea of {concept}"
            ]

        if mode == "History":
            return [
                f"The examples describe related historical details but support a different idea from {concept}",
                f"The examples belong to the same broad topic but refer to another period or development",
                f"The examples show historical background but not the exact point about {concept}"
            ]

        if mode == "Novel / Literature":
            return [
                f"The examples describe the story but focus more on setting than {concept}",
                f"The examples are connected to the passage but support a different literary idea",
                f"The examples show a story detail but not the specific idea of {concept}"
            ]

        return self._mode_fallbacks(mode, "examples", meta)
# function to generate distractor candidates for application questions
    def _application_distractors(self, correct, sentence, mode, meta):
        text = f"{correct} {sentence}".lower()

        if mode == "Science":
            if "potential energy" in text:
                return [
                    "A raised object has kinetic energy because gravity is acting on it",
                    "A raised object has chemical energy because it may later move",
                    "A raised object has no mechanical energy until it starts falling"
                ]

            if "kinetic energy" in text:
                return [
                    "A moving object stores potential energy because it changes position",
                    "A moving object has no energy unless a force keeps pushing it",
                    "A moving object has chemical energy because it is travelling"
                ]

            if "velocity" in text:
                return [
                    "An object has velocity when only its speed is known",
                    "An object has velocity when its distance is known but direction is missing",
                    "An object has velocity only when it is slowing down"
                ]

        if mode == "Business":
            return [
                "The example describes a business opportunity but ignores whether customers need it",
                "The example focuses on promotion before checking demand, cost, or competition",
                "The example shows business activity but applies the wrong stage of planning"
            ]

        if mode == "History":
            return [
                "The example uses a correct historical topic but gives it the wrong significance",
                "The example describes a related event but places it in the wrong period",
                "The example connects to the passage but changes the cause or consequence"
            ]

        if mode == "Novel / Literature":
            return [
                "The example describes what happens but misses the character's motivation",
                "The example focuses on the setting while missing the conflict",
                "The example gives a possible meaning but changes the lesson of the story"
            ]

        return self._mode_fallbacks(mode, "application", meta)
# function to generate distractor candidates for comparison questions
    def _comparison_distractors(self, correct, sentence, mode, meta):
        first_part = self._clean(meta.get("first_part", "the first idea"))
        second_part = self._clean(meta.get("second_part", "the second idea"))
        marker = meta.get("marker", "")

        if marker == "at first/later":
            return [
                f"It changed from {second_part} to {first_part}",
                f"It kept the earlier stage while the later stage remained less important",
                f"It developed through similar stages but without the major change described"
            ]

        if mode == "Science":
            return [
                f"{second_part} is presented as the cause of {first_part}",
                f"{first_part} and {second_part} describe the same scientific process",
                f"{first_part} is treated as a later result of {second_part}"
            ]

        if mode == "Business":
            return [
                f"{second_part} is presented as the business cause of {first_part}",
                f"{first_part} and {second_part} are treated as the same business decision",
                f"{first_part} is shown as useful only after {second_part} has failed"
            ]

        if mode == "History":
            return [
                f"{second_part} is presented as the earlier historical development",
                f"{first_part} and {second_part} are treated as the same historical process",
                f"{first_part} is described as the result rather than the contrast to {second_part}"
            ]

        if mode == "Novel / Literature":
            return [
                f"{second_part} is presented as the main reason for {first_part}",
                f"{first_part} and {second_part} reveal the same mood or character idea",
                f"{first_part} is treated as the outcome of {second_part} rather than a contrast"
            ]

        return self._mode_fallbacks(mode, "comparison", meta)
# function to generate distractor candidates for cause and effect questions
    def _cause_effect_distractors(self, correct, sentence, mode, meta):
        cause = self._clean(meta.get("cause", "the cause"))
        effect = self._clean(meta.get("effect", "the effect"))

        return [
            f"{effect} is presented as the cause of {cause}",
            f"{cause} is connected to the topic but produces a different result from {effect}",
            f"A related factor is made more important than {cause} in explaining {effect}"
        ]
# function to generate distractor candidates for importance questions
    def _importance_distractors(self, correct, sentence, mode, meta):
        if mode == "Science":
            return [
                "It explains one example but does not connect the concept to the wider scientific process",
                "It focuses mainly on observation while reducing the role of force, motion, or energy",
                "It describes the concept as a single event rather than part of a larger physical relationship"
            ]

        if mode == "Business":
            return [
                "It focuses mainly on making profit while giving less attention to customers and planning",
                "It explains business growth but gives less attention to risk, finance, and market demand",
                "It describes business activity without fully connecting it to long-term success"
            ]

        if mode == "History":
            return [
                "It focuses mainly on one period while giving less attention to wider historical development",
                "It describes important events but does not fully connect them to later political change",
                "It explains historical background but gives less attention to long-term consequences"
            ]

        if mode == "Novel / Literature":
            return [
                "It explains the event but gives less attention to the character's growth or decision",
                "It focuses mainly on the setting while giving less attention to theme and conflict",
                "It describes what happens but gives less attention to the lesson developed by the story"
            ]

        return [
            "It explains one part of the topic but gives a narrower meaning than the passage",
            "It focuses on background details more than the main point being developed",
            "It describes the topic generally without fully explaining its wider importance"
        ]
# function to generate distractor candidates for consequence questions
    def _consequence_distractors(self, correct, sentence, mode, meta):
        if mode == "Science":
            return [
                "The result reverses the energy change described in the passage",
                "The result describes a related physical process but not the one caused here",
                "The result keeps the same scientific terms but changes their relationship"
            ]

        if mode == "Business":
            return [
                "The result affects business growth but ignores the role of planning and finance",
                "The result improves sales while making customer demand less important",
                "The result changes the business outcome by confusing growth with stability"
            ]

        if mode == "History":
            return [
                "The result describes a related historical outcome but changes its significance",
                "The result focuses on a short-term effect rather than the main consequence",
                "The result uses the correct historical topic but gives the wrong outcome"
            ]

        if mode == "Novel / Literature":
            return [
                "The result changes the story outcome by missing the character's decision",
                "The result focuses on the setting rather than the conflict's consequence",
                "The result gives a possible event but not the one developed by the passage"
            ]

        return self._mode_fallbacks(mode, "consequence", meta)
# function to generate distractor candidates for chronology 
    def _chronology_distractors(self, correct, sentence, mode, meta):
        if mode == "Science":
            return [
                "The process begins with the final energy change before the object moves",
                "The stages happen at the same time rather than in the order described",
                "The sequence reverses the relationship between movement and energy change"
            ]

        if mode == "Business":
            return [
                "The business expands before identifying customers, costs, or demand",
                "The business attracts investors before developing its goals or plan",
                "The business grows first and later checks whether customers need the product"
            ]

        if mode == "History":
            return [
                "The later event is placed before the earlier historical development",
                "The events are treated as happening at the same time instead of in sequence",
                "The cause is placed after the result in the historical order"
            ]

        if mode == "Novel / Literature":
            return [
                "The resolution is placed before the main conflict is discovered",
                "The character's lesson appears before the problem that teaches it",
                "The events are arranged as if the outcome happened before the decision"
            ]

        return self._mode_fallbacks(mode, "chronology", meta)
# function to generate distractor candidates for literary interpretation questions
    def _literary_distractors(self, correct, sentence, mode, meta):
        text = f"{correct} {sentence}".lower()

        if "mood" in text:
            return [
                "The scene creates a relaxed mood by showing that the problem is already solved",
                "The scene creates a humorous mood by making the conflict seem unimportant",
                "The scene creates a peaceful mood by removing tension from the situation"
            ]

        if "character" in text or "courage" in text:
            return [
                "The character mainly shows curiosity without responsibility or growth",
                "The character shows that fear disappears before courage is needed",
                "The character's action mainly proves that others should solve the problem"
            ]

        if "conflict" in text:
            return [
                "The conflict is mainly between two ideas rather than actions in the story",
                "The conflict is resolved before the character makes an important choice",
                "The conflict affects the setting but not the character's decisions"
            ]

        return [
            "The passage mainly develops setting without affecting character or conflict",
            "The passage presents the event as ordinary rather than meaningful",
            "The passage focuses on action but gives little meaning to the character's choice"
        ]

    def _inference_distractors(self, correct, sentence, mode, meta):
        return self._mode_fallbacks(mode, "inference", meta)

    def _mode_fallbacks(self, mode, pattern, meta):
        if mode == "Science":
            return [
                "The option uses a related scientific term but applies it to the wrong process",
                "The option describes part of the topic but reverses the scientific relationship",
                "The option sounds scientific but does not match the process in the passage"
            ]

        if mode == "Business":
            return [
                "The option uses a related business idea but applies it at the wrong stage",
                "The option focuses on profit while reducing the role of planning and customers",
                "The option describes business growth but changes the decision-making logic"
            ]

        if mode == "History":
            return [
                "The option describes a related historical issue but gives it the wrong role",
                "The option focuses on one period while missing the wider historical development",
                "The option uses a correct topic but changes the cause, effect, or sequence"
            ]

        if mode == "Novel / Literature":
            return [
                "The option describes the event but misses the character's motivation",
                "The option focuses on the setting while ignoring the conflict or theme",
                "The option gives a possible theme but changes the lesson of the story"
            ]

        return [
            "The option is related to the passage but explains a different idea",
            "The option uses the same topic but changes the relationship between ideas",
            "The option gives a narrower meaning than the one supported by the passage"
        ]
# helper function to check if a word is present in a text as a separate word, ignoring case and punctuation
    def _contains_word(self, text, word):
        pattern = rf"\b{re.escape(word)}\b"
        return re.search(pattern, text, flags=re.IGNORECASE) is not None

    def _replace_once(self, text, old, new):
        return re.sub(
            rf"\b{re.escape(old)}\b",
            new,
            text,
            count=1,
            flags=re.IGNORECASE
        )

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
# function to remove duplicate distractor candidates while ignoring case and extra spaces
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
# helper function to negate a statement by replacing key words with their opposites
    def _negate_statement(self, statement):
        replacements = {
            "can": "cannot",
            "helps": "does not help",
            "allows": "does not allow",
            "causes": "does not cause",
            "caused": "did not cause",
            "leads to": "does not lead to",
            "led to": "did not lead to",
            "affects": "does not affect",
            "influences": "does not influence",
            "is": "is not",
            "are": "are not",
            "was": "was not",
            "were": "were not",
            "has": "does not have",
            "have": "do not have"
        }

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

        return f"The statement changes the meaning of this idea: {statement}"