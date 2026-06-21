# import required modules
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None

# class to filter out distractor candidates that are too similar
class SimilarityFilter:
    def filter_distractors(self, correct, candidates, limit=8):
        candidates = self._unique([
            self._clean(candidate)
            for candidate in candidates
            if candidate and candidate.lower().strip() != correct.lower().strip()
        ])

        candidates = [
            candidate
            for candidate in candidates
            if not self._is_obviously_bad(candidate)
        ]

        if len(candidates) <= limit:
            return candidates

        if TfidfVectorizer is None or cosine_similarity is None:
            return candidates[:limit]

        documents = [correct] + candidates

        try:
            matrix = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2)
            ).fit_transform(documents)

            scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        except ValueError:
            return candidates[:limit]

        scored = []

        for candidate, score in zip(candidates, scores):
            if 0.05 <= score <= 0.90:
                distance_from_target = abs(0.40 - score)
                scored.append((distance_from_target, candidate))

        scored.sort(key=lambda item: item[0])

        selected = [candidate for _, candidate in scored[:limit]]

        if len(selected) < limit:
            for candidate in candidates:
                if candidate not in selected:
                    selected.append(candidate)

                if len(selected) == limit:
                    break

        return selected[:limit]
# function to check if a candidate distractor contains phrases that indicate it is not a good choice
    def _is_obviously_bad(self, text):
        lower = text.lower()

        bad_phrases = [
            "no connection",
            "unrelated",
            "no support",
            "gives no support",
            "the passage rejects",
            "has no importance",
            "does not exist",
            "only because of one single event"
        ]

        return any(phrase in lower for phrase in bad_phrases)
# function to clean a candidate distractor by removing extra whitespace and punctuation
    def _clean(self, text):
        text = re.sub(r"\s+", " ", str(text))
        text = text.strip()
        text = text.strip(".,;:!?")
        return text
# function to ensure that the list of candidate distractors is unique, ignoring case and extra whitespace
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