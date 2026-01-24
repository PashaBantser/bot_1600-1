import json


def create_json(data: dict, name_file:str):
    with open(file=f"data/{name_file}", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))

def read_json(name_file: str) -> dict:
    with open(file=f"data/{name_file}", mode="r", encoding="utf-8") as file:
        return json.load(file)