from openai import OpenAI
from config import MODEL, CHUNK_TOKENS, OVERLAP_TOKENS
from chunksData import num_tokens, chunk_text_by_tokens
import os
import json


class summarization:
    @staticmethod
    def call_model(prompt: str, max_tokens):
        """Call OpenAI Responses API with a prompt and return the text summary."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY not set in environment. Aborting API call.")
            raise RuntimeError("OPENAI_API_KEY missing")

        client = OpenAI(api_key=api_key)
        try:
            response = client.responses.create(
                model=MODEL,
                input=[
                    {"role": "system", "content": "You are a helpful assistant that produces concise accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_output_tokens=max_tokens,
                temperature=0.2
            )
        except Exception as e:
            print("API call failed:", type(e).__name__, e)
            raise

        # DEBUG: show truncated raw response for inspection
        try:
            raw = str(response)
            #print("DEBUG: raw response (truncated):", raw[:3000])
        except Exception:
            pass

        # Robust extraction: try multiple common SDK fields
        text = ""
        # 1) Responses API may expose 'output_text'
        if hasattr(response, "output_text") and response.output_text:
            text = response.output[0].content[0].text
            
        else:
            # 2) Fall back to iterating response.output items with content lists
            try:
                for item in getattr(response, "output", []):
                    if isinstance(item, dict) and "content" in item:
                        for c in item["content"]:
                            if isinstance(c, dict):
                                # common keys: 'text' or 'content' subfields
                                if "text" in c and c.get("text"):
                                    text += c.get("text", "")
                                elif "content" in c:
                                    # content might be a list or dict
                                    if isinstance(c["content"], list):
                                        for sub in c["content"]:
                                            if isinstance(sub, dict) and sub.get("text"):
                                                text += sub.get("text", "")
                                    elif isinstance(c["content"], dict) and c["content"].get("text"):
                                        text += c["content"].get("text", "")
                    # Some SDKs return object-like outputs; attempt str() fallback per item
                    elif not text:
                        try:
                            item_str = json.dumps(item) if not isinstance(item, str) else item
                            text += item_str
                        except Exception:
                            text += str(item)
            except Exception as e:
                print("Failed to extract from response.output:", type(e).__name__, e)

        text = (text or "").strip()
        if not text:
            print("DEBUG: extracted text empty. Consider increasing max_output_tokens, reducing prompt length, or inspecting the raw response above.")
        return text


    @staticmethod
    def summarize_file(filepath, chunk_tokens=CHUNK_TOKENS, overlap_tokens=OVERLAP_TOKENS):
        """Read file, chunk if necessary, summarize chunks, and combine."""
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            return "File empty."

        tok = num_tokens(text)
        print(f"File has approximately {tok} tokens.")
        # If short enough, single-shot summarization
        if tok <= chunk_tokens:
            prompt = (
                "Summarize the following document into a concise summary (5-8 bullet points). "
                "Be factual and avoid adding new facts. Keep each bullet short.\n\n"
                + text
            )
            summary = summarization.call_model(prompt, max_tokens=400)
            # fallback: retry with simpler prompt if empty
            if not summary:
                print("Empty reply — retrying with simpler prompt...")
                fallback = "Summarize the text below in 4 short bullets:\n\n" + text[:4000]
                summary = summarization.call_model(fallback, max_tokens=300)
            return summary or "Summary empty after retries."

        # Otherwise: chunk -> summarize chunks -> combine
        chunks = chunk_text_by_tokens(text, chunk_tokens, overlap_tokens)
        chunk_summaries = []
        print(f"Detected large file: {len(chunks)} chunks. Summarizing each chunk...")
        for i, c in enumerate(chunks, 1):
            prompt = (
                f"Chunk {i}/{len(chunks)}: Provide a 1-2 sentence summary of the following text.\n\n{c}"
            )
            s = summarization.call_model(prompt, max_tokens=200)
            if not s:
                # retry once shorter
                print(f"Chunk {i} empty – retrying with truncated chunk...")
                s = summarization.call_model(prompt[:3000], max_tokens=150)
            chunk_summaries.append(f"Chunk {i}: {s or '[no content]'}")

        # Combine chunk summaries
        combine_prompt = (
            "Combine the following short chunk summaries into a single coherent summary of the whole document. "
            "Output 6 bullet points that capture the key ideas, findings, and action items. "
            "Be concise and factual.\n\n" + "\n\n".join(chunk_summaries)
        )
        final = summarization.call_model(combine_prompt, max_tokens=600)
        if not final:
            print("Final combine returned empty — returning joined chunk summaries as fallback.")
            return "\n\n".join(chunk_summaries)
        return final
