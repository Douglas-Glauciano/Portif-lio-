# game/states/gameplay_state.py
from ..base_state import BaseState
from game.database import save_character
from game.utils import get_display_name, calculate_enhanced_damage, calculate_enhanced_armor_bonus
import os

class GameplayState(BaseState):
    def __init__(self, game):
        super().__init__(game) # <--- PASSE 'game' AQUI
        self.game = game
    
    def render(self):
        """Renderiza a tela principal do jogo, mostrando o status do jogador e opções."""
        player = self.game.player
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Atualiza os status do personagem
        player.recalculate()
        
        # Calcula percentuais para barras de HP e Mana
        hp_percent = min(100, int((player.hp / player.hp_max) * 100))
        mana_percent = min(100, int((player.mana / player.mana_max) * 100)) if player.mana_max > 0 else 0
        
        # Monta a string da barra de mana se o personagem tiver mana
        mana_display = ""
        if player.mana_max > 0:
            mana_display = (
                f"\n🔷 Mana: {player.mana}/{player.mana_max}\n"
                f"   [{'▓' * (mana_percent // 5)}{'░' * (20 - (mana_percent // 5))}] {mana_percent}%"
            )
        
        # Informações básicas do personagem
        print("\n" + "=" * 50)
        print(f"    🌟 AVENTURA DE {player.name.upper()} 🌟".center(50))
        print("=" * 50)
        print(f"🏹 Raça: {player.race} | ⚔️ Classe: {player.char_class} | ⭐ Nível: {player.level}")
        print(f"🧠 EXP: {player.exp}/{player.exp_max}")
        print(f"💰 Ouro: {player.gold}")
        print(f"\n❤️ Vida: {player.hp}/{player.hp_max}")
        print(f"   [{'█' * (hp_percent // 5)}{'░' * (20 - (hp_percent // 5))}] {hp_percent}%")
        
        # Mostra informações de mana se aplicável
        if mana_display:
            print(mana_display)
        
        # Mostra equipamentos principais com detalhes de aprimoramento
        equipped_items = player.get_equipped_items()
        weapon = next((item for item in equipped_items if item.get('category') == 'weapon' and item.get('equip_slot') == 'main_hand'), None)
        armor = next((item for item in equipped_items if item.get('category') == 'armor' and item.get('equip_slot') == 'body'), None)
        shield = next((item for item in equipped_items if item.get('category') == 'shield' and item.get('equip_slot') == 'off_hand'), None)

        # Calcula resistências totais
        physical_res = player.get_physical_resistance()
        magical_res = player.get_magical_resistance()
        dex_penalty = player.get_dexterity_penalty()
        
        print("\n" + "-" * 50)
        print("EQUIPAMENTO PRINCIPAL".center(50))
        print("-" * 50)
        
        # Exibição da Arma
        if weapon:
            display_name = get_display_name(weapon)
            enhanced_damage_str = calculate_enhanced_damage(weapon)
            damage_info = f"{enhanced_damage_str} {weapon.get('damage_type', '')}"
            enhancement_level = weapon.get('enhancement_level', 0)
            enhancement_str = f" (+{enhancement_level})" if enhancement_level > 0 else ""
            print(f"⚔️ Arma: {display_name} ({damage_info}{enhancement_str})")
        else:
            print("⚔️ Arma: Punhos (1d4 impacto)") # Dano desarmado padrão
            
        # Exibição da Armadura - agora mostra resistências em vez de bônus de AC
        if armor:
            display_name = get_display_name(armor)
            physical = armor.get('physical_resistance', 0)
            magical = armor.get('magical_resistance', 0)
            penalty = armor.get('dexterity_penalty', 0)
            enhancement_level = armor.get('enhancement_level', 0)
            enhancement_str = f" (+{enhancement_level})" if enhancement_level > 0 else ""
            
            print(f"🛡️ Armadura: {display_name}{enhancement_str}")
            print(f"   🛡️ Resistência Física: {physical} | ✨ Resistência Mágica: {magical}")
        else:
            print(f"🛡️ Armadura: Nenhuma")
        
        # Exibição do Escudo - mantém bônus de AC
        if shield:
            display_name = get_display_name(shield)
            shield_bonus = calculate_enhanced_armor_bonus(shield)
            enhancement_level = shield.get('enhancement_level', 0)
            enhancement_str = f" (+{enhancement_level})" if enhancement_level > 0 else ""
            print(f"🔰 Escudo: {display_name} (CA +{shield_bonus}{enhancement_str})")
        else:
            print("🔰 Escudo: Nenhum")

        print(f"⚠️ Penalidade Destreza Total: {dex_penalty}")

        # Determinar localização atual
        location = self._get_current_location()
        
        print("\n" + "=" * 50)
        print(f"{location.upper()} - AÇÕES".center(50))
        print("=" * 50)
        print("1. Explorar área (encontrar monstros e tesouros)")
        print("2. Descansar (recuperar vida e mana)")
        print("3. Viajar para outra região")
        print("-" * 50)
        print("MENU DO PERSONAGEM".center(50))
        print("-" * 50)
        print("4. Ver Atributos detalhados")
        print("5. Abrir inventário")
        print("6. Configurações")
        print("=" * 50)

    def _get_current_location(self):
        """Retorna o nome da localização atual baseada na posição do jogador"""
        locations = {
            # Regiões selvagens
            "forest": "Floresta Sombria",
            "mountains": "Montanhas Gélidas",
            "plains": "Planícies Ventosas",
            
            # Cidades
            "lindenrock": "Lindenrock",
            "vallengar": "Vallengar"
        }
        return locations.get(self.game.player.location, "Região Desconhecida")
    
    def handle_input(self):
        """Lida com a entrada do usuário na tela principal do jogo."""
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            from .explore_state import ExploreState
            self.game.change_state(ExploreState(self.game))
        elif choice == "2":
            from .rest_state import RestState
            self.game.change_state(RestState(self.game))
        elif choice == "3":
            self._handle_travel()
        elif choice == "4":
            from ..character.attributes_state import AttributesState
            self.game.push_state(AttributesState(self.game))
        elif choice == "5":
            from ..character.inventory_state import InventoryState
            self.game.push_state(InventoryState(self.game))
        elif choice == "6":
            from ..system.settings_state import SettingsState
            self.game.push_state(SettingsState(self.game))
        else:
            print("Opção inválida!")
            # Adiciona um pequeno atraso para o usuário ler a mensagem
            import time
            time.sleep(1) 
    
    def _handle_travel(self):
        """Mostra opções de viagem e lida com a escolha do jogador."""
        print("\n" + "=" * 50)
        print("DESTINOS DISPONÍVEIS".center(50))
        print("=" * 50)
        print("1. Lindenrock (Vila nas Montanhas)")
        print("2. Vallengar (Cidade Portuária)")
        print("3. Cancelar")
        print("=" * 50)
        
        travel_choice = input("Para onde deseja viajar? ").strip()
        
        if travel_choice == "1":
            self._travel_to("lindenrock")
        elif travel_choice == "2":
            self._travel_to("vallengar")
        elif travel_choice == "3":
            print("\nViagem cancelada.")
            import time
            time.sleep(1)
        else:
            print("\nOpção inválida!")
            import time
            time.sleep(1)

    def _travel_to(self, city_name):
        """Viaja para uma cidade e muda para o estado da cidade."""
        # Salva a localização atual como última região selvagem
        self.game.player.last_wilderness = self.game.player.location
        
        # Atualiza para a nova localização (cidade)
        self.game.player.location = city_name
        
        # Salva o progresso do personagem
        save_character(self.game.db_conn, self.game.player)
        
        # Importa dinamicamente o hub da cidade para evitar importações circulares
        from states.city import get_city_hub
        city_state = get_city_hub(self.game, city_name)
        
        # Empilha o estado da cidade
        self.game.push_state(city_state)

