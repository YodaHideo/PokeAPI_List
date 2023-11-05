from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from ftplib import FTP
from datetime import datetime
import random
from flask_sqlalchemy import SQLAlchemy
#пароль от почты яндекс: kuqiqkiiyplmnhey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@127.0.0.2:5433/poke'
db = SQLAlchemy(app)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_gmail(subject, text, attachment_path=None):
    # Настройки почты
    smtp_server = 'smtp.yandex.ru'
    smtp_port = 465  # Порт вашего SMTP-сервера
    smtp_username = 'Alex09918@yandex.ru'
    smtp_password = 'kuqiqkiiyplmnhey'
    sender_email = 'Alex09918@yandex.ru'
    receiver_email = 'alex0991818628@mail.ru'  # Адрес получателя

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Добавление текстового сообщения
    text_part = MIMEText(text, 'plain', 'utf-8')
    msg.attach(text_part)

    # Установка соединения с SMTP-сервером Gmail
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

class BattleHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pokemon1_name = db.Column(db.String(50), nullable=False)
    pokemon2_name = db.Column(db.String(50), nullable=False)
    round_data = db.Column(db.JSON, nullable=False)

    def __init__(self, pokemon1_name, pokemon2_name, round_data):
        self.pokemon1_name = pokemon1_name
        self.pokemon2_name = pokemon2_name
        self.round_data = round_data


# Функция для добавления раунда в историю боя и сохранения ее в файл
def add_round_to_battle_history(pokemon1_name, pokemon2_name, round_data):
    existing_record = BattleHistory.query.filter_by(pokemon1_name=pokemon1_name, pokemon2_name=pokemon2_name).first()

    if existing_record:
        # Если запись существует, обновляем ее
        existing_record.round_data = [round_data]
    else:
        # Если записи нет, создаем новую
        battle_record = BattleHistory(pokemon1_name=pokemon1_name, pokemon2_name=pokemon2_name, round_data=[round_data])
        db.session.add(battle_record)

    db.session.commit()


# Функция для сохранения истории боя в файл
def save_battle_history_to_db(pokemon1_name, pokemon2_name, battle_history):
    battle_record = BattleHistory(pokemon1_name=pokemon1_name, pokemon2_name=pokemon2_name, round_data=battle_history)
    db.session.add(battle_record)
    db.session.commit()

# Функция для загрузки истории боя из JSON
def load_battle_history_from_db(pokemon1_name, pokemon2_name):
    battle_records = BattleHistory.query.filter_by(pokemon1_name=pokemon1_name, pokemon2_name=pokemon2_name).all()
    battle_history = [record.round_data for record in battle_records]
    return battle_history

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

import requests

def get_pokemon_ids(id=0):
    url = f"https://pokeapi.co/api/v2/pokemon?offset=0&limit=1000"
    if id == 0:
        id = random.randint(1, 20)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_list = []
        for pokemon in data['results']:
            pokemon_data = get_pokemon_infoS(pokemon['name'])
            if pokemon_data['id'] == id:
                pokemon_list.append({
                    'id': pokemon_data['id'],
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

@app.route("/pokemon/list<filters>", methods=["GET"])
def get_filtered_pokemon_list(filters):
    filters = request.args.get("filters")
    if filters:
        # Вызываем функцию get_filtered_pokemon для получения отфильтрованного списка
        filtered_pokemon_list = get_filtered_pokemon(filters)
    else:
        # Если фильтры не указаны, возвращаем список всех покемонов
        filtered_pokemon_list = get_pokemon_list()

    return jsonify(filtered_pokemon_list)
@app.route("/pokemon/random", methods=["GET"])
def get_random_pokemon():
    pokemon_data = get_pokemon_ids()
    return jsonify(pokemon_data)
@app.route("/pokemon/<int:pokemon_id>", methods=["GET"])
def get_random_pokemon_by_id(pokemon_id):
    pokemon_data = get_pokemon_ids(pokemon_id)
    return jsonify(pokemon_data)

# Логика для получения информации о покемоне с фильтрацией
def get_filtered_pokemon(pokemon_id, filters):
    # Получаем информацию о покемоне без фильтрации
    pokemon_info = get_pokemon_infoS(pokemon_id)

    # Применяем фильтры к информации о покемоне
    filtered_pokemon_info = {}
    print(filters)
    if "abilities" in filters:
        # Фильтр по способностям покемона
        abilities_filter = filters["abilities"].split(", ")
        filtered_pokemon_info["abilities"] = [ability for ability in pokemon_info["abilities"] if ability in abilities_filter]

    if "type" in filters:
        # Фильтр по типу покемона
        type_filter = filters["type"]
        if pokemon_info["type"] == type_filter:
            filtered_pokemon_info["type"] = pokemon_info["type"]

    return filtered_pokemon_info
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
def get_pokemon_infoS(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        id = data['id']
        name = data['name'].capitalize()
        weight = data['weight']
        height = data['height']
        image = data['sprites']['front_default']
        hp = data['stats'][0]['base_stat']
        attack_power = data['stats'][1]['base_stat']
        abilities = [ability['ability']['name'] for ability in data['abilities']]

        return {
            "id": id,
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

def save_pokemon_info_to_ftp(pokemon_name, info):
    # Параметры подключения к FTP-серверу
    ftp_host = '127.0.0.1'  # Замените на адрес своего FTP-сервера
    ftp_port = 21
    ftp_user = 'lexa'
    ftp_password = '1234'

    # Создаем имя файла в формате yyyymmdd_pokemon_name.md
    current_date = datetime.now().strftime('%Y%m%d')
    filename = f"{current_date}_{pokemon_name}.md"

    # Формируем содержимое файла в формате Markdown
    markdown_content = f"# {pokemon_name}\n\n{info}"

    try:
        # Подключаемся к FTP-серверу
        with FTP() as ftp:
            ftp.connect(ftp_host, ftp_port)
            ftp.login(ftp_user, ftp_password)

            # Создаем папку с именем текущей даты
            ftp.mkd(current_date)

            # Переходим в созданную папку
            ftp.cwd(current_date)

            # Загружаем файл на FTP-сервер
            with open(filename, 'wb') as file:
                file.write(markdown_content.encode('utf-8'))
            ftp.storbinary(f"STOR {filename}", open(filename, 'rb'))

            return f"Информация о покемоне {pokemon_name} сохранена на FTP-сервере в папке {current_date}."
    except Exception as e:
        return f"Ошибка при сохранении информации на FTP: {str(e)}"


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

    battle_history = load_battle_history_from_db(name1, name2)
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
                print(battle_history)
                email_text = "\n".join(str(item) for item in battle_history)  # Объединяем элементы списка в одну строку
                send_email_gmail("Результаты боя Pokemon", email_text)  # Отправляем текстовое письмо


            save_battle_history_to_db(name1, name2, battle_history)

    return render_template("fight.html", pokemon1=pokemon1, pokemon2=pokemon2, battle_result=battle_result, battle_history=battle_history)


@app.route("/pokemon/<name>", methods=["GET", "POST"])
def pokemon_info(name):
    pokemon = get_pokemon_info(name)
    pokemon_list = get_pokemon_list()
    opponent = random.choice(pokemon_list)
    user_attack = request.form.get("user_attack")
    info = f"Тип: {pokemon['type']}\n"
    info += f"Вес: {pokemon['weight']}\n"
    info += f"Высота: {pokemon['height']}\n"
    info += f"Здоровье: {pokemon['hp']}\n"
    info += f"Сила атаки: {pokemon['attack_power']}\n"
    info += f"Способности: {pokemon['abilities']}\n"
    save_pokemon_info_to_ftp(pokemon['name'], info)
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