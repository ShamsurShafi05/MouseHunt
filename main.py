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
from game.world import scavenge, sleep, eat_food, travel_event_damage


# ---------------------------------------------------------------------------
# End-of-game screen
# ---------------------------------------------------------------------------

def _show_mouse_king_ending() -> None:
    """Full ending sequence when the Mouse King is caught."""
    import time

    print("\n" + "=" * 60)
    print("         *** THE MOUSE KING HAS FALLEN ***")
    print("=" * 60 + "\n")
    time.sleep(2)

    print("The land grows still.")
    time.sleep(1)
    print("For the first time in years... silence.")
    time.sleep(1)
    print("The chittering stops. The shadows retreat.")
    time.sleep(3)

    input("\nPress Enter to make your way back to the Trader...\n")

    # --- Trader scene ---
    print("\n~ The Trader's Shack ~\n")
    time.sleep(1)
    print("You push open the door. The Trader looks up.")
    time.sleep(1)
    print("Trader: ...")
    time.sleep(2)
    print("Trader: Is that... is that HIM?")
    time.sleep(2)
    print("Trader: *voice breaks*")
    time.sleep(1)
    print("Trader: My boy... you've avenged my boy.")
    time.sleep(2)
    print("Trader: I never thought I'd see the day.")
    time.sleep(2)
    print("Trader: *wipes eye, composes himself*")
    time.sleep(1)
    print("Trader: You have earned more than gold today, Hunter.")
    time.sleep(2)
    print("Trader: Take this. Every coin I have. It means nothing compared to what you've done.")
    state.gold += 500
    print(f"\n  +500 GOLD  →  Total: {state.gold} gold\n")
    time.sleep(2)

    choice = input("Trader: Before you go — shall I read my son's notes one last time? (yes/no): ").strip().lower()
    if choice == "yes":
        print("\nTrader: *unfolds a worn piece of paper, hands trembling*")
        time.sleep(1)
        print("  'Swiss cheese... Multilayer trap...'")
        time.sleep(1)
        print("  'He knew. He always knew.'")
        time.sleep(2)
        print("Trader: He would have made a fine hunter.")
        time.sleep(2)

    input("\nPress Enter to visit the Old Carpenter...\n")

    # --- Carpenter scene ---
    print("\n~ Old Carpenter's Shop ~\n")
    time.sleep(1)
    print("The Carpenter is sitting outside, whittling a small figurine.")
    time.sleep(1)
    print("Old Carpenter: *squints up at you* Well I'll be...")
    time.sleep(1)
    print("Old Carpenter: You actually did it, didn't ye?")
    time.sleep(2)
    print("Old Carpenter: Hah! HAAAAH!")
    time.sleep(1)
    print("Old Carpenter: I KNEW my Multilayer trap would be the one to do it!")
    time.sleep(2)
    print("Old Carpenter: They laughed at me, ye know. Said I was too old.")
    time.sleep(1)
    print("Old Carpenter: *slaps knee* Who's laughing now, eh?!")
    time.sleep(2)
    print("Old Carpenter: You tell everyone — it was MY trap that caught the Mouse King!")
    time.sleep(2)
    print("Old Carpenter: *proudly* They'll be writing songs about that trap.")
    time.sleep(2)

    input("\nPress Enter to visit the Witch Doctor...\n")

    # --- Witch Doctor scene ---
    print("\n~ The Witch Doctor's Hut ~\n")
    time.sleep(1)
    print("The Witch Doctor is standing at her door, as if she was expecting you.")
    time.sleep(1)
    print("Witch Doctor: I felt it. The moment the King fell.")
    time.sleep(2)
    print("Witch Doctor: The forest... it breathed again.")
    time.sleep(2)
    print("Witch Doctor: *pauses* You know... they used to spit at me in the market.")
    time.sleep(1)
    print("Witch Doctor: 'Old hag', they said. 'Trickster'.")
    time.sleep(2)
    print("Witch Doctor: This morning, three children left flowers at my door.")
    time.sleep(2)
    print("Witch Doctor: *looks at you* You did that, child. You and your reckless bravery.")
    time.sleep(2)

    blessing = input("\nWitch Doctor: Shall I send you off with a blessing? (yes/no): ").strip().lower()
    if blessing == "yes":
        state.player_health = 100
        state.player_energy = 100
        state.player_hunger = 100
        print("\nWitch Doctor: *chants softly, places hands on your shoulders*")
        time.sleep(2)
        print("Witch Doctor: Go now. Whole. And may the road be kind to you.")
        time.sleep(2)
        print("\n  Full health, energy and hunger restored.\n")
    else:
        print("\nWitch Doctor: Then go. The land is safer for what you've done.")
        time.sleep(2)

    input("\nPress Enter to make your way out of the Kingdom...\n")

    # --- Trail scene ---
    print("\n~ The Old Trail ~\n")
    time.sleep(1)
    print("You walk the trail back toward the world beyond.")
    time.sleep(1)
    print("The trees seem lighter. Birds call for the first time in what feels like years.")
    time.sleep(2)
    print("Behind you, footsteps.")
    time.sleep(2)
    print("It is the Trader. Out of breath. He presses a folded note into your hand.")
    time.sleep(2)
    print("Trader: I wasn't going to say anything but...")
    time.sleep(1)
    print("Trader: The Mouse King wasn't the only thing in these lands.")
    time.sleep(2)
    print("Trader: My son's notes... there were other pages.")
    time.sleep(1)
    print("Trader: *lowers voice* Things worse than mice.")
    time.sleep(2)

    answer = input("\nTrader: Are you ready for what comes next? (yes/not yet): ").strip().lower()
    if answer == "yes":
        print("\nTrader: *nods slowly*")
        time.sleep(1)
        print("Trader: Then find me when you're ready. I'll have more than gold waiting.")
        time.sleep(2)
        print("\n  ... A new adventure awaits. Coming soon.")
    else:
        print("\nTrader: *nods* Rest then, Hunter. You've earned it.")
        time.sleep(2)
        print("Trader: When you're ready... I'll be here.")
    time.sleep(3)

    input("\nPress Enter for end credits...\n")
    _show_credits()


def _show_credits() -> None:
    credits = [
        "",
        "=" * 60,
        "",
        "          MOUSE HUNT  —  VERSION 2.0  (2026)",
        "",
        "=" * 60,
        "",
        "         ~ The Mouse King has fallen. ~",
        "    ~ The Kingdom breathes once more. ~",
        "",
        "  Game Design & Programming  —  Shamsur Shafi",
        "  Mice ASCII Art             —  ChatGPT",
        "  NPC Dialogue & Story       —  Claude (Anthropic)",
        "",
        "  Inspired by MouseHunt™",
        "  A ShafsterGames Release",
        "",
        "  Thank you for playing, Hunter " + state.name + ".",
        "",
        "=" * 60,
        "",
        "        ... something stirs in the shadows ...",
        "",
    ]
    for line in credits:
        print(line)
        time.sleep(0.4)

    print()
    show_stats()
    input("\nPress Enter to exit... ")


def _show_ending() -> None:
    """Loss / early-exit ending."""
    print(f"\nThanks for joining our adventure, Hunter {state.name}!")
    time.sleep(2)
    show_stats()
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
            if state.mouse_king_caught:
                _show_mouse_king_ending()
                break
            state.game_over = check_game_over()


        elif choice == 3:
            print("Travelling to Cheese Shop...\n")
            time.sleep(3)
            state.increase_time(2)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)
            
            cheese_shop_art()
            visit_cheese_shop()

            print("\nReturning...\n")
            travel_event_damage()
            time.sleep(3)
            state.increase_time(2)


        elif choice == 4:
            change_cheese()
            state.increase_time(1)


        elif choice == 5:
            scavenge()


        elif choice == 6:
            print("Travelling to the Trader...\n")
            time.sleep(3)
            state.increase_time(3)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)
            
            visit_trader()

            print("\nReturning...\n")
            travel_event_damage()
            time.sleep(3)
            state.increase_time(3)


        elif choice == 7:
            print("Travelling to the Witch Doctor...\n")
            time.sleep(3)
            state.increase_time(6)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)

            visit_witch_doctor()
            
            print("\nReturning...\n")
            travel_event_damage()
            time.sleep(3)
            state.increase_time(6)


        elif choice == 8:
            print("Travelling to Old Carpenter...\n")
            state.increase_time(2)
            state.drain_energy(ENERGY_TRAVEL_COST)
            state.drain_hunger(HUNGER_DRAIN_TRAVEL)
            time.sleep(3)

            visit_carpenter()

            print("Returning...\n")
            travel_event_damage()
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