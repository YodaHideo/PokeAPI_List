from flask import Flask, render_template, request, redirect, url_for
import requests
import random
import os
import json

app = Flask(__name__)

# Создаем папку для хранения истории боя, если она не существует
if not os.path.exists("battle_history"):
    os.mkdir("battle_history")

# Функция для добавления раунда в историю боя и сохранения ее в файл
def add_round_to_battle_history(pokemon1_name, pokemon2_name, round_data):
    filename = f"{pokemon1_name}_{pokemon2_name}_battle_history.json"

    # Загрузим существующую историю, если она есть
    battle_history = load_battle_history_from_json(pokemon1_name, pokemon2_name)

    # Добавим новый раунд в историю
    battle_history.append(round_data)

    # Сохраним обновленную историю обратно в файл
    save_battle_history_to_json(pokemon1_name, pokemon2_name, battle_history)

def save_battle_history_to_json(pokemon1_name, pokemon2_name, battle_history):
    filename = f"{pokemon1_name}_{pokemon2_name}_battle_history.json"
    with open(filename, 'w') as file:
        json.dump(battle_history, file)

# Функция для сохранения истории боя в файл
def save_battle_history(name1, name2, battle_history):
    filename = f"{name1}_{name2}_battle_history.json"
    with open(filename, 'w') as file:
        json.dump(battle_history, file)

# Функция для загрузки истории боя из JSON
def load_battle_history_from_json(pokemon1_name, pokemon2_name):
    filename = f"{pokemon1_name}_{pokemon2_name}_battle_history.json"
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Функция для получения списка покемонов
def get_pokemon_list(offset=0, limit=20):
    url = f"https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_list = []
        for pokemon in data['results']:
            pokemon_data = get_pokemon_info(pokemon['name'])
            if pokemon_data:
                pokemon_list.append({
                    'name': pokemon_data['name'],
                    'image': pokemon_data['image'],
                    'type': pokemon_data['type'],
                    'height': pokemon_data['height'],
                    'weight': pokemon_data['weight'],
                    'hp': pokemon_data['hp'],
                    'attack_power': pokemon_data['attack_power'],
                    'abilities': pokemon_data['abilities'],
                })
        return pokemon_list
    return []

# Функция для получения информации о покемоне по его имени
def get_pokemon_info(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        name = data['name'].capitalize()
        weight = data['weight']
        height = data['height']
        image = data['sprites']['front_default']
        hp = data['stats'][0]['base_stat']
        attack_power = data['stats'][1]['base_stat']
        abilities = [ability['ability']['name'] for ability in data['abilities']]

        return {
            "name": name,
            "weight": weight,
            "height": height,
            "image": image,
            "hp": hp,
            "attack_power": attack_power,
            "abilities": ", ".join(abilities),
            "type": data['types'][0]['type']['name']
        }
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pokemon_name = request.form["pokemon_name"].strip().lower()
        if pokemon_name:
            return redirect(url_for("pokemon_info", name=pokemon_name))

    offset = int(request.args.get("offset", 0))
    limit = 20
    total_pokemon = 1000  # Обновите с фактическим общим количеством покемонов
    total_pages = (total_pokemon + limit - 1) // limit
    prev_offset = max(0, offset - limit)
    next_offset = min(offset + limit, total_pokemon)
    current_page = (offset // limit) + 1
    page_range = range(max(1, current_page - 3), min(total_pages + 1, current_page + 4))
    pokemon_list = get_pokemon_list(offset=offset, limit=limit)
    pagination_info = {
        "offset": offset,
        "limit": limit,
        "total_pokemon": total_pokemon,
        "total_pages": total_pages,
        "prev_offset": prev_offset,
        "next_offset": next_offset,
        "current_page": current_page,
        "page_range": page_range,
    }
    return render_template("index.html", pokemon_list=pokemon_list, **pagination_info)

@app.route("/fight/<name1>/<name2>", methods=["GET", "POST"])
def fight(name1, name2):
    pokemon1 = get_pokemon_info(name1)
    pokemon2 = get_pokemon_info(name2)

    # Получаем значения "pokemon1_hp" и "pokemon2_hp" из формы
    pokemon1_hp = request.form.get("pokemon1_hp")
    pokemon2_hp = request.form.get("pokemon2_hp")

    if pokemon1_hp and pokemon2_hp:
        pokemon1['hp'] = int(pokemon1_hp)
        pokemon2['hp'] = int(pokemon2_hp)

    battle_filename = f"{name1}_{name2}_battle_history.json"

    if os.path.exists(battle_filename):
        with open(battle_filename, 'r') as file:
            battle_history = json.load(file)
    else:
        battle_history = []

    battle_result = None

    if request.method == "POST":
        user_damage = request.form.get("user_damage")

        if user_damage and user_damage.isdigit():
            user_damage = int(user_damage)
            program_damage = random.randint(1, 10)

            if user_damage % 2 == program_damage % 2:
                attacker = pokemon1
                defender = pokemon2
                damage = attacker['attack_power']
            else:
                attacker = pokemon2
                defender = pokemon1
                damage = attacker['attack_power']

            defender['hp'] -= damage

            round_data = f"{attacker['name']} нанес {defender['name']} урон {damage}. {defender['name']} HP: {defender['hp']}"
            battle_history.append(round_data)

            if pokemon1['hp'] <= 0:
                battle_result = f"{pokemon2['name']} победил!"
            elif pokemon2['hp'] <= 0:
                battle_result = f"{pokemon1['name']} победил!"

            if battle_result:
                battle_history.append(f"Победитель: {battle_result}")

            with open(battle_filename, 'w') as file:
                json.dump(battle_history, file)

    return render_template("fight.html", pokemon1=pokemon1, pokemon2=pokemon2, battle_result=battle_result, battle_history=battle_history)

@app.route("/pokemon/<name>", methods=["GET", "POST"])
def pokemon_info(name):
    pokemon = get_pokemon_info(name)
    pokemon_list = get_pokemon_list()
    opponent = random.choice(pokemon_list)
    user_attack = request.form.get("user_attack")

    if user_attack and user_attack.isdigit():
        user_attack = int(user_attack)

        if pokemon:
            opponent_attack = random.randint(1, 10)
            user_hp = pokemon['hp']
            opponent_hp = random.randint(80, 120)

            if user_attack % 2 == 0:
                opponent_hp -= user_attack
            else:
                user_hp -= opponent_attack

            result = f"{pokemon['name'].capitalize()} HP: {user_hp}, Opponent HP: {opponent_hp}"
        else:
            result = "Pokemon not found."
    else:
        result = None

    return render_template("pokemon_info.html", pokemon=pokemon, opponent=opponent, result=result, pokemon_list=pokemon_list)

if __name__ == "__main__":
    app.run(debug=True)
