from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_dynamic_chunk_params(text_length: int):
    """
    Dynamically adjust chunk size based on document size.
    """

    # Small documents (resume, short PDF)
    if text_length < 3000:
        return 600, 100

    # Medium documents (10–20 page policy docs)
    elif text_length < 15000:
        return 800, 150

    # Large documents (big government schemes)
    else:
        return 1000, 200


def chunk_text(text: str):
    """
    Production-grade text splitting.
    """

    chunk_size, chunk_overlap = get_dynamic_chunk_params(len(text))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    return splitter.split_text(text)