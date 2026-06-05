"""
game/shops.py
=============
All NPC shop visits: Carpenter, Trader, Witch Doctor, Cheese Shop.
Every function reads/writes state directly — no parameters, no return values.
"""

import random
import time

from state import state
from constants import (
    TRAP,
    CHEESE_PRICES,
    ENERGY_TRAVEL_COST,
    HUNGER_DRAIN_TRAVEL,
    XP_UNLOCK_TIER_1, XP_UNLOCK_TIER_2,
)
from models.crate import Crate
from art.ascii_art import character_art, show_description


# ---------------------------------------------------------------------------
# Cheese Shop
# ---------------------------------------------------------------------------

def _buy_cheese() -> None:
    """Inner shopping loop for the Cheese Shop."""
    while True:
        print(f"You have {state.gold} gold to spend.")
        user_input = input(
            "Cheese Dealer: Enter 'back' when you're done. To buy, type [cheese quantity]: "
        ).strip()

        if not user_input:
            print("Cheese Dealer: I don't seem to understand what you want..\n")
            continue

        if user_input.lower() == "back":
            return

        parts = user_input.split()
        cheese = parts[0].lower()

        if cheese not in CHEESE_PRICES:
            print(f"Cheese Dealer: We don't sell any {cheese}!")
            continue

        # XP lock checks
        if state.points < XP_UNLOCK_TIER_1 and cheese != "cheddar":
            print("Cheese Dealer: You do not have enough XP to unlock this item yet.")
            continue
        if state.points < XP_UNLOCK_TIER_2 and cheese == "swiss":
            print("Cheese Dealer: You do not have enough XP to unlock this item yet.")
            continue

        if len(parts) == 1:
            print("Cheese Dealer: If you don't tell me the quantity, how can I sell?")
            continue

        quantity_str = parts[1]
        if not quantity_str.isnumeric():
            print("Cheese Dealer: Do you need me to teach you how numbers work..?")
            continue

        qty = int(quantity_str)
        if qty <= 0:
            print("Cheese Dealer: You need.. a negative amount of cheese, huh?")
            continue

        # unit_price = CHEESE_PRICES[cheese]
        base_price = CHEESE_PRICES[cheese]
        unit_price = int(base_price * state.diff("cheese_price_mult"))
        total_cost = qty * unit_price

        if total_cost > state.gold:
            print("Cheese Dealer: You don't have enough gold.")
            continue

        state.gold -= total_cost
        state.cheese_bought[cheese.capitalize()] += qty

        for entry in state.cheese:
            if entry[0] == cheese.capitalize():
                entry[1] += qty

        print(
            f"Cheese Dealer: Pleasure doing business! "
            f"You purchased {qty} {cheese}.\n"
        )


def visit_cheese_shop() -> None:
    print("Cheese Dealer: Welcome to The Cheese Shop!")
    print()

    while True:
        print("Cheese Dealer: How can I help ye?")
        print("1. Buy cheese\n2. View inventory\n3. Leave shop")
        user_input = input().strip()

        if not user_input.isdigit():
            print("Cheese Dealer: I did not understand.\n")
            continue

        choice = int(user_input)

        if choice == 1:
            print("Cheese Dealer: The more expensive the cheese, the better your hunts!")
            _buy_cheese()
        elif choice == 2:
            _display_inventory()
            print()
        elif choice == 3:
            print("Cheese Dealer: Goodbye, then..")
            time.sleep(2)
            state.increase_time(2)
            break
        else:
            print("Cheese Dealer: I did not understand.\n")


# ---------------------------------------------------------------------------
# Old Carpenter
# ---------------------------------------------------------------------------

# def _update_trap_option(trap_name: str) -> None:
#     """Mark a trap as owned and reset its durability from the TRAP menu."""
#     for i, entry in enumerate(state.trap_option):
#         if entry[0] == trap_name:
#             entry[1] += 1
#             entry[2] = TRAP[i][3]   # durability from constants


def _buy_trap() -> None:
    """Inner shopping loop for buying traps at the Carpenter."""
    while True:
        print(f"\nOld Carpenter: You have {state.gold} gold and {state.wood} wood.\n")
        print("At my age, I can only make one trap of a kind in one go.")
        user_input = input(
            "\nEnter '0' when done. Choose a trap number:\n"
            "1. Wood-and-Spring Trap\n"
            "2. Reinforced Wood-Cage Trap\n"
            "3. Multilayer Glued-Board Trap\n"
        ).strip()

        if not user_input.isdigit():
            print("Old Carpenter: I did not understand.\n")
            continue

        choice = int(user_input)

        if choice == 0:
            return

        if choice < 1 or choice > 3:
            print("Old Carpenter: I did not understand.\n")
            continue

        # XP locks
        if state.points < XP_UNLOCK_TIER_1 and choice != 1:
            print("Old Carpenter: You do not have enough XP for that yet.\n")
            continue
        if state.points < XP_UNLOCK_TIER_2 and choice == 3:
            print("Old Carpenter: You do not have enough XP for that yet.\n")
            continue

        trap_entry = state.trap_option[choice - 1]
        trap_data  = TRAP[choice - 1]           # (name, wood_cost, gold_cost, durability)

        if trap_entry[2] > 0:
            print(f"Old Carpenter: Your {trap_entry[0]} is still in fine shape! Come back when it's broken!\n")
            continue

        wood_cost  = trap_data[1]
        gold_cost  = int(trap_data[2] * state.diff("trap_price_mult"))
        durability = int(trap_data[3] * state.diff("trap_durability_mult"))
        durability = max(1, durability)

        if state.wood < wood_cost:
            print("Old Carpenter: You didn't bring enough wood.\n")
            continue

        if state.gold < gold_cost:
            print("Old Carpenter: You don't seem to have enough gold, kid.\n")
            continue

        trap_name = trap_data[0]
        state.wood -= wood_cost
        state.gold -= gold_cost
        # Apply difficulty-scaled durability
        for i, entry in enumerate(state.trap_option):
            if entry[0] == trap_name:
                entry[1] += 1
                entry[2] = durability
        state.points += 10

        print(
            f"\nOld Carpenter: I can make a {trap_name} for you, no problem! "
            f"It will last you {durability} hunts."
        )
        print("You earned 10 XP!\n")
        if choice == 3:
            print("Old Carpenter: *pauses, lowers voice*")
            time.sleep(1)
            print("Old Carpenter: That's the one they say can hold the King himself...")
            time.sleep(2)
        continue   # back to top of while loop

def _display_inventory() -> None:
    character_art(state.name)
    print("Hunter, you currently have:\n")
    print(f"Wood  - {state.wood}")
    print(f"Gold  - {state.gold}")
    print("Cheese:")
    for entry in state.cheese:
        print(f"  {entry[0]} - {entry[1]}")
    print(f"Trap  - {state.current_trap}")
    print("``````````````````````````````````")


def visit_carpenter() -> None:
    if state.carpenter_visit == 0:
        # First visit — free starter trap and crate
        msg = (
            "Old Carpenter:\nI thought I heard some scurrying last night. "
            "A strange chittering, like whispers in the dark.\n"
            "Anyways, sorry I can't let you stay here if that's what ya're here for-\n\n"
            "If you got some wood, I might be able to get you something "
            "to help you survive better on your own.\n"
            "Might come in handy when the Mouse King's minions are lurking.\n"
        )
        show_description(msg)
        input("Press Enter to give wooden crate...")

        msg = (
            "A fine piece, I daresay. Withstood the forces of time but the pine wood can still be utilised. Wait here\n"
            "*chop* .. *grind* .. *scraping* .. *thumping* ..\n"
            "You are welcome, kid."
        )
        show_description(msg)

        print("\nYOU GOT WOOD-AND-SPRING TRAP!\n")
        state.trap_option[0][1] += 1
        # state.trap_option[0][2] = 10
        state.trap_option[0][2] = max(1, int(10 * state.diff("trap_durability_mult")))

        state.crate = Crate()
        print("\nYOU ALSO GOT A BASIC CRATE! (holds 5 mice)\n")

    else:
        # Return visits
        while True:
            user_input = input(
                "Old Carpenter: Ah, didn't forget the old fella! How can I help?\n"
                "1. Make Trap\n2. View inventory\n3. Upgrade Crate\n4. Leave shop\n"
            ).strip()

            if not user_input.isdigit():
                print("Old Carpenter: I did not understand.\n")
                continue

            choice = int(user_input)

            if choice < 1 or choice > 4:
                print("Old Carpenter: I did not understand.\n")
                continue

            if choice == 1:
                _buy_trap()
            elif choice == 2:
                _display_inventory()
                print()
            elif choice == 3:
                if state.crate is None:
                    print("Old Carpenter: You don't have a crate yet, kid.\n")
                else:
                    success, msg = state.crate.upgrade()
                    print(msg)
                    print()
            else:
                print("Old Carpenter: Goodbye, then..")
                time.sleep(2)
                break

    state.carpenter_visit += 1


# ---------------------------------------------------------------------------
# Trader
# ---------------------------------------------------------------------------

def visit_trader() -> None:
    if state.crate is None or state.crate.size() == 0:
        print("Trader: *swings door open*")
        time.sleep(1)
        print("Trader: Ohoho! A visitor! And what do you bring me today..?")
        time.sleep(2)
        print("Trader: ...")
        time.sleep(1)
        print("Trader: Nothing?! NOTHING?!")
        time.sleep(1)
        print("Trader: Just because you came from far away, expect me to make tea, huh?")
        time.sleep(2)
        print("Trader: Come back when you have something worth my time. OUT!")
        time.sleep(2)
        print("\nReturning...\n")
        state.increase_time(3)
        return

    print(f"Trader: Ohoho, welcome welcome, Hunter {state.name}!")
    time.sleep(1)
    if not state.trader_visited:
        time.sleep(1)
        print("Trader: Before we do business... there's something you should know.")
        time.sleep(2)
        print("Trader: That wretched beast — the Mouse King — he took my boy.")
        time.sleep(2)
        print("Trader: He was just a lad. Thought he could slay the King himself.")
        time.sleep(2)
        print("Trader: They found his trap shattered. Blood on the ground.")
        time.sleep(1)
        print("Trader: No sign of him. Only those cursed claw marks leading into the dark..")
        time.sleep(3)
        print("Trader: So I put a price on the Mouse King's head.")
        time.sleep(1)
        print("Trader: Bring it to me — and you'll be richer than any hunter here.")
        time.sleep(2)
        print("\nTrader: My boy left behind some notes. Press Enter to read them.")
        input()
        print("---------------------- Experiment 821 --------------------------")
        print("                      `````````````````")
        print("To catch the Mouse King, you must use BOTH:")
        print("")
        print("1. Swiss Cheese")
        print("2. A Multilayer Glued-Board Trap")
        print("")
        print("Conclusion: Without both, the King will never fall. Be prepared.")
        print("------------------------------------------------------------------\n")
        time.sleep(2)
        state.trader_visited = True
    else:
        # Return visits — brief reminder if XP is high
        if state.points >= 300:
            # time.sleep(1)
            print("Trader: *looks you over* You're getting closer, I can feel it.")
            time.sleep(1)
            print("Trader: Swiss cheese. Multilayer trap. Don't forget.")
            time.sleep(2)

    while True:
        print(f"\nYour gold: {state.gold}")
        state.crate.display()
        user_input = input(
            "Trader: So then, what'll it be?\n"
            "1. Sell all mice\n2. Sell one by one\n3. View crate\n4. Leave\n"
        ).strip()

        if not user_input.isdigit():
            print("Trader: Speak plainly, friend!")
            continue

        choice = int(user_input)

        if choice < 1 or choice > 4:
            print("Trader: Speak plainly, friend!")
            continue

        if choice == 1:
            if state.crate.size() == 0:
                print("Trader: Nothing left to sell! Heheheh.")
                continue
            total_gold = 0
            count = 0
            while state.crate.size() > 0:
                mouse = state.crate.remove()
                total_gold += mouse.get_gold()
                count += 1
            state.gold += total_gold
            print(f"\nTrader: Lovely batch, {count} mice — don't ask where they're going! Heheheh.")
            time.sleep(1)
            print(f"Trader: Here's your {total_gold} gold. Pleasure doing business!")
            print(f"Total gold now: {state.gold}\n")

        elif choice == 2:
            if state.crate.size() == 0:
                print("Trader: Nothing left to sell! Heheheh.")
                continue
            while state.crate.size() > 0:
                next_mouse = state.crate._queue[0]
                print(f"\nNext up: {next_mouse.get_name()} mouse — worth {next_mouse.get_gold()} gold")
                confirm = input("Sell it? (yes/no): ").strip().lower()
                if confirm == "yes":
                    mouse = state.crate.remove()
                    state.gold += mouse.get_gold()
                    print(f"Trader: Ohoho! {mouse.get_gold()} gold for you. {state.crate.size()} left in crate.")
                elif confirm == "no":
                    print("Trader: Suit yourself, keeping the rest then?")
                    break
                else:
                    print("Trader: Yes or no, friend, I'm a busy man!")

        elif choice == 3:
            state.crate.display()

        else:
            print(f"Trader: Safe travels, Hunter {state.name}! Come back with more next time. Heheheh.")
            time.sleep(2)
            break


# ---------------------------------------------------------------------------
# Witch Doctor
# ---------------------------------------------------------------------------

_FOOD_PRICES = {
    1: ("apple",     5),
    2: ("banana",    8),
    3: ("berries",   6),
    4: ("mushrooms", 10),
    5: ("frog",      3),
}

# _HEALING = {
#     1: (25,  50,  "Herbal Wrap"),
#     2: (50,  90,  "Bone Brew"),
#     3: (100, 150, "Full Revival"),
# }


def _witch_food_submenu() -> None:
    while True:
        print(f"\nYour gold: {state.gold}")
        print("Witch Doctor: My pantry is humble but it will keep you alive.\n")
        food_input = input(
            "1. Apple      - 5 gold\n"
            "2. Banana     - 8 gold\n"
            "3. Berries    - 6 gold\n"
            "4. Mushrooms  - 10 gold\n"
            "5. Frog       - 3 gold\n"
            "6. Back\n"
        ).strip()

        if not food_input.isdigit():
            print("Witch Doctor: Speak clearly, child.")
            continue

        fi = int(food_input)
        if fi < 1 or fi > 6:
            print("Witch Doctor: Speak clearly, child.")
            continue
        if fi == 6:
            break

        # item_name, item_cost = _FOOD_PRICES[fi]
        item_name, base_cost = _FOOD_PRICES[fi]
        item_cost = base_cost + state.diff("witch_food_price_bonus")
        if state.gold < item_cost:
            print(f"Witch Doctor: You cannot afford even a {item_name}? The spirits weep.")
            continue

        state.gold -= item_cost
        state.food[item_name] += 1

        if item_name == "frog":
            print("Witch Doctor: A frog. You buy... a frog.")
            time.sleep(1)
            print("Witch Doctor: I will not judge. The frog does not judge either.")
        else:
            print(f"Witch Doctor: Good choice. The {item_name} will serve you well.")


def _witch_ancient_ritual() -> None:
    if state.gold < 200:
        print("Witch Doctor: The Ancient Ritual demands 200 gold. You do not have enough.")
        print("Witch Doctor: Perhaps... a lesser remedy first.")
        return

    print("\nWitch Doctor: The Ancient Ritual... are you certain, child?")
    if input("(yes/no): ").strip().lower() != "yes":
        print("Witch Doctor: Wise hesitation. Choose another remedy.")
        return

    state.gold -= 200
    print("\nWitch Doctor: Close your eyes. Do NOT open them. Whatever you hear... do not open them.\n")
    time.sleep(2)
    print("*chanting* ... *rattling* ... *something wet* ...")
    time.sleep(3)

    if random.random() < 0.20:
        state.player_health = max(1, state.player_health - 5)
        print("Witch Doctor: Hmm.")
        time.sleep(1)
        print(f"Witch Doctor: The spirits were uncooperative. You lost 5 HP. HP: {state.player_health}/100")
    else:
        state.player_health = 100
        print("Witch Doctor: It is done.")
        time.sleep(1)
        print(f"Witch Doctor: You are whole again, child. HP: {state.player_health}/100")


def _witch_healing(option_key: int) -> None:
    hp_amounts  = state.diff("witch_hp_restore")   # tuple of 3
    hp_restore  = hp_amounts[option_key - 1]
    _HEALING_COSTS = {1: 50, 2: 90, 3: 150}
    _HEALING_NAMES = {1: "Herbal Wrap", 2: "Bone Brew", 3: "Full Revival"}
    cost        = _HEALING_COSTS[option_key]
    remedy_name = _HEALING_NAMES[option_key]
    # rest of function unchanged

    if state.gold < cost:
        print(f"Witch Doctor: {remedy_name} costs {cost} gold. You fall short, child.")
        return

    if state.player_health == 100:
        print("Witch Doctor: You are already at full health. Do not waste my remedies.")
        return

    print(f"\nWitch Doctor: The {remedy_name}... an old recipe. Hold still.\n")
    time.sleep(2)

    if random.random() < 0.10:
        state.player_health = max(1, state.player_health - 10)
        state.gold -= cost
        print("Witch Doctor: Curious. The herbs... they disagreed with you.")
        time.sleep(1)
        print(f"Witch Doctor: You lost 10 HP instead. My apologies. HP: {state.player_health}/100")
    else:
        state.gold -= cost
        state.player_health = min(100, state.player_health + hp_restore)
        print(f"Witch Doctor: There. {remedy_name} administered.")
        time.sleep(1)
        print(f"Witch Doctor: HP restored. You are at {state.player_health}/100 now, child.")


def visit_witch_doctor() -> None:

    print(r"""
        .   *   .   *   .
      *   _____   *   .
         /     \       *
        | o   o |
      * |   ^   |  *
         \_____/
       ~ Witch Doctor ~
    """)
    time.sleep(1)

    near_death = state.player_health < 10

    if near_death:
        print("Witch Doctor: Ohhh... you come to me barely breathing, child.")
        time.sleep(2)
        print("Witch Doctor: The spirits... they whisper your name already.")
        time.sleep(2)
        print("Witch Doctor: Sit. SIT. We must work quickly.\n")
        time.sleep(2)
    else:
        print("Witch Doctor: Ahhhh... another lost soul finds their way here.")
        time.sleep(2)
        print(f"Witch Doctor: The forest told me you were coming, Hunter {state.name}.")
        time.sleep(2)
        if state.points >= 300:
            print("Witch Doctor: The Mouse King's shadow grows longer every day...")
            time.sleep(1)
            print("Witch Doctor: I've been healing hunters who crossed his minions.")
            time.sleep(1)
            print("Witch Doctor: Be careful out there, child. Very careful.\n")
        else:
            print("Witch Doctor: What do you seek?\n")
        time.sleep(1)

    while True:
        print(f"\nYour gold: {state.gold}  |  HP: {state.player_health}/100")

        if near_death:
            menu = (
                "1. Herbal Wrap     (+25 HP  | 50 gold)\n"
                "2. Bone Brew       (+50 HP  | 90 gold)\n"
                "3. Full Revival    (+100 HP | 150 gold)\n"
                "4. Ancient Ritual  (full HP | 200 gold) [NEAR DEATH ONLY]\n"
                "5. Buy food rations\n"
                "6. Leave\n"
            )
        else:
            menu = (
                "1. Herbal Wrap     (+25 HP  | 50 gold)\n"
                "2. Bone Brew       (+50 HP  | 90 gold)\n"
                "3. Full Revival    (+100 HP | 150 gold)\n"
                "4. Buy food rations\n"
                "5. Leave\n"
            )

        user_input = input(f"Witch Doctor: Choose wisely, child...\n{menu}").strip()

        if not user_input.isdigit():
            print("Witch Doctor: The spirits do not understand your mumbling.")
            continue

        choice = int(user_input)
        max_option = 6 if near_death else 5

        if choice < 1 or choice > max_option:
            print("Witch Doctor: The spirits do not understand your mumbling.")
            continue

        leave_option = 6 if near_death else 5
        food_option  = 5 if near_death else 4

        if choice == leave_option:
            print("Witch Doctor: Go now, child. The forest watches over you... mostly.")
            time.sleep(2)
            break
        elif choice == food_option:
            _witch_food_submenu()
        elif near_death and choice == 4:
            _witch_ancient_ritual()
        else:
            _witch_healing(choice)