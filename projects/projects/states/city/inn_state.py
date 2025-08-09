# states/city/inn_state.py
from states.base_state import BaseState

class InnState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        
    def render(self):
        print("\n" + "=" * 50)
        print("🏠  ESTALAGEM".center(50))
        print("=" * 50)
        print(f"Bem-vindo à estalagem! O que deseja fazer?")
        print(f"💰 Ouro: {self.player.gold}")
        print(f"❤️ Vida: {self.player.hp}/{self.player.hp_max}")
        print(f"🔷 Mana: {self.player.mana}/{self.player.mana_max}")
        print("=" * 50)
        print("1. Dormir (recupera toda a vida e mana)")
        print("2. Meditar (ganha bônus de XP por 5 combates)")
        print("3. Voltar")
        print("=" * 50)

    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            self._sleep()
        elif choice == "2":
            self._meditate()
        elif choice == "3":
            self.game.pop_state()
        else:
            print("Opção inválida!")
            input("Pressione Enter para continuar...")

    def _sleep(self):
        # Custo baseado no nível do jogador
        cost = self.player.level * 10
        
        if self.player.gold < cost:
            print(f"\nVocê não tem ouro suficiente! Custo: {cost}g")
            input("Pressione Enter para continuar...")
            return
            
        # Confirmação
        print(f"\nDormir na estalagem custará {cost}g. Confirmar? (s/n)")
        if input().strip().lower() != 's':
            return
            
        # Recupera tudo
        self.player.gold -= cost
        self.player.hp = self.player.hp_max
        self.player.mana = self.player.mana_max
        print("\nVocê dormiu profundamente e acordou totalmente recuperado!")
        input("Pressione Enter para continuar...")

    def _meditate(self):
        cost = self.player.level * 25
        if self.player.gold < cost:
            print(f"\nVocê não tem ouro suficiente! Custo: {cost}g")
            input("Pressione Enter para continuar...")
            return
            
        print(f"\nMeditar custará {cost}g. Confirmar? (s/n)")
        if input().strip().lower() != 's':
            return
            
        self.player.gold -= cost
        # Adiciona um modificador temporário ao jogador
        self.player.add_temporary_modifier(
            "xp_bonus", 
            {"xp_multiplier": 1.2, "remaining_combats": 5}
        )
        print("\nVocê medita profundamente e ganha uma visão clara das batalhas futuras.")
        print("Você ganhará 20% de XP extra nos próximos 5 combates!")
        input("Pressione Enter para continuar...")