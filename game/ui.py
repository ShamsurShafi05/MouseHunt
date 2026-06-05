"""
game/ui.py
==========
Status checks, menus, stats display, and trap/cheese selection UI.
All functions read/write state directly — no parameters, no return values
(except the pure query functions check_health, check_energy, check_game_over
 which return bools so callers can branch on them).
"""

import time

from state import state
from game.hunt import has_cheese


# ---------------------------------------------------------------------------
# Game menu
# ---------------------------------------------------------------------------

def get_game_menu() -> str:
    return (
        "1.  Exit Game\n"
        "2.  Join the Hunt\n"
        "3.  The Cheese Shop\n"
        "4.  Change Trap Cheese\n"
        "5.  Scavenge forest floor\n"
        "6.  Visit Trader\n"
        "7.  Visit Witch Doctor\n"
        "8.  Visit Old Carpenter\n"
        "9.  Change Trap\n"
        "10. Check stats\n"
        "11. Sleep / Rest\n"
        "12. Eat food\n"
    )


# ---------------------------------------------------------------------------
# Status checks
# ---------------------------------------------------------------------------

def check_health() -> bool:
    """Return True if the player is alive, False if dead."""
    if state.player_health <= 0:
        print("\nUnfortunately, you've succumbed to your wounds and illnesses..\n")
        return False
    if state.player_health < 10:
        print("\nYour health needs immediate medical attention. Head to the Witch Doctor!\n")
    return True


def check_energy() -> bool:
    """Return True if the player has energy to act, False if exhausted."""
    if state.player_energy <= 0:
        state.player_energy = 0
        print("\nYou're too exhausted to do that. Rest or eat something!\n")
        return False
    if state.player_energy <= 20:
        print(
            f"\nPro Tip: Energy critically low ({state.player_energy}/100). "
            "Eat food or sleep before you collapse!\n"
        )
    return True


def check_game_over() -> bool:
    """
    Evaluate all loss conditions.
    Returns True if the game should end, False if the player can continue.
    """
    if not check_health():
        print("\nYou have succumbed to your injuries... Game over!\n")
        return True

    if state.player_hunger <= 0:
        print("\nYou have starved to death... Game over!\n")
        return True

    if state.player_hunger <= 20:
        print("\nYou're starving. Eat something before it's too late!\n")

    if state.gold < 10:
        total_cheese = state.count_cheese()

        if total_cheese == 1:
            print("\nYour survival comes down to this one cheese.\n")
            print("Here's a ritual believed to help generations of hunters before you:\n")
            print(r"""
                    Waluuudulan dandanali
                    Watoblutob tobtobali
            """)
            return False

        if total_cheese == 0:
            print("\nYou've run out of cheese and don't have enough gold to buy more.")
            return True

    return False


# ---------------------------------------------------------------------------
# Pro tips shown in the main loop
# ---------------------------------------------------------------------------

def show_pro_tips() -> None:
    """Print contextual hints based on current player state."""
    if state.count_food() == 0:
        print(
            "Pro Tip: You have no food! Scavenge nearby or visit the Witch Doctor "
            "to buy rations.\nREMEMBER: Starvation can kill you!\n"
        )

    if state.current_trap is None:
        functional = sum(1 for t in state.trap_option if t[1] > 0 and t[2] > 0)
        if functional > 0:
            print("Pro Tip: You still have functional traps. Choose one!\n")
        else:
            print("Pro Tip: You need a trap. Head to the Old Carpenter!\n")
    else:
        total_cheese = state.count_cheese()
        if total_cheese == 0:
            print("Pro Tip: Before hunting you need cheese. Head to the Cheese Shop!\n")
        elif state.trap_cheese is None:
            print("Pro Tip: Get started by placing your cheese on the trap!\n")
        elif has_cheese(state.trap_cheese) == 0:
            print("Pro Tip: Your trap cheese has run out. Arm it with something new!\n")
        else:
            print("Looking like a pro right there! Ready to hunt?\n")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def show_stats() -> None:
    """Print end-of-session stats from state."""
    total_time = round((time.time() - state.start_time) / 60 + state.minutes_spent, 2)

    print("\n==============================================================\n")
    print("--- Game Stats ---")
    print(f"Total time played: {total_time} minutes")

    print("\nCheese Bought:")
    for cheese_type, amount in state.cheese_bought.items():
        print(f"  {cheese_type}: {amount}")

    print("\nMice Caught:")
    for mouse_type, count in state.caught_mouse_dictionary.items():
        print(f"  {mouse_type}: {count}")

    print("\nHunt Results:")
    print(f"  Successful hunts:   {state.attempts['Successful hunt']}")
    print(f"  Unsuccessful hunts: {state.attempts['Unsuccessful hunt']}")

    total_hunts = sum(state.attempts.values())
    if total_hunts > 0:
        rate = (state.attempts["Successful hunt"] / total_hunts) * 100
        print(f"  Hunt success rate:  {rate:.2f}%")
    else:
        print("  No hunts conducted yet.")

    print("\n==============================================================\n")


# ---------------------------------------------------------------------------
# Trap selection
# ---------------------------------------------------------------------------

def choose_trap() -> None:
    """Let the player select an active trap from their inventory."""
    print("You currently have:")
    for t in state.trap_option:
        print(f"  {t[0]}: {t[2]} hunts remaining")
    print()

    while True:
        user_input = input(
            "1. Wood-and-Spring Trap\n"
            "2. Reinforced Wood-Cage Trap\n"
            "3. Multilayer Glued-Board Trap\n"
        ).strip()

        if not user_input.isdigit():
            print("Invalid input.")
            continue

        choice = int(user_input)
        if choice < 1 or choice > 3:
            print("Invalid input.")
            continue

        selected = state.trap_option[choice - 1]
        if selected[1] == 0 or selected[2] == 0:
            print(f"You don't have a functional {selected[0]}.\n")
            continue

        state.current_trap = selected[0]
        print(f"Trap set to: {state.current_trap}\n")
        return


# ---------------------------------------------------------------------------
# Cheese arming
# ---------------------------------------------------------------------------

_CHEESE_BENEFITS = {
    "cheddar": "+25 XP drop by next Brown mouse",
    "marble":  "+25 gold drop by next Brown mouse",
    "swiss":   "+0.25 attraction to Tiny mouse",
}


def change_cheese() -> None:
    """
    Let the player arm their trap with a cheese from their inventory.
    Updates state.trap_cheese and state.enchant directly.
    """
    while True:
        print(f"Hunter {state.name}, you currently have:")
        for entry in state.cheese:
            print(f"  {entry[0]} - {entry[1]}")
        print()

        cheese_name = input(
            "Press 'back' to cancel. Type cheese name to arm trap: "
        ).strip().capitalize()

        if cheese_name == "Back":
            return

        # Check cheese exists in the game at all
        valid_names = [entry[0] for entry in state.cheese]
        if cheese_name not in valid_names:
            print("No such cheese!\n")
            continue

        # Check player has stock
        if has_cheese(cheese_name) == 0:
            print("Out of cheese!\n")
            continue

        # Show enchantment benefit if Swiss is active
        if state.enchant and cheese_name.lower() in _CHEESE_BENEFITS:
            benefit = _CHEESE_BENEFITS[cheese_name.lower()]
            print(f"Your {state.current_trap} has a one-time enchantment granting {benefit}")

        confirm = input(f"Arm your trap with {cheese_name}? (yes/no/back): ").strip().lower()

        if confirm == "yes":
            state.trap_cheese = cheese_name
            # Enchant is only active when Swiss is loaded
            state.enchant = cheese_name.lower() == "swiss"
            print(f"{state.current_trap} is now armed with {cheese_name}!\n")
            return
        elif confirm == "back" or confirm == "no":
            if confirm == "back":
                return
            continue