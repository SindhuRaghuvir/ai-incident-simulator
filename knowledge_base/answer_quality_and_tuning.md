# Answer Quality and Tuning

## Understanding How Answers Are Built

### How does Stratify Labs produce an answer?
Every answer goes through two steps, often called RAG (retrieval-augmented generation):

1. **Retrieval** — your question is turned into a vector and compared with every chunk in the collection. The `top_k` most similar chunks are selected.
2. **Generation** — those chunks and your question are sent to the answer model, which is instructed to answer **only** from the provided content and cite its sources.

When an answer is wrong, the cause is almost always in one of these two steps. Check retrieval first: if the right content never reached the model, no amount of prompt tuning will fix the answer.

### How do I tell if a bad answer is a retrieval problem or a generation problem?
Look at the `sources` in the response (or the **Sources** panel in the dashboard):

- **The right document isn't in the sources** → retrieval problem. Check that the content exists, check chunking, and try rephrasing.
- **The right document is in the sources but the answer is still wrong** → generation problem. Check temperature, the custom instructions, and whether the chunk contains the complete answer or only part of it.

---

## Hallucinations

### The AI made up an answer that isn't in our documents — why?
Common causes:
1. **High temperature** — values above 0.7 make answers more creative and less faithful to the source. Use 0.0–0.3 for support content.
2. **Low confidence threshold** — weakly related chunks are being passed to the model, and it tries to stitch an answer together from them.
3. **Custom instructions that encourage guessing** — phrases like "always give the customer an answer" override the grounding rules.
4. **Partial content** — the chunk mentions a topic but not the specific answer, so the model fills the gap.

### How do I reduce hallucinations?
- Keep temperature at **0.0–0.3**
- Raise the **confidence threshold** so weak matches are dropped (see below)
- Enable **Strict Grounding** at **Collections > Settings > Answer Behavior**. The model must cite a source for every claim, and answers without citations are replaced by your fallback message.
- Write a clear fallback message, such as "I couldn't find that in our help center — here's how to reach a person."

---

## Tuning Retrieval

### What is the confidence threshold and how do I set it?
Every retrieved chunk has a relevance score from 0 to 1. Chunks below the confidence threshold are discarded before generation. If nothing passes, the user gets your fallback message instead of a guess.

- **Too high** (e.g., 0.90): the system says "I don't know" even when the answer exists.
- **Too low** (e.g., 0.40): irrelevant content gets through and answers drift off-topic.

Start at **0.70**, then adjust using the **Retrieval Debugger** at **Collections > Debug**, which shows every chunk's score for a test question.

### What chunk size should I use?
Chunk size controls how much text goes into each searchable piece.

| Content type | Recommended chunk size |
|--------------|-----------------------|
| FAQs and short Q&A | 300–500 characters |
| How-to guides and runbooks | 800–1,200 characters |
| Long policy or legal documents | 1,200–2,000 characters |

Chunks that are too small lose context (the answer gets split from its question). Chunks that are too large mix several topics, which lowers relevance scores. Changing chunk size requires re-indexing the collection.

### What is hybrid search?
Hybrid search combines semantic (meaning-based) search with keyword search. It helps when users search for exact terms that semantic search can miss, such as error codes (`ERR_4012`), product SKUs, or API parameter names. Enable it at **Collections > Settings > Search Mode > Hybrid** (Professional and Enterprise).

### What is reranking?
Reranking takes the top 20–50 retrieved chunks and re-scores them with a more precise model before choosing the final `top_k`. It typically improves answer accuracy by 10–20% on large or messy collections, at the cost of about 150 ms extra latency. Available on Professional and Enterprise.

---

## Measuring Quality

### How do I know if our answers are getting better or worse?
Use three signals:
1. **User feedback** — thumbs up/down on answers, shown at **Analytics > Answer Feedback**
2. **"I don't know" rate** — the share of questions that hit the fallback message. A sudden jump often means content was deleted or a sync broke.
3. **An evaluation set** — 30 to 100 real questions with known correct answers. Run it at **Collections > Evaluate** after every major content or settings change and compare the score with the last run.

### How do I find gaps in our knowledge base?
Go to **Analytics > Unanswered Questions**. It groups questions that hit the fallback message by topic, sorted by volume. These are the articles you should write next. Many teams review this list weekly.

### Can I customize the tone and format of answers?
Yes. Add **Custom Instructions** at **Collections > Settings > Answer Behavior** — for example, "Use a friendly tone, keep answers under 120 words, and use numbered steps for procedures." Custom instructions change style only. They cannot override the grounding rules, and the model will still refuse to answer from outside your content.
