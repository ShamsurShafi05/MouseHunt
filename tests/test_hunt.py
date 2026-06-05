"""
tests/test_hunt.py
==================
Tests for hunt.py: probability tables, mouse generation, loot lookup,
coat generation, cheese helpers, trap durability, and level-up flag logic.

Notes on Poison mouse:
  Poison was removed from the live game (_LOOT_TABLE, _COAT_TABLE,
  _XP_ALLOWED all omit it).  Tests that previously referenced "Poison"
  have been updated to use real game mice instead.
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
    def test_cheddar_returns_7_tuple(self):
        p = generate_probabilities("cheddar")
        assert len(p) == 7

    def test_cheddar_sums_to_one(self):
        p = generate_probabilities("cheddar")
        assert abs(sum(p) - 1.0) < 1e-9

    def test_marble_sums_to_one(self):
        p = generate_probabilities("marble")
        assert abs(sum(p) - 1.0) < 1e-9

    def test_swiss_normal_sums_to_one(self):
        p = generate_probabilities("swiss", enchant=False)
        assert abs(sum(p) - 1.0) < 1e-9

    def test_swiss_enchanted_sums_to_one(self):
        p = generate_probabilities("swiss", enchant=True)
        assert abs(sum(p) - 1.0) < 1e-9

    def test_swiss_enchanted_has_higher_tiny_prob(self):
        # index 5 = Tiny mouse
        normal    = generate_probabilities("swiss", enchant=False)
        enchanted = generate_probabilities("swiss", enchant=True)
        assert enchanted[5] > normal[5]

    def test_swiss_enchanted_uses_separate_table_key(self):
        normal    = generate_probabilities("swiss", enchant=False)
        enchanted = generate_probabilities("swiss", enchant=True)
        assert normal != enchanted

    def test_unknown_cheese_falls_back_to_cheddar(self):
        assert generate_probabilities("mystery") == generate_probabilities("cheddar")

    def test_case_insensitive(self):
        assert generate_probabilities("Cheddar") == generate_probabilities("cheddar")
        assert generate_probabilities("SWISS")   == generate_probabilities("swiss")

    def test_all_probabilities_non_negative(self):
        for cheese in ("cheddar", "marble", "swiss"):
            for p in generate_probabilities(cheese):
                assert p >= 0


# ===========================================================================
# generate_mouse  (XP gates)
# Swiss probability bands (non-enchanted):
#   miss      : roll < 0.67
#   Brown     : 0.67  <= roll < 0.68
#   Field     : 0.68  <= roll < 0.73
#   Grey      : 0.73  <= roll < 0.78
#   White     : 0.78  <= roll < 0.82
#   Tiny      : 0.82  <= roll < 0.97
#   MouseKing : 0.97  <= roll <= 1.0
# ===========================================================================

class TestGenerateMouse:
    def test_none_mouse_at_tier0(self, reset_state):
        reset_state.points = 0
        with patch("game.hunt.random.random", return_value=0.0):
            result = generate_mouse("cheddar", False, 0)
        assert result is None

    def test_tier0_only_gets_none_or_field(self, reset_state):
        """At tier0 only None and Field are allowed; everything else re-rolls."""
        reset_state.points = 0
        results = set()
        for i in range(20):
            rolls = iter([i / 20.0, 0.0])
            with patch("game.hunt.random.random", side_effect=rolls):
                r = generate_mouse("cheddar", False, 0)
            results.add(r)
        assert results.issubset({None, "Field"})

    def test_tier1_allows_brown_grey_white(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_1
        # Brown band on swiss: 0.675
        with patch("game.hunt.random.random", return_value=0.675):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result == "Brown"

    def test_tier2_allows_tiny(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2
        # Tiny band on swiss: 0.90
        with patch("game.hunt.random.random", return_value=0.90):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result == "Tiny"

    def test_mouseking_blocked_before_tier3(self, reset_state):
        """MouseKing requires tier3; at tier2 the roll re-rolls until a valid type."""
        reset_state.points = XP_UNLOCK_TIER_2
        # MouseKing roll (0.99) should re-roll; supply miss (0.0) as the retry
        rolls = iter([0.99, 0.0])
        with patch("game.hunt.random.random", side_effect=rolls):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result != "MouseKing"

    def test_tier3_allows_mouse_king(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3
        # MouseKing band: roll >= 0.97
        with patch("game.hunt.random.random", return_value=0.99):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result == "MouseKing"

    def test_tier3_allows_tiny(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3
        with patch("game.hunt.random.random", return_value=0.90):
            result = generate_mouse("swiss", False, reset_state.points)
        assert result == "Tiny"

    def test_enchant_boosts_tiny_spawn(self, reset_state):
        """Swiss enchanted raises Tiny probability — more Tiny spawns in repeated rolls."""
        reset_state.points = XP_UNLOCK_TIER_2
        tiny_normal = tiny_enchanted = 0
        trials = 200
        for _ in range(trials):
            r = generate_mouse("swiss", False, reset_state.points)
            if r == "Tiny":
                tiny_normal += 1
        for _ in range(trials):
            r = generate_mouse("swiss", True, reset_state.points)
            if r == "Tiny":
                tiny_enchanted += 1
        assert tiny_enchanted >= tiny_normal


# ===========================================================================
# loot_lut
# ===========================================================================

class TestLootLut:
    def test_none_mouse_zero_gold_one_xp(self):
        gold, pts = loot_lut(None)
        assert gold == 0 and pts == 1

    def test_brown_mouse_loot(self):
        gold, pts = loot_lut("Brown")
        assert gold == 70 and pts == 60

    def test_field_mouse_loot(self):
        gold, pts = loot_lut("Field")
        assert gold == 15 and pts == 20

    def test_grey_mouse_loot(self):
        gold, pts = loot_lut("Grey")
        assert gold == 60 and pts == 50

    def test_white_mouse_loot(self):
        gold, pts = loot_lut("White")
        assert gold == 80 and pts == 70

    def test_tiny_mouse_loot(self):
        gold, pts = loot_lut("Tiny")
        assert gold == 100 and pts == 100

    def test_mouse_king_zero_gold_200_xp(self):
        """MouseKing gives no gold (boss fight) but maximum XP."""
        gold, pts = loot_lut("MouseKing")
        assert gold == 0 and pts == 200

    def test_unknown_mouse_returns_zeros(self):
        gold, pts = loot_lut("Alien")
        assert gold == 0 and pts == 0

    def test_all_real_mice_have_positive_xp(self):
        for name in ("Brown", "Field", "Grey", "White", "Tiny"):
            _, pts = loot_lut(name)
            assert pts > 0, f"{name} should give XP"


# ===========================================================================
# generate_coat
# ===========================================================================

class TestGenerateCoat:
    def test_known_coats_return_non_empty_strings(self):
        # Poison was removed; only live mice are tested
        for name in ("Tiny", "Brown", "White", "Grey", "Field", "MouseKing"):
            coat = generate_coat(name)
            assert isinstance(coat, str) and len(coat) > 0, \
                f"Expected non-empty coat for {name}"

    def test_none_mouse_returns_empty_string(self):
        assert generate_coat(None) == ""

    def test_unknown_mouse_returns_empty_string(self):
        assert generate_coat("Alien") == ""

    def test_coat_contains_mouse_name_or_art(self):
        """Coats should be multi-line ASCII art strings."""
        coat = generate_coat("Brown")
        assert "\n" in coat


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

    def test_has_cheese_marble(self, reset_state):
        reset_state.cheese[1][1] = 2
        assert has_cheese("Marble") == 2

    def test_has_cheese_swiss(self, reset_state):
        reset_state.cheese[2][1] = 1
        assert has_cheese("Swiss") == 1

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

    def test_consume_returns_false_on_unknown_cheese(self, reset_state):
        result = consume_cheese("Brie")
        assert result is False


# ===========================================================================
# _decrement_trap
# ===========================================================================

class TestDecrementTrap:
    def test_decrement_reduces_durability(self, reset_state):
        reset_state.trap_option[0] = ["Wood-and-Spring Trap", 1, 5]
        _decrement_trap("Wood-and-Spring Trap")
        assert reset_state.trap_option[0][2] == 4

    def test_trap_marked_broken_at_zero(self, reset_state):
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
        assert reset_state.trap_option[0][2] == 0

    def test_decrement_correct_trap_by_name(self, reset_state):
        """Decrement targets the named trap, not index 0."""
        reset_state.trap_option[1] = ["Reinforced Wood-Cage Trap", 1, 8]
        _decrement_trap("Reinforced Wood-Cage Trap")
        assert reset_state.trap_option[1][2] == 7
        # Other traps untouched
        assert reset_state.trap_option[0][2] == 0

    def test_unknown_trap_name_no_crash(self, reset_state):
        """Gracefully handles a trap name not in the list."""
        _decrement_trap("Phantom Trap")   # should not raise


# ===========================================================================
# _check_level_flags
# ===========================================================================

class TestLevelFlags:
    def test_level1_flag_fires_at_threshold(self, reset_state, capsys):
        reset_state.points = XP_UNLOCK_TIER_1
        _check_level_flags()
        assert reset_state.level_flags["level_check_1"] is True

    def test_level1_flag_does_not_fire_before_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_1 - 1
        _check_level_flags()
        assert reset_state.level_flags["level_check_1"] is False

    def test_level1_flag_fires_only_once(self, reset_state, capsys):
        reset_state.points = XP_UNLOCK_TIER_1
        _check_level_flags()
        capsys.readouterr()
        _check_level_flags()
        out = capsys.readouterr().out
        assert "Marble" not in out

    def test_level2_flag_fires_at_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2
        reset_state.level_flags["level_check_1"] = True
        _check_level_flags()
        assert reset_state.level_flags["level_check_2"] is True

    def test_level2_flag_does_not_fire_before_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2 - 1
        reset_state.level_flags["level_check_1"] = True
        _check_level_flags()
        assert reset_state.level_flags["level_check_2"] is False

    def test_level3_flag_fires_at_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3
        reset_state.level_flags["level_check_1"] = True
        reset_state.level_flags["level_check_2"] = True
        _check_level_flags()
        assert reset_state.level_flags["level_check_3"] is True

    def test_level3_flag_does_not_fire_before_threshold(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3 - 1
        reset_state.level_flags["level_check_1"] = True
        reset_state.level_flags["level_check_2"] = True
        _check_level_flags()
        assert reset_state.level_flags["level_check_3"] is False

    def test_all_three_flags_fire_at_max_xp(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3 + 50
        _check_level_flags()
        assert reset_state.level_flags["level_check_1"] is True
        assert reset_state.level_flags["level_check_2"] is True
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

    def test_miss_returns_none_mouse(self, reset_state):
        reset_state.difficulty = 0
        with patch("game.hunt.random.random", return_value=0.0):
            m = spawn_mouse("cheddar", False, 0)
        assert m.get_name() is None

    def test_tiny_mouse_has_correct_pts(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_2
        # Tiny band on swiss: roll=0.90
        with patch("game.hunt.random.random", return_value=0.90):
            m = spawn_mouse("swiss", False, reset_state.points)
        assert m.name == "Tiny"
        assert m.get_points() == 100

    def test_mouse_king_has_correct_pts(self, reset_state):
        reset_state.points = XP_UNLOCK_TIER_3
        with patch("game.hunt.random.random", return_value=0.99):
            m = spawn_mouse("swiss", False, reset_state.points)
        assert m.name == "MouseKing"
        assert m.get_points() == 200

    def test_survivalist_miss_bonus_forces_miss(self, reset_state):
        """On Survivalist (diff=1), hunt_miss_bonus=0.08: roll < 0.08 → forced miss."""
        reset_state.difficulty = 1
        reset_state.points = XP_UNLOCK_TIER_2
        # First random() call is the miss-bonus check (0.01 < 0.08 → forced miss)
        with patch("game.hunt.random.random", return_value=0.01):
            m = spawn_mouse("swiss", False, reset_state.points)
        assert m.get_name() is None