# China payment / slider regression

Use Python 3.9 and oTree 5.11.5 (the version tested). All tests create synthetic data.
Run in a **disposable copy** of this repository, never against an experimental database.
Keep `DATABASE_URL` unset so these commands use only the copy's local SQLite file.
Artifacts default to `tmp/qa_results`; override with `QA_OUTPUT_DIR` if needed.

1. Before starting a server, run `python tests/payment_boundaries.py`.
2. Start `otree prodserver 8020` in that disposable copy.
3. Run `python tests/concurrent_flows.py` then `python tests/edge_flows.py`.
4. Stop the server and its timeoutworker before running `python tests/verify_saved.py`.

The HTTP tests use barriers to synchronize 15 clients and do not retry HTTP errors.
They verify six 20-round treatments plus test-only four-round groups (4/4, 15/15,
15/5), a delayed last submission, independent small groups, and duplicate POSTs.
The four-person configuration is only a regression fixture; official configurations
remain odd-sized groups of 5 or 15.

Browser checks: untouched slider + Enter leaves the hidden choice empty; clicking
initial 50 reveals/enables Submit immediately; Home/End select 0/100; submitting
waits for the group; complete the survey; payment and admin total both equal 64.75
when the paid round has all players choosing 10. Refresh payment repeatedly.

## Observed limitation

The synchronized six-treatment run passed, but a separate mixed browser/HTTP run
with participants lingering on pages reproduced `sqlite3.OperationalError: database
is locked` / HTTP 500, also reproduced during manual browser testing. Therefore this
is **not a production concurrency approval**. Investigate with the actual deployment
and PostgreSQL. A passing fast local run does not cancel the recorded failure.
