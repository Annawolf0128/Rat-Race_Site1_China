# Rat Race (RBC) experiment — China site

Standalone deployment of the oTree Reversed Beauty Contest (RBC / "Rat Race") experiment for the China site (Site 1). All participant-facing text is in Chinese (LANGUAGE_CODE zh-hans); payment is in RMB (¥15 show-up fee, ¥0.50 per point, one common randomly drawn round paid per session).

Each round, participants choose an integer in `[0, 100]`. Higher numbers cost more (cost = x²/k). A fixed penalty `L` is paid by anyone whose choice is **strictly below the group median**. The combination of cost and below-median penalty creates a "match-or-quit" best response and a continuum of symmetric equilibria.

## Quick start

Python 3.9 is required. Run the commands for your operating system one at a time so that, if cloning or installation fails, later commands do not run in the wrong directory.

### macOS / Linux

```bash
git clone https://github.com/Annawolf0128/Rat-Race_Site1_China.git
cd Rat-Race_Site1_China
python3.9 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
otree devserver
```

### Windows PowerShell

```powershell
git clone https://github.com/Annawolf0128/Rat-Race_Site1_China.git
Set-Location Rat-Race_Site1_China
py -3.9 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
otree devserver
```

If PowerShell blocks `Activate.ps1`, open Command Prompt in the repository and activate with `venv\Scripts\activate.bat` instead.

Open http://localhost:8000/demo/ after the server starts.

### Clone troubleshooting

If `git clone` reports an HTTP/2 framing error, retry it with HTTP/1.1:

```bash
git -c http.version=HTTP/1.1 clone https://github.com/Annawolf0128/rbc-experiment.git
```

If it still cannot connect to `github.com:443`, check the computer's VPN, firewall, or proxy settings. Proxy addresses are machine- and network-specific, so do not copy another user's localhost proxy address.

## Treatment configurations

| Config | Session grouping | L | Rounds | x̄ = √(Lk) | Purpose |
|---|---|---|---|---|---|
| `rbc_preview` | 1 | 20 | 2 | 63.2 | Solo quick test, no belief elicitation |
| `rbc_test_2p_2r` | 2 | 20 | 2 | 63.2 | 2-player quick test |
| `rbc_test_2p_2r_belief` | 2 | 20 | 2 | 63.2 | 2-player quick test with belief elicitation |
| `rbc_site1_small_low` | 3 × 5 (15 total) | 20 | 20 | 63.2 | Small–Low |
| `rbc_site1_small_high` | 3 × 5 (15 total) | 40 | 20 | 89.4 | Small–High |
| `rbc_site1_large_low` | 1 × 15 (15 total) | 20 | 20 | 63.2 | Large–Low |
| `rbc_site1_large_high` | 1 × 15 (15 total) | 40 | 20 | 89.4 | Large–High |
| `rbc_site1_small_low_belief` | 3 × 5 (15 total) | 20 | 20 | 63.2 | Small–Low–Belief |
| `rbc_site1_large_low_belief` | 1 × 15 (15 total) | 20 | 20 | 63.2 | Large–Low–Belief |

Shared parameters: endowment `E = 100`, cost denominator `k = 200`, `T = 20` rounds by default.

## Planned Singapore sessions

The same oTree configuration can be used to create more than one independent session. The planned run count is:

| Treatment | oTree config | Groups per session | Sessions to run | Total groups | Participants |
|---|---|---:|---:|---:|---:|
| Small–Low | `rbc_site1_small_low` | 3 × 5 | 1 | 3 | 15 |
| Small–High | `rbc_site1_small_high` | 3 × 5 | 1 | 3 | 15 |
| Large–Low | `rbc_site1_large_low` | 1 × 15 | 3 | 3 | 45 |
| Large–High | `rbc_site1_large_high` | 1 × 15 | 3 | 3 | 45 |
| Small–Low–Belief | `rbc_site1_small_low_belief` | 3 × 5 | 1 | 3 | 15 |
| Large–Low–Belief | `rbc_site1_large_low_belief` | 1 × 15 | 1 | 1 | 15 |
| **Total** |  |  | **10** | **16** | **150** |

This gives each of the four main no-belief blocks three independent groups. The two belief treatments are exploratory additions and each uses one 15-person session.

## Page flow

```
Group formation wait page → Welcome → Consent → Instructions → Quiz
       → 20 × ([Belief, if enabled] → Choice → WaitForGroup → Results)
       → Survey (risk, strategy, median-use, and demographics items)
       → Payment (show-up fee + one randomly selected round's earnings)
```

## Project layout

```
Rat-Race_Site1_China/
├── settings.py          # SESSION_CONFIGS, participation fee, currency
├── requirements.txt     # otree>=5.10,<6
├── _static/             # Required by oTree (empty placeholder)
├── _templates/          # Required by oTree (empty placeholder)
└── rbc/
    ├── __init__.py      # Constants C, Subsession, Group, Player, page_sequence
    ├── Welcome.html     # Welcome / waiting screen
    ├── Consent.html     # Placeholder consent screen
    ├── Instructions.html
    ├── Quiz.html        # Comprehension check (must answer correctly to proceed)
    ├── Belief.html      # Optional belief elicitation page
    ├── Choice.html      # Slider 0–100 with live cost panel
    ├── Results.html     # Round-end feedback
    ├── Survey.html      # Post-experiment survey
    └── Payment.html     # Final payment summary
```

## Launching

### Development

```
otree devserver
```

The dev server includes a debug panel and auto-reloads on code changes. Not for real participants.

### Production / real sessions

```
otree prodserver
```

Then log in at http://localhost:8000/sessions, create a session, and distribute the unique `SessionStartLink` URLs to the participants. After the session ends, export data from http://localhost:8000/export.

For a public URL (so remote participants can join), deploy via [oTree Hub](https://www.otreehub.com), Heroku, Render, or an equivalent platform — `localhost` is only reachable from the host machine.

## Implementation notes

- Every official session requires exactly 15 participants and contains one treatment only. A small-arm session forms three groups of 5; a large-arm session forms one group of 15. Group membership then stays unchanged across all rounds.
- For the four main no-belief blocks, run each small-group configuration once and each large-group configuration three times, giving three groups per block. Run each belief configuration once. This schedule contains 10 sessions and 150 recruited participants in total.
- The randomly paid round is drawn once in `creating_session()` and stored on `participant.paid_round`, independent of in-session behaviour.
- The consent page body is intentionally a placeholder. Replace the text in `rbc/Consent.html` with the institution-specific consent statement (purpose, voluntary participation, data use, contact, ethics ID) before any real run.
