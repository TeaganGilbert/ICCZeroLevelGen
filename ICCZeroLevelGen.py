import os
import random
import csv
import re

def roll_dice(sides=6):
    return random.randint(1, sides)

def generate_random_stat():
    return sum(roll_dice() for _ in range(3))

def generate_modifier(stat):
    modifier_table = {
        3: -3,
        4: -2,
        5: -2,
        6: -1,
        7: -1,
        8: -1,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 1,
        14: 1,
        15: 1,
        16: 2,
        17: 2,
        18: 3
    }
    return modifier_table.get(stat, 0)

def generate_starting_funds():
    return sum(roll_dice(12) for _ in range(5))

def load_occupations(file_path):
    occupations = []
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Normalize keys by stripping spaces
            row = {key.strip(): value for key, value in row.items()}
            occupations.append(row)
    return occupations

def load_weapons(file_path):
    weapons = {}
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            weapons[row['Weapon'].strip().lower()] = {
                'Damage': row['Damage'].strip(),
                'Range': row['Range'].strip()
            }
    return weapons

def load_birth_augur_table(file_path):
    birth_augur_table = []
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            birth_augur_table.append({
                'd30': int(row['d30'].strip()),
                'Birth Augur': row['Birth Augur'].strip(),
                'Lucky Roll': row['Lucky Roll'].strip()
            })
    return birth_augur_table

def get_occupation(occupations):
    roll = roll_dice(100)
    for occupation in occupations:
        if '-' in occupation['roll']:
            start, end = map(int, occupation['roll'].split('-'))
            if start <= roll <= end:
                return occupation
        elif int(occupation['roll']) == roll:
            return occupation
    return None

def get_equipment():
    equipment_table = {
        1: ("Backpack", "2 gp"),
        2: ("Candle", "1 cp"),
        3: ("Chain 10'", "30 gp"),
        4: ("Chalk, 1 piece", "1 cp"),
        5: ("Chest, empty", "2 gp"),
        6: ("Crowbar", "2 gp"),
        7: ("Flask, empty", "3 cp"),
        8: ("Flint & steel", "15 cp"),
        9: ("Grappling hook", "1 gp"),
        10: ("Hammer, small", "5 sp"),
        11: ("Book", "25 gp"),
        12: ("Ball bearings, 1lb", "1 gp"),
        13: ("Bag of caltrops", "5 sp"),
        14: ("Lantern", "10 gp"),
        15: ("Mirror, hand sized", "10 gp"),
        16: ("Oil, 1 flask", "2 sp"),
        17: ("Pole 10-ft", "15 cp"),
        18: ("Rations, per day", "5 cp"),
        19: ("Rope, 50 '", "25 cp"),
        20: ("Sack, large", "12 cp"),
        21: ("Sack, small", "8 cp"),
        22: ("Thieves' tools", "25 gp"),
        23: ("Torch, each", "1 cp"),
        24: ("Waterskin", "5 sp")
    }
    roll = roll_dice(24)
    return equipment_table[roll]

def extract_weapon_name(weapon):
    match = re.search(r'\((as )?([^\)]+)\)', weapon)
    if match:
        return match.group(2).strip().lower()
    else:
        return weapon.strip().lower()

def get_weapon_damage(weapon, weapons):
    weapon_name = extract_weapon_name(weapon)
    
    # Look up the damage value for the weapon
    if weapon_name in weapons:
        return weapons[weapon_name]['Damage']
    else:
        raise ValueError(f"Weapon '{weapon_name}' not found in weapons table")

def get_weapon_modifier(weapon, weapons, stats):
    weapon_name = extract_weapon_name(weapon)
    
    # Determine if the weapon is melee or ranged
    if weapon_name in weapons:
        if weapons[weapon_name]['Range'] == '-':
            return generate_modifier(stats['Strength'])
        else:
            return generate_modifier(stats['Agility'])
    else:
        raise ValueError(f"Weapon '{weapon_name}' not found in weapons table")

def get_birth_augur(birth_augur_table):
    roll = roll_dice(30)
    for entry in birth_augur_table:
        if entry['d30'] == roll:
            return entry
    return None

def generate_content(occupations, weapons, birth_augur_table):
    stats = {
        "Strength": generate_random_stat(),
        "Agility": generate_random_stat(),
        "Stamina": generate_random_stat(),
        "Personality": generate_random_stat(),
        "Intelligence": generate_random_stat(),
        "Luck": generate_random_stat()
    }

    occupation = get_occupation(occupations)
    equipment, cost = get_equipment()
    weapon_damage = get_weapon_damage(occupation['Trained Weapon'], weapons)
    weapon_modifier = get_weapon_modifier(occupation['Trained Weapon'], weapons, stats)

    # Set speed based on occupation
    speed = 20 if occupation['Occupation'].lower().startswith('goblin') else 30

    # Set Init, Ref, Fort, and Will based on corresponding modifiers
    init = generate_modifier(stats['Agility'])
    ref = generate_modifier(stats['Agility'])
    fort = generate_modifier(stats['Stamina'])
    will = generate_modifier(stats['Personality'])

    # Calculate AC and HP
    ac = 10 + generate_modifier(stats['Agility'])
    hp = max(1, roll_dice(4) + generate_modifier(stats['Stamina']))

    # Format weapon modifier with a + sign if it is >= 0
    weapon_modifier_str = f"+{weapon_modifier}" if weapon_modifier >= 0 else str(weapon_modifier)

    # Get birth augur
    birth_augur = get_birth_augur(birth_augur_table)
    birth_augur_str = f"{birth_augur['Birth Augur']} ({birth_augur['Lucky Roll']}) ({generate_modifier(stats['Luck'])})"

    # Apply luck modifier based on birth augur roll
    luck_modifier = generate_modifier(stats['Luck'])
    if luck_modifier != 0:
        weapon_name = extract_weapon_name(occupation['Trained Weapon'])
        if birth_augur['d30'] == 1:
            weapon_modifier += luck_modifier
        elif birth_augur['d30'] == 2 and weapons[weapon_name]['Range'] == '-':
            weapon_modifier += luck_modifier
        elif birth_augur['d30'] == 3 and weapons[weapon_name]['Range'] != '-':
            weapon_modifier += luck_modifier
        elif birth_augur['d30'] == 6:
            weapon_damage += f"+{luck_modifier}" if luck_modifier > 0 else str(luck_modifier)
        elif birth_augur['d30'] == 7 and weapons[weapon_name]['Range'] == '-':
            weapon_damage += f"+{luck_modifier}" if luck_modifier > 0 else str(luck_modifier)
        elif birth_augur['d30'] == 8 and weapons[weapon_name]['Range'] != '-':
            weapon_damage += f"+{luck_modifier}" if luck_modifier > 0 else str(luck_modifier)
        elif birth_augur['d30'] == 9:
            weapon_damage += f"+{luck_modifier}" if luck_modifier > 0 else str(luck_modifier)
            weapon_modifier += luck_modifier
        elif birth_augur['d30'] == 17:
            ref += luck_modifier
            fort += luck_modifier
            will += luck_modifier
        elif birth_augur['d30'] == 20:
            ref += luck_modifier
        elif birth_augur['d30'] == 21:
            fort += luck_modifier
        elif birth_augur['d30'] == 22:
            will += luck_modifier
        elif birth_augur['d30'] == 23:
            ac += luck_modifier
        elif birth_augur['d30'] == 24:
            init += luck_modifier
        elif birth_augur['d30'] == 25:
            hp = max(1, hp + luck_modifier)
        elif birth_augur['d30'] == 30:
            speed += luck_modifier * 5

    # Reformat weapon modifier string after applying luck modifier
    weapon_modifier_str = f"+{weapon_modifier}" if weapon_modifier >= 0 else str(weapon_modifier)

    # Set languages based on occupation
    languages = ["Trade Common"]
    if occupation['Occupation'].lower().startswith('goblin'):
        languages.append("Goblin")
    elif occupation['Occupation'].lower().startswith('orc'):
        languages.append("Orc")
    elif occupation['Occupation'].lower().startswith('siren'):
        languages.append("Siren")

    content = f"""0-level Occupation: {occupation['Occupation']}
Strength: {stats['Strength']} ({generate_modifier(stats['Strength'])})
Agility: {stats['Agility']} ({generate_modifier(stats['Agility'])})
Stamina: {stats['Stamina']} ({generate_modifier(stats['Stamina'])})
Personality: {stats['Personality']} ({generate_modifier(stats['Personality'])})
Intelligence: {stats['Intelligence']} ({generate_modifier(stats['Intelligence'])})
Luck: {stats['Luck']} ({generate_modifier(stats['Luck'])})

AC: {ac}; HP: {hp}
Weapon: {occupation['Trained Weapon']} {weapon_modifier_str} ({weapon_damage})
Speed: {speed}; Init: {init}; Ref: {ref}; Fort: {fort}; Will: {will}

Equipment: {equipment} ({cost})
Trade good: {occupation['Trade Good']}
Starting Funds: {generate_starting_funds()} cp
Lucky sign: {birth_augur_str}
Languages: {', '.join(languages)}
"""
    return content

def generate_text_file(file_path, content):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Check if the file exists and iterate the filename if it does
    base, extension = os.path.splitext(file_path)
    counter = 1
    new_file_path = file_path
    while os.path.exists(new_file_path):
        new_file_path = f"{base}_{counter}{extension}"
        counter += 1
    
    with open(new_file_path, 'w') as file:
        file.write(content)

    return new_file_path

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load occupations from CSV
    occupations_file_path = os.path.join(script_dir, 'occupation csv.csv')
    occupations = load_occupations(occupations_file_path)
    
    # Load weapons from CSV
    weapons_file_path = os.path.join(script_dir, 'Weapons_Table.csv')
    weapons = load_weapons(weapons_file_path)
    
    # Load birth augur table from CSV
    birth_augur_table_file_path = os.path.join(script_dir, 'Birth_Augur_Table.csv')
    birth_augur_table = load_birth_augur_table(birth_augur_table_file_path)
    
    # Generate content for four character sheets
    content = ""
    for _ in range(4):
        content += generate_content(occupations, weapons, birth_augur_table)
        content += "\n\n"  # Add a couple of line breaks between character sheets
    
    # Update the file path to the specified directory
    file_path = os.path.join(script_dir, 'ICC_0-Level_sheet.txt')
    
    # Generate the text file with the content
    new_file_path = generate_text_file(file_path, content)
    print(f"File generated at {new_file_path}")