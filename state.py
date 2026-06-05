"""
state.py
========
Single shared GameState instance that replaces every `global` declaration
in the original code. Import `state` from here in any module that needs
to read or write game state.

Usage in any module:
    from state import state
    state.gold += 50
    state.player_health -= 10
"""

import time
from constants import TYPE_OF_MOUSE


class GameState:
    def __init__(self):

        # ---------------------------------------------------------------
        # Player vitals
        # ---------------------------------------------------------------
        self.player_health: int = 100
        self.player_energy: int = 100
        self.player_hunger: int = 100   # 0 = starving

        # ---------------------------------------------------------------
        # Resources
        # ---------------------------------------------------------------
        self.gold:  int = 0
        self.points: int = 0
        self.wood:  int = 0
        self.food: dict = {
            "apple": 0, "banana": 0, "berries": 0,
            "mushrooms": 0, "frog": 0,
        }

        # ---------------------------------------------------------------
        # Cheese inventory  [name, quantity]
        # ---------------------------------------------------------------
        self.cheese: list = [
            ["Cheddar", 0],
            ["Marble",  0],
            ["Swiss",   0],
        ]

        # ---------------------------------------------------------------
        # Trap inventory  [name, owned, uses_remaining]
        # ---------------------------------------------------------------
        self.trap_option: list = [
            ["Wood-and-Spring Trap",        0, 0],
            ["Reinforced Wood-Cage Trap",   0, 0],
            ["Multilayer Glued-Board Trap", 0, 0],
        ]
        self.current_trap:  str | None = None
        self.trap_cheese:   str | None = None
        self.enchant:      bool = False

        # ---------------------------------------------------------------
        # Crate
        # ---------------------------------------------------------------
        self.crate = None   # set to Crate() once the player gets one

        # ---------------------------------------------------------------
        # World / time
        # ---------------------------------------------------------------
        self.game_time: str = "09 00"
        self.day:       int = 1

        # ---------------------------------------------------------------
        # Session tracking
        # ---------------------------------------------------------------
        self.name:             str  = "Hunter"
        self.carpenter_visit:  int  = 0
        self.trader_visited: bool = False
        self.game_over:       bool  = False
        self.mouse_king_caught: bool = False
        self.start_time:     float  = time.time()
        self.difficulty: int = 0   # 0 = Noob, 1 = Survivalist
        self.minutes_spent:  float  = 0.0

        self.attempts: dict = {
            "Successful hunt":   0,
            "Unsuccessful hunt": 0,
        }
        self.cheese_bought: dict = {
            "Cheddar": 0,
            "Marble":  0,
            "Swiss":   0,
        }
        self.caught_mouse_dictionary: dict = {
            mouse: 0 for mouse in TYPE_OF_MOUSE if mouse is not None
        }

        # ---------------------------------------------------------------
        # Level-up flags  (replaces called_functions dict)
        # ---------------------------------------------------------------
        self.level_flags: dict = {
            "level_check_1": False,
            "level_check_2": False,
            "level_check_3": False,
        }

    # -------------------------------------------------------------------
    # Energy helpers  (replaces restore_energy / drain_energy globals)
    # -------------------------------------------------------------------

    def restore_energy(self, amount: int) -> None:
        from constants import MAX_ENERGY
        self.player_energy = min(MAX_ENERGY, self.player_energy + amount)

    def drain_energy(self, amount: int) -> None:
        self.player_energy = max(0, self.player_energy - amount)

    # -------------------------------------------------------------------
    # Hunger helper
    # -------------------------------------------------------------------

    def drain_hunger(self, amount: int) -> None:
        self.player_hunger = max(0, self.player_hunger - amount)

    # -------------------------------------------------------------------
    # Time helper  (replaces increase_time + day global)
    # -------------------------------------------------------------------

    def increase_time(self, increment: int) -> None:
        """Advance game clock by `increment` hours, rolling over days."""
        hour = int(self.game_time.split()[0])
        new_hour = hour + increment
        if new_hour >= 24:
            self.day += 1
            print(f"\n--- Day {self.day} begins ---\n")
        self.game_time = f"{new_hour % 24:02d} 00"

    # -------------------------------------------------------------------
    # Convenience read
    # -------------------------------------------------------------------

    def is_daytime(self) -> bool:
        hour = int(self.game_time.split()[0])
        return 6 <= hour <= 18

    def count_food(self) -> int:
        return sum(self.food.values())

    def count_cheese(self) -> int:
        return sum(qty for _, qty in self.cheese)
    

# -------------------------------------------------------------------
# Difficulty helper  (single lookup point for all difficulty values)
# -------------------------------------------------------------------

    def diff(self, key: str):
        """
        Return the difficulty-scaled value for `key` from DIFFICULTY dict.
        Always use this instead of indexing DIFFICULTY[key][n] directly.
        """
        from constants import DIFFICULTY
        return DIFFICULTY[key][self.difficulty]


# ---------------------------------------------------------------------------
# Single shared instance — import this everywhere
# ---------------------------------------------------------------------------

state = GameState()