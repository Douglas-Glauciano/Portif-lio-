# game/states/city/city_hub_base.py
from ..base_state import BaseState
from .shop_state import ShopState
from game.database import save_character
import os

class CityHubBase(BaseState):
    def __init__(self, game, city_name, description):
        super().__init__(game)
        self.city_name = city_name
        self.description = description
        self.shops = self.get_city_shops()
        self.services = self.get_city_services()
        
    def get_city_shops(self):
        """Retorna lista de lojas da cidade"""
        raise NotImplementedError("Cada cidade deve implementar get_city_shops")
        
    def get_city_services(self):
        """Retorna lista de serviços da cidade"""
        return []  # Implementação básica - pode ser sobrescrita
        
    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        player = self.game.player
        
        # Cabeçalho com informações do jogador
        print("\n" + "=" * 50)
        print(f"    🌆 {self.city_name.upper()} 🌆".center(50))
        print("=" * 50)
        print(f"💰 Ouro: {player.gold} | ❤️ Vida: {player.hp}/{player.hp_max} | Mana💧: {player.mana}/{player.mana_max}")
        print("=" * 50)
        
        # Descrição da cidade
        print(f"\n{self.description}")
        
        # Lojas disponíveis
        print("\n" + "=" * 50)
        print("LOJAS E SERVIÇOS".center(50))
        print("=" * 50)
        for idx, shop in enumerate(self.shops, 1):
            print(f"{idx}. {shop['name']}")
        
        for idx, service in enumerate(self.services, len(self.shops) + 1):
            print(f"{idx}. {service['name']}")
        
        # Ações gerais
        print("\n" + "-" * 50)
        print("AÇÕES")
        print("-" * 50)
        action_start = len(self.shops) + len(self.services) + 1
        print(f"{action_start}. Explorar a cidade")
        print(f"{action_start+1}. Descansar na estalagem")
        
        # Menu do personagem
        print("\n" + "-" * 50)
        print("MENU DO PERSONAGEM")
        print("-" * 50)
        menu_start = action_start + 2
        print(f"{menu_start}. Atributos")
        print(f"{menu_start+1}. Inventário")
        print(f"{menu_start+2}. Configurações")
        print(f"{menu_start+3}. Voltar ao mundo aberto")
        print("=" * 50)
        
        # Armazena os índices para processamento
        self.total_shops = len(self.shops)
        self.total_services = len(self.services)
        self.action_start = action_start
        self.menu_start = menu_start
        self.return_option = menu_start + 3  # CORREÇÃO: Armazene o índice de retorno

    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        
        try:
            choice_idx = int(choice)
            
            # Lojas
            if 1 <= choice_idx <= self.total_shops:
                shop = self.shops[choice_idx-1]
                self.game.push_state(ShopState(
                    self.game,
                    shop_name=shop["name"],
                    npc_greeting=shop["greeting"],
                    shop_items=shop["items"]
                ))
                return
                
            # Serviços
            elif (self.total_shops + 1) <= choice_idx <= (self.total_shops + self.total_services):
                service_idx = choice_idx - self.total_shops - 1
                service = self.services[service_idx]
                self._handle_service(service)
                return
                
            # Ações
            elif choice_idx == self.action_start:
                self._explore_city()
            elif choice_idx == self.action_start + 1:
                self._rest_at_inn()
                
            # Menu do Personagem
            elif choice_idx == self.menu_start:
                from states.character.attributes_state import AttributesState
                self.game.push_state(AttributesState(self.game))
            elif choice_idx == self.menu_start + 1:
                from states.character.inventory_state import InventoryState
                self.game.push_state(InventoryState(self.game))
            elif choice_idx == self.menu_start + 2:
                from states.system.settings_state import SettingsState
                self.game.push_state(SettingsState(self.game))
            elif choice_idx == self.return_option:
                # Restaura a localização anterior (região selvagem)
                self.game.player.location = self.game.player.last_wilderness
                # Salva o progresso
                save_character(self.game.db_conn, self.game.player)

                # Volta ao mundo aberto
                self.game.pop_state()
                
            else:
                print("Opção inválida!")
                input("Pressione Enter para continuar...")
                
        except ValueError:
            print("Por favor, digite um número válido.")
            input("Pressione Enter para continuar...")

    def _handle_service(self, service):
        """Lida com serviços específicos da cidade"""
        # Implementação básica - pode ser expandida por cidade
        print(f"\nServiço selecionado: {service['name']}")
        input("Pressione Enter para continuar...")

    def _explore_city(self):
        """Exploração na cidade (eventos aleatórios)"""
        print("\nVocê explora as ruas da cidade...")
        # TODO: Implementar eventos aleatórios na cidade
        input("Pressione Enter para continuar...")

    def _rest_at_inn(self):
        from .inn_state import InnState  # Importe o novo estado
        self.game.push_state(InnState(self.game))