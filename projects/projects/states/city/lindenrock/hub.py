# states/city/lindenrock/hub.py
from states.city.city_hub_base import CityHubBase 
from game.config import CITY_DATA

class LindenrockHub(CityHubBase):
    def __init__(self, game):
        description = (
            "Uma pequena vila encravada nas montanhas rochosas. O ar frio da montanha "
            "e o cheiro de fogueiras preenchem as ruas de pedra. A vila é conhecida por "
            "seus mineradores resistentes e ferreiros habilidosos."
        )
        super().__init__(game, "Lindenrock", description)
        
    def get_city_shops(self):
        city_info = CITY_DATA["lindenrock"]
        return [
            {
                "name": "🏪 Mercado de Lindenrock",
                "greeting": "Bem-vindo ao melhor mercado da região!",
                "items": city_info["shops"]["market"]
            },
            {
                "name": "⚒️ Ferraria do Rolf",
                "greeting": "Armas e armaduras de qualidade para aventureiros!",
                "items": city_info["shops"]["blacksmith"]
            }
        ]
    
    def get_city_services(self):
        return [
            {
                "name": "📜 Casa do Sábio (Aprender Habilidades)",
                "type": "training"
            }
        ]