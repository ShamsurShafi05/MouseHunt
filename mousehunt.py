"""

Mouse Hunt 2.0 

Original file is located at https://colab.research.google.com/drive/10sKji9qtTMZsBiSgvFY8A3HpamY1LpN1

"""

import random
import time
from collections import deque

class Mouse:
    def __init__(self, cheese = "Cheddar", enchant = False, points = 0):
        self.name = generate_mouse(cheese, enchant, points)
        values = loot_lut(self.name)
        self.gold = values[0]
        self.points = values[1]
        self.coat = generate_coat(self.name)


    def get_name(self) -> str:
        return self.name

    def get_gold(self) -> int:
        return self.gold

    def get_points(self) -> int:
        return self.points

    def get_coat(self):
        return self.coat

    def __str__(self) -> str:
        if self.name == None:
            return "None"
        else:
            return self.name


class Animal:
    def __init__(self, type):
        if type == "tiger":
            self.type = "tiger"
            self.damage = 60
        elif type == "wild boar":
            self.type = "wild boar"
            self.damage = 20

    def attack(self, current_health):
        alive = True
        current_health -= self.damage
        if current_health <= 0:
            current_health = 0
            alive = False

        print(f"A {self.type} just attacked you! You lost {self.damage} HP")
        return (current_health, alive)


class Crate:
    TIERS = [
        ("Basic Crate",       5,  0,   0),    # name, capacity, xp_req, gold_cost
        ("Reinforced Crate", 10, 100, 80),
        ("Iron Crate",       20, 300, 200),
    ]

    def __init__(self):
        self._queue = deque()
        self.tier_index = 0
        self.capacity = self.TIERS[0][0]   # "Basic Crate"
        self.capacity = self.TIERS[0][1]   # 5

    def add(self, mouse) -> bool:
        """Enqueue a mouse. Returns False if crate is full."""
        if len(self._queue) >= self.capacity:
            return False
        self._queue.append(mouse)
        return True

    def remove(self):
        """Dequeue the oldest mouse (for Trader). Returns None if empty."""
        if not self._queue:
            return None
        return self._queue.popleft()

    def is_full(self) -> bool:
        return len(self._queue) >= self.capacity

    def size(self) -> int:
        return len(self._queue)

    def contents(self) -> list:
        """Returns list of mouse names currently in crate."""
        return [m.get_name() for m in self._queue]

    def poison_wipe(self):
        """Poison mouse kills everything in the crate."""
        if not self._queue:
            print("Your crate is empty — nothing to poison.")
            return
        print("\nThe Poison Mouse's toxins seep through the crate...")
        time.sleep(1)
        while self._queue:
            victim = self._queue.popleft()
            print(f"  ...the {victim.get_name()} mouse convulses and goes still.")
            time.sleep(0.6)
        print("Your crate is now empty.\n")

    def upgrade(self, points: int, gold: int) -> tuple:
        """
        Attempts to upgrade crate to next tier.
        Returns (success: bool, new_gold: int, message: str)
        """
        if self.tier_index >= len(self.TIERS) - 1:
            return (False, gold, "Old Carpenter: That crate's already as good as it gets, kid.")

        next_tier = self.TIERS[self.tier_index + 1]
        name, capacity, xp_req, gold_cost = next_tier

        if points < xp_req:
            return (False, gold, f"Old Carpenter: You'll need at least {xp_req} XP before I upgrade that crate.")

        if gold < gold_cost:
            return (False, gold, f"Old Carpenter: That'll cost {gold_cost} gold. You're a bit short, kid.")

        self.tier_index += 1
        self.capacity = capacity
        gold -= gold_cost
        return (True, gold, f"Old Carpenter: There ye go — upgraded to a {name}! Holds {capacity} mice now.")

    def display(self):
        """Prints crate status."""
        tier_name = self.TIERS[self.tier_index][0]
        print(f"\n[ Crate: {tier_name} | {self.size()}/{self.capacity} mice ]")
        if self._queue:
            for i, m in enumerate(self._queue, 1):
                print(f"  {i}. {m.get_name()} mouse  |  Worth: {m.get_gold()} gold")
        else:
            print("  (empty)")
        print()



def tiny_mouse():
    str = r"""
        (\_/)
        (o.o)  Tiny Mouse
        (")(")
        """
    return str


def brown_mouse():
    str = r"""
        (\_/)
       ( o.o )  Brown Mouse
       (  :  )
       /     \
      /       \
    """
    return str

def white_mouse():
    str = r"""
         (\__/)
        ( o . o )  White Mouse
         (  "  )
         /    \
        /      \
       (________)
    """
    return str

def grey_mouse():
    str = r"""
         (\_/)
        ( o.o )  Grey Mouse
        (  :  )
       /       \
      (         )
       \_______/
    """
    return str

def field_mouse():
    str = r"""
         (\__/)
        ( o.o )  Field Mouse
         (__:__)/

    """
    return str

def poison_mouse():
    str = r"""
         (\_/)
        ( x.x )  Poison Mouse
        (  :  )
       /  ~~~  \
      ( *dead* )
    """
    return str

def generate_mouse(cheese="Cheddar", enchant=False, points=0) -> str | None:
    while True:
        probability = generate_probabilities(cheese, enchant)
        num = random.random()
        if num >= (1 - probability[6]):
            spawn_mouse = "Poison"
        elif num >= (1 - probability[6] - probability[5]):
            spawn_mouse = "Tiny"
        elif num >= (1 - probability[6] - probability[5] - probability[4]):
            spawn_mouse = "White"
        elif num >= (1 - probability[6] - probability[5] - probability[4] - probability[3]):
            spawn_mouse = "Grey"
        elif num >= (1 - probability[6] - probability[5] - probability[4] - probability[3] - probability[2]):
            spawn_mouse = "Field"
        elif num >= (1 - probability[6] - probability[5] - probability[4] - probability[3] - probability[2] - probability[1]):
            spawn_mouse = "Brown"
        else:
            spawn_mouse = None
        # XP gates
        if points < 100:
            if spawn_mouse not in [None, "Field"]:
                continue
        elif points < 300:
            if spawn_mouse not in [None, "Field", "Grey", "White", "Brown"]:
                continue
        elif points < 500:
            if spawn_mouse == "Poison":
                continue   # Poison locked until 500 XP
        break
    return spawn_mouse


def loot_lut(mouse_type: str | None) -> tuple:
    '''
    Look-up-table for gold and points for different types of mouse
    Parameter:
        mouse_type: str | None, type of mouse
    Returns:
        gold:       int, amount of gold reward for mouse
        points:     int, amount of points given for mouse
    '''
    if mouse_type == None:
        gold = 0
        points = 1              # hunt korlei 1 xp
    elif mouse_type == "Brown":
        gold = 70
        points = 60
    elif mouse_type == "Field":
        gold = 15
        points = 20
    elif mouse_type == "Grey":
        gold = 60
        points = 50
    elif mouse_type == "White":
        gold = 80
        points = 70
    elif mouse_type == "Tiny":
        gold = 100
        points = 100
    elif mouse_type == "Poison":
        gold = 0
        points = 150    

    return (gold, points)


def generate_probabilities(cheese_type, enchant=False):
    if cheese_type.lower() == "cheddar":
        return (0.47, 0.1, 0.15, 0.1, 0.1, 0.05, 0.03)   # added poison prob at end
    elif cheese_type.lower() == "marble":
        return (0.57, 0.05, 0.2, 0.05, 0.02, 0.08, 0.03)
    else:
        if enchant == False:
            return (0.67, 0.01, 0.05, 0.05, 0.04, 0.15, 0.03)
        else:
            return (0.42, 0.01, 0.05, 0.05, 0.04, 0.4, 0.03)

def generate_coat(type):
    if type == "Tiny":
        return tiny_mouse()
    elif type == "Brown":
        return brown_mouse()
    elif type == "White":
        return white_mouse()
    elif type == "Grey":
        return grey_mouse()
    elif type == "Field":
        return field_mouse()
    elif type == "Poison":
        return poison_mouse()


def get_game_menu():
    return ("1. Exit Game\n2. Join the Hunt\n3. The Cheese Shop\n4. Change Trap Cheese\n"
            "5. Scavenge forest floor\n6. Visit Trader\n7. Visit Witch Doctor\n"
            "8. Visit Old Carpenter\n9. Change Trap\n10. Check stats\n"
            "11. Sleep / Rest\n12. Eat food\n")

