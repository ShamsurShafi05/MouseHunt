"""
tutorial/tutorial.py
====================
Larry's introductory tutorial sequence.
Self-contained — does not read or write state since the tutorial
uses dummy traps and cheese that don't carry over to the real game.
"""


# ---------------------------------------------------------------------------
# Individual tutorial steps  (all return False on ESC to allow early exit)
# ---------------------------------------------------------------------------

def _intro() -> None:
    print("``````````````````````````````````````````````````")
    print("                 TUTORIAL                         \n")
    print("Larry: Hi! I'm Larry. I'll be your hunting instructor.")


def _travel_to_camp() -> bool:
    """Returns False if the player presses ESC."""
    print("Larry: Let's go to the Meadow to begin your training!")
    value = input("Press Enter to travel to the Meadow...").strip()
    if value == chr(27):
        return False
    print("Travelling to the Meadow...")
    print("Larry: This is your camp. Here you'll set up your mouse trap.")
    return True


def _setup_trap() -> tuple | bool:
    """
    Returns a (trap_name, has_cheese: int) tuple on success,
    or False if the player presses ESC.
    """
    print("\nLarry: Let's get your first trap...")
    val = input("Press Enter to view the traps Larry is holding...").strip()
    if val == chr(27):
        return False

    print("Larry is holding...")
    print("  Left:  Wood-and-Spring Trap")
    print("  Right: Reinforced Wood-Cage Trap")
    trap_input = input('Select a trap by typing "left" or "right": ').strip()

    if trap_input == chr(27):
        return False

    if trap_input.lower() in ("left", "right"):
        trap_name = (
            "Wood-and-Spring Trap" if trap_input.lower() == "left"
            else "Reinforced Wood-Cage Trap"
        )
        print(f"Larry: Excellent choice.")
        print(f"Your {trap_name} is now set!")
        print("Larry: You need cheese to attract a mouse.")
        print("Larry places one Cheddar on the trap!")
        return (trap_name, 1)
    else:
        print("Invalid command! No trap selected.")
        print("Larry: Odds are slim with no trap!")
        return ("Wood-and-Spring Trap", 0)


def _sound_horn(trap_result: tuple) -> str | bool:
    """
    Returns "success" on a valid catch, False on ESC,
    or the raw input string otherwise.
    """
    print("\nSound the horn to call for the mouse...")
    horn = input('Sound the horn by typing "yes": ').strip().lower()

    if horn == chr(27):
        return False

    has_trap_and_cheese = trap_result[1] == 1

    if horn == "yes" and has_trap_and_cheese:
        print("Caught a Brown mouse!")
        print("Congratulations. Ye have completed the training.\nGood luck~")
        return "success"
    elif horn == "yes" and not has_trap_and_cheese:
        print("Nothing happens.\nTo catch a mouse, you need both a trap and cheese!")
    else:
        print("Nothing happens.")

    return horn


# ---------------------------------------------------------------------------
# Dead code from original — kept for reference, not called anywhere
# ---------------------------------------------------------------------------

def _basic_hunt(cheddar: int, horn_input: str) -> bool:
    """Unused in original. Kept for reference."""
    if cheddar == 1 and horn_input.lower() == "yes":
        print("Caught a Brown mouse!")
        return True
    elif cheddar == 0 and horn_input.lower() == "yes":
        print("Larry: Nothing happens.")
        return False
    return False


# ---------------------------------------------------------------------------
# Main tutorial entry point
# ---------------------------------------------------------------------------

def run_tutorial() -> None:
    """
    Run Larry's full tutorial sequence.
    The player can skip individual steps with ESC or exit with 'no'.
    Nothing here writes to state — tutorial results are discarded.
    """
    user_input1 = input('\nPress "Enter" to start training or "skip" to Start Game: ')
    if user_input1.strip().lower() == "skip":
        return

    while True:
        print()
        _intro()

        if not _travel_to_camp():
            break

        while True:
            trap_result = _setup_trap()
            if trap_result is False:
                break

            horn_result = _sound_horn(trap_result)
            if horn_result is False:
                break

            print()
            again = input(
                'Press Enter to repeat training or "no" to finish: '
            ).strip().lower()

            if again in ("no", chr(27)):
                break

        # Exit outer loop if inner loop broke on ESC or trap_result was False
        if trap_result is False or horn_result is False:
            break

        if again in ("no", chr(27)):
            break