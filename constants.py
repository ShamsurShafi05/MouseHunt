"""
===================================================
All fixed game data that never changes at runtime.
===================================================
"""

# ---------------------------------------------------------------------------
# Mouse types
# ---------------------------------------------------------------------------

TYPE_OF_MOUSE = (None, "Brown", "Field", "Grey", "White", "Tiny", "MouseKing")

# ---------------------------------------------------------------------------
# Cheese
# ---------------------------------------------------------------------------

CHEESE_MENU = (
    ("Cheddar",  10),
    ("Marble",   50),
    ("Swiss",   100),
)

CHEESE_PRICES = {
    "cheddar": 10,
    "marble":  50,
    "swiss":  100,
}

# ---------------------------------------------------------------------------
# Traps  (name, wood_cost, gold_cost, durability_in_hunts)
# ---------------------------------------------------------------------------

TRAP = (
    ("Wood-and-Spring Trap",        10,  5, 10),
    ("Reinforced Wood-Cage Trap",   30, 15, 20),
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
# Difficulty settings
# Index 0 = Noob, Index 1 = Survivalist
# ---------------------------------------------------------------------------

DIFFICULTY_NAMES = ("Noob", "Survivalist")

DIFFICULTY = {
    # Starting gold
    "start_gold":               (200, 125),

    # Base hunt miss-rate modifier (added on top of cheese probability)
    # Noob: no penalty. Survivalist: 8% extra miss chance.
    "hunt_miss_bonus":          (0.00, 0.08),

    # Trap durability multipliers (applied to TRAP[i][3])
    "trap_durability_mult":     (1.0, 0.70),

    # Cheese price multipliers
    "cheese_price_mult":        (1.0, 1.10),

    # Trap price multipliers
    "trap_price_mult":          (1.0, 1.15),

    # Animal attack chance (day): risk1, risk2 thresholds
    "animal_risk_day":          ((0.10, 0.20), (0.20, 0.25)),

    # Animal attack chance (night): risk1, risk2 thresholds
    "animal_risk_night":        ((0.50, 0.60), (0.55, 0.70)),

    # Extra energy drain per action (added on top of base constants)
    "energy_drain_bonus":       (0, 2),

    # Extra hunger drain per action
    "hunger_drain_bonus":       (0, 1),

    # Witch Doctor potion HP restore amounts (Herbal, Bone Brew, Full Revival)
    "witch_hp_restore":         ((25, 50, 100), (20, 40, 80)),

    # Witch Doctor food price bonus (added to base price per item)
    "witch_food_price_bonus":   (0, 2),

    # Scavenge success rate (0.0–1.0; rolls below this = something found)
    "scavenge_success_rate":    (0.75, 0.65),

    # HP lost from travel events (rock scrape, rain drench): (min, max)
    "travel_damage_range":      ((1, 2), (2, 4)),
}

# ---------------------------------------------------------------------------
# Energy costs
# ---------------------------------------------------------------------------

MAX_ENERGY           = 100
ENERGY_HUNT_COST     =   8
ENERGY_SCAVENGE_COST =   5
ENERGY_TRAVEL_COST   =   3
ENERGY_ANIMAL_COST   =   6

# ---------------------------------------------------------------------------
# Hunger drain per action
# ---------------------------------------------------------------------------

HUNGER_DRAIN_HUNT     =  5
HUNGER_DRAIN_TRAVEL   =  3
HUNGER_DRAIN_SCAVENGE =  3

# ---------------------------------------------------------------------------
# XP thresholds for unlocks
# ---------------------------------------------------------------------------

XP_UNLOCK_TIER_1 = 100    # Marble cheese, Reinforced trap, new mice
XP_UNLOCK_TIER_2 = 300    # Swiss cheese, Multilayer trap, enchantment
XP_UNLOCK_TIER_3 = 500    # Mouse King unlocked — catch him to win

# ---------------------------------------------------------------------------
# Travel events  (message, base_damage — overridden by difficulty range)
# ---------------------------------------------------------------------------

TRAVEL_EVENTS = (
    ("You trip over a sharp rock and scrape your leg!",          1),
    ("A sudden drizzle hits and you're soaked and shivering.",   2),
    ("A branch whips your face as you push through the brush.",  1),
    ("You slip on wet mud and twist your ankle.",                 2),
    ("A thorn bush catches your arm as you pass.",               1),
)