def check_game_over():
    # global gold, cheese, points

    status = check_health()
    if status == False:
        print("\nYou have succumbed to your injuries... Game over!\n")
        return True
    
    if player_hunger <= 0:
        print("\nYou have starved to death... Game over!\n")
        return True

    if player_hunger <= 20:
        print("\nYou're starving. Eat something before it's too late!\n")

    if gold < 10:
        total = 0
        for i in cheese:
            total += i[-1]

        if total == 1:
            print("\nYour survival comes down to this cheese.\n")
            print("Here's our special ritual that is believed to help a long generation of hunters alike yourself:\n")
            print(r"""
                    Waluuudulan dandanali
                    Watoblutob tobtobali
            """)
            print()
            return False

        if total == 0:
            print("\nSorry you've run out of cheese and do not have any more gold to make purchases!")
            return True
    else:
        return False


def consume_cheese(to_eat: str, my_cheese: list) -> tuple:           #cheese parameter to my_cheese parameter bc of question 7

    left = has_cheese(to_eat, my_cheese)
    if left == 0:
        return (my_cheese, False)
    else:
        for i in range(len(my_cheese)):
            if my_cheese[i][0] == to_eat.capitalize():
                my_cheese[i][1] -= 1

    return (my_cheese, True)

def has_cheese(to_check, my_cheese):            #new for question 7; used in the function above to check is cheese exists in inventory

    # if to_check == None:
    #     print("HAS CHEESE E NONE ASHCHE")
    #     return 0
    for i in range(len(my_cheese)):
        if my_cheese[i][0] == to_check.capitalize():
            if my_cheese[i][1] == 0:
                return 0
            else:
                return my_cheese[i][1]

def get_benefit(cheese):
    if cheese.lower() == "cheddar":
        return "+25 XP drop by next Brown mouse"
    elif cheese.lower() == "marble":
        return "+25 gold drop by next Brown mouse"
    elif cheese.lower() == "swiss":
        return "+0.25 attraction to tiny mouse"


def level_check_1():
    print("=========================================================")
    print("Congrats you have unlocked new items:\n")
    print("NEW CHEESE: MARBLE")
    print("NEW TRAP: REINFORCED WOOD-CAGE")
    print(white_mouse())
    print(grey_mouse())
    print(brown_mouse())
    print("=========================================================")


def level_check_2():
    print("=========================================================")
    print("Congrats you have unlocked new items:\n")
    print("NEW CHEESE: SWISS")
    print("NEW TRAP: MULTILAYER GLUED-BOARD")
    print("ENCHANTMENT UNLOCKED")
    print(tiny_mouse())
    print("=========================================================")

def level_check_3():
    print("=========================================================")
    print("Congrats you have unlocked new content:\n")
    print("WARNING: Something has changed in these lands...")
    print("Rumour has it a deadly Poison Mouse has been spotted nearby.")
    print("Keep your crate close — and your wits closer.")
    print("=========================================================")

def check_health():
    global player_health

    alive = True
    if player_health <= 0:
        print("\nUnfortunately, you've succumbed to your wounds and illnesses..\n")
        alive = False
        return alive
    elif player_health < 10:
        print("\nYour health needs immediate medical attention. Head out to Hospital asap!\n")

    return alive


def check_energy():
    global player_energy
    if player_energy <= 0:
        player_energy = 0
        print("\nYou're too exhausted to do that. You need to rest or eat something!\n")
        return False
    elif player_energy <= 20:
        print(f"\nPro Tip: Energy critically low ({player_energy}/100). Eat food or sleep before you collapse!\n")
    return True

def restore_energy(amount: int) -> None:
    global player_energy
    player_energy = min(MAX_ENERGY, player_energy + amount)

def drain_energy(amount: int) -> None:
    global player_energy
    player_energy = max(0, player_energy - amount)

def drain_hunger(amount: int) -> None:
    global player_hunger
    player_hunger = max(0, player_hunger - amount)

def sleep(hours: int) -> None:
    global game_time, player_health, player_energy, MAX_ENERGY
    energy_gain = min(MAX_ENERGY, hours * 30)
    hp_gain = hours * 3
    restore_energy(energy_gain)
    player_health = min(100, player_health + hp_gain)
    game_time = increase_time(game_time, hours)
    print(f"\nYou rest for {hours} hour(s).")
    print(f"  +{energy_gain} energy  →  {player_energy}/100")
    print(f"  +{hp_gain} HP       →  {player_health}/100\n")

def eat_food(food: dict) -> dict:
    FOOD_ENERGY = {"apple": 10, "banana": 15, "berries": 8, "mushrooms": 20, "frog": 5}
    FOOD_HUNGER = {"apple": 20, "banana": 25, "berries": 15, "mushrooms": 30, "frog": 10}

    available = {k: v for k, v in food.items() if v > 0}
    if not available:
        print("You have no food to eat.")
        return food
    print("What do you want to eat?")
    for i, (item, qty) in enumerate(available.items(), 1):
        print(f"  {i}. {item.capitalize()} (x{qty}) → +{FOOD_ENERGY[item]} energy")
    choice = input("Enter number (or 'back'): ").strip()
    if choice == "back":
        return food
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        item = list(available.keys())[int(choice) - 1]
        food[item] -= 1
        restore_energy(FOOD_ENERGY[item])
        # print(f"You ate a {item}. +{FOOD_ENERGY[item]} energy → {player_energy}/100")

        player_hunger = min(100, player_hunger + FOOD_HUNGER[item])
        print(f"You ate a {item}. +{FOOD_ENERGY[item]} energy → {player_energy}/100 | Hunger: {player_hunger}/100")
    else:
        print("Invalid choice.")
    return food


