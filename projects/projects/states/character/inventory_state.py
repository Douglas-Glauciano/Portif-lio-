from ..base_state import BaseState
import os
# Importar a função para mostrar nomes aprimorados e o dano aprimorado
from game.utils import get_display_name, calculate_enhanced_damage, calculate_enhanced_value

class InventoryState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self._player = game.player  # Usar atributo privado
        self.current_menu = "main"
        self.feedback_message = ""
        self.needs_render = True
        self.selected_item = None
        self.previous_menu = None
        self.item_icons = {
            'weapon': '⚔️',
            'armor': '🛡️',
            'shield': '🔰',
            'consumable': '🧪',
            'ammo': '🏹',
            'misc': '📦',
            'other': '❓' # Fallback para tipos não reconhecidos
        }

    def enter(self):
        """Método chamado ao entrar neste estado."""
        self.feedback_message = ""
        self.render()
        self.needs_render = True

    def go_back(self):
        """Navega de volta no menu do inventário."""
        if self.current_menu in ["equip", "unequip", "item_detail"]:
            self.current_menu = "main"
            self.needs_render = True
        else:
            # Se estiver no menu principal, volta para o estado anterior do jogo
            self.game.pop_state()

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "=" * 60)
        print(f"   🎒 INVENTÁRIO DE {self._player.name.upper()} 🎒".center(60))
        print("=" * 60)
        
        if self.feedback_message:
            print(f"\n>>> {self.feedback_message} <<<\n")
            self.feedback_message = ""

        if self.current_menu == "main":
            self.render_main_menu()
        elif self.current_menu == "equip":
            self.render_equip_menu()
        elif self.current_menu == "unequip":
            self.render_unequip_menu()
        elif self.current_menu == "item_detail":
            self.render_item_detail()

    def render_main_menu(self):
        print("\n" + "⚔️ EQUIPAMENTO ATUAL".center(60, '-'))
        equipped_items = self._player.get_equipped_items()
        
        if not equipped_items:
            print("   Nenhum item equipado.")
        else:
            equipped_slots = {item['equipped_slot_technical']: item for item in equipped_items}

            display_order = [
                ('main_hand_inventory_id', "⚔️ Arma"),
                ('off_hand_inventory_id', "🛡️ Mão Secundária"),
                ('head_inventory_id', "🎩 Cabeça"),
                ('body_inventory_id', "👕 Corpo"),
                ('hands_inventory_id', "🧤 Mãos"),
                ('feet_inventory_id', "👟 Pés"),
                ('ring1_inventory_id', "💍 Anel 1"),
                ('ring2_inventory_id', "💍 Anel 2"),
                ('amulet_inventory_id', "💎 Amuleto")
            ]

            for slot_tech_name, display_label in display_order:
                item = equipped_slots.get(slot_tech_name)
                if item:
                    display_name = get_display_name(item)
                    enhancement = item.get('enhancement_level', 0)
                    enhancement_str = f" +{enhancement}" if enhancement > 0 else ""

                    details = ""
                    if item.get('category') == 'weapon':
                        details = f"({calculate_enhanced_damage(item)} {item.get('damage_type', '')}{enhancement_str})"
                    elif item.get('category') == 'armor':
                        # Mostra resistências e penalidade para armaduras
                        details = f"(Fís: +{item.get('physical_resistance', 0)} | Mág: +{item.get('magical_resistance', 0)} | Penal: {item.get('dexterity_penalty', 0)}{enhancement_str})"
                    elif item.get('category') == 'shield':
                        # Mostra apenas bônus de CA para escudos
                        details = f"(CA +{item.get('armor_bonus', 0)}{enhancement_str})"
                    
                    print(f"   {display_label}: {display_name} {details}")
                else:
                    print(f"   {display_label}: {'Nenhuma equipada' if 'Arma' in display_label else 'Vazio'}")

        print("\n" + "🎒 ITENS NA MOCHILA".center(60, '-'))
        inventory = self._player.get_inventory()
        
        if not inventory:
            print("   Sua mochila está vazia.")
        else:
            items_by_category = {}
            for item in inventory:
                category = item.get('category', 'other')
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            for category, items in items_by_category.items():
                icon = self.item_icons.get(category, '📦')
                print(f"\n   {icon} {category.upper()} {icon}")
                
                for i, item in enumerate(items, 1):
                    display_name = get_display_name(item)
                    equipable_str = " (Equipável)" if item.get('equip_slot') else ""
                    enhancement = item.get('enhancement_level', 0)
                    enhancement_str = f" +{enhancement}" if enhancement > 0 else ""
                    
                    print(f"      {i}. {display_name}{enhancement_str} x{item['quantity']}{equipable_str}")
        
        print("\n" + "=" * 60)
        print("OPÇÕES".center(60))
        print("-" * 60)
        print("1. 🧥 Equipar item da mochila")
        print("2. 🧺 Desequipar item")
        print("3. 🔍 Ver detalhes de item")
        print("4. ↩️ Voltar ao jogo")
        print("=" * 60)

    def handle_main_menu_input(self, choice):
        """Lida com a entrada do usuário no menu principal."""
        if choice == "1":
            self.current_menu = "equip"
        elif choice == "2":
            self.current_menu = "unequip"
        elif choice == "3":
            self.show_item_details_menu()
        elif choice == "4":
            self.game.pop_state()
        else:
            self.feedback_message = "Opção inválida!"
        self.needs_render = True

    def show_item_details_menu(self):
        """Exibe o menu para escolher um item e ver seus detalhes."""
        inventory = self._player.get_inventory()
        if not inventory:
            self.feedback_message = "Sua mochila está vazia!"
            self.needs_render = True
            return
            
        print("\n" + "=" * 60)
        print("🔍 ESCOLHA UM ITEM PARA VER DETALHES".center(60))
        print("=" * 60)
        
        for i, item in enumerate(inventory, 1):
            # Usa nome aprimorado
            display_name = get_display_name(item)
            # USAR CATEGORIA EM VEZ DE TYPE
            icon = self.item_icons.get(item.get('category', 'other'), '📦')
            
            # Mostra nível de aprimoramento se existir
            enhancement = item.get('enhancement_level', 0)
            enhancement_str = f" +{enhancement}" if enhancement > 0 else ""
            
            print(f"{i}. {icon} {display_name}{enhancement_str} x{item['quantity']}")
        
        print("\n0. ↩️ Voltar")
        
        choice = input("\nEscolha: ").strip()
        if choice == "0":
            self.current_menu = "main"
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(inventory):
                self.selected_item = inventory[idx]
                self.previous_menu = "main" # Define o menu anterior para voltar
                self.current_menu = "item_detail"
            else:
                self.feedback_message = "Número inválido!"
        else:
            self.feedback_message = "Entrada inválida!"
        self.needs_render = True

    def render_item_detail(self):
        if not self.selected_item:
            self.feedback_message = "Item não encontrado!"
            self.current_menu = self.previous_menu if self.previous_menu else "main"
            self.needs_render = True
            return
            
        item = self.selected_item
        icon = self.item_icons.get(item.get('category', 'other'), '📦')
        
        print("\n" + "=" * 60)
        print(f"{icon} DETALHES: {get_display_name(item).upper()} {icon}".center(60))
        print("=" * 60)
        
        print(f"\nTipo: {item['category'].capitalize()}")
        print(f"Quantidade: x{item['quantity']}")
        print(f"Valor: {calculate_enhanced_value(item)} ouro")
        print(f"Peso: {item.get('weight', 0):.1f} kg")
        
        enhancement_level = item.get('enhancement_level', 0)
        if enhancement_level > 0:
            print(f"\n⭐ Nível de Aprimoramento: +{enhancement_level}")
        
        description = item.get('description', 'Nenhuma descrição disponível.')
        print(f"\n📝 Descrição:\n   {description}")
        
        print("\n⚙️ Atributos:")
        if item['category'] == 'weapon':
            print(f"   Dano: {calculate_enhanced_damage(item)} {item.get('damage_type', '')}")
            print(f"   Atributo principal: {item.get('main_attribute', 'força').capitalize()}")
            print(f"   Duas Mãos: {'Sim' if item.get('two_handed') else 'Não'}")
            
        elif item['category'] == 'armor':
            print(f"   Resistência Física: +{item.get('physical_resistance', 0)}")
            print(f"   Resistência Mágica: +{item.get('magical_resistance', 0)}")
            print(f"   Penalidade de Destreza: {item.get('dexterity_penalty', 0)}")
            print(f"   Tipo: {item.get('armor_class', 'N/A').capitalize()}")
            if item.get('strength_requirement'):
                print(f"   Requisito de Força: {item['strength_requirement']}")
                
        elif item['category'] == 'shield':
            print(f"   Bônus de CA: +{item.get('armor_bonus', 0)}")
        
        print("\n" + "=" * 60)
        print("OPÇÕES".center(60))
        print("-" * 60)
        
        is_equipped = any(equipped_item['inventory_id'] == item['inventory_id'] 
                         for equipped_item in self._player.get_equipped_items())
        if item.get('equip_slot') and not is_equipped:
            print("1. 🧥 Equipar este item")
        
        print("0. ↩️ Voltar")
        print("=" * 60)
        self.needs_render = True


    def render_equip_menu(self):
        """Renderiza o menu para escolher um item para equipar."""
        print("\n" + "=" * 60)
        print("🧥 ESCOLHA UM ITEM PARA EQUIPAR".center(60))
        print("=" * 60)
        
        # Filtra itens equipáveis que NÃO estão atualmente equipados e têm quantidade > 0
        equipable_items = [
            item for item in self._player.get_inventory() 
            if item.get('equip_slot') and item['quantity'] > 0 and
            not any(eq_item['inventory_id'] == item['inventory_id'] for eq_item in self._player.get_equipped_items())
        ]
        
        if not equipable_items:
            print("   Você não tem itens equipáveis na mochila.")
        else:
            for i, item in enumerate(equipable_items, 1):
                # Usa nome aprimorado
                display_name = get_display_name(item)
                # USAR CATEGORIA EM VEZ DE TYPE
                icon = self.item_icons.get(item.get('category', 'other'), '📦')
                slot = item.get('equip_slot', 'slot desconhecido') # Usa 'equip_slot' diretamente
                
                # Mostra nível de aprimoramento se existir
                enhancement = item.get('enhancement_level', 0)
                enhancement_str = f" +{enhancement}" if enhancement > 0 else ""
                
                print(f"{i}. {icon} {display_name}{enhancement_str} (Slot: {slot.replace('_', ' ').capitalize()})")
        
        print("\n0. ↩️ Voltar")
        self.needs_render = True

    def render_unequip_menu(self):
        """Renderiza o menu para escolher um item para desequipar."""
        print("\n" + "=" * 60)
        print("🧺 ESCOLHA UM ITEM PARA DESEQUIPAR".center(60))
        print("=" * 60)
        
        equipped_items = self._player.get_equipped_items()

        if not equipped_items:
            print("   Você não tem itens equipados.")
        else:
            for i, item in enumerate(equipped_items, 1):
                # Usa nome aprimorado
                display_name = get_display_name(item)
                # USAR CATEGORIA EM VEZ DE TYPE
                icon = self.item_icons.get(item.get('category', 'other'), '📦')
                # Usa 'equipped_slot_friendly' para exibição
                slot_name = item.get('equipped_slot_friendly', 'Slot Desconhecido') 
                
                # Mostra nível de aprimoramento se existir
                enhancement = item.get('enhancement_level', 0)
                enhancement_str = f" +{enhancement}" if enhancement > 0 else ""
                
                print(f"{i}. {icon} {display_name}{enhancement_str} ({slot_name})")
        
        print("\n0. ↩️ Voltar")
        self.needs_render = True

    def handle_input(self):
        choice = input("\nEscolha uma opção: ").strip().lower()
        
        if self.current_menu == "main":
            if choice == "1":
                self.current_menu = "equip"
            elif choice == "2":
                self.current_menu = "unequip"
            elif choice == "3":
                self.show_item_details_menu()
            elif choice == "4":
                self.game.pop_state()
            else:
                self.feedback_message = "Opção inválida!"
            self.needs_render = True
        
        elif self.current_menu == "equip":
            if choice == "0":
                self.current_menu = "main"
            elif choice.isdigit():
                equipable_items = [
                    item for item in self._player.get_inventory() 
                    if item.get('equip_slot') and item['quantity'] > 0 and
                    not any(eq_item['inventory_id'] == item['inventory_id'] 
                           for eq_item in self._player.get_equipped_items())
                ]
                
                idx = int(choice) - 1
                if 0 <= idx < len(equipable_items):
                    self.equip_selected_item(equipable_items[idx]) 
                else:
                    self.feedback_message = "Número inválido!"
            else:
                self.feedback_message = "Entrada inválida!"
            self.needs_render = True
        
        elif self.current_menu == "unequip":
            if choice == "0":
                self.current_menu = "main"
            elif choice.isdigit():
                equipped_items = self._player.get_equipped_items()
                idx = int(choice) - 1
                if 0 <= idx < len(equipped_items):
                    self.unequip_selected_item(equipped_items[idx]) 
                else:
                    self.feedback_message = "Número inválido!"
            else:
                self.feedback_message = "Entrada inválida!"
            self.needs_render = True
        
        elif self.current_menu == "item_detail":
            if choice == "0":
                self.current_menu = self.previous_menu
            elif choice == "1" and self.selected_item.get('equip_slot'):
                if not any(equipped_item['inventory_id'] == self.selected_item['inventory_id'] 
                          for equipped_item in self._player.get_equipped_items()):
                    self.equip_selected_item(self.selected_item)
                else:
                    self.feedback_message = "Este item já está equipado!"
            else:
                self.feedback_message = "Opção inválida!"
            self.needs_render = True

    def unequip_selected_item(self, item_to_unequip):
        slot_tech = item_to_unequip.get('equipped_slot_technical')
        if not slot_tech:
            self.feedback_message = "Erro: Slot técnico não encontrado para o item."
            return
        
        success, message = self._player.unequip_item(slot_tech)
        display_name = get_display_name(item_to_unequip)
        
        self.feedback_message = (f"{display_name} desequipado com sucesso! ✅" if success 
                                else f"❌ Falha ao desequipar {display_name}: {message}")
        self.needs_render = True

    def equip_selected_item(self, item_to_equip):
        if not item_to_equip.get('equip_slot'):
            self.feedback_message = "Este item não pode ser equipado."
            return

        if any(equipped_item['inventory_id'] == item_to_equip['inventory_id'] 
              for equipped_item in self._player.get_equipped_items()):
            self.feedback_message = "Este item já está equipado!"
            return

        success, message = self._player.equip_item(item_to_equip['inventory_id'])
        display_name = get_display_name(item_to_equip)
        
        if success:
            self.feedback_message = f"{display_name} equipado com sucesso! ✅"
            self.current_menu = "main"
        else:
            self.feedback_message = f"❌ Não foi possível equipar {display_name}: {message}"
        self.needs_render = True