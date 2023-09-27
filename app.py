from flask import Flask, render_template, request, redirect, url_for
import requests
from prettytable import PrettyTable

app = Flask(__name__)

def get_pokemon_list():
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [pokemon['name'] for pokemon in data['results']]
    return []

def get_pokemon_info(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        table = PrettyTable()
        table.field_names = ["Параметр", "Значение"]
        table.add_row(["Имя", data['name'].capitalize()])
        table.add_row(["Вес (г)", data['weight']])
        table.add_row(["Рост (дм)", data['height']])

        types = ", ".join([entry['type']['name'].capitalize() for entry in data['types']])
        table.add_row(["Типы", types])

        return table.get_html_string()
    else:
        return f"Покемон с именем {pokemon_name} не найден."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pokemon_name = request.form["pokemon_name"].strip().lower()
        if pokemon_name:
            return redirect(url_for("pokemon_info", name=pokemon_name))

    pokemon_list = get_pokemon_list()
    return render_template("index.html", pokemon_list=pokemon_list)

@app.route("/pokemon/<name>")
def pokemon_info(name):
    result = get_pokemon_info(name)
    return render_template("pokemon_info.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
