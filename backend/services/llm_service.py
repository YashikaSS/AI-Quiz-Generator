"""
llm_service.py
----------------
SHARED MODULE - used by summary_service.py (Member 4) and quiz_service.py (Member 5)

WHAT THIS FILE DOES:
This file is responsible for loading a Large Language Model (LLM) like
Qwen2.5 or Llama3 ONE TIME when the server starts, and giving other files
a simple function to call: generate_text(prompt) -> returns a string answer.

WHY "LOAD ONCE"?
LLMs are huge (several GB). If every function reloaded the model every time
it was called, the app would be extremely slow and would likely run out of
memory. So we load it once into a global variable and reuse it.

NOTE FOR MEMBER 6 / WHOEVER FINALIZES THIS FILE:
This is a placeholder/minimal version so Member 4 and Member 5 can develop
and test against a REAL working function instead of waiting. Feel free to
swap the internals (e.g. swap HuggingFace transformers for vLLM, Ollama,
or an API-based model) as long as you keep the function signature:

    generate_text(prompt: str, max_new_tokens: int = 512) -> str

That way nobody else's code has to change.
"""

import os

# Toggle this in your .env later (see config.py). For now, a simple flag.
# If True, we use a real local HuggingFace model.
# If False, we use a tiny offline "echo" fallback so the code still runs
# on a laptop with no GPU and no internet (useful for early development).
USE_REAL_MODEL = os.environ.get("USE_REAL_LLM", "false").lower() == "true"

_model = None
_tokenizer = None


def _load_model():
    """
    Loads the model and tokenizer into memory ONE TIME.
    This is called automatically the first time generate_text() is used.
    """
    global _model, _tokenizer

    if _model is not None:
        # Already loaded, don't reload.
        return

    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")

    print(f"[llm_service] Loading model: {model_name} (this happens once)...")

    _tokenizer = AutoTokenizer.from_pretrained(model_name)
    _model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )

    print("[llm_service] Model loaded successfully.")


def is_model_available() -> bool:
    """
    Lets OTHER files (like summary_service.py) check, before calling
    generate_text(), whether a real model is actually wired up.

    This is more reliable than wrapping generate_text() in try/except,
    because the placeholder fallback mode returns a normal string (not
    an error) - so a try/except alone would never notice anything is wrong.
    """
    return USE_REAL_MODEL


def generate_text(prompt: str, max_new_tokens: int = 512) -> str:
    """
    The ONE function other files should call.

    Args:
        prompt: The full text prompt/instruction to send to the LLM.
        max_new_tokens: Roughly how long the answer is allowed to be.

    Returns:
        The model's text response as a plain string.

    Raises:
        RuntimeError: if no real model is configured (USE_REAL_LLM is not
            "true"). Callers (like summary_service.py) are expected to
            catch this and fall back to a non-LLM method instead.
    """
    if not USE_REAL_MODEL:
        # No real model is wired up yet. We raise instead of silently
        # returning placeholder text, so callers can reliably detect
        # this case with a try/except and fall back appropriately.
        raise RuntimeError(
            "No real LLM is configured. Set environment variable "
            "USE_REAL_LLM=true and ensure a model is downloaded to "
            "enable real LLM generation."
        )

    _load_model()

    messages = [{"role": "user", "content": prompt}]
    inputs = _tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    )

    outputs = _model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
    )

    # Only decode the NEW tokens (the model's answer), not the input prompt.
    new_tokens = outputs[0][inputs.shape[-1]:]
    response = _tokenizer.decode(new_tokens, skip_special_tokens=True)
    return response.strip()



