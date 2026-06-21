#i,port required modules 
import re

# Detects question patterns in sentences to guide question generation
class QuestionPatternDetector:
    def __init__(self, nlp):
        self.nlp = nlp

    
    # main function to detect the pattern of a sentence
    

    def detect_pattern(self, sentence, mode):
        lower = sentence.lower()

        if self.detect_comparison(lower):
            return "comparison"

        if self.detect_examples(lower):
            return "examples"

        if self.detect_identification(lower):
            return "identification"

        if self.detect_cause_effect(lower):
            return "cause_effect"

        if self.detect_chronology(sentence):
            return "chronology"

        if self.detect_definition(lower):
            return "definition"

        if mode == "Novel / Literature" and self.detect_literary_signal(lower):
            return "literary"

        return "inference"

   
    # function to detect rules that indicate a definition pattern in the sentence
    

    def detect_definition(self, lower):
        patterns = [
            r"\bcan be defined as\b",
            r"\brefers to\b",
            r"\bmeans\b",
            r"\bis known as\b",
            r"\bis\b",
            r"\bare\b"
        ]

        return any(re.search(pattern, lower) for pattern in patterns)
# function to detect rules that indicate an identification pattern in the sentence
    def detect_identification(self, lower):
        markers = [
            "also known as",
            "known as",
            "called",
            "named"
        ]

        return any(marker in lower for marker in markers)
# function to detect rules that indicate a cause/effect pattern in the sentence
    def detect_cause_effect(self, lower):
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
            "effects",
            "impact",
            "consequence",
            "consequences",
            "continued to",
            "helps explain"
        ]

        return any(marker in lower for marker in markers)
# function to detect rules that indicate a comparison pattern in the sentence
    def detect_comparison(self, lower):
        markers = [
            "the main difference between",
            "while",
            "whereas",
            "unlike",
            "however",
            "but",
            "compared to",
            "in contrast",
            "different from",
            "difference between",
            "at first",
            "later"
        ]

        return any(marker in lower for marker in markers)
# function to detect rules that indicate an example pattern in the sentence
    def detect_examples(self, lower):
        markers = [
            "for example",
            "for instance",
            "such as",
            "including",
            "includes",
            "include",
            "examples of",
            "are examples of"
        ]

        return any(marker in lower for marker in markers)
# function to detect rules that indicate a chronology pattern in the sentence
    def detect_chronology(self, sentence):
        lower = sentence.lower()
        doc = self.nlp(sentence)

        dates = [
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ == "DATE"
        ]

        sequence_markers = [
            "first",
            "second",
            "third",
            "then",
            "eventually",
            "following",
            "previously"
        ]

        if len(dates) >= 2:
            return True

        if any(marker in lower for marker in sequence_markers):
            return True

        return False
# function to detect rules that indicate a literary pattern in the sentence
    def detect_literary_signal(self, lower):
        markers = [
            "said",
            "asked",
            "whispered",
            "shouted",
            "replied",
            "felt",
            "feared",
            "dark",
            "silent",
            "empty",
            "storm",
            "shadow",
            "mirror",
            "letter",
            "door",
            "conflict",
            "courage",
            "fear",
            "village",
            "river",
            "lesson",
            "realized",
            "learned"
        ]

        return any(marker in lower for marker in markers)

   
    # function to extract the subject and explanation from a definition sentence based on common patterns
    
    def extract_definition_parts(self, sentence):
        patterns = [
            r"(.+?)\s+can be defined as\s+(.+)",
            r"(.+?)\s+refers to\s+(.+)",
            r"(.+?)\s+means\s+(.+)",
            r"(.+?)\s+is known as\s+(.+)",
            r"(.+?)\s+is\s+(.+)",
            r"(.+?)\s+are\s+(.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)

            if match:
                subject = self.clean_answer(match.group(1))
                explanation = self.clean_answer(match.group(2))
                return subject, explanation

        return None, None

   
    # function to extract the subject, main name, and alternate name from an identification sentence based on common patterns
   
    def extract_identification_parts(self, sentence):
        patterns = [
            r"(.+?)\s+was\s+(.+?),\s+also known as\s+(.+?)(?:,|\.| which| that|$)",
            r"(.+?)\s+is\s+(.+?),\s+also known as\s+(.+?)(?:,|\.| which| that|$)",
            r"(.+?)\s+was\s+(.+?)\s+called\s+(.+?)(?:,|\.| which| that|$)",
            r"(.+?)\s+is\s+(.+?)\s+called\s+(.+?)(?:,|\.| which| that|$)",
            r"(.+?)\s+known as\s+(.+?)(?:,|\.| which| that|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)

            if not match:
                continue

            groups = match.groups()

            if len(groups) == 3:
                subject_area = self.clean_answer(groups[0])
                main_name = self.clean_answer(groups[1])
                alternate_name = self.clean_answer(groups[2])
                return subject_area, main_name, alternate_name

            if len(groups) == 2:
                subject_area = "the passage"
                main_name = self.clean_answer(groups[0])
                alternate_name = self.clean_answer(groups[1])
                return subject_area, main_name, alternate_name

        return None, None, None

    
    # function to extract the concept and examples
    

    def extract_example_parts(self, sentence):
        patterns = [
            r"for example,?\s*(.+?)\s+are\s+(?:all\s+)?examples of\s+(.+)",
            r"(.+?)\s+are\s+(?:all\s+)?examples of\s+(.+)",
            r"examples of\s+(.+?)\s+include\s+(.+)",
            r"(.+?)\s+include\s+(.+)",
            r"(.+?)\s+includes\s+(.+)",
            r"(.+?)\s+including\s+(.+)",
            r"(.+?)\s+such as\s+(.+)"
        ]

        lower = sentence.lower()

        for pattern in patterns:
            match = re.search(pattern, sentence, flags=re.IGNORECASE)

            if not match:
                continue

            part_one = self.clean_answer(match.group(1))
            part_two = self.clean_answer(match.group(2))

            if "examples of" in lower and " are " in lower:
                examples = part_one
                concept = part_two

            elif "include" in lower or "including" in lower:
                concept = part_one
                examples = part_two

            elif "such as" in lower:
                concept = part_one
                examples = part_two

            else:
                continue

            return concept, examples

        return None, None

    
    # function to extract the two sides of a comparison 
    
    def extract_comparison_parts(self, sentence):
        lower = sentence.lower()

        # Handles:
        # "The main difference between kinetic energy and potential energy is that
        # kinetic energy is energy of motion, while potential energy is stored energy."
        difference_pattern = (
            r"the main difference between\s+(.+?)\s+and\s+(.+?)\s+is that\s+(.+?),\s+while\s+(.+)"
        )

        match = re.search(difference_pattern, sentence, flags=re.IGNORECASE)

        if match:
            first_description = self.clean_answer(match.group(3))
            second_description = self.clean_answer(match.group(4))

            return (
                first_description,
                second_description,
                "main difference"
            )

        # Handles:
        # "At first..., but later..."
        # "At first..., later..."
        if "at first" in lower and "later" in lower:
            clean_sentence = sentence

            clean_sentence = re.sub(
                r"\bbut\s+later\b",
                "later",
                clean_sentence,
                flags=re.IGNORECASE
            )

            parts = re.split(r"\blater\b", clean_sentence, flags=re.IGNORECASE)

            if len(parts) >= 2:
                first_part = re.sub(
                    r"^at first,?\s*",
                    "",
                    parts[0],
                    flags=re.IGNORECASE
                ).strip()

                second_part = parts[1].strip()

                return (
                    self.clean_answer(first_part),
                    self.clean_answer(second_part),
                    "at first/later"
                )

        # Handles normal contrast:
        # "Speed is..., but velocity is..."
        # "Speed tells..., while velocity includes..."
        markers = [
            "while",
            "whereas",
            "unlike",
            "however",
            "but",
            "compared to",
            "in contrast"
        ]

        for marker in markers:
            if marker in lower:
                parts = re.split(
                    rf"\b{re.escape(marker)}\b",
                    sentence,
                    flags=re.IGNORECASE
                )

                if len(parts) >= 2:
                    first_part = self.clean_answer(parts[0])
                    second_part = self.clean_answer(parts[1])

                    return first_part, second_part, marker

        return None, None, None

    
    # function to extract the cause and effect 
   
    def extract_cause_effect_parts(self, sentence):
        lower = sentence.lower()

        if "because" in lower:
            parts = re.split(r"\bbecause\b", sentence, flags=re.IGNORECASE)

            if len(parts) >= 2:
                effect = self.clean_answer(parts[0])
                cause = self.clean_answer(parts[1])
                return cause, effect

        if "due to" in lower:
            parts = re.split(r"\bdue to\b", sentence, flags=re.IGNORECASE)

            if len(parts) >= 2:
                effect = self.clean_answer(parts[0])
                cause = self.clean_answer(parts[1])
                return cause, effect

        markers = [
            "led to",
            "leads to",
            "caused",
            "causes",
            "resulted in",
            "contributed to",
            "helps",
            "allows",
            "affects",
            "influences"
        ]

        for marker in markers:
            if marker in lower:
                parts = re.split(
                    rf"\b{re.escape(marker)}\b",
                    sentence,
                    flags=re.IGNORECASE
                )

                if len(parts) >= 2:
                    cause = self.clean_answer(parts[0])
                    effect = self.clean_answer(parts[1])
                    return cause, effect

        return None, None

   
    # function to extract dates from a sentence using spaCy's
    
    def extract_dates(self, sentence):
        doc = self.nlp(sentence)

        return [
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ == "DATE"
        ]

   
    # function to clean and standardize answer text by removing extra whitespace and punctuation
    
    def clean_answer(self, text):
        text = re.sub(r"\s+", " ", str(text))
        text = text.strip()
        text = text.strip(".,;:!?")
        return text