# game/states/city/__init__.py
from .lindenrock.hub import LindenrockHub  # Importação relativa correta
from .vallengar.hub import VallengarHub    # Importação relativa correta

def get_city_hub(game, city_name):
    # Normaliza o nome da cidade para minúsculas
    normalized_name = city_name.lower()
    
    cities = {
        "lindenrock": LindenrockHub,
        "vallengar": VallengarHub
    }
    
    city_class = cities.get(normalized_name)
    if city_class:
        return city_class(game)
    else:
        # Fallback para Lindenrock se a cidade não for encontrada
        return LindenrockHub(game)