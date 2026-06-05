"""
tests/test_player.py
====================
Tests for player/player.py: name validation helpers and difficulty setup.

The game has TWO difficulty levels (index 0=Noob, index 1=Survivalist).
Starting gold comes from DIFFICULTY["start_gold"][difficulty_index].
There is no START_GOLD constant and no third "Adventurer" option.
"""

import pytest
from unittest.mock import patch

from player.player import (
    _is_valid_length,
    _is_valid_start,
    _is_one_word,
    _is_valid_name,
    setup_name,
    setup_difficulty,
)
from constants import DIFFICULTY

# Convenience aliases matching the two real difficulty levels
NOOB_GOLD        = DIFFICULTY["start_gold"][0]   # 200
SURVIVALIST_GOLD = DIFFICULTY["start_gold"][1]   # 125


# ===========================================================================
# Name validation helpers  (pure functions — no state)
# ===========================================================================

class TestIsValidLength:
    def test_empty_string_invalid(self):
        assert not _is_valid_length("")

    def test_single_char_valid(self):
        assert _is_valid_length("A")

    def test_nine_chars_valid(self):
        assert _is_valid_length("Abcdefghi")

    def test_ten_chars_invalid(self):
        assert not _is_valid_length("Abcdefghij")

    def test_max_boundary_exactly_9(self):
        assert _is_valid_length("123456789")

    def test_min_boundary_exactly_1(self):
        assert _is_valid_length("X")


class TestIsValidStart:
    def test_letter_start_valid(self):
        assert _is_valid_start("Alice")

    def test_digit_start_invalid(self):
        assert not _is_valid_start("1Alice")

    def test_empty_string_invalid(self):
        assert not _is_valid_start("")

    def test_underscore_start_invalid(self):
        assert not _is_valid_start("_Alice")

    def test_uppercase_letter_valid(self):
        assert _is_valid_start("Bob")

    def test_space_start_invalid(self):
        assert not _is_valid_start(" Alice")


class TestIsOneWord:
    def test_single_word_valid(self):
        assert _is_one_word("Hunter")

    def test_two_words_invalid(self):
        assert not _is_one_word("John Doe")

    def test_empty_invalid(self):
        assert not _is_one_word("")

    def test_trailing_space_invalid(self):
        assert not _is_one_word("Alice ")

    def test_leading_space_invalid(self):
        assert not _is_one_word(" Alice")


class TestIsValidName:
    def test_valid_name_passes(self):
        assert _is_valid_name("Alice")

    def test_too_long_fails(self):
        assert not _is_valid_name("Abcdefghij")   # 10 chars

    def test_starts_with_digit_fails(self):
        assert not _is_valid_name("1Abc")

    def test_two_words_fails(self):
        assert not _is_valid_name("John Doe")

    def test_empty_fails(self):
        assert not _is_valid_name("")

    def test_all_rules_pass_for_normal_name(self):
        assert _is_valid_name("Hunter")

    def test_single_letter_passes(self):
        assert _is_valid_name("A")


# ===========================================================================
# setup_name  (writes state.name)
# ===========================================================================

class TestSetupName:
    def test_valid_name_stored(self, reset_state):
        with patch("builtins.input", return_value="Archer"):
            setup_name()
        assert reset_state.name == "Archer"

    def test_defaults_to_bob_after_max_failed_attempts(self, reset_state):
        # All inputs invalid (too long, 10 chars)
        with patch("builtins.input", return_value="Abcdefghij"):
            setup_name()
        assert reset_state.name == "Bob"

    def test_second_attempt_valid_name_accepted(self, reset_state):
        responses = iter(["1InvalidName", "ValidName"])
        with patch("builtins.input", side_effect=responses):
            setup_name()
        assert reset_state.name == "ValidName"

    def test_name_with_spaces_rejected_then_valid(self, reset_state):
        responses = iter(["John Doe", "John Doe", "John Doe", "John"])
        with patch("builtins.input", side_effect=responses):
            setup_name()
        assert reset_state.name == "John"

    def test_stripped_name_stored(self, reset_state):
        """Leading/trailing whitespace is stripped before validation."""
        with patch("builtins.input", return_value="  Alice  "):
            setup_name()
        # "Alice" (stripped) is valid
        assert reset_state.name == "Alice"


# ===========================================================================
# setup_difficulty  (writes state.gold and state.difficulty)
# ===========================================================================

class TestSetupDifficulty:
    def test_noob_sets_correct_gold(self, reset_state):
        reset_state.gold = 0
        with patch("builtins.input", return_value="1"):
            setup_difficulty()
        assert reset_state.gold == NOOB_GOLD

    def test_noob_sets_difficulty_index_0(self, reset_state):
        with patch("builtins.input", return_value="1"):
            setup_difficulty()
        assert reset_state.difficulty == 0

    def test_survivalist_sets_correct_gold(self, reset_state):
        reset_state.gold = 0
        with patch("builtins.input", return_value="2"):
            setup_difficulty()
        assert reset_state.gold == SURVIVALIST_GOLD

    def test_survivalist_sets_difficulty_index_1(self, reset_state):
        with patch("builtins.input", return_value="2"):
            setup_difficulty()
        assert reset_state.difficulty == 1

    def test_noob_gets_more_gold_than_survivalist(self, reset_state):
        assert NOOB_GOLD > SURVIVALIST_GOLD

    def test_invalid_non_digit_then_valid(self, reset_state):
        reset_state.gold = 0
        responses = iter(["x", "abc", "1"])
        with patch("builtins.input", side_effect=responses):
            setup_difficulty()
        assert reset_state.gold == NOOB_GOLD

    def test_out_of_range_then_valid(self, reset_state):
        reset_state.gold = 0
        responses = iter(["0", "3", "99", "2"])
        with patch("builtins.input", side_effect=responses):
            setup_difficulty()
        assert reset_state.gold == SURVIVALIST_GOLD

    def test_gold_accumulates_on_existing_balance(self, reset_state):
        """Difficulty gold is added to existing balance, not a reset."""
        reset_state.gold = 50
        with patch("builtins.input", return_value="1"):
            setup_difficulty()
        assert reset_state.gold == 50 + NOOB_GOLD