# states/city/blacksmith_state.py
from ..base_state import BaseState
from game.db_queries import update_character_gold, enhance_inventory_item # Importa nova função de aprimoramento
from game.utils import get_display_name, calculate_enhanced_damage, calculate_enhanced_value # Importa funções de utilidade
import os 
from game.utils import calculate_attack_bonus, calculate_enhanced_resistances, calculate_enhanced_armor_bonus

class BlacksmithState(BaseState):
    def __init__(self, game, shop_name, npc_greeting, shop_items):
        super().__init__(game)
        self.shop_name = shop_name
        self.npc_greeting = npc_greeting
        self.shop_items = shop_items
        self.mode = "main"  # main, buy, enhance_list, enhance_detail
        self.selected_item = None
        self.items_to_enhance = []
        self.feedback_message = ""
        self.item_icons = {
            'weapon': '⚔️',
            'armor': '🛡️',
            'shield': '🔰',
            'consumable': '🧪',
            'misc': '📦',
            'other': '❓'
        }
    
    def enter(self):
        self.feedback_message = ""
        self.mode = "main"
        self.render()

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "=" * 60)
        print(f"FERRARIA - {self.shop_name.upper()}".center(60))
        print("=" * 60)
        
        if self.feedback_message:
            print(f"\n>>> {self.feedback_message} <<<\n")
            self.feedback_message = ""

        if self.mode == "main":
            self._render_main_menu()
        elif self.mode == "buy":
            self._render_buy_menu()
        elif self.mode == "enhance_list":
            self._render_enhance_list_menu()
        elif self.mode == "enhance_detail":
            self._render_enhance_detail_menu()

    def _render_main_menu(self):
        print(f"\n{self.npc_greeting}\n")
        print("1. Comprar equipamentos")
        print("2. Aprimorar equipamentos")
        print("3. Voltar para a cidade")
        print("=" * 60)

    def _render_buy_menu(self):
        print("\nModo de compra ainda não implementado.")
        print("1. Voltar ao menu principal")
        print("=" * 60)

    def _render_enhance_list_menu(self):
        print("\n" + "FORJA DE APRIMORAMENTO".center(60, '-'))
        print("Escolha um item para aprimorar:".center(60))
        print("-" * 60)

        inventory_items = self.game.player.get_inventory()
        equipped_items = self.game.player.get_equipped_items()
        all_player_items = inventory_items + equipped_items
        
        self.items_to_enhance = [
            item for item in all_player_items 
            if item.get('category') in ['weapon', 'armor', 'shield']
        ]

        if not self.items_to_enhance:
            print("   Você não tem itens aprimoráveis (armas, armaduras, escudos).")
        else:
            for i, item in enumerate(self.items_to_enhance, 1):
                display_name = get_display_name(item)
                icon = self.item_icons.get(item.get('category', 'other'), '❓')
                enhancement_level = item.get('enhancement_level', 0)
                enhancement_str = f" +{enhancement_level}" if enhancement_level > 0 else ""
                
                # Adiciona um indicador se o item está equipado
                is_equipped = any(eq_item['inventory_id'] == item['inventory_id'] for eq_item in equipped_items)
                equipped_indicator = " (Equipado)" if is_equipped else ""
                
                print(f"{i}. {icon} {display_name}{enhancement_str}{equipped_indicator}")
        
        print("\n0. ↩️ Voltar")
        print("=" * 60)

    def _render_enhance_detail_menu(self):
        if not self.selected_item:
            self.feedback_message = "Nenhum item selecionado para aprimoramento."
            self.mode = "enhance_list"
            return
        
        item = self.selected_item
        display_name = get_display_name(item)
        icon = self.item_icons.get(item.get('category', 'other'), '❓')
        current_level = item.get('enhancement_level', 0)
        
        print(f"\n{icon} APRIMORAR: {display_name.upper()}".center(60))
        print("-" * 60)
        
        print(f"Nível atual: +{current_level}")

        if current_level >= 5:
            print("\nEste item já alcançou o nível máximo de aprimoramento! ⭐")
            print("\n1. Escolher outro item")
            print("2. Voltar ao menu principal")
        else:
            new_level = current_level + 1
            cost = self._calculate_enhancement_cost(current_level)
            
            print(f"\nCusto para aprimorar para +{new_level}: {cost} de ouro")
            print(f"Seu ouro: {self.game.player.gold}\n")
            
            # Exibe estatísticas detalhadas baseadas no tipo de item
            if item['category'] == 'weapon':
                self._render_weapon_details(item, new_level)
            elif item['category'] == 'armor':
                self._render_armor_details(item, new_level)
            elif item['category'] == 'shield':
                self._render_shield_details(item, new_level)
            
            # Exibe benefícios adicionais
            benefits = self.game.player.get_enhancement_benefits(item, new_level)
            if benefits:
                print("\nBenefícios adicionais do próximo nível:")
                for benefit in benefits:
                    print(f"   {benefit}")
            
            print("\n1. Aprimorar")
            print("2. Escolher outro item")
            print("3. Voltar ao menu principal")
        print("=" * 60)

    def _render_weapon_details(self, item, new_level):
        """Exibe detalhes específicos para armas"""
        current_damage = calculate_enhanced_damage(item)
        current_attack_bonus = calculate_attack_bonus(item)
        
        # Simula o item com o próximo nível
        temp_item = item.copy()
        temp_item['enhancement_level'] = new_level
        new_damage = calculate_enhanced_damage(temp_item)
        new_attack_bonus = calculate_attack_bonus(temp_item)
        
        print(f"Dano atual: {current_damage}")
        print(f"Bônus de ataque atual: +{current_attack_bonus}")
        print(f"Após aprimoramento: {new_damage} (+{new_attack_bonus - current_attack_bonus} ataque)")

    def _render_armor_details(self, item, new_level):
        """Exibe detalhes específicos para armaduras"""
        current_res = calculate_enhanced_resistances(item)
        current_penalty = item.get('dexterity_penalty', 0) - (item.get('enhancement_level', 0) // 3)
        
        # Simula o item com o próximo nível
        temp_item = item.copy()
        temp_item['enhancement_level'] = new_level
        new_res = calculate_enhanced_resistances(temp_item)
        new_penalty = item.get('dexterity_penalty', 0) - (new_level // 3)
        
        print("Resistências atuais:")
        print(f"  Física: {current_res['physical_resistance']}")
        print(f"  Mágica: {current_res['magical_resistance']}")
        if current_penalty > 0:
            print(f"  Penalidade de destreza: -{current_penalty}")
        
        print("\nApós aprimoramento:")
        print(f"  Física: {new_res['physical_resistance']} (+1)")
        print(f"  Mágica: {new_res['magical_resistance']} (+1)")
        if new_penalty < current_penalty:
            print(f"  Penalidade de destreza: -{new_penalty} (reduzida)")

    def _render_shield_details(self, item, new_level):
        """Exibe detalhes específicos para escudos"""
        current_armor_bonus = calculate_enhanced_armor_bonus(item)
        
        # Simula o item com o próximo nível
        temp_item = item.copy()
        temp_item['enhancement_level'] = new_level
        new_armor_bonus = calculate_enhanced_armor_bonus(temp_item)
        
        print(f"Bônus de CA atual: +{current_armor_bonus}")
        print(f"Após aprimoramento: +{new_armor_bonus} (+1)")

    def _calculate_enhancement_cost(self, current_level):
        return 50 * (2 ** current_level)

    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        
        if self.mode == "main":
            self._handle_main_input(choice)
        elif self.mode == "buy":
            self._handle_buy_input(choice)
        elif self.mode == "enhance_list":
            self._handle_enhance_list_input(choice)
        elif self.mode == "enhance_detail":
            self._handle_enhance_detail_input(choice)

    def _handle_main_input(self, choice):
        if choice == "1":
            self.mode = "buy"
        elif choice == "2":
            self.mode = "enhance_list"
        elif choice == "3":
            self.game.pop_state()
        else:
            self.feedback_message = "Opção inválida!"

    def _handle_buy_input(self, choice):
        if choice == "1":
            self.mode = "main"
        else:
            self.feedback_message = "Opção inválida!"

    def _handle_enhance_list_input(self, choice):
        if choice == "0":
            self.mode = "main"
            self.selected_item = None
            self.items_to_enhance = []
            return
            
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(self.items_to_enhance):
                self.selected_item = self.items_to_enhance[choice_idx]
                self.mode = "enhance_detail"
            else:
                self.feedback_message = "Seleção inválida!"
        except ValueError:
            self.feedback_message = "Por favor, digite um número válido."

    def _handle_enhance_detail_input(self, choice):
        if self.selected_item.get('enhancement_level', 0) >= 5:
            if choice == "1":
                self.mode = "enhance_list"
            elif choice == "2":
                self.mode = "main"
            else:
                self.feedback_message = "Opção inválida!"
        else:
            if choice == "1":
                self._perform_enhancement()
            elif choice == "2":
                self.mode = "enhance_list"
            elif choice == "3":
                self.mode = "main"
            else:
                self.feedback_message = "Opção inválida!"

    def _perform_enhancement(self):
        current_level = self.selected_item.get('enhancement_level', 0)
        
        if current_level >= 5:
            self.feedback_message = "Este item já está no nível máximo!"
            return
            
        cost = self._calculate_enhancement_cost(current_level)
        player = self.game.player
        
        if player.gold < cost:
            self.feedback_message = "Ouro insuficiente para aprimorar!"
            return
            
        player.gold -= cost
        update_character_gold(player.conn, player.id, player.gold)
        
        new_level = current_level + 1
        enhancement_type = self.selected_item.get('enhancement_type') 

        success, message = enhance_inventory_item(
            player.conn, 
            self.selected_item['inventory_id'], 
            new_level, 
            enhancement_type
        )
        
        if success:
            self.selected_item['enhancement_level'] = new_level
            if enhancement_type:
                self.selected_item['enhancement_type'] = enhancement_type

            player.recalculate()
            self.feedback_message = f"'{get_display_name(self.selected_item)}' foi aprimorado para +{new_level}! ✅"
            self.mode = "enhance_detail" 
        else:
            self.feedback_message = f"❌ Erro ao aprimorar: {message}"