"""
===================================================
All fixed game data that never changes at runtime.
===================================================
"""

# ---------------------------------------------------------------------------
# Mouse types
# ---------------------------------------------------------------------------

TYPE_OF_MOUSE = (None, "Brown", "Field", "Grey", "White", "Tiny", "Poison")

# ---------------------------------------------------------------------------
# Cheese
# ---------------------------------------------------------------------------

# (name, gold_price)
CHEESE_MENU = (
    ("Cheddar", 10),
    ("Marble",  50),
    ("Swiss",  100),
)

CHEESE_PRICES = {
    "cheddar": 10,
    "marble":  50,
    "swiss":  100,
}

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

# (name, wood_cost, gold_cost, durability_in_hunts)
TRAP = (
    ("Wood-and-Spring Trap",       10,  5, 10),
    ("Reinforced Wood-Cage Trap",  30, 15, 20),
    ("Multilayer Glued-Board Trap", 50, 50, 15),
)

# ---------------------------------------------------------------------------
# Food
# ---------------------------------------------------------------------------

FOOD_ENERGY = {
    "apple":     10,
    "banana":    15,
    "berries":    8,
    "mushrooms": 20,
    "frog":       5,
}

FOOD_HUNGER = {
    "apple":     20,
    "banana":    25,
    "berries":   15,
    "mushrooms": 30,
    "frog":      10,
}

# ---------------------------------------------------------------------------
# Starting gold per difficulty  (index 0 = Noob, 1 = Adventurer, 2 = Survivalist)
# ---------------------------------------------------------------------------

START_GOLD = (200, 150, 125)

# ---------------------------------------------------------------------------
# Energy costs
# ---------------------------------------------------------------------------

MAX_ENERGY         = 100
ENERGY_HUNT_COST   = 15
ENERGY_SCAVENGE_COST = 10
ENERGY_TRAVEL_COST =  5
ENERGY_ANIMAL_COST = 10

# ---------------------------------------------------------------------------
# Hunger drain per action
# ---------------------------------------------------------------------------

HUNGER_DRAIN_HUNT     = 10
HUNGER_DRAIN_TRAVEL   =  5
HUNGER_DRAIN_SCAVENGE =  8

# ---------------------------------------------------------------------------
# XP thresholds for unlocks
# ---------------------------------------------------------------------------

XP_UNLOCK_TIER_1 = 100   # Marble cheese, Reinforced trap, new mice
XP_UNLOCK_TIER_2 = 300   # Swiss cheese, Multilayer trap, enchantment
XP_UNLOCK_TIER_3 = 500   # Poison mouse, win condition