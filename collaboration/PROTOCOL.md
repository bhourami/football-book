# Claude and Codex review protocol

This protocol exists to prevent one specific, expensive, invisible-after-the-
fact bug: in an earlier attempt at this project, Claude opened its selection
against an empty transcript while Codex's first turn already contained
Claude's opening view. The "Codex solo" book was therefore really Codex
reacting to Claude, and the three-book comparison (methodology section 4)
was flattered without anyone noticing until much later. It can only be
prevented mechanically — review after the fact does not catch it, because the
transcript looks normal either way.

## Sequence

1. **Sealed opening.** For each fixture under consideration, Claude and Codex
   each write an independent opening selection — market, probability
   estimate, price, stake — to their own file (`claude-input.json` /
   `codex-input.json`), **without having been given the other's file, or any
   content derived from it, in context.** Both files are committed to disk
   before either process is invoked again on that fixture.
2. **Reveal.** Only after both opening files exist on disk does the debate
   stage begin. Codex is shown Claude's opening (or vice versa) and may
   challenge it; the original is shown Codex's rebuttal and may respond. The
   exchange continues while either side is still adding decision-relevant
   evidence, changing market, stake or view, withdrawing a claim, or
   resolving a question. There is no fixed exchange count.
3. **Transcript.** The full exchange is retained under `/collaboration/debates/
   <fixture-id>.json`. Opening records inside it are immutable — a later turn
   never rewrites what an opening said, only what came after it.
4. **Conclusion.** A deterministic reconciliation writes
   `/collaboration/debate-conclusions.json`. It returns a bet only when both
   final positions agree on market, selection and stake, and neither analyst's
   input is blocked by fail-closed (methodology section 6). Disagreement, or
   either analyst declining, returns no position for the conclusion book —
   the reconciliation never merges the two views or resolves a disagreement
   itself.

## File ownership

- Claude writes only `claude-input.json`.
- Codex writes only `codex-input.json`.
- Neither edits the other's file, ever.
- `debate-conclusions.json` is written only by the reconciliation step, never
  hand-edited to fit a result (methodology: frozen rules).

## What counts as "seeing" the other analyst

Not just reading the file directly. A summary, a paraphrase, a "the other
analyst leans towards X" from the owner or from a third process, or any
context window that has ever contained the other file's content, all count.
If there is doubt about whether an opening was genuinely sealed, the opening
is discarded and redone — a suspect opening is worse than a slower one.
