from config import CHUNK_TOKENS, OVERLAP_TOKENS, MODEL
try:
    import tiktoken
    TOK = tiktoken.encoding_for_model(MODEL)
except Exception:
    TOK = None

def num_tokens(text: str) -> int:
    if TOK:
        return len(TOK.encode(text))
    # fallback: estimate 1 token ~= 4 characters
    return max(1, len(text) // 4)

def chunk_text_by_tokens(text: str, chunk_tokens=CHUNK_TOKENS, overlap=OVERLAP_TOKENS):
    if TOK is None:
        # fallback: chunk by characters (approx)
        approx_chunk_chars = chunk_tokens * 4
        approx_overlap_chars = overlap * 4
        chunks = []
        start = 0
        while start < len(text):
            end = start + approx_chunk_chars
            chunks.append(text[start:end])
            start = max(0, end - approx_overlap_chars)
        return chunks
    # token-aware chunking
    tokens = TOK.encode(text)
    chunks = []
    start = 0
    L = len(tokens)
    while start < L:
        end = start + chunk_tokens
        slice_tokens = tokens[start:end]
        chunks.append(TOK.decode(slice_tokens))
        start = max(0, end - overlap)
    return chunks