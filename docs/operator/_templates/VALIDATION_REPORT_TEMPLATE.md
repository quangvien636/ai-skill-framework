# Validation Report: <Change Title>

Date: <YYYY-MM-DD>

Per DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md's Validation Report Standard.
Never report a command as passed without having run it.

## Repository and Branch

<Absolute path; branch name.>

## HEAD Before / After

<Commit hash before this change; commit hash after (fill in after
committing, or state "pending commit").>

## Commands Run

```text
<exact commands, verbatim, one per line>
```

## Environment

<Python/tool versions relevant to reproducing this exactly.>

## Results

| Command | Result | Notes |
| --- | --- | --- |
| <command> | <pass/fail + count> | <any relevant detail> |

## Skipped Checks

<What was not run and why — e.g., an opt-in live-service test with no
server available in this environment.>

## Known Warnings

<Any non-blocking finding surfaced by validation.>

## Limitations

<What this validation run does NOT prove.>

## Artifacts

<Any generated report file this run produced, if applicable.>

## Conclusion

<Plainly state: is this change safe to commit?>
