"""
tests/test_shops.py
===================
Tests for game/shops.py: cheese buying, trap buying at the Carpenter,
and Witch Doctor healing. All shop menus use input() so we mock it.
"""

import pytest
from unittest.mock import patch, call

from game.shops import (
    _buy_cheese,
    _buy_trap,
    _witch_healing,
    _witch_ancient_ritual,
    _witch_food_submenu,
)
from constants import CHEESE_PRICES, XP_UNLOCK_TIER_1, XP_UNLOCK_TIER_2


# ===========================================================================
# _buy_cheese
# ===========================================================================

class TestBuyCheese:
    def _run(self, inputs, points=0):
        """Helper: patch input and state.points, then call _buy_cheese."""
        from state import state
        state.points = points
        with patch("builtins.input", side_effect=iter(inputs)):
            _buy_cheese()

    def test_buy_cheddar_deducts_gold(self, reset_state):
        reset_state.gold = 100
        self._run(["cheddar 3", "back"])
        assert reset_state.gold == 100 - (3 * CHEESE_PRICES["cheddar"])

    def test_buy_cheddar_adds_to_inventory(self, reset_state):
        reset_state.gold = 50
        self._run(["cheddar 2", "back"])
        assert reset_state.cheese[0][1] == 2

    def test_buy_records_in_cheese_bought(self, reset_state):
        reset_state.gold = 50
        self._run(["cheddar 2", "back"])
        assert reset_state.cheese_bought["Cheddar"] == 2

    def test_insufficient_gold_rejected(self, reset_state, capsys):
        reset_state.gold = 5
        self._run(["cheddar 5", "back"])
        out = capsys.readouterr().out
        assert "enough gold" in out.lower()
        assert reset_state.cheese[0][1] == 0

    def test_xp_locked_marble_rejected(self, reset_state, capsys):
        reset_state.gold = 1000
        self._run(["marble 1", "back"], points=0)
        out = capsys.readouterr().out
        assert "xp" in out.lower()

    def test_marble_unlocked_above_tier1(self, reset_state):
        reset_state.gold = 500
        self._run(["marble 2", "back"], points=XP_UNLOCK_TIER_1)
        assert reset_state.cheese[1][1] == 2

    def test_swiss_locked_below_tier2(self, reset_state, capsys):
        reset_state.gold = 1000
        self._run(["swiss 1", "back"], points=XP_UNLOCK_TIER_1)
        out = capsys.readouterr().out
        assert "xp" in out.lower()

    def test_unknown_cheese_rejected(self, reset_state, capsys):
        reset_state.gold = 100
        self._run(["brie 1", "back"])
        out = capsys.readouterr().out
        assert "don't sell" in out.lower()

    def test_zero_quantity_rejected(self, reset_state, capsys):
        reset_state.gold = 100
        self._run(["cheddar 0", "back"])
        out = capsys.readouterr().out
        assert "negative" in out.lower()

    def test_non_numeric_quantity_rejected(self, reset_state, capsys):
        reset_state.gold = 100
        self._run(["cheddar abc", "back"])
        out = capsys.readouterr().out
        assert "numbers" in out.lower()

    def test_missing_quantity_rejected(self, reset_state, capsys):
        reset_state.gold = 100
        self._run(["cheddar", "back"])
        out = capsys.readouterr().out
        assert "quantity" in out.lower()


# ===========================================================================
# _buy_trap (Carpenter)
# ===========================================================================

class TestBuyTrap:
    def _run(self, inputs, gold=100, wood=20, points=0):
        from state import state
        state.gold   = gold
        state.wood   = wood
        state.points = points
        with patch("builtins.input", side_effect=iter(inputs)):
            _buy_trap()

    def test_buy_basic_trap_deducts_resources(self, reset_state):
        self._run(["1", "0"], gold=100, wood=20, points=0)
        assert reset_state.wood == 20 - 10   # TRAP[0] wood_cost=10
        assert reset_state.gold == 100 - 5   # TRAP[0] gold_cost=5

    def test_buy_basic_trap_sets_ownership(self, reset_state):
        self._run(["1", "0"], gold=100, wood=20, points=0)
        assert reset_state.trap_option[0][1] == 1
        assert reset_state.trap_option[0][2] == 10

    def test_buy_trap_grants_xp(self, reset_state):
        self._run(["1", "0"], gold=100, wood=20, points=0)
        assert reset_state.points == 10

    def test_not_enough_wood_rejected(self, reset_state, capsys):
        self._run(["1", "0"], gold=100, wood=0, points=0)
        out = capsys.readouterr().out
        assert "wood" in out.lower()
        assert reset_state.trap_option[0][1] == 0

    def test_not_enough_gold_rejected(self, reset_state, capsys):
        self._run(["1", "0"], gold=0, wood=20, points=0)
        out = capsys.readouterr().out
        assert "gold" in out.lower()

    def test_xp_locked_trap2_rejected(self, reset_state, capsys):
        self._run(["2", "0"], gold=500, wood=100, points=0)
        out = capsys.readouterr().out
        assert "xp" in out.lower()

    def test_existing_functional_trap_rejected(self, reset_state, capsys):
        reset_state.trap_option[0][2] = 5   # already has durability
        self._run(["1", "0"], gold=100, wood=20, points=0)
        out = capsys.readouterr().out
        assert "still in fine shape" in out.lower()

    def test_invalid_non_digit_input(self, reset_state, capsys):
        self._run(["x", "0"], gold=100, wood=20, points=0)
        out = capsys.readouterr().out
        assert "understand" in out.lower()


