# Related work

The five papers / benchmarks that establish the long-context-safety landscape Slowburn positions against. Each entry includes the unclaimed quadrant Slowburn occupies relative to it.

## 1. Many-Shot Jailbreaking — Anthropic, April 2024

**Claim:** Frontier LLMs (Claude 3, GPT-4) can be reliably jailbroken using their large context windows. Packing the context with hundreds of fake user-assistant turns where the assistant complies with harmful requests causes the model to comply with a final real harmful request.

**Pressure type:** adversarial filler (intentional context poisoning).

**Slowburn's differentiation:** Slowburn uses **strictly innocuous filler** that is enforced by a banlist at filler-build time and on the assembled context ([src/slowburn/fillers/base.py](../src/slowburn/fillers/base.py)). If safety properties degrade even with provably-benign filler, the failure mode is more deployment-relevant: normal users with long benign conversations are at risk, not just attackers running attack chains.

## 2. Crescendo — Mark Russinovich et al., Microsoft, 2024

**Claim:** Multi-turn jailbreak that incrementally escalates semantically related queries — each individually innocuous — until the model produces dangerous content.

**Pressure type:** semantic escalation (each turn is topically related to the goal).

**Slowburn's differentiation:** Slowburn **decouples filler from probe**. Filler is hand-authored Q&A on programming or trivia topics with no semantic relationship to the safety probe. The filler banlist explicitly bars probe-topic vocabulary (phishing, codenames, COPD, salary surveys, value-priority language) to make the disjointness verifiable. The pressure being measured is *pure context length*, not topical escalation.

## 3. Sycophancy in Language Models — Sharma et al., Anthropic, October 2023

**Claim:** Models become more sycophantic — agreeing with the user's false beliefs — over longer conversations and after RLHF.

**Pressure type:** conversational length (somewhat analogous to ours).

**Slowburn's differentiation:** Slowburn applies the same methodology to **five distinct safety properties** simultaneously: refusal, instruction hierarchy, sycophancy, faithful uncertainty, and stated values. The novel contribution is not "models degrade with context" — that's confirmed by the Sycophancy paper — but the **relative half-life ordering** across properties, which is a structural claim about RLHF that single-property work cannot produce.

## 4. Long-context capability benchmarks — NIAH, RULER, InfiniteBench

**Claim:** Frontier LLMs with claimed context windows of 1M+ tokens often degrade on capability tasks (retrieval, multi-hop reasoning) far before they hit the window limit.

**Pressure type:** benign filler — but tests *capability*, not safety.

**Slowburn's differentiation:** Slowburn is the **"safety needle in a haystack"** analog. The "needle" is the RLHF-trained safety property; the "haystack" is innocuous benign context. The methodology is borrowed from this line of work, but the property being measured is alignment retention rather than factual retrieval.

## 5. Sleeper Agents — Hubinger et al., Anthropic, January 2024

**Claim:** Models can be trained to behave safely in normal conditions but produce malicious behavior when triggered by a specific context cue. Standard safety training does not remove the backdoor.

**Pressure type:** intentional training-time corruption.

**Slowburn's differentiation:** Slowburn evaluates **off-the-shelf, commercially-deployed frontier models** with no fine-tuning. The question is whether *naturally accumulating context* in normal usage acts as an unintentional trigger for unsafe behavior — i.e. whether benign long usage produces an effect *resembling* a sleeper-agent activation without anyone having trained one in.

## The unclaimed quadrant

| Axis | Many-Shot | Crescendo | Sycophancy (2023) | NIAH / RULER | Sleeper Agents | **Slowburn** |
|---|---|---|---|---|---|---|
| Filler content | adversarial | semantically related | conversational | benign | n/a (training) | **provably benign + disjoint** |
| Pressure mechanism | poisoning | escalation | length | length | trigger | **pure length** |
| Properties measured | refusal | refusal | sycophancy | capability | triggered behavior | **5 safety properties** |
| Model state | off-the-shelf | off-the-shelf | off-the-shelf | off-the-shelf | trained-in backdoor | **off-the-shelf** |
| Headline output | "can jailbreak with N shots" | "can escalate to harmful" | "sycophancy grows w/ length" | "retrieval fades" | "backdoors persist" | **relative half-life ordering across properties** |

The novel claim Slowburn is positioned to land: **safety properties have measurably different context half-lives, and the ordering is a structural fingerprint of how each lab's RLHF prioritizes alignment dimensions.** No prior work measures this because no prior work tests multiple properties × innocuous filler × off-the-shelf models in one design.
