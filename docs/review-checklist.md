# Review Checklist

Use this before merging a Dev-State change.

- Keep repository-state reporting deterministic and easy to explain.
- Do not mutate a target repository unless the command explicitly promises to.
- Treat missing, dirty, detached, and diverged Git states as normal inputs to handle safely.
- Keep output concise enough to scan in a terminal.
- Preserve clear exit behavior for automation and CI use.
- Add or update a smoke check when changing repository inspection logic.

A safe Dev-State patch should improve signal without making Git state harder to reason about.
