# states/city/vallengar/hub.py
from states.city.city_hub_base import CityHubBase
from states.city.blacksmith_state import BlacksmithState  # Importe o novo estado
from game.config import CITY_DATA

class VallengarHub(CityHubBase):
    def __init__(self, game):
        description = (
            "Uma movimentada cidade portuária onde o cheiro do mar se mistura com o aroma "
            "de especiarias exóticas. Navios de todas as partes do mundo atracam aqui, "
            "trazendo mercadorias raras e notícias de terras distantes."
        )
        super().__init__(game, "Vallengar", description)
        
    def get_city_shops(self):
        city_info = CITY_DATA["vallengar"]
        return [
            {
                "name": "🏪 Mercado do Porto",
                "greeting": "Produtos frescos direto dos navios!",
                "items": city_info["shops"]["market"]
            },
            {
                "name": "⚓ Estaleiro Naval",
                "greeting": "Equipamentos para navegantes destemidos!",
                "items": city_info["shops"]["shipyard"]
            },
            {
                "name": "Ferraria do Magnus",
                "greeting": "Bem-vindo à minha ferraria! Eu forjo as melhores armas e armaduras desta terra. "
                           "Posso vender equipamentos para você ou aprimorar seus itens existentes.",
                "items": self._get_blacksmith_items(),
                "service_type": "blacksmith"  # Identificador único para ferraria
            }
        ]
    
    def get_city_services(self):
        return [
            {
                "name": "⚓ Guilda dos Marinheiros (Missões)",
                "type": "quests"
            },
            {
                "name": "⚔️ Arena de Combate",
                "type": "arena"
            },
            {
                "name": "🔨 Ferraria do Marco",
                "type": "blacksmith"
            }
        ]
    
    def _handle_service(self, service):
        if service['type'] == 'arena':
            print("\nVocê entra na Arena de Combate de Vallengar!")
            # TODO: Implementar sistema de arena
            input("Pressione Enter para continuar...")
        elif service['type'] == 'blacksmith':
            # Direciona para a ferraria principal
            self._go_to_blacksmith()
        else:
            super()._handle_service(service)
    
    def _go_to_blacksmith(self):
        """Direciona o jogador para a ferraria principal"""
        blacksmith_shop = next(
            shop for shop in self.shops 
            if shop.get("service_type") == "blacksmith"
        )
        
        self.game.push_state(BlacksmithState(
            self.game,
            shop_name=blacksmith_shop["name"],
            npc_greeting=blacksmith_shop["greeting"],
            shop_items=blacksmith_shop["items"]
        ))
    
    def _get_blacksmith_items(self):
        """Itens básicos vendidos na ferraria"""
        # Retorna IDs dos itens básicos de ferraria
        return  [
    # Armas (1–22)
    1, 2, 3, 4, 5,
    6, 7, 8, 9, 10,
    11, 12, 13, 14,
    15, 16, 17, 18,
    19, 20, 21, 22,

    # Armaduras (101–120)
    101, 102, 103, 104,
    105, 106, 107, 108,
    109, 110, 111, 112,
    113, 114, 115, 116,
    117, 118, 119, 120,

    # Escudos (201–203)
    201, 202, 203
]