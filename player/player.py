"""
player/player.py
================
Player setup: name validation and difficulty selection.
Both functions write to state directly — no parameters, no return values.
"""

from state import state
from constants import START_GOLD


# ---------------------------------------------------------------------------
# Name validation helpers  (pure functions — no state, no side effects)
# ---------------------------------------------------------------------------

def _is_valid_length(name: str) -> bool:
    return 1 <= len(name) <= 9


def _is_valid_start(name: str) -> bool:
    return len(name) > 0 and name[0].isalpha()


def _is_one_word(name: str) -> bool:
    return len(name) > 0 and " " not in name


def _is_valid_name(name: str) -> bool:
    """
    Print a specific error for each rule broken,
    then return True only if all rules pass.
    """
    valid = True
    if not _is_valid_length(name):
        print("Name must be between 1 and 9 characters.")
        valid = False
    if not _is_valid_start(name):
        print("Name must start with a letter.")
        valid = False
    if not _is_one_word(name):
        print("Name must be a single word.")
        valid = False
    return valid


# ---------------------------------------------------------------------------
# Name setup  (writes state.name)
# ---------------------------------------------------------------------------

def setup_name() -> None:
    """Prompt for a hunter name and store it in state.name."""
    print("What's ye name, Hunter?")
    name = input().strip()

    attempts_remaining = 3
    while not _is_valid_name(name) and attempts_remaining > 0:
        print(f"You have {attempts_remaining} tries remaining.")
        name = input("Re-enter your name, Hunter: ").strip()
        attempts_remaining -= 1

    if not _is_valid_name(name):
        name = "Bob"
        print("\nOur systems have decided to name you Bob!\n")

    state.name = name
    print(f"Welcome to the Kingdom, Hunter {state.name}!")


# ---------------------------------------------------------------------------
# Difficulty setup  (writes state.gold)
# ---------------------------------------------------------------------------

def setup_difficulty() -> None:
    """Prompt for difficulty and set starting gold in state."""
    while True:
        difficulty = input(
            "\nChoose game difficulty:\n"
            "1. Noob\n"
            "2. Adventurer\n"
            "3. Survivalist\n"
        ).strip()

        if not difficulty.isdigit():
            print("Invalid option.\n")
            continue

        choice = int(difficulty)
        if choice < 1 or choice > 3:
            print("Invalid option.\n")
            continue

        if choice == 1:
            print("Oh my.. with such little nerve, you might not come out alive from what awaits you..")
        elif choice == 2:
            print("A rational thinker, I see. Too scared to risk it, are we..")
        else:
            print("Daring, are we? We all sometimes live to regret the decisions we make. Will you too..")

        state.gold += START_GOLD[choice - 1]
        break