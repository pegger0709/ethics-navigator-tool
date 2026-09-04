# Loom script — Ethics Navigator, what makes it great

Target: under 2 minutes. Screen recording of the running app; no slides needed.
Before recording, have the app open with a jurisdiction already selected, so
you don't burn time narrating the setup. This version leads with the
differentiators rather than an ask — swap the closing beat back to "the ask"
(kept at the bottom) if this is going specifically to the ethics board.

---

**[0:00–0:15] What this is, in one line**

"This is the Ethics Navigator. Instead of me — or an AI — telling you what I
think the rules say, it answers your question from the actual texts: UNESCO's
neurotechnology recommendation, the OECD principles, GDPR, CCPA, the UN
frameworks. Every answer is grounded and cited."

**[0:15–0:50] The thing that makes it trustworthy: it won't make things up**

Type a real question, let it answer, then point at the citation.

"Watch — I'll ask [e.g. 'What is cognitive liberty?']. It searches the actual
text, answers from what it finds, and shows exactly which document and passage
it came from. That's the part that matters: I can go verify it myself instead
of taking a chatbot's word for it."

Now show a refusal case (~15s): ask something the corpus doesn't cover.

"And if I ask something the documents don't actually address, it says so —
instead of confidently guessing. That's the difference between this and just
asking a general-purpose AI."

**[0:50–1:20] It also handles the big-picture question, not just lookups**

"It's not only for narrow lookups. I can also ask something broad — 'summarize
the principles governing responsible neurotechnology development' — and it
draws on a digest of the whole document rather than one passage, so it doesn't
miss things a narrow search would."

**[1:20–1:45] Why it's safe to actually use**

"Everything here runs locally — the documents, the questions, the answers
never leave this machine. That matters because the questions we'd ask about a
real partnership are themselves sensitive, and nothing gets sent anywhere."

**[1:45–2:00] The close**

"So: grounded answers, honest refusals, handles both quick lookups and big
questions, and it's completely private. That's what I wanted you to see."

---

## Alternative closing — if this goes to the ethics board specifically

Swap the [1:45–2:00] beat for:

"Two things worth knowing: it's a reference tool, not a decision-maker — it
doesn't replace the conversation we have as a board, it makes that
conversation faster to prepare for. I'd like ten minutes at the next meeting
to walk through it live and get your reaction."

---

## Notes for recording

- Pick questions you've already verified work well — the eval results show
  four-model-agreement on straightforward lookups. Don't put a known-weak case
  (CCPA specifics, cross-jurisdiction scoping) on camera; save those for a live
  session where you can narrate around them.
- If a jurisdiction toggle is visible, mention it once ("I've told it I only
  care about EU and California law here") — it's the detail non-technical
  viewers most often ask about afterward.
- Keep the recording to the running app only. No terminal, no code, no Docker —
  viewers don't need to see how it's built to react to what it does.
