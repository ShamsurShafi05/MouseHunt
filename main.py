"""
main.py
=======
Entry point. Handles game setup and the main loop.
All heavy logic lives in the imported modules — main() just orchestrates.
"""

import time

from state import state
from constants import ENERGY_TRAVEL_COST, HUNGER_DRAIN_TRAVEL
from art.ascii_art import cheese_shop_art, show_description, game_intro
from player.player import setup_name, setup_difficulty
from tutorial.tutorial import run_tutorial
from game.ui import (
    get_game_menu, check_game_over,
    show_stats, show_pro_tips,
    choose_trap, change_cheese,
)
from game.hunt import hunt
from game.shops import visit_carpenter, visit_trader, visit_witch_doctor, visit_cheese_shop
from game.world import scavenge, sleep, eat_food


# ---------------------------------------------------------------------------
# End-of-game screen
# ---------------------------------------------------------------------------

def _show_ending() -> None:
    if state.points < 500:
        print(f"Thanks for joining our adventure, Hunter {state.name}! Better luck next time.")
    else:
        print(f"Congrats on surviving this adventure, Hunter {state.name}!")
        print("There were moments I doubted you, but you knew your way in the face of crisis!")

    time.sleep(3)
    print("\nDon't forget to check out your achievements:\n")
    show_stats()
    print("\nStay tuned for upcoming versions~")
    input("Enter any key to exit... ")


# ---------------------------------------------------------------------------
# Main menu input
# ---------------------------------------------------------------------------

def _get_menu_choice() -> int:
    """Print pro tips and prompt for a valid menu choice. Returns the int."""
    while True:
        show_pro_tips()
        user_input = input("Enter a number between 1 and 12: ").strip()
        if not user_input.isdigit():
            print("Invalid input.")
            continue
        choice = int(user_input)
        if choice < 1 or choice > 12:
            print("Must be between 1 and 12.")
            continue
        return choice


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def _game_loop() -> None:
    while True:
        # Game-over check at top of every loop
        if state.game_over:
            _show_ending()
            break

        # Enchant flag kept in sync with trap cheese
        state.enchant = (
            state.trap_cheese is not None and
            state.trap_cheese.lower() == "swiss"
        )

        # Status bar
        day_night = "Day" if state.is_daytime() else "Night"
        print(
            f"\nDay {state.day} [{day_night}]  "
            f"Time: {state.game_time}  "
            f"Gold: {state.gold}  "
            f"XP: {state.points}  "
            f"Energy: {state.player_energy}/100\n"
        )

        print(f"What do ye want to do now, Hunter {state.name}?")
        print(get_game_menu())

        choice = _get_menu_choice()
        print()

        if choice == 1:
            print(f"Thanks for joining our adventure, Hunter {state.name}!")
            time.sleep(3)
            print("\nDon't forget to check out your achievements:\n")
            show_stats()
            input("Enter any key to exit... ")
            break

        elif choice == 2:
            hunt()
            state.game_over = check_game_over()

        elif choice == 3:
            print("Travelling to Cheese Shop...\n")
            time.sleep(3)
            state.increase_time(2)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)
            cheese_shop_art()
            visit_cheese_shop()

        elif choice == 4:
            change_cheese()
            state.increase_time(1)

        elif choice == 5:
            scavenge()

        elif choice == 6:
            visit_trader()

        elif choice == 7:
            visit_witch_doctor()

        elif choice == 8:
            print("Travelling to Old Carpenter...\n")
            state.increase_time(2)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)
            time.sleep(3)
            visit_carpenter()
            print("Returning...\n")
            time.sleep(3)
            state.increase_time(2)

        elif choice == 9:
            choose_trap()
            state.increase_time(1)

        elif choice == 10:
            show_stats()

        elif choice == 11:
            sleep()

        elif choice == 12:
            eat_food()

        state.game_over = check_game_over()


# ---------------------------------------------------------------------------
# Setup sequence
# ---------------------------------------------------------------------------

def main() -> None:
    intro_text = (
        "In this thrilling adventure game, you step into the boots of a skilled hunter "
        "on a daring quest to outwit and capture elusive mice.\n"
        "You must use strategy and be cunning to lure your tiny targets while carefully "
        "managing your limited gold.\n"
        "Every decision counts — choose the right cheese, set the perfect trap, and adapt "
        "to the ever-changing challenges ahead.\n"
        "As you progress, you'll earn gold, unlock powerful upgrades, and discover new "
        "tools to catch even rarer and trickier mice.\n"
        "But beware! Your ultimate goal is to reach 500 XP before your gold runs dry.\n"
        "A true hunter knows that every misstep could mean an empty purse and a failed quest.\n"
        "Will you rise to the challenge, master the hunt, and claim your place among the "
        "legendary trappers?\n"
        "The adventure begins now!"
    )
    game_intro(intro_text)

    setup_name()
    run_tutorial()
    setup_difficulty()

    print("\nStarting...\n")
    time.sleep(2)

    # Opening narrative
    message = (
        "Stranded.\n\nLost.\n\nScavenging...\n\n"
        "You find a broken wooden crate behind a towering, damp oak tree..\n"
    )
    show_description(message)
    input("Press Enter to check its contents...")

    message = (
        f"\nYOU FOUND {state.gold} GOLD!\n"
        "\nBefore you can start hunting you need a trap.\n"
        "I've heard there's an Old Carpenter who still lives in these god-forsaken lands.\n"
        "Take the wooden crate to him. I've heard the man still got plenty of tricks up his sleeve.\n"
        "He will get the job done but often for a charge. "
        "Maybe he'll feel pity for you and get started with a free trap.."
    )
    show_description(message)

    state.wood += 10

    _game_loop()


if __name__ == "__main__":
    main()