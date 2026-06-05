"""
tests/test_hunt.py
==================
Tests for hunt.py: probability tables, mouse generation, loot lookup,
cheese helpers, trap durability, and level-up flag logic.
"""

import pytest
from unittest.mock import patch

from game.hunt import (
    generate_probabilities,
    generate_mouse,
    loot_lut,
    generate_coat,
    spawn_mouse,
    has_cheese,
    consume_cheese,
    _check_level_flags,
    _decrement_trap,
)
from constants import XP_UNLOCK_TIER_1, XP_UNLOCK_TIER_2, XP_UNLOCK_TIER_3


# ===========================================================================
# generate_probabilities
# ===========================================================================

class TestGenerateProbabilities:
    def test_cheddar_returns_tuple(self):
        p = generate_probabilities("cheddar")
        assert len(p) == 7
        assert abs(sum(p) - 1.0) < 1e-9

    def test_marble_sums_to_one(self):
        p = generate_probabilities("marble")
        assert abs(sum(p) - 1.0) < 1e-9

    def test_swiss_normal_sums_to_one(self):
        p = generate_probabilities("swiss", enchant=False)
        assert abs(sum(p) - 1.0) < 1e-9

    def test_swiss_enchanted_has_higher_tiny_prob(self):
        normal   = generate_probabilities("swiss", enchant=False)
        enchanted = generate_probabilities("swiss", enchant=True)
        assert enchanted[5] > normal[5]   # index 5 = Tiny

    def test_unknown_cheese_falls_back_to_cheddar(self):
        assert generate_probabilities("mystery") == generate_probabilities("cheddar")

    def test_case_insensitive(self):
        assert generate_probabilities("Cheddar") == generate_probabilities("cheddar")


# ===========================================================================
# generate_mouse  (XP gates)
# ===========================================================================

class TestGenerateMouse:
    """Patch random.random to force deterministic outcomes."""

    def test_none_mouse_at_tier0(self, reset_state):
        reset_state.points = 0
        # Force a miss (random < miss probability)
        with patch("game.hunt.random.random", return_value=0.0):
            result = generate_mouse("cheddar", False, 0)
        assert result is None

    def test_poison_blocked_before_tier3(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2 + 1   # tier 2, not 3
        # First roll would give Poison (0.999), second gives a miss (0.0).
        # generate_mouse re-rolls until an allowed type is returned.
        rolls = iter([0.999, 0.0])
        with patch("game.hunt.random.random", side_effect=rolls):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result != "Poison"

    def test_tier0_only_gets_none_or_field(self, reset_state):
        """At tier0 only None and Field are allowed; everything else re-rolls.
        Supply alternating rolls: first roll picks a band, second is 0.0 (miss)
        so the loop always exits on retry.
        """
        reset_state.points = 0
        results = set()
        # Use deterministic pairs: (trial roll, fallback miss roll)
        for i in range(20):
            rolls = iter([i / 20.0, 0.0])
            with patch("game.hunt.random.random", side_effect=rolls):
                r = generate_mouse("cheddar", False, 0)
            results.add(r)
        assert results.issubset({None, "Field"})

    def test_tier3_allows_poison(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3 + 1
        # 0.999 lands in Poison probability band for swiss cheese
        with patch("game.hunt.random.random", return_value=0.999):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result == "Poison"


# ===========================================================================
# loot_lut
# ===========================================================================

class TestLootLut:
    def test_none_mouse_zero_loot(self):
        gold, pts = loot_lut(None)
        assert gold == 0 and pts == 1

    def test_tiny_mouse_loot(self):
        gold, pts = loot_lut("Tiny")
        assert gold == 100 and pts == 100

    def test_poison_mouse_zero_gold(self):
        gold, pts = loot_lut("Poison")
        assert gold == 0
        assert pts == 150

    def test_brown_mouse_loot(self):
        gold, pts = loot_lut("Brown")
        assert gold == 70 and pts == 60

    def test_unknown_mouse_returns_zeros(self):
        gold, pts = loot_lut("Alien")
        assert gold == 0 and pts == 0


# ===========================================================================
# generate_coat
# ===========================================================================

class TestGenerateCoat:
    def test_known_coats_return_strings(self):
        for name in ("Tiny", "Brown", "White", "Grey", "Field", "Poison"):
            coat = generate_coat(name)
            assert isinstance(coat, str) and len(coat) > 0

    def test_none_mouse_returns_empty_string(self):
        assert generate_coat(None) == ""

    def test_unknown_mouse_returns_empty_string(self):
        assert generate_coat("Alien") == ""


# ===========================================================================
# has_cheese / consume_cheese
# ===========================================================================

class TestCheeseHelpers:
    def test_has_cheese_zero_when_empty(self, reset_state):
        assert has_cheese("Cheddar") == 0

    def test_has_cheese_returns_quantity(self, reset_state):
        reset_state.cheese[0][1] = 5
        assert has_cheese("Cheddar") == 5

    def test_has_cheese_case_insensitive(self, reset_state):
        reset_state.cheese[0][1] = 3
        assert has_cheese("cheddar") == 3

    def test_consume_cheese_reduces_quantity(self, reset_state):
        reset_state.cheese[0][1] = 3
        result = consume_cheese("Cheddar")
        assert result is True
        assert reset_state.cheese[0][1] == 2

    def test_consume_cheese_fails_when_empty(self, reset_state):
        result = consume_cheese("Cheddar")
        assert result is False

    def test_consume_cheese_does_not_go_negative(self, reset_state):
        reset_state.cheese[0][1] = 1
        consume_cheese("Cheddar")
        assert reset_state.cheese[0][1] == 0
        result = consume_cheese("Cheddar")
        assert result is False


# ===========================================================================
# _decrement_trap
# ===========================================================================

class TestDecrementTrap:
    def test_decrement_reduces_durability(self, reset_state):
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 5]
        _decrement_trap("Wood-and-Spring Trap")
        assert reset_state.trap_option[0][2] == 4

    def test_trap_marked_broken_at_zero(self, reset_state, capsys):
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 1]
        _decrement_trap("Wood-and-Spring Trap")
        assert reset_state.trap_option[0][2] == 0
        assert reset_state.trap_option[0][1] == 0

    def test_broken_trap_prints_warning(self, reset_state, capsys):
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 1]
        _decrement_trap("Wood-and-Spring Trap")
        out = capsys.readouterr().out
        assert "broken" in out.lower()

    def test_already_broken_trap_not_decremented(self, reset_state):
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 0, 0]
        _decrement_trap("Wood-and-Spring Trap")
        assert reset_state.trap_option[0][2] == 0   # stays 0


