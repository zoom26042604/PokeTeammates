import pandas as pd
import numpy as np
import requests
import threading

api_url = "https://pokeapi.co/api/v2/"

def get_pokemon_from_range(start_id, end_id):
    pokemon_list = []
    for i in range(start_id, end_id + 1):
        try:
            response = requests.get(f"{api_url}pokemon/{i}", timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Failed to fetch data for Pokemon ID {i}: {exc}")
            continue
        data = response.json()

        try:
            resp = requests.get(data["species"]["url"], timeout=10)
            resp.raise_for_status()
            generation = resp.json()["generation"]["name"]
            name = next(entry["name"] for entry in resp.json()["names"] if entry["language"]["name"] == "fr")
        except requests.RequestException as exc:
            print(f"Failed to fetch generation for Pokemon ID {i}: {exc}")
            generation = None
            name = None

        pokemon_list.append({
            "id": data["id"],
            "name": name,
            "types": [t["type"]["name"] for t in data["types"]],
            "abilities": [a["ability"]["name"] for a in data["abilities"]],
            "moves": [m["move"]["name"] for m in data["moves"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "game_indices": [g["version"]["name"] for g in data["game_indices"]],
            "generation": generation
        })
        print(f"Fetched data for Pokemon ID {i}: {data['name']}")
    return pd.DataFrame(pokemon_list)

def get_all_pokemon_in_csv():
    def _fetch_range(start_id, end_id):
        df = get_pokemon_from_range(start_id, end_id)
        pokemon_dataframes.append(df)
    
    total_pokemon = requests.get(f"{api_url}pokemon", timeout=10).json()["count"]
    print(f"Total Pokemon to fetch: {total_pokemon}")
    threads = []
    pokemon_dataframes = []

    for i in range(1, total_pokemon + 1, 100):
        start = i
        end = min(i + 99, total_pokemon)
        thread = threading.Thread(target=_fetch_range, args=(start, end))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    if not pokemon_dataframes:
        print("No Pokemon data was fetched. No CSV file will be created.")
    else:
        print("Successfully fetched all Pokemon data.")
        print("Creating CSV file for all Pokemon...")
        for df in pokemon_dataframes:
            df.dropna(inplace=True)
        pd.concat(pokemon_dataframes).sort_values(by="id").to_csv("pokemon_data.csv", index=False)
        print("CSV file for all Pokemon created successfully.")

def get_pokemon_by_id(pokemon_id):
    try:
        response = requests.get(f"{api_url}pokemon/{pokemon_id}", timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Failed to fetch data for Pokemon ID {pokemon_id}: {exc}")
        return None

    data = response.json()
    try:
        resp = requests.get(data["species"]["url"], timeout=10)
        resp.raise_for_status()
        generation = resp.json()["generation"]["name"]
        name = next(entry["name"] for entry in resp.json()["names"] if entry["language"]["name"] == "fr")
    except requests.RequestException:
        generation = None
        name =None

    return {
        "id": data["id"],
        "name": name,
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "moves": [m["move"]["name"] for m in data["moves"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
        "game_indices": [g["version"]["name"] for g in data["game_indices"]],
        "generation": generation
    }

def get_types_in_csv():
    type_list = []
    for i in range(1, requests.get(f"{api_url}type").json()["count"] + 1):
        response = requests.get(f"{api_url}type/{i}")
        if response.status_code == 200:
            data = response.json()
            type_list.append({
                "id": data["id"],
                "name": data["name"],
                "doubles_damage_from": [d["name"] for d in data["damage_relations"]["double_damage_from"]],
                "doubles_damage_to": [d["name"] for d in data["damage_relations"]["double_damage_to"]],
                "half_damage_from": [d["name"] for d in data["damage_relations"]["half_damage_from"]],
                "half_damage_to": [d["name"] for d in data["damage_relations"]["half_damage_to"]],
                "no_damage_from": [d["name"] for d in data["damage_relations"]["no_damage_from"]],
                "no_damage_to": [d["name"] for d in data["damage_relations"]["no_damage_to"]]
            })
            print(f"Fetched data for Type ID {i}: {data['name']}")
        else:
            print(f"Failed to fetch data for Type ID {i}")
    if not type_list:
        print("No types were fetched. No CSV file will be created.")
    else:
        print("Successfully fetched Pokemon types.")
        print("Creating CSV file for Pokemon types...")
        pd.DataFrame(type_list).to_csv("pokemon_types.csv", index=False)
        print("CSV file for Pokemon types created successfully.")


get_types_in_csv()
get_all_pokemon_in_csv()