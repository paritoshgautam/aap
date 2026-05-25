from app.services.knowledge_graph.kb_mapping import KnowledgeBaseMapper
from app.services.knowledge_graph.topic_taxonomy import topics_for_subject


def test_taxonomy_has_chemistry_and_physics_topics() -> None:
    assert topics_for_subject("Chemistry")
    assert topics_for_subject("Physics")


def test_best_topic_matches_stoichiometry() -> None:
    mapper = KnowledgeBaseMapper(session=None)  # type: ignore[arg-type]
    definitions = topics_for_subject("Chemistry")

    topic = mapper._best_topic("mole ratio limiting reagent stoichiometry", definitions, 1)

    assert topic is not None
    assert topic.code == "chem-stoichiometry"
