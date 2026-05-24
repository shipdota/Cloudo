## 2023-10-27 - Dependency Constraints
**Learning:** Altering dependency versions in `requirements.txt` just to get local tests passing can cause unexpected behavior and violates the 'no breaking changes' constraint.
**Action:** Revert any test-specific dependency changes in `requirements.txt` before committing, or avoid them altogether by running mock tests that bypass dependency conflicts.
