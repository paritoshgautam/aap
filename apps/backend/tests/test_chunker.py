from app.services.ingestion.chunker import TextChunker


def test_chunker_preserves_text_and_progresses() -> None:
    text = "A" * 300 + ". " + "B" * 300 + ". " + "C" * 300
    chunks = TextChunker(chunk_size=250, overlap=25).chunk(text)

    assert len(chunks) >= 3
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.text for chunk in chunks)


def test_chunker_rejects_invalid_overlap() -> None:
    try:
        TextChunker(chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected invalid overlap to raise")