# ===========================================================================
# _check_level_flags
# ===========================================================================

class TestLevelFlags:
    def test_level1_flag_fires_at_threshold(self, reset_state, capsys):
        reset_state.points = XP_UNLOCK_TIER_1
        _check_level_flags()
        assert reset_state.level_flags["level_check_1"] is True

    def test_level1_flag_does_not_fire_before_threshold(self, reset_state, capsys):
        reset_state.points = XP_UNLOCK_TIER_1 - 1
        _check_level_flags()
        assert reset_state.level_flags["level_check_1"] is False

    def test_level1_flag_fires_only_once(self, reset_state, capsys):
        reset_state.points = XP_UNLOCK_TIER_1
        _check_level_flags()
        capsys.readouterr()   # clear output
        _check_level_flags()  # second call
        out = capsys.readouterr().out
        # The level-up message should NOT appear a second time
        assert "Marble" not in out

    def test_level2_flag_fires_at_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2
        reset_state.level_flags["level_check_1"] = True   # suppress tier-1 re-fire
        _check_level_flags()
        assert reset_state.level_flags["level_check_2"] is True

    def test_level3_flag_fires_at_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3
        reset_state.level_flags["level_check_1"] = True
        reset_state.level_flags["level_check_2"] = True
        _check_level_flags()
        assert reset_state.level_flags["level_check_3"] is True


# ===========================================================================
# spawn_mouse  (integration: roll → loot → coat → Mouse)
# ===========================================================================

class TestSpawnMouse:
    def test_returns_mouse_object(self, reset_state):
        from models.mouse import Mouse
        with patch("game.hunt.random.random", return_value=0.0):
            m = spawn_mouse("cheddar", False, 0)
        assert isinstance(m, Mouse)

    def test_poison_mouse_has_correct_pts(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3 + 1
        with patch("game.hunt.random.random", return_value=0.999):
            m = spawn_mouse("swiss", False, reset_state.points)
        assert m.name == "Poison"
        assert m.get_points() == 150
