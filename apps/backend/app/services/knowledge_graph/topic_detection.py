import re
import uuid

from app.models.curriculum import Topic


class TopicDetector:
    def detect_topic_id(self, text: str, topics: list[Topic]) -> uuid.UUID | None:
        haystack = text.lower()
        scored: list[tuple[int, Topic]] = []
        for topic in topics:
            terms = [topic.title, topic.code, *topic.misconception_tags]
            score = sum(len(re.findall(re.escape(term.lower()), haystack)) for term in terms if term)
            if score:
                scored.append((score, topic))
        if not scored:
            return None
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1].id