def hunt(gold, cheese, trap_cheese, enchant, points, called_functions, attempts, caught_mouse_dictionary, game_over_status, crate, current_trap, trap_option):
    global game_time, player_health, ENERGY_HUNT_COST, ENERGY_ANIMAL_COST, day

    hunt_count = 0
    succes_streak = 0

    while True:
        game_over_status = check_game_over()
        if game_over_status == True:
            break

        check_health()              # returned values apatoto kaj e lagtesa, lagle catch korbone
        # print("Time", game_time, "Gold:", str(gold) + ", XP:", points)

        day_night = "Day" if is_daytime(game_time) else "Night"
        print(f"Day {day} [{day_night}]  Time: {game_time}  Gold: {gold}  XP: {points}  Energy: {player_energy}/100\n")


        # energy gate
        if not check_energy():
            break

        # Stopping condition: Sound the horn by typing "yes": #stop hunt

        check_game_time = int(str(game_time).split()[0])

        if 6 <= check_game_time <= 18:
            risk1, risk2 = 0.1, 0.2  # Daytime risks
        else:
            print("ProTip: The elders say it's best to avoid what lurks in the shadows of these unknown realms once dusk falls.")
            user_input_timewise = input("Do you want to still continue to hunt? ['yes' or 'no'] ")
            if user_input_timewise.lower() == "no":
                break

            risk1, risk2 = 0.5, 0.6  # Night risks


        # Block hunt if no trap selected
        if current_trap is None:
            print("You have no trap set. Head to the Old Carpenter first.")
            dec_input1 = input('Type "stop" to leave, or anything else to stay: ')
            if dec_input1.isdigit() != True:
                if dec_input1.lower() == "stop":
                    break
            continue

        # Block hunt if current trap is broken
        trap_broken = all(t[1] == 0 for t in trap_option if t[0] == current_trap)
        if trap_broken:
            print(f"Your {current_trap} is broken. Visit the Old Carpenter to get a new one.")
            dec_input2 = input('Type "stop" to leave, or anything else to stay: ')
            if dec_input2.isdigit() != True:
                if dec_input2.lower() == "stop":
                    break
            continue

        print("\nSound the horn to call for the mouse...")
        sound_input = input('Sound the horn by typing "yes". Type "stop" to end hunting session: ')
        if sound_input.isdigit() == True:
            print("Invalid input.\n")
            continue

        if sound_input.lower() == "stop":
            break

        drain_energy(ENERGY_HUNT_COST)
        drain_hunger(HUNGER_DRAIN_HUNT)

        # Random chance for encountering an animal
        num_new = random.random()
        if num_new < risk1:
            animal = Animal("tiger")
        elif num_new < risk2:
            animal = Animal("wild boar")
        else:
            animal = None

        if animal:
            player_health, alive = animal.attack(player_health)
            drain_energy(ENERGY_ANIMAL_COST)
            continue


        if sound_input == '' or sound_input != "yes":
            print("You did not properly sound the horn. Hunt wasted.")
            hunt += 1
            game_time = increase_time(game_time, 3)
        else:
            print("\n~~ ~ ~~~~ ~~~ ~~ ~~ ~ ~~~~\n")
            if trap_cheese == None:
                hunt += 1
                game_time = increase_time(game_time, 1)
                print("Nothing happens. You are out of cheese!")

            else:
                cheese, status = consume_cheese(trap_cheese, cheese)
                if status == False:
                    hunt_count += 1
                    game_time = increase_time(game_time, 1)
                    print("Nothing happens. You are out of cheese!")
                else:
                    mouse = Mouse(trap_cheese, enchant, points)
                    # print("CURRENTLY Cheese list is:", cheese)

                    # if mouse.name != None:
                    #     hunt_count = 0
                    #     points += mouse.get_points()
                    #     gold += mouse.get_gold()
                    #     print("``````````````````````````````````````````")
                    #     print("You caught a {} mouse!".format(mouse.name))
                    #     print(mouse.get_coat())
                    #     print("``````````````````````````````````````````")
                    #     caught_mouse_dictionary[mouse.name] += 1
                    #     attempts["Successful hunt"] += 1
                    #     print(f"You earned {mouse.get_gold()} gold and {mouse.get_points()} XP!")
                    #     game_time = increase_time(game_time, 3)
                    
                    if mouse.name == "Poison":
                        print("``````````````````````````````````````````")
                        print("You caught a Poison Mouse!")
                        print(mouse.get_coat())
                        print("``````````````````````````````````````````")
                        points += mouse.get_points()
                        attempts["Successful hunt"] += 1
                        caught_mouse_dictionary["Poison"] = caught_mouse_dictionary.get("Poison", 0) + 1
                        print(f"You earned {mouse.get_points()} XP!")
                        time.sleep(1)
                        if crate is not None and crate.size() > 0:
                            crate.poison_wipe()
                        else:
                            print("Lucky — your crate was empty. Nothing lost.\n")
                        game_time = increase_time(game_time, 3)

                    elif mouse.name != None:
                        hunt_count = 0
                        points += mouse.get_points()
                        gold += mouse.get_gold()
                        print("``````````````````````````````````````````")
                        print("You caught a {} mouse!".format(mouse.name))
                        print(mouse.get_coat())
                        print("``````````````````````````````````````````")
                        # caught_mouse_dictionary[mouse.name] += 1

                        # In hunt(), use .get() for all mouse name increments:
                        caught_mouse_dictionary[mouse.name] = caught_mouse_dictionary.get(mouse.name, 0) + 1
                        
                        attempts["Successful hunt"] += 1
                        print(f"You earned {mouse.get_gold()} gold and {mouse.get_points()} XP!")
                        game_time = increase_time(game_time, 3)

                        # --- CRATE PROMPT ---
                        if crate is not None:
                            if crate.is_full():
                                print(f"Your crate is full. You watch the {mouse.name} mouse scurry away...")
                            else:
                                crate_input = input("What do you want to do with it?\n1. Let Go\n2. Put in Crate\n").strip()
                                if crate_input == "2":
                                    crate.add(mouse)
                                    print(f"{mouse.name} mouse added to crate. [{crate.size()}/{crate.capacity}]")
                                else:
                                    print(f"You let the {mouse.name} mouse go.")

                    else:
                        #print("H1:", hunt)
                        hunt += 1
                        attempts["Unsuccessful hunt"] += 1
                        #print("H2:", hunt)
                        print("The wilderness can sometimes be cruel. Hunt unsuccessful")
                        game_time = increase_time(game_time, 3)

        # print("Gold:", str(gold) + ", Points:", points)

        # --- TRAP DURABILITY DECREMENT ---
        if sound_input.lower() == "yes" and trap_cheese is not None:
            for t in trap_option:
                if t[0] == current_trap and t[2] > 0:
                    t[2] -= 1
                    if t[2] == 0:
                        t[1] = 0    # mark as broken/unowned
                        print(f"\n*** Your {current_trap} has broken! Visit the Old Carpenter to get a new one. ***\n")
                    break

        print()

        if points >= 100:
            if called_functions["level_check_1"] == False:
                level_check_1()
                called_functions["level_check_1"] = True

        if points >= 300:
            if called_functions["level_check_2"] == False:
                level_check_2()
                called_functions["level_check_2"] = True

        if points >= 500:
            if called_functions["level_check_3"] == False:
                level_check_3()
                called_functions["level_check_3"] = True

        #print(hunt)
        if hunt%5 == 0 and hunt != 0:
            print("Looks like you're not having a great hunting session today.")
            user_input4 = input("Do you want to still continue to hunt? ['yes' or 'no'] ")
            if user_input4.lower() == "no":
                break

    return (gold, points, cheese, called_functions, attempts, caught_mouse_dictionary, game_over_status)



def display_cheese_inventory(name: str, cheese: list) -> None:

    print(f"Hunter {name}, you currently have:")
    #print(cheese)
    print("Cheddar -", cheese[0][1])
    print("Marble -", cheese[1][1])
    print("Swiss -", cheese[2][1])
    print()


def change_cheese(hunter_name: str, trap: str, cheese: list, e_flag: bool = False) -> tuple:

    while True:
        display_cheese_inventory(hunter_name, cheese)

        cheese_name = input("Press 'back' when you're done. Type cheese name to arm trap: ")
        cheese_name = cheese_name.strip().capitalize()

        if cheese_name == "Back":
            return (False, None)

        cheese_found = False
        for i in cheese:
            if i[0] == cheese_name:
                cheese_found = True
                break

        if cheese_found == False:
            print("No such cheese!\n")
            continue


        cheese_available = False
        for i in cheese:
            if i[0] == cheese_name:
                if i[1] != 0:
                    cheese_available = True
                    break

        if cheese_available == False:
            print("Out of cheese!\n")
            continue

        if e_flag == True:
            print("Your {} has a one-time enchantment granting {}".format(trap, get_benefit(cheese_name)))

        #print(cheese_found, cheese_available)
        confirm = input(f"Do you want to arm your trap with {cheese_name}? ")
        confirm = confirm.lower().strip()


        if confirm == "yes":
            print(f"{trap} is now armed with {cheese_name}!")
            return (True, cheese_name)
        elif confirm == "back":
            return (False, None)
        elif confirm == "no":
            print()
            continue


def show_description(message):
    description = message
    lines = description.strip().split("\n")
    for line in lines:
        print(line)
        time.sleep(2)  # Delay of 2 seconds before showing the next line

def game_intro(message):

    # title = "Mousehunt"
    logo = """
      (\_/)
      (• .•)  < Mouse Hunt!
     \(  ><)
    ` ` ` ` `
    """
    Inspired_by = "Inspired by MouseHunt™, a release by ShafsterGames."
    author = "Programmer - Shamsur Shafi"
    credits = "Mice art - ChatGPT"

    # print(title + "\n")
    print(logo)
    print(Inspired_by)
    time.sleep(2)
    print(author)
    time.sleep(2)
    print(credits)
    time.sleep(2)
    print("Version launch - 1.1 (2025)")
    time.sleep(2)
    print()
    show_description(message)
    print()

def check_special_key(char):
    special_keys = {
        27: "Escape (ESC)",
        10: "Enter (LF - Line Feed)",   # Also '\n'
        13: "Enter (CR - Carriage Return)",  # Older Macs
        9:  "Tab (Horizontal Tab)",  # Also '\t'
        8:  "Backspace",
        32: "Space",
        127: "Delete"
    }

    ascii_value = ord(char)
    if ascii_value in special_keys:
        # print(f"Detected: {special_keys[ascii_value]}")
        return True
    else:
        # print("Not a special key.")
        return False

def is_valid_length(name):
    return 1 <= len(name) <= 9


def is_valid_start(name):
    if len(name) == 0:
        return False
    return name[0].isalpha()

def is_one_word(name):
    if len(name) == 0:
        return False
    for i in range(len(name)):
        if name[i] == ' ':
            return False
    return True

def is_valid_name(name):
    if not is_valid_length(name):
        print("Name must be between 1 and 9 characters")
    if not is_valid_start(name):
        print("Name must start with an alphabet")
    if not is_one_word(name):
        print("Name must be at least one word")

    return is_valid_length(name) and is_valid_start(name) and is_one_word(name)


def intro():
    print("``````````````````````````````````````````````````")
    print("                 TUTORIAL                         \n")
    print("Larry: Hi I'm Larry. I'll be your hunting instructor.")


def travel_to_camp():
    print("Larry: Let's go to the Meadow to begin your training!")
    value = input("Press Enter to travel to the Meadow...")
    value = value.strip()
    if value == chr(27):
        return False
    else:
        print("Travelling to the Meadow...")
        print("Larry: This is your camp. Here you'll set up your mouse trap.")


def setup_trap():
    print("Larry: Let's get your first trap...")

    val1 = input("Press Enter to view traps that Larry is holding...")
    val1 = val1.strip()

    if val1 == chr(27):
        return False
    print("Larry is holding...")
    print("Left: Wood-and-Spring Trap")
    print("Right: Reinforced Wood-Cage Trap")
    trap_input = input('Select a trap by typing "left" or "right": ').strip()

    trap_input = trap_input.strip()
    if trap_input == chr(27):
        return False

    if trap_input.lower() == "left":
        print("Larry: Excellent choice.")
        print('Your Wood-and-Spring Trap is now set!')
        print("Larry: You need cheese to attract a mouse.")
        print("Larry places one cheddar on the trap!")
        return ("Wood-and-Spring Trap", 1)
    elif trap_input.lower() == "right":
        print("Larry: Excellent choice.")
        print('Your Reinforced Wood-Cage Trap is now set!')
        print("Larry: You need cheese to attract a mouse.")
        print("Larry places one cheddar on the trap!")
        return ("Reinforced Wood-Cage Trap", 1)
    else:
        print("Invalid command! No trap selected.")
        print("Larry: Odds are slim with no trap!")
        return ("Wood-and-Spring Trap", 0)


def sound_horn(trap_result):                                    #CHANGE
    print("Sound the horn to call for the mouse...")
    horn_sound = input('Sound the horn by typing "yes": ').lower()
    horn_sound = horn_sound.strip()
    horn_sound = horn_sound.lower()

    if horn_sound == chr(27):
        return False

    if horn_sound != "yes" and trap_result == ("Wood-and-Spring Trap", 0): #no trap, no horn
        print("Nothing happens.")

    elif horn_sound == "yes" and trap_result != ("Wood-and-Spring Trap", 0):
        print("Caught a Brown mouse!\nCongratulations. Ye have completed the training.\nGood luck~")
        return "success"

    elif horn_sound == "yes" and trap_result == ("Wood-and-Spring Trap", 0):
         print("Nothing happens.\nTo catch a mouse, you need both trap and cheese!")

    else:
        print("Nothing happens.\nTo catch a mouse, you need both trap and cheese!")
        #print("To catch a mouse, you need both trap and cheese!")
    return horn_sound



def basic_hunt(cheddar: int, horn_input: str):
    if cheddar == 1 and horn_input.lower() == 'yes':
        print("Caught a Brown mouse!")
        return True

    elif  cheddar == 0 and horn_input.lower() == 'yes':
        print("Larry: Nothing happens.")
        return False
  # else:
    # print("Larry: Odds are slim with no trap!")
    # return False

def end(hunt_status: bool):
    if hunt_status:
        print("Congratulations. Ye have completed the training.\nGood luck~")



def cheese_shop_art():

    str = r"""
      ________________________
     /                        \
    /    The  Cheese  Shop     \
   /____________________________\
        ||                ||
       _||________________||__
      |                      |
      |   PRICES (IN GOLD)   |
      |                      |
      |     Cheddar - 10     |
      |     Marble  - 50     |
      |     Swiss   - 100    |
      |______________________|
       (____________________)
    """
    print(str)


def cheese_art():
    str = " "
    print(str)

def character_art(name):
    character = r"""
      O
     /|\
     / \
    """
    print(character)
    print(f"~ {name} ~")


def cheese_shop_intro():
    print("Cheese Dealer: How can I help ye?\n1. Buy cheese\n2. View inventory\n3. Leave shop")


def buy_cheese(gold: int, points: int) -> tuple:

    remain = gold
    spent = 0

    cheddar = 0
    marble = 0
    swiss = 0

    while True:

        print(f"You have {gold} gold to spend.")
        user_input = input("Cheese Dealer: Enter 'back' when you're done shopping. To buy, state [cheese quantity]: ")

        if len(user_input) == 0:
            print("Cheese Dealer: I don't seem to understand what you want..", end = '\n\n')
            continue

        #returning to main menu
        if user_input.lower() == "back":
            return (spent, (cheddar, marble, swiss))

        user_input = user_input.split()
        cheese = user_input[0].lower()

        #checking is cheese name is valid
        if cheese not in ["cheddar", "marble", "swiss"]:
            print(f"Cheese Dealer: We don't sell any {cheese}!")
            continue
        else:
            if points < 100:
                if cheese != "cheddar":
                    print(f"Cheese Dealer: You do not have enough XP to unlock this item yet. Choose another cheese.")
                    continue
            elif points < 300:
                if cheese == "swiss":
                    print(f"Cheese Dealer: You do not have enough XP to unlock this item yet. Choose another cheese.")
                    continue


        #checking if quantity is missing
        if len(user_input) == 1:
            print("Cheese Dealer: If you don't tell me what quantity of cheese you want how can I sell?")
            continue
        else:
            quantity = user_input[1]

        #checking if quantity enteres is not a number
        if quantity.isnumeric() == False:
            print("Cheese Dealer: Do you need me to teach you how numbers work..?")
            continue
        else:
            cheese_bought = int(quantity)

        #checking if quantity entered is non-positive
        if cheese_bought <= 0:
            print("Cheese Dealer: You need.. a negative amount of cheese, huh?")
            continue

        #cheese-wise base price setting
        if cheese == "cheddar":
            unit_price = 10
        elif cheese == "marble":
            unit_price = 50
        else:
            unit_price = 100

        gold_needed = cheese_bought * unit_price

        #successful buy or sell
        if gold_needed <= gold:
            print(f"Cheese Dealer: Pleasure doing business with you! You have successfully purchased {cheese_bought} {cheese}.", end = " ")
            cheese_art()
            if cheese == "cheddar":
                cheddar += cheese_bought
            elif cheese == "marble":
                marble += cheese_bought
            else:
                swiss += cheese_bought
            gold -= gold_needed
            spent += gold_needed

        else:
            print("Cheese Dealer: You don't have enough gold.")
            continue


def display_inventory(wood: int, gold: int, cheese: list, trap: str, name: str) -> None:

    character_art(name)
    print(f"Hunter, you currently have:\n")
    print("Wood -", wood)
    print("Gold -", gold)
    print("Cheese:")
    print("Cheddar -", cheese[0][1])
    print("Marble -", cheese[1][1])
    print("Swiss -", cheese[2][1])
    print("Trap -", trap)
    print("``````````````````````````````````")

def showStats(start_time, minutes_spent, cheese_bought, caught_mouse_dictionary, attempts):
    global ENERGY_SCAVENGE_COST

    # Total playtime
    total_time = (time.time() - start_time) / 60
    total_time = round(total_time + minutes_spent, 2)

    print("\n==============================================================\n")
    print("\n--- Game Stats ---")
    print(f"Total time played: {total_time} minutes")

    # Cheese bought summary
    print("\nCheese Bought:")
    for cheese_type, amount in cheese_bought.items():
        print(f"  {cheese_type}: {amount}")

    # Mice caught summary
    print("\nMice Caught:")
    for mouse_type, count in caught_mouse_dictionary.items():
        print(f"  {mouse_type}: {count}")

    # Hunt results
    print("\nHunt Results:")
    print(f"  Successful hunts:  {attempts['Successful hunt']}")
    print(f"  Unsuccessful hunts: {attempts['Unsuccessful hunt']}")

    # Win rate calculation
    total_hunts = attempts['Successful hunt'] + attempts['Unsuccessful hunt']
    if total_hunts > 0:
        success_rate = (attempts['Successful hunt'] / total_hunts) * 100
        print(f"  Hunt success rate: {success_rate:.2f}%")
    else:
        print("  No hunts conducted yet.")

    print("\n==============================================================\n")


def scavenge():
    global wood, food, game_time, points, player_health, day
    
    current_hour = int(str(game_time).split()[0])
    # print(f"Time: {game_time} HP: {player_health}/100  Energy: {player_energy}/100\n")

    day_night = "Day" if is_daytime(game_time) else "Night"
    print(f"Day {day} [{day_night}]  Time: {game_time}  Gold: {gold}  XP: {points}  Energy: {player_energy}/100\n")

    if not check_energy():
        return
    
    drain_energy(ENERGY_SCAVENGE_COST)

    success_scavenge_messages = [
        "You carefully search the forest floor and find some dry twigs.. \nThey can be handy!",
        "You dig through the leaves and discover a few sturdy branches.. \nDefinitely some good loots for the day!",
        "You stumble upon a fallen tree branch, perfect for crafting.. \nThe carpenter will be delighted!",
        "You gather some scattered sticks from the ground.. \nGod's mercy, indeed!",
        "You rummage through the underbrush and find a pile of firewood.. \nCan definitely chop it up and put to good use!"
    ]

    fail_scavenge_messages = [
        "You carefully search the forest floor and find some dry twigs.. \nOh no- They are too brittle!",
        "You dig through the leaves and discover a few sturdy branches.. \nNvm- They are too easily snappable!",
        "You stumble upon a fallen tree branch, perfect for crafting.. \nWelp- It's too heavy to carry it back to the carpenter!",
        "You gather some scattered sticks from the ground.. \nDrop and run- Termites!",
        "You rummage through the underbrush and find a pile of firewood.. \nHard luck- It's soaking wet!"
    ]

    food_options = ["apple", "banana", "berries", "mushrooms", "frog"]  # Replaced fish with frog
    food_found = random.choice(food_options)

    current_hour = int(str(game_time).split()[0])
    if 6 <= current_hour <= 18:
        risk1, risk2 = 0.1, 0.2  # Daytime risks
    else:
        risk1, risk2 = 0.5, 0.6  # Night risks

    event_roll = random.random()
    random_index = random.randint(0, 4)  # 5 elements, so index range 0-4

    if event_roll < 0.25:
        # print("You found usable wood!")
        msg = success_scavenge_messages[random_index]
        wood += random_index + 1  # Add wood if successful
    elif event_roll < 0.50:
        # print("You found unusable wood.")
        msg = fail_scavenge_messages[random_index]
    elif event_roll < 0.75:
        # print(f"You found some food: {food_found}!")
        food[food_found] += 1
        msg = f"You scavenge the forest and discover a {food_found}. Might come in handy!"
    else:
        print("You didn’t find anything.")
        msg = "Despite your efforts, the forest floor yields nothing today."

    print(f"Wood collected: {wood}")
    show_description(msg)



    # Random chance for encountering an animal
    num1 = random.random()
    if num1 < risk1:
        animal = Animal("tiger")
    elif num1 < risk2:
        animal = Animal("wild boar")
    else:
        animal = None

    if animal:
        player_health, alive = animal.attack(player_health)
        drain_energy(ENERGY_ANIMAL_COST)
        check_game_over()



# UNTESTED
def choose_trap(trap_option, current_trap):
    print("You currently have:")
    for i in trap_option:
        print(f"{i[0]}: will last {i[2]} more hunts")
    print()

    while True:
        user_input = input("1. Wood-and-Spring Trap\n2. Reinforced Wood-Cage Trap\n3. Multilayer Glued-Board Trap\n")
        if user_input.isdigit() == True:
            user_input = int(user_input)
        else:
            print("Invalid input.")
            continue

        if user_input < 1 or user_input > 3:
            print("Invalid input.")
            continue

        if trap_option[user_input-1][1] == 0 or trap_option[user_input-1][2] == 0:
            print(f"You don't have a functional {trap_option[user_input-1][0]}")
            continue
        else:
            current_trap = trap_option[user_input-1][0]
            return current_trap


def count_trap(trap_option):
    total = 0
    for i in trap_option:
        total += i[1]
    return total

def update_trap_option(trap_option, trap_name, trap_menu):
    for i in range(len(trap_option)):
        if trap_option[i][0] == trap_name:
            trap_option[i][1] += 1                 # owned count
            trap_option[i][2] = trap_menu[i][3]    # uses_remaining = durability from TRAP menu
    return trap_option

def buy_trap(wood: int, gold: int, points: int, trap_menu: tuple, trap_option: list) -> tuple:

    while True:

        print("\nOld Carpenter:")
        print(f"You have {gold} gold to spend.\n")


        print(f"FOR TESTING ========= Wood: {wood}, Gold: {gold}, Points: {points}", "Trap options:", trap_option)
        print("At my age, I can only make one trap of a kind in one go")
        user_input = input("\nEnter '0' when you're done shopping. To buy, choose [trap number]:\n1. Wood-and-Spring Trap\n2. Reinforced Wood-Cage Trap\n3. Multilayer Glued-Board Trap\n")

        if user_input.isdigit() == True:
            user_input = int(user_input)
        else:
            print("Old Carpenter: I did not understand.")
            print()
            continue

        if user_input < 0 or user_input > 3:
            print("Old Carpenter: I did not understand.")
            print()
            continue

        if user_input == 0:
            return (wood, gold, points, trap_option)

        if points < 100:
            if user_input != 1:
                print(f"Old Carpenter: You do not have enough XP to unlock this item yet. Choose another trap.\n")
                continue

        if points < 300:
            if user_input == 3:
                print(f"Old Carpenter: You do not have enough XP to unlock this item yet. Choose another trap.\n")
                continue

        if trap_option[user_input-1][2] > 0:
            print(f"Old Carpenter: Your current {trap_option[user_input-1][0]} is still in fine shape! Come back when it's broken!\n")
            continue

        if wood < trap_menu[user_input-1][1]:
            print("Old Carpenter: You didn't bring enough wood. Select a different trap.\n")
            continue

        if gold < trap_menu[user_input-1][2]:
            print("Old Carpenter: You don't seem to have enough gold, kid. Select a different trap.\n")
            continue

        trap_name = trap_menu[user_input-1][0]



        trap_name = trap_menu[user_input-1][0]
        quantity = 1
        wood -= trap_menu[user_input-1][1]*quantity
        gold -= trap_menu[user_input-1][2]*quantity
        trap_option = update_trap_option(trap_option, trap_name, trap_menu)
        print(f"Old Carpenter: \nI can make {quantity} {trap_name} for you worries, no problem! It will last you {trap_menu[user_input-1][3]} hunts.")
        print("You earned 10 XP!\n")
        points += 10

    return (wood, gold, points, trap_option)

def visit_trader(gold, crate, name):
    global game_time, ENERGY_TRAVEL_COST

    print("Travelling to the Trader...\n")
    time.sleep(3)
    game_time = increase_time(game_time, 3)
    drain_energy(ENERGY_TRAVEL_COST)
    drain_hunger(HUNGER_DRAIN_TRAVEL)

    if crate is None or crate.size() == 0:
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
        game_time = increase_time(game_time, 3)
        return gold

    print("Trader: Ohoho, welcome welcome, Hunter", name + "!")
    time.sleep(1)
    print("Trader: I don't ask where they come from... and you don't ask where they go. Heheheh.")
    time.sleep(2)

    while True:
        print(f"\nYour gold: {gold}")
        crate.display()
        user_input = input("Trader: So then, what'll it be?\n1. Sell all mice\n2. Sell one by one\n3. View crate\n4. Leave\n").strip()

        if user_input.isdigit():
            user_input = int(user_input)
        else:
            print("Trader: Speak plainly, friend!")
            continue

        if user_input < 1 or user_input > 4:
            print("Trader: Speak plainly, friend!")
            continue

        if user_input == 1:
            if crate.size() == 0:
                print("Trader: Nothing left to sell! Heheheh.")
                continue

            total_gold = 0
            count = 0
            while crate.size() > 0:
                mouse = crate.remove()
                total_gold += mouse.get_gold()
                count += 1

            gold += total_gold
            print(f"\nTrader: Lovely batch, {count} mice — don't ask where they're going! Heheheh.")
            time.sleep(1)
            print(f"Trader: Here's your {total_gold} gold. Pleasure doing business!")
            print(f"Total gold now: {gold}\n")

        elif user_input == 2:
            if crate.size() == 0:
                print("Trader: Nothing left to sell! Heheheh.")
                continue

            while crate.size() > 0:
                # peek at the front mouse without removing
                next_mouse = crate._queue[0]
                print(f"\nNext up: {next_mouse.get_name()} mouse — worth {next_mouse.get_gold()} gold")
                confirm = input("Sell it? (yes/no): ").strip().lower()

                if confirm == "yes":
                    mouse = crate.remove()
                    gold += mouse.get_gold()
                    print(f"Trader: Ohoho! {mouse.get_gold()} gold for you. {crate.size()} left in crate.")
                elif confirm == "no":
                    print("Trader: Suit yourself, keeping the rest then?")
                    break
                else:
                    print("Trader: Yes or no, friend, I'm a busy man!")

        elif user_input == 3:
            crate.display()

        else:
            print("Trader: Safe travels, Hunter", name + "! Come back with more next time. Heheheh.")
            time.sleep(2)
            break

    print("\nReturning...\n")
    time.sleep(3)
    game_time = increase_time(game_time, 3)
    return gold

def visit_witch_doctor(gold, food, player_health, name):
    global game_time, ENERGY_TRAVEL_COST

    print("Travelling to the Witch Doctor...\n")
    time.sleep(3)
    game_time = increase_time(game_time, 6)
    drain_energy(ENERGY_TRAVEL_COST)
    drain_hunger(HUNGER_DRAIN_TRAVEL)

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

    # near-death detection
    near_death = player_health < 10

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
        print("Witch Doctor: The forest told me you were coming, Hunter", name + ".")
        time.sleep(2)
        print("Witch Doctor: What do you seek?\n")
        time.sleep(1)

    while True:
        print(f"\nYour gold: {gold}  |  HP: {player_health}/100")
        

        if near_death:
            menu = "1. Herbal Wrap     (+25 HP | 50 gold)\n2. Bone Brew       (+50 HP | 90 gold)\n3. Full Revival    (+100 HP | 150 gold)\n4. Ancient Ritual  (full HP | 200 gold) [NEAR DEATH ONLY]\n5. Buy food rations\n6. Leave\n"
        else:
            menu = "1. Herbal Wrap     (+25 HP | 50 gold)\n2. Bone Brew       (+50 HP | 90 gold)\n3. Full Revival    (+100 HP | 150 gold)\n4. Buy food rations\n5. Leave\n"

        user_input = input(f"Witch Doctor: Choose wisely, child...\n{menu}").strip()

        if user_input.isdigit():
            user_input = int(user_input)
        else:
            print("Witch Doctor: The spirits do not understand your mumbling.")
            continue

        max_option = 6 if near_death else 5
        if user_input < 1 or user_input > max_option:
            print("Witch Doctor: The spirits do not understand your mumbling.")
            continue

        # remap food/leave options based on near_death
        food_option  = 5 if near_death else 4
        leave_option = 6 if near_death else 5

        if user_input == leave_option:
            print("Witch Doctor: Go now, child. The forest watches over you... mostly.")
            time.sleep(2)
            break

        elif user_input == food_option:
            # food rations submenu
            while True:
                print(f"\nYour gold: {gold}")
                print("Witch Doctor: My pantry is humble but it will keep you alive.\n")
                food_menu = "1. Apple      - 5 gold\n2. Banana     - 8 gold\n3. Berries    - 6 gold\n4. Mushrooms  - 10 gold\n5. Frog       - 3 gold\n6. Back\n"
                food_input = input(food_menu).strip()

                if food_input.isdigit():
                    food_input = int(food_input)
                else:
                    print("Witch Doctor: Speak clearly, child.")
                    continue

                if food_input < 1 or food_input > 6:
                    print("Witch Doctor: Speak clearly, child.")
                    continue

                if food_input == 6:
                    break

                food_prices = {1: ("apple", 5), 2: ("banana", 8), 3: ("berries", 6), 4: ("mushrooms", 10), 5: ("frog", 3)}
                item_name, item_cost = food_prices[food_input]

                if gold < item_cost:
                    print(f"Witch Doctor: You cannot afford even a {item_name}? The spirits weep.")
                    continue

                gold -= item_cost
                food[item_name] += 1

                if item_name == "frog":
                    print("Witch Doctor: A frog. You buy... a frog.")
                    time.sleep(1)
                    print("Witch Doctor: I will not judge. The frog does not judge either.")
                else:
                    print(f"Witch Doctor: Good choice. The {item_name} will serve you well.")

        elif near_death and user_input == 4:
            # ancient ritual — near death only
            if gold < 200:
                print("Witch Doctor: The Ancient Ritual demands 200 gold. You do not have enough.")
                print("Witch Doctor: Perhaps... a lesser remedy first.")
                continue

            print("\nWitch Doctor: The Ancient Ritual... are you certain, child?")
            confirm = input("(yes/no): ").strip().lower()
            if confirm != "yes":
                print("Witch Doctor: Wise hesitation. Choose another remedy.")
                continue

            gold -= 200
            print("\nWitch Doctor: Close your eyes. Do NOT open them. Whatever you hear... do not open them.\n")
            time.sleep(2)
            print("*chanting* ... *rattling* ... *something wet* ...")
            time.sleep(3)

            backfire_roll = random.random()
            if backfire_roll < 0.20:
                player_health = max(1, player_health - 5)
                print("Witch Doctor: Hmm.")
                time.sleep(1)
                print("Witch Doctor: The spirits were... uncooperative today.")
                time.sleep(1)
                print(f"Witch Doctor: You lost 5 HP. But you live. That counts for something. HP: {player_health}/100")
            else:
                player_health = 100
                near_death = False
                print("Witch Doctor: It is done.")
                time.sleep(1)
                print(f"Witch Doctor: You are whole again, child. Do not waste it. HP: {player_health}/100")

        else:
            # normal healing packages
            healing_options = {1: (25, 50, "Herbal Wrap"), 2: (50, 90, "Bone Brew"), 3: (100, 150, "Full Revival")}

            # remap key 3 to Full Revival when near_death shifts menu
            option_key = user_input
            hp_restore, cost, remedy_name = healing_options[option_key]

            if gold < cost:
                print(f"Witch Doctor: {remedy_name} costs {cost} gold. You fall short, child.")
                continue

            if player_health == 100:
                print("Witch Doctor: You are already at full health. Do not waste my remedies.")
                continue

            print(f"\nWitch Doctor: The {remedy_name}... an old recipe. Hold still.\n")
            time.sleep(2)

            backfire_roll = random.random()
            if backfire_roll < 0.10:
                player_health = max(1, player_health - 10)
                gold -= cost
                print("Witch Doctor: Curious. The herbs... they disagreed with you.")
                time.sleep(1)
                print(f"Witch Doctor: You lost 10 HP instead. My apologies. HP: {player_health}/100")
            else:
                gold -= cost
                player_health = min(100, player_health + hp_restore)
                print(f"Witch Doctor: There. {remedy_name} administered.")
                time.sleep(1)
                print(f"Witch Doctor: HP restored. You are at {player_health}/100 now, child.")

    print("\nReturning...\n")
    time.sleep(3)
    game_time = increase_time(game_time, 6)
    return (gold, food, player_health)


def visit_carpenter(menu, trap_option, wood, gold, points, carpenter_visit, cheese, current_trap, name, crate):
    # ALLOW OPTION TO FIXXX TRAP??
    if carpenter_visit == 0:
        msg = "Old Carpenter:\nI thought I heard some noise last night. But there's just been so much noise lately, innit?\n"
        msg = msg + "Anyways, sorry I can't let you stay here if that's what ya're here for, mate-\n"
        msg = msg + "If you got some wood, I might be able to get you something to help you survive better on your own\n"

        show_description(msg)

        user_input = input("Press Enter to give wooden crate...")

        msg = "A fine piece, I daresay. Withstood the forces of time but the pine wood can still be utilised. Wait here\n"
        msg = msg + "*chop* .. *grind* .. *scraping* .. *thumping* .. \n"
        msg = msg + "You are welcome, kid."

        show_description(msg)

        print("\nYOU GOT WOOD-AND-SPRING TRAP!\n")
        trap_option[0][1] += 1
        trap_option[0][2] = 10  # use limit [NEW]
        carpenter_visit += 1

        crate = Crate()
        print("\nYOU ALSO GOT A BASIC CRATE! (holds 5 mice)\n")
        return (wood, gold, points, trap_option, carpenter_visit, crate)
    
        # return (wood, gold, points, trap_option, carpenter_visit)

    else:
        while True:

            user_input = input("Old Carpenter: Ah didn't forget the old fella, I see. How can I help you?\n1. Make Trap\n2. View inventory\n3. Upgrade Crate\n4. Leave shop\n")

            if user_input.isdigit() == True:
                user_input = int(user_input)
            else:
                print("Old Carpenter: I did not understand.")
                print()
                continue

            if user_input < 1 or user_input > 4:
                print("Old Carpenter: I did not understand.")
                print()
                continue

            if user_input == 1:
                result = buy_trap(wood, gold, points, menu, trap_option)
                # return (wood, gold, points, trap_option)
                wood = result[0]
                gold = result[1]
                points = result[2]
                trap_option = result[3]

            elif user_input == 2:
                display_inventory(wood, gold, cheese, current_trap, name)                     # wood add hobe (CHEESE OPTION EO ADD KORA LAGBE)
                print()
            
            elif user_input == 3:
                success, gold, msg = crate.upgrade(points, gold)
                print(msg)
                print()

            else:
                print("Old Carpenter: Goodbye, then..")
                time.sleep(2)
                break

        carpenter_visit += 1
        return (wood, gold, points, trap_option, carpenter_visit, crate)

# def increase_time(game_time, increment):
#     hour = int(str(game_time).split()[0])  # safe: split on space
#     hour = (hour + increment) % 24
#     return f"{hour:02d} 00"  # always zero-padded e.g. "09 00"

def increase_time(game_time, increment):
    global day
    hour = int(str(game_time).split()[0])
    new_hour = hour + increment
    if new_hour >= 24:
        day += 1
        print(f"\n--- Day {day} begins ---\n")
    hour = new_hour % 24
    return f"{hour:02d} 00"

def is_daytime(game_time) -> bool:
    hour = int(str(game_time).split()[0])
    return 6 <= hour <= 18

def count_food():
    global food

    total = 0
    for i in food.values():
        total += i
    return total

# allow tutorial to be visited anytime later





def main():
    global player_health, player_energy, player_hunger, wood, food, points, gold, cheese, game_time, day
    global ENERGY_HUNT_COST, ENERGY_SCAVENGE_COST, ENERGY_TRAVEL_COST, ENERGY_ANIMAL_COST, MAX_ENERGY
    global HUNGER_DRAIN_HUNT, HUNGER_DRAIN_SCAVENGE, HUNGER_DRAIN_TRAVEL

    TYPE_OF_MOUSE = (None, "Brown", "Field", "Grey", "White", "Tiny", "Poison")
    CHEESE_MENU = (("Cheddar", 10), ("Marble", 50), ("Swiss", 100))
    TRAP = (("Wood-and-Spring Trap", 10, 5, 10), ("Reinforced Wood-Cage Trap", 30, 15, 20), ("Multilayer Glued-Board Trap", 50, 50, 15))
    # format: name - wood - gold - lasting duration(turns/hunts) - making duration (turns) [consider adding later]

    # add time to make for each trap (speed up korte extra gold: double its price)
    # vary hunt chance based on trap too (LATER)[add buffs like 2% or 3%]

    player_energy = 100
    MAX_ENERGY = 100
    ENERGY_HUNT_COST = 15
    ENERGY_SCAVENGE_COST = 10
    ENERGY_TRAVEL_COST = 5
    ENERGY_ANIMAL_COST = 10

    player_hunger = 100     # 0 = starving
    HUNGER_DRAIN_HUNT = 10
    HUNGER_DRAIN_TRAVEL = 5
    HUNGER_DRAIN_SCAVENGE = 8

    start_gold = (200, 150, 125)
    game_over = False
    crate = None
    carpenter_visit = 0                                                                              # set wood alada bhabe (need to collect)
    points = 0
    gold = 0
    cheese = [["Cheddar", 0], ["Marble", 0], ["Swiss", 0]]
    
    # Each entry is now [name, owned, uses_remaining].
    # trap_option = [["Wood-and-Spring Trap", 0], ["Reinforced Wood-Cage Trap", 0], ["Multilayer Glued-Board Trap", 0]]
    trap_option = [["Wood-and-Spring Trap", 0, 0], ["Reinforced Wood-Cage Trap", 0, 0], ["Multilayer Glued-Board Trap", 0, 0]]
    
    
    food = {"apple": 0, "banana": 0, "berries": 0, "mushrooms": 0, "frog": 0}

    trap_cheese = None
    current_trap = None

    enchant = False
    wood = 0
    player_health = 100
    game_time = "09 00"
    day = 1

    called_functions = {
        "level_check_1": False,
        "level_check_2": False,
        "level_check_3": False
    }

    # caught_mouse_dictionary = {}
    # for i in TYPE_OF_MOUSE:
    #     caught_mouse_dictionary[i] = 0
    caught_mouse_dictionary = {mouse: 0 for mouse in TYPE_OF_MOUSE if mouse is not None}

    minutes_spent = 0
    attempts = {"Successful hunt": 0, "Unsuccessful hunt": 0}
    cheese_bought = {"Cheddar": 0, "Marble": 0, "Swiss": 0}
    start_time = time.time()


    intro_text = "In this thrilling adventure game, you step into the boots of a skilled hunter on a daring quest to outwit and capture elusive mice.\nYou must use strategy and be cunning to lure your tiny targets while carefully managing your limited gold.\nEvery decision counts—choose the right cheese, set the perfect trap, and adapt to the ever-changing challenges ahead.\nAs you progress, you'll earn gold, unlock powerful upgrades, and discover new tools to catch even rarer and trickier mice.\nBut beware! Your ultimate goal is to reach 500 XP before your gold runs dry.\nA true hunter knows that every misstep could mean an empty purse and a failed quest.\nWill you rise to the challenge, master the hunt, and claim your place among the legendary trappers?\nThe adventure begins now!"
    game_intro(intro_text)
    print()
    print("What's ye name, Hunter?")
    name = input()
    flag = is_valid_name(name)
    flag_check = 3

    while flag != True and flag_check != 0:
        print(f"You have {flag_check} tries remaining")
        name = input("Re-enter your name, Hunter: ")
        flag = is_valid_name(name)
        flag_check -= 1

    if flag != True:
        name = "Bob"
        print(f"\nOur systems has decided to name you Bob!\n")

    print("Welcome to the Kingdom, Hunter", name+"!")
    print("\nBefore we begin, let's train you up!")
    user_input1 = input('Press "Enter" to start training or "skip" to Start Game: ')

    if user_input1 != 'skip':

        while True:
            print()
            intro()
            val1 = travel_to_camp()
            if val1 == False:
                break

            while True:
                tutorial_trap_result = setup_trap()
                if tutorial_trap_result == False:
                    break
                tutorial_trap = tutorial_trap_result[0]
                if tutorial_trap == "Wood-and-Spring Trap" or tutorial_trap == "Hot Tub Trap":
                    tutorial_enchant = True
                    tutorial_trap = "One-time Enchanted " + tutorial_trap

                tutorial_sound = sound_horn(tutorial_trap_result)
                if tutorial_sound == False:
                    break
                #cheddar -= 1
                print()
                user_input = input('Press Enter to continue training and "no" to stop training: ')
                user_input = user_input.strip()
                user_input = user_input.lower()
                if user_input == '':
                    continue

                if user_input == chr(27) or user_input == "no":
                    break

            if tutorial_trap_result == False:
                break

            if tutorial_sound == False:
                break

            if user_input == chr(27) or user_input == "no":
                break

    if enchant == False:
        trap_cheese = None

    while True:
        print()
        difficulty = input("Choose game difficulty:\n1. Noob\n2. Adventurer\n3. Survivalist\n")

        if difficulty.isdigit() == True:
            difficulty = int(difficulty)
        else:
            print("Invalid option.\n")
            continue

        if difficulty < 1 or difficulty > 3:
            print("Invalid option.\n")
            continue
        else:
            if difficulty == 1:
                print("Oh my.. with such little nerve, you might not be able to come out alive from what awaits you ahead..")
            elif difficulty == 2:
                print("A rational thinker, I see. Too scared to risk it, are we..")
            else:
                print("Daring, are we? We all sometimes live to regret the decisions we make. Will you too..")
            break

    # add je you check your pockets to find name is Bob

    print("\nStarting...\n")
    time.sleep(2)
    print()
    gold += start_gold[difficulty-1]
    message = "Stranded.\n\nLost.\n\nScavenging...\n\nYou find a broken wooden crate behind a towering, damp oak tree..\n"
    show_description(message)
    r_press = input("Press Enter to check its contents...")
    message = ""
    message = message + f"\nYOU FOUND {gold} GOLD!\n"
    message = message + "\nBefore you can start hunting you need a trap.\nI've heard there's an Old Carpenter who still lives in these god-foresaken lands\nTake the wooden crate to him. I've heard the man still got plenty of tricks up his sleeve."
    message = message + "\nHe will get the job done but often for a charge. Maybe he'll feel pity for you and get started with a free trap.."
    show_description(message)
    wood += 10

    while True:
        if game_over == True:
            if points < 500:
                print(f"Thanks for joining our adventure, Hunter {name}! Better luck next time.")
                time.sleep(3)
                print("\nDon't forget to check out your achievements:\n\n")
                showStats(start_time, minutes_spent, cheese_bought, caught_mouse_dictionary, attempts)
                print("\nStay tuned for upcoming versions~")
                key = input("Enter any key to exit... ")
                break
            else:
                print(f"Congrats on surviving this adventure, Hunter {name}!")
                print("There are moments I doubted you but you surely knew your way in the face of crisis!")
                time.sleep(3)
                print("\nDon't forget to check out your achievements:\n\n")
                showStats(start_time, minutes_spent, cheese_bought, caught_mouse_dictionary, attempts)
                print("\nStay tuned for upcoming versions~")
                key = input("Enter any key to exit... ")
                break


        print()

        if trap_cheese == None:
            enchant = False
        elif trap_cheese.lower() == "swiss":
            enchant = True
        else:
            enchant = False

        # print(f"Time: {game_time} Health: {player_health}\n")
        # print(f"Time: {game_time}  HP: {player_health}/100  Energy: {player_energy}/100\n")
        # print(f"Time: {game_time}  HP: {player_health}/100  Energy: {player_energy}/100  Hunger: {player_hunger}/100\n")

        day_night = "Day" if is_daytime(game_time) else "Night"
        print(f"Day {day} [{day_night}]  Time: {game_time}  Gold: {gold}  XP: {points}  Energy: {player_energy}/100\n")


        print("What do ye want to do now, Hunter",name+'?')
        # print("=================================")
        # print("Current cheese is:", trap_cheese)
        # print("=================================")
        print(get_game_menu())

        while True:
            cheese_count = 0
            for i in range(len(cheese)):
                cheese_count += cheese[i][1]

            if count_food() == 0:
                print("Pro Tip: You don't have any food! You can try scavenging nearby for food or visit the Witch Doctor to buy off some of her rations.")
                print("REMEMBER: When unfed for too long, you can die from starvation!\n")

            if current_trap == None:
                if trap_option[0][1] + trap_option[1][1] + trap_option[2][1] != 0:
                    print("Pro Tip: You still have functional traps. Choose one!")
                else:
                    print("Pro Tip: Before joining the hunt, you need a trap. Heading to the Carpenter might be a wise idea!")
            else:
                if cheese_count == 0:
                    print("Pro Tip: Before joining the hunt, you need cheese. Heading to the Cheese Shop might be a wise idea!")
                else:
                    if trap_cheese == None:
                        print("Pro Tip: Get started by placing your cheese on the trap!")
                    elif has_cheese(trap_cheese, cheese) == 0:
                        print("Pro Tip: Call it a cheesy advice but you know a cheese is only good for a hunt when placed in a trap, right?")
                    else:
                        print("Looking like a pro right there! Ready to hunt?")


            user_input2 = (input("Enter a number between 1 and 10: "))
            if user_input2.isdigit() == True:
                user_input2 = int(user_input2)
            else:
                print("Invalid input.")
                continue
            if user_input2 < 1 or user_input2 > 12:
                print("Must be between 1 and 12.")
                continue
            else:
                break
        print()

        if user_input2 == 11:
            while True:
                try:
                    hours = int(input("How many hours do you want to sleep? (1-8): ").strip())
                except ValueError:
                    print("Please enter a number.")
                    continue
                if 1 <= hours <= 8:
                    break
                print("Enter a number between 1 and 8.")
            sleep(hours)

        elif user_input2 == 12:
            food = eat_food(food)        
        
        elif user_input2 == 10:
            showStats(start_time, minutes_spent, cheese_bought, caught_mouse_dictionary, attempts)

        elif user_input2 == 9:
            current_trap = choose_trap(trap_option, current_trap)
            game_time = increase_time(game_time, 1)

        elif user_input2 == 8:
            print("Travelling to Old Carpenter...\n\n")
            game_time = increase_time(game_time, 2)
            drain_energy(ENERGY_TRAVEL_COST)
            drain_hunger(HUNGER_DRAIN_TRAVEL)

            time.sleep(3)
            result = visit_carpenter(TRAP, trap_option, wood, gold, points, carpenter_visit, cheese, current_trap, name, crate)
            # return (wood, gold, points, trap_option, carpenter_visit)
            wood = result[0]
            gold = result[1]
            points = result[2]
            trap_option = result[3]
            carpenter_visit = result[4]
            crate = result[5]

            print("Returning..\n\'n")
            time.sleep(3)
            game_time = increase_time(game_time, 2)

        elif user_input2 == 7:
            print("Travelling to Witch Doctor...\n\n")
            result = visit_witch_doctor(gold, food, player_health, name)
            gold = result[0]
            food = result[1]
            player_health = result[2]
            drain_energy(ENERGY_TRAVEL_COST)
            drain_hunger(HUNGER_DRAIN_TRAVEL)

        elif user_input2 == 6:
            gold = visit_trader(gold, crate, name)

        elif user_input2 == 5:
            scavenge()

        elif user_input2 == 4:
            if enchant == True:
                cheese_val = change_cheese(name, current_trap, cheese, True)
                #print(f"\nAfter change cheese: {cheese_val}\n")
            else:
                cheese_val = change_cheese(name, current_trap, cheese)

            trap_cheese = cheese_val[1]

            print("Returning..\n\'n")
            time.sleep(3)
            game_time = increase_time(game_time, 1)


        elif user_input2 == 3: #untested

            print("Travelling to Cheese Shop... \n\n")
            time.sleep(3)
            game_time = increase_time(game_time, 2)
            drain_energy(ENERGY_TRAVEL_COST)
            drain_hunger(HUNGER_DRAIN_TRAVEL)

            print("Cheese Dealer: Welcome to The Cheese Shop!")
            cheese_shop_art()
            print()

            while True:
                cheese_shop_intro()
                user_input3 = input()

                if user_input3.isdigit() == True:
                    user_input3 = int(user_input3)
                else:
                    print("Cheese Dealer: I did not understand.")
                    print()
                    continue

                if user_input3 < 1 or user_input3 > 3:
                    print("Cheese Dealer: I did not understand.")
                    print()
                    continue

                if user_input3 == 1:                        # need to do something with cheese dictioanry
                    print("Cheese Dealer: Welcome! Don't be stingy around here.\nThe more expensive cheese will help you have more successful and rewarding hunts!")
                    value = buy_cheese(gold, points)
                    gold -= value[0]
                    cheese[0][1] += value[1][0]
                    cheese[1][1] += value[1][1]
                    cheese[2][1] += value[1][2]
                    cheese_bought["Cheddar"] += value[1][0]
                    cheese_bought["Marble"] += value[1][1]
                    cheese_bought["Swiss"] += value[1][2]
                    #print(cheese)
                    print()
                elif user_input3 == 2:
                    display_inventory(wood, gold, cheese, current_trap, name)
                    print()
                else:
                    print("Cheese Dealer: Goodbye, then..")
                    print("Returning...")
                    time.sleep(2)
                    game_time = increase_time(game_time, 2)
                    break

        elif user_input2 == 1:
            # show final stats
            print(f"Thanks for joining our adventure, Hunter {name}!")
            time.sleep(3)
            print("\nDon't forget to check out your achievements:\n\n")
            showStats(start_time, minutes_spent, cheese_bought, caught_mouse_dictionary, attempts)
            key = input("Enter any key to exit... ")
            break

        else: #user_input = 2
            results = hunt(gold, cheese, trap_cheese, enchant, points, called_functions, attempts, caught_mouse_dictionary, game_over, crate, current_trap, trap_option)
            gold = results[0]
            points = results[1]
            cheese = results[2]
            called_functions = results[3]
            attempts = results[4]
            caught_mouse_dictionary = results[5]
            game_over = results[6]



if __name__ == '__main__':
    main()

