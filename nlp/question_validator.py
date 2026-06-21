
# class to validate the structure and content of a question dictionary
class QuestionValidator:
    def validate(self, question):
        if not isinstance(question, dict):
            return False

        required_keys = [
            "question",
            "context",
            "options",
            "answer",
            "type",
            "mode",
            "explanation"
        ]

        for key in required_keys:
            if key not in question:
                return False

        options = question["options"]

        if not isinstance(options, list):
            return False

        if len(options) not in [2, 4]:
            return False

        cleaned_options = [
            option.lower().strip()
            for option in options
        ]

        if len(set(cleaned_options)) != len(cleaned_options):
            return False

        answer = question["answer"]

        if not isinstance(answer, int):
            return False

        if answer < 0 or answer >= len(options):
            return False

        if len(options) == 2:
            return self._validate_boolean(question)

        return self._validate_multiple_choice(question)
# For boolean questions, checks that the options are "true" and "false" in some form
    def _validate_boolean(self, question):
        options = [
            option.lower().strip()
            for option in question["options"]
        ]

        return options == ["true", "false"]
# function to validate multiple choice questions
    def _validate_multiple_choice(self, question):
        question_type = question["type"].lower()
        options = question["options"]

        full_statement_types = [
            "inference",
            "cause",
            "effect",
            "consequence",
            "comparison",
            "application",
            "literary"
        ]

        requires_full_statements = any(
            item in question_type
            for item in full_statement_types
        )

        if requires_full_statements:
            for option in options:
                if len(option.split()) < 5:
                    return False

        weak_options = [
            "not supported by the passage",
            "the passage",
            "the text",
            "the article"
        ]

        obvious_wrong_phrases = [
            "no connection",
            "unrelated",
            "no support",
            "gives no support",
            "the passage rejects",
            "only because of one single event",
            "has no importance",
            "has no effect",
            "does not exist"
        ]

        for option in options:
            lower = option.lower().strip()

            if lower in weak_options:
                return False

            if any(phrase in lower for phrase in obvious_wrong_phrases):
                return False

        word_lengths = [
            len(option.split())
            for option in options
        ]

        if max(word_lengths) - min(word_lengths) > 18:
            return False

        return True