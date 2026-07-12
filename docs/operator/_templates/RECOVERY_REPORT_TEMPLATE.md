# Recovery Report: <Situation>

Date: <YYYY-MM-DD>

Documents one execution of a procedure from RECOVERY_PROCEDURES.md.

## Situation

<Which row of RECOVERY_PROCEDURES.md's table applied — e.g., "Interrupted
session," "Merge conflict.">

## Detection

<How the situation was noticed — which boot step, which command output.>

## Preservation

<What was preserved before any other action — e.g., `git stash push -u`.>

## Inspection

<What was found on inspection — diffs read, context compared against
PROJECT_TRACKER.md.>

## Recovery Action Taken

<The specific safe recovery step(s) taken, per RECOVERY_PROCEDURES.md's
table for this situation.>

## Validation After Recovery

<Commands run to confirm the recovered state is correct.>

## Escalation

<Was this escalated? If the situation turned out to be Hard Stop 15.1
class, note that explicitly and cross-reference the resulting Incident
Report.>
