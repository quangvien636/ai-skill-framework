# CLAUDE.md

This file exists so Claude Code auto-loads repository orientation at
session start.

Read [MASTER_OPERATOR.md](MASTER_OPERATOR.md) in full before making any
change. It is the authoritative operating manual for this repository:
Vision, Philosophy, the Repository Truth Hierarchy, Operating Principles,
Autonomous Development Rules, the Decision Hierarchy, and the complete
documentation map.

This file carries no authority of its own. If it and `MASTER_OPERATOR.md`
ever appear to disagree, `MASTER_OPERATOR.md` wins — see its Repository
Truth Hierarchy section.

Minimum session-start sequence (`MASTER_OPERATOR.md`'s planned Session
Bootstrap Protocol chapter defines the full version):

1. `MASTER_OPERATOR.md`
2. `PROJECT_CONTEXT.md`
3. `PROJECT_TRACKER.md` — Current Sprint and Next Actions
4. Whichever architecture document, ADR, or guide the specific task touches

Do not restate this project's architecture, governance, or constraints in a
new prompt — they already live in the files above.