# ===========================================================================
# Witch Doctor — _witch_healing
# ===========================================================================

class TestWitchHealing:
    def test_herbal_wrap_restores_hp_on_success(self, reset_state):
        reset_state.gold = 100
        reset_state.player_health = 50
        with patch("game.shops.random.random", return_value=0.5):   # > 0.10 → success
            _witch_healing(1)
        assert reset_state.player_health == 75   # +25
        assert reset_state.gold == 50            # -50

    def test_herbal_wrap_fails_when_no_gold(self, reset_state, capsys):
        reset_state.gold = 0
        reset_state.player_health = 50
        _witch_healing(1)
        out = capsys.readouterr().out
        assert "short" in out.lower() or "cost" in out.lower()
        assert reset_state.player_health == 50

    def test_already_full_health_rejected(self, reset_state, capsys):
        reset_state.gold = 200
        reset_state.player_health = 100
        _witch_healing(1)
        out = capsys.readouterr().out
        assert "full health" in out.lower()
        assert reset_state.gold == 200   # no deduction

    def test_hp_capped_at_100(self, reset_state):
        reset_state.gold = 200
        reset_state.player_health = 90
        with patch("game.shops.random.random", return_value=0.5):
            _witch_healing(3)   # Full Revival +100
        assert reset_state.player_health == 100

    def test_bad_luck_reduces_hp(self, reset_state):
        reset_state.gold = 200
        reset_state.player_health = 80
        with patch("game.shops.random.random", return_value=0.05):   # < 0.10 → bad luck
            _witch_healing(1)
        assert reset_state.player_health == 70   # -10


# ===========================================================================
# Witch Doctor — _witch_ancient_ritual
# ===========================================================================

class TestWitchAncientRitual:
    def test_insufficient_gold_rejected(self, reset_state, capsys):
        reset_state.gold = 100
        _witch_ancient_ritual()
        out = capsys.readouterr().out
        assert "200 gold" in out
        assert reset_state.gold == 100

    def test_player_declines_no_charge(self, reset_state):
        reset_state.gold = 300
        with patch("builtins.input", return_value="no"):
            _witch_ancient_ritual()
        assert reset_state.gold == 300

    def test_ritual_success_restores_hp(self, reset_state):
        reset_state.gold = 300
        reset_state.player_health = 50
        with patch("builtins.input", return_value="yes"), \
             patch("game.shops.random.random", return_value=0.5):   # > 0.20 → success
            _witch_ancient_ritual()
        assert reset_state.player_health == 100
        assert reset_state.gold == 100

    def test_ritual_failure_reduces_hp(self, reset_state):
        reset_state.gold = 300
        reset_state.player_health = 50
        with patch("builtins.input", return_value="yes"), \
             patch("game.shops.random.random", return_value=0.1):   # < 0.20 → fail
            _witch_ancient_ritual()
        assert reset_state.player_health == 45   # -5
        assert reset_state.gold == 100           # still charged


# ===========================================================================
# Witch Doctor — _witch_food_submenu
# ===========================================================================

class TestWitchFoodSubmenu:
    def test_buy_apple_deducts_gold_and_adds_food(self, reset_state):
        reset_state.gold = 50
        with patch("builtins.input", side_effect=["1", "6"]):
            _witch_food_submenu()
        assert reset_state.gold == 45
        assert reset_state.food["apple"] == 1

    def test_buy_frog_deducts_correct_amount(self, reset_state):
        reset_state.gold = 50
        with patch("builtins.input", side_effect=["5", "6"]):
            _witch_food_submenu()
        assert reset_state.gold == 47
        assert reset_state.food["frog"] == 1

    def test_cannot_afford_item(self, reset_state, capsys):
        reset_state.gold = 0
        with patch("builtins.input", side_effect=["1", "6"]):
            _witch_food_submenu()
        out = capsys.readouterr().out
        assert "afford" in out.lower()
        assert reset_state.food["apple"] == 0

    def test_invalid_input_rejected(self, reset_state, capsys):
        reset_state.gold = 50
        with patch("builtins.input", side_effect=["x", "6"]):
            _witch_food_submenu()
        out = capsys.readouterr().out
        assert "clearly" in out.lower()