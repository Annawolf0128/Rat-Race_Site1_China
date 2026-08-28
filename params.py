"""
Central parameter file for the Reversed Beauty Contest experiment.

EDIT VALUES HERE — settings.py and rbc/__init__.py both import from this file.
Restart `otree devserver` after editing for changes to take effect.
"""

# ============================================================
# Game parameters (shared across all treatments)
# ============================================================
ENDOWMENT     = 100      # E   each round starts with this many points
COST_DIVISOR  = 200      # k   cost = x^2 / k  (so x=100 costs 50, x=10 costs 0.5)
NUM_ROUNDS    = 20       # T   how many rounds per session

# ============================================================
# Treatment parameters
# ============================================================
PENALTY_LOW   = 20       # L   penalty for the "low penalty" treatments    -> xbar = sqrt(L*k) ~ 63.2
PENALTY_HIGH  = 40       # L   penalty for the "high penalty" treatments   -> xbar = sqrt(L*k) ~ 89.4

SESSION_SIZE      = 15    # site 2: recruit exactly 15 participants per official session
GROUP_SIZE_SMALL  = 5     # n   a small-arm session contains exactly 3 groups of 5
GROUP_SIZE_LARGE  = 15    # n   a large-arm session contains exactly 1 group of 15

# ============================================================
# Payment parameters
# ============================================================
SHOW_UP_FEE         = 15.00   # RMB (CNY) paid to every participant who completes (regardless of choices)
CURRENCY_PER_POINT  = 0.50    # RMB per 1 oTree point (so 1 point = ¥0.50)
