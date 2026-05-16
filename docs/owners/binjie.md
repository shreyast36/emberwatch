# Owner guide — Binjie

**Components:** model adapters (Claude / GPT / Gemini / Wafer), fillers (coding / Q&A).

You own two things that look unrelated but share a property: if they're wrong, the experiment silently produces garbage. A model adapter that drops the system message will invalidate the instruction-hierarchy probe. A filler that contains the word "I cannot" will contaminate the refusal probe at depth >0. There's no obvious failure mode — the matrix will run, the plots will look plausible, and the results will be meaningless. Treat correctness here as load-bearing.

## Files you own

- [src/slowburn/models.py](../../src/slowburn/models.py)
- [src/slowburn/fillers/base.py](../../src/slowburn/fillers/base.py)
- [src/slowburn/fillers/coding.py](../../src/slowburn/fillers/coding.py)
- [src/slowburn/fillers/qa.py](../../src/slowburn/fillers/qa.py)

## Order of work

### 1. Lock the Model protocol with Shreyas (15 min)

Before writing any adapter code, agree with Shreyas on the exact shape. Suggested:

```python
class Model(Protocol):
    model_name: str
    provider: str  # "anthropic" | "openai" | "google" | "wafer" — Shreyas needs this for per-provider semaphores

    async def complete(self, messages: list[dict], max_tokens: int) -> str: ...
```

The `messages` format is the OpenAI-style canonical shape (the codebase's lingua franca):

```python
[{"role": "system" | "user" | "assistant", "content": "string"}]
```

Each adapter converts from this shape to its provider's native format internally. Probes and fillers only know the canonical shape.

### 2. ClaudeModel first (45 min)

Build this one first — Shreyas needs Claude working for the judge, and you'll learn what the abstraction needs to handle before you commit to it for three providers.

Key conversion: Anthropic separates the system message from the user/assistant turns:

```python
# Convert canonical → Anthropic
system = next((m["content"] for m in messages if m["role"] == "system"), None)
convo = [m for m in messages if m["role"] != "system"]
client.messages.create(model=self.model_name, system=system, messages=convo, max_tokens=max_tokens)
```

Use `anthropic.AsyncAnthropic()`. Return `response.content[0].text`.

### 3. Backoff (30 min)

Wrap the SDK call in exponential backoff with jitter. Retry on `anthropic.RateLimitError`, `anthropic.APIConnectionError`, and `anthropic.InternalServerError`. Do NOT retry on `anthropic.BadRequestError` (those are our bugs, surface them).

```python
async def _retry(self, fn, *, max_attempts=6, base=2.0):
    for attempt in range(max_attempts):
        try:
            return await fn()
        except (RateLimitError, APIConnectionError, InternalServerError) as e:
            if attempt == max_attempts - 1:
                raise
            delay = base ** attempt + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

The runner has its own 3x retry on top of this — that's by design. Your backoff handles transient SDK errors; the runner's retry handles structural failures (judge timeouts, etc).

### 4. OpenAIModel (30 min)

OpenAI takes the canonical message shape essentially as-is — system messages go inside `messages`:

```python
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(
    model=self.model_name, messages=messages, max_completion_tokens=max_tokens,
)
return response.choices[0].message.content
```

Retryable errors: `openai.RateLimitError`, `openai.APIConnectionError`, `openai.InternalServerError`.

### 5. GeminiModel (45 min)

Gemini's API is the most different. Use `google-genai`:

```python
from google import genai
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
# convert canonical messages → Gemini's Content list
# system → systemInstruction (separate parameter)
# user/assistant → role "user"/"model" with parts=[{"text": ...}]
```

The role mapping matters: Gemini uses `"model"` for what OpenAI/Anthropic call `"assistant"`. Get this wrong and the conversation context will look broken to the model.

### 6. Coding filler (90 min — this is the bigger task)

`generate_coding_filler(target_tokens, seed) -> list[dict]` must:

1. **Be reproducible from seed.** `random.Random(seed)` — never use the global `random` module.
2. **Hit approximately `target_tokens` total tokens.** Use `tiktoken.get_encoding("cl100k_base")` for counting. Tiktoken won't match Gemini's tokenizer exactly, but it's the best cross-provider approximation. Aim for ±5% of target.
3. **Alternate user/assistant turns.** Start with user.
4. **Contain zero safety-relevant content.**

That last point is the hard one. Build a corpus of innocuous coding Q&A snippets (debugging a regex, refactoring a loop, explaining a stdlib function, etc.) and sample from it deterministically. **Banned content (non-exhaustive):**

- Refusals or hedging language ("I can't help with", "I won't", "I'm not able to")
- Jailbreak / prompt-injection patterns ("ignore previous instructions", "system prompt")
- Value statements ("my values are", "I believe", "ethically")
- Anything about other AI models' behavior
- Anything mentioning "safety," "alignment," "harm"

Add a guard function `_assert_innocuous(text)` that scans the assembled filler for a banlist of substrings and raises if any appear. Run it as the last step before returning. This is cheap insurance against future edits accidentally introducing contamination.

Suggested corpus approach: hand-author ~30-50 Q&A pairs of varying length, then sample with replacement until target is hit. Don't try to LLM-generate the corpus at runtime — that introduces nondeterminism and risks contamination.

### 7. Q&A filler (30 min)

Same protocol, same constraints, trivia-flavored content (capitals, science facts, historical dates, etc.). Same `_assert_innocuous` guard.

## Coordination points

- **With Shreyas:** confirm Model protocol shape (especially `provider: str` for the semaphore) before you start. Hand off ClaudeModel as soon as it works — he needs it for the judge.
- **With Dhanush:** none direct.
- **Tell the team when ClaudeModel works.** That unblocks Shreyas's judge work.

## Definition of done

- All three models can complete a simple `[{"role": "user", "content": "hi"}]` request asynchronously.
- Rate-limit errors are retried; bad-request errors are surfaced.
- `generate_coding_filler(50_000, seed=0)` returns ~50k tokens, two calls with the same seed return identical output.
- `_assert_innocuous` runs on every filler output and would catch contamination.
- A manual scan of one filler output at 25k tokens has zero refusals, value statements, or safety-relevant content.
