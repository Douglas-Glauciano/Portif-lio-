# game/states/shop_state.py
from ..base_state import BaseState
from game.db_queries import get_item_by_id, add_item_to_inventory, remove_item_from_inventory, update_character_gold
import os
from game.utils import modifier

# game/states/shop_state.py
from ..base_state import BaseState
from game.db_queries import get_item_by_id, add_item_to_inventory, remove_item_from_inventory, update_character_gold
import os
from game.utils import modifier

class ShopState(BaseState):
    def __init__(self, game, shop_name, npc_greeting, shop_items):
        super().__init__(game)
        self.shop_name = shop_name
        self.npc_greeting = npc_greeting
        self.shop_items = shop_items
        self.mode = 'browse'
        self.player_inventory = []
        self._player = None  # Atributo privado para armazenar o jogador
        
    @property
    def player(self):
        """Getter para a propriedade player"""
        return self._player
    
    @player.setter
    def player(self, value):
        """Setter para a propriedade player"""
        # Aqui você pode adicionar validações se necessário
        self._player = value
        
    def enter(self):
        # Agora podemos usar o setter normalmente
        self.player = self.game.player
        self.player_inventory = self.player.get_inventory()
        self._calculate_price_modifiers()
        self._refresh_shop_items()
        
    def _calculate_price_modifiers(self):
        cha_mod = modifier(self.player.get_effective_charisma())
        self.buy_modifier = max(0.5, 1.0 - (cha_mod * 0.02))
        self.sell_modifier = min(1.5, 0.5 + (cha_mod * 0.02))
        
        if cha_mod > 0:
            self.cha_effect = f"(Carisma +{cha_mod}: -{cha_mod*2}% compra, +{cha_mod*2}% venda)"
        elif cha_mod < 0:
            self.cha_effect = f"(Carisma {cha_mod}: +{abs(cha_mod)*2}% compra, -{abs(cha_mod)*2}% venda)"
        else:
            self.cha_effect = "(Carisma neutro: preços normais)"

    def _refresh_shop_items(self):
        """Carrega dados completos dos itens da loja"""
        self.shop_items_data = []
        for item_id in self.shop_items:
            item = get_item_by_id(self.game.db_conn, item_id)
            if item:
                item['buy_price'] = int(item['value'] * self.buy_modifier)
                self.shop_items_data.append(item)

    def _refresh_inventory(self):
        """Atualiza o inventário do jogador"""
        self.player_inventory = self.player.get_inventory()
        for item in self.player_inventory:
            item['sell_price'] = int(item['value'] * self.sell_modifier)

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "=" * 50)
        print(f"🏪  {self.shop_name}  🏪".center(50))
        print("=" * 50)
        print(f"NPC: \"{self.npc_greeting}\"")
        print(f"Ouro: {self.player.gold}g {self.cha_effect}")
        print("=" * 50)
        
        if self.mode == 'browse':
            self._render_browse()
        elif self.mode == 'buy':
            self._render_buy()
        elif self.mode == 'sell':
            self._render_sell()

    def _render_browse(self):
        print("\nITENS À VENDA:")
        print("-" * 50)
        print(f"{'ID':<4} {'Nome':<20} {'Tipo':<12} {'Preço':<10}")
        print("-" * 50)
        
        for idx, item in enumerate(self.shop_items_data, 1):
            print(f"{idx:<4} {item['name'][:18]:<20} {item['category'][:10]:<12} {item['buy_price']:<10}g")
        
        print("\nSEU INVENTÁRIO:")
        print("-" * 50)
        if not self.player_inventory:
            print("Seu inventário está vazio!")
        else:
            print(f"{'ID':<4} {'Nome':<20} {'Qtd':<4} {'Valor':<10}")
            print("-" * 50)
            for idx, item in enumerate(self.player_inventory, 1):
                sell_price = item.get('sell_price', int(item['value'] * self.sell_modifier))
                print(f"{idx:<4} {item['name'][:18]:<20} {item['quantity']:<4} {sell_price:<10}g")
        
        print("\n" + "=" * 50)
        print("1. Comprar item")
        print("2. Vender item")
        print("3. Voltar")
        print("=" * 50)

    def _render_buy(self):
        print("\nSELECIONE UM ITEM PARA COMPRAR:")
        print("-" * 50)
        print(f"{'ID':<4} {'Nome':<20} {'Tipo':<12} {'Preço':<10}")
        print("-" * 50)
        
        for idx, item in enumerate(self.shop_items_data, 1):
            print(f"{idx:<4} {item['name'][:18]:<20} {item['category'][:10]:<12} {item['buy_price']:<10}g")
        
        print("\n0. Voltar")
        print("=" * 50)

    def _render_sell(self):
        print("\nSELECIONE UM ITEM PARA VENDER:")
        print("-" * 50)
        if not self.player_inventory:
            print("Seu inventário está vazio!")
        else:
            print(f"{'ID':<4} {'Nome':<20} {'Qtd':<4} {'Valor':<10}")
            print("-" * 50)
            for idx, item in enumerate(self.player_inventory, 1):
                sell_price = item.get('sell_price', int(item['value'] * self.sell_modifier))
                print(f"{idx:<4} {item['name'][:18]:<20} {item['quantity']:<4} {sell_price:<10}g")
        
        print("\n0. Voltar")
        print("=" * 50)

    def handle_input(self):
        if self.mode == 'browse':
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                if not self.shop_items_data:
                    input("\nA loja está sem estoque! Pressione Enter...")
                else:
                    self.mode = 'buy'
            elif choice == '2':
                if not self.player_inventory:
                    input("\nSeu inventário está vazio! Pressione Enter...")
                else:
                    self.mode = 'sell'
            elif choice == '3':
                self.game.pop_state()  # Volta para o estado anterior (hub da cidade)
            else:
                print("Opção inválida!")
                input("Pressione Enter para continuar...")
                
        elif self.mode == 'buy':
            choice = input("\nDigite o ID do item que deseja comprar (0 para voltar): ").strip()
            
            if choice == '0':
                self.mode = 'browse'
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(self.shop_items_data):
                    self._buy_item(idx - 1)
                else:
                    print("ID inválido!")
                    input("Pressione Enter para continuar...")
            else:
                print("Entrada inválida!")
                input("Pressione Enter para continuar...")
                
        elif self.mode == 'sell':
            choice = input("\nDigite o ID do item que deseja vender (0 para voltar): ").strip()
            
            if choice == '0':
                self.mode = 'browse'
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(self.player_inventory):
                    self._sell_item(idx - 1)
                else:
                    print("ID inválido!")
                    input("Pressione Enter para continuar...")
            else:
                print("Entrada inválida!")
                input("Pressione Enter para continuar...")

    def _buy_item(self, item_idx):
        item_data = self.shop_items_data[item_idx]
        buy_price = item_data['buy_price']
        
        print(f"\nItem: {item_data['name']}")
        print(f"Preço: {buy_price}g")
        print(f"Seu ouro: {self.player.gold}g")
        
        if self.player.gold < buy_price:
            print("\nVocê não tem ouro suficiente!")
            input("Pressione Enter para continuar...")
            return
            
        confirm = input("\nConfirmar compra? (s/n): ").strip().lower()
        if confirm == 's':
            # Atualiza ouro do jogador
            self.player.gold -= buy_price
            update_character_gold(self.game.db_conn, self.player.id, self.player.gold)
            
            # Adiciona item ao inventário
            add_item_to_inventory(self.game.db_conn, self.player.id, item_data['id'])
            
            print(f"\nVocê comprou {item_data['name']} por {buy_price}g!")
            
            # Atualiza dados locais
            self._refresh_inventory()
            self._refresh_shop_items()
        else:
            print("Compra cancelada!")
            
        input("Pressione Enter para continuar...")

    def _sell_item(self, item_idx):
        inv_item = self.player_inventory[item_idx]
        sell_price = inv_item.get('sell_price', int(inv_item['value'] * self.sell_modifier))
        
        print(f"\nItem: {inv_item['name']}")
        print(f"Quantidade: {inv_item['quantity']}")
        print(f"Preço de venda: {sell_price}g")
        
        quantity = 1
        if inv_item['quantity'] > 1:
            try:
                quantity = int(input(f"Quantos deseja vender (1-{inv_item['quantity']})? "))
                quantity = max(1, min(quantity, inv_item['quantity']))
            except ValueError:
                quantity = 1
                print("Usando quantidade 1")
        
        total_price = sell_price * quantity
        
        confirm = input(f"\nVender {quantity}x {inv_item['name']} por {total_price}g? (s/n): ").strip().lower()
        if confirm == 's':
            # Atualiza ouro do jogador
            self.player.gold += total_price
            update_character_gold(self.game.db_conn, self.player.id, self.player.gold)
            
            # Remove item do inventário
            remove_item_from_inventory(self.game.db_conn, inv_item['inventory_id'], quantity)
            
            print(f"\nVocê vendeu {quantity}x {inv_item['name']} por {total_price}g!")
            
            # Atualiza dados locais
            self._refresh_inventory()
        else:
            print("Venda cancelada!")
            
        input("Pressione Enter para continuar...")