# Understanding Similarity Scoring in ChromaDB

## The Problem (Now Fixed)

The system was incorrectly filtering out relevant documents due to a misunderstanding of ChromaDB's distance metric.

### What Was Wrong

**Original Code (INCORRECT):**
```python
similarities = results.get("distances", [[]])[0]
if not similarities or min(similarities) < 0.70:
    return "I don't have enough information to answer this question."
```

**The Issue:**
- ChromaDB returns **distance scores**, not similarity scores
- **Lower distance = MORE similar** (0 = identical, 2 = completely different)
- The code checked `min(similarities) < 0.70`, which means:
  - If best match has distance < 0.70 → REJECT (this is BACKWARDS!)
  - Very similar documents (distance 0.3, 0.4, 0.5) were being rejected
  - Only poor matches (distance > 0.70) would pass through

### The Fix

**New Code (CORRECT):**
```python
distances = results.get("distances", [[]])[0]
if not distances or min(distances) > 1.5:
    return "I don't have enough information to answer this question."
```

**Now it correctly:**
- Checks if distance is TOO HIGH (> 1.5)
- Accepts documents with LOW distance (high similarity)
- Rejects only genuinely irrelevant documents

## ChromaDB Distance Metric

### Cosine Distance Explained

ChromaDB uses **cosine distance** by default:

```
Distance = 1 - Cosine Similarity
```

**Scale:**
- **0.0** = Identical vectors (perfect match)
- **0.5** = Moderately similar (45° angle)
- **1.0** = Orthogonal vectors (no similarity)
- **2.0** = Opposite vectors (completely different)

### Typical Ranges for Documents

| Distance Range | Meaning | Action |
|---------------|---------|---------|
| 0.0 - 0.3 | Highly relevant | ✅ Use |
| 0.3 - 0.8 | Moderately relevant | ✅ Use |
| 0.8 - 1.5 | Weakly relevant | ⚠️ Use with caution |
| > 1.5 | Not relevant | ❌ Reject |

### Current Threshold

**Set at 1.5** - This is generous and allows moderately relevant documents through while filtering out clearly irrelevant content.

## Example Scenarios

### Scenario 1: Generic Question
**Query:** "What is the file about?"
- **Distance:** ~0.2-0.5 (generic terms match well)
- **Result:** ✅ Passes threshold
- **Behavior:** System provides overview

### Scenario 2: Specific Question
**Query:** "What are the best practices for LinkedIn profiles?"
- **Distance:** ~0.4-0.9 (specific terms need closer match)
- **Old behavior:** ❌ Rejected (distance < 0.70)
- **New behavior:** ✅ Passes threshold (distance < 1.5)

### Scenario 3: Unrelated Question
**Query:** "What is the capital of France?"
- **Distance:** ~1.6-2.0 (completely unrelated)
- **Result:** ❌ Rejected (distance > 1.5)
- **Response:** "I don't have enough information..."

## Adjusting the Threshold

You can tune the threshold in `src/app.py`:

```python
# More strict (only highly relevant documents)
if not distances or min(distances) > 0.8:
    return "I don't have enough information..."

# Current setting (balanced)
if not distances or min(distances) > 1.5:
    return "I don't have enough information..."

# More lenient (allows weakly relevant documents)
if not distances or min(distances) > 1.8:
    return "I don't have enough information..."
```

### Recommendations

- **1.5** (current) - Good default for most cases
- **1.2** - If getting too many irrelevant answers
- **1.8** - If getting too many "don't have enough information" responses

## Debugging Tips

Check the console output when querying:
```
Best distance score: 0.4523 (lower = more similar)
```

- **< 0.5:** Excellent match
- **0.5 - 1.0:** Good match
- **1.0 - 1.5:** Acceptable match
- **> 1.5:** Poor match (rejected)

## System Prompt Behavior

Even if documents pass the threshold, the LLM has a strict system prompt:

```
You may ONLY use information fully and explicitly contained within <context>.
If the answer is not 100% contained in <context>, respond exactly:
"I don't have enough information to answer this question."
```

So you might still get this response if:
1. ✅ Documents were retrieved (passed distance threshold)
2. ✅ Context was sent to LLM
3. ❌ But LLM determined the answer isn't explicitly in the context

This is correct behavior - the system is being cautious and not hallucinating answers.
