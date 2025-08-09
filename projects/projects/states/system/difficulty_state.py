# game/states/difficulty_state.py
from ..base_state import BaseState
from game.config import DIFFICULTY_MODIFIERS
from game.database import save_character
import os

class DifficultyState(BaseState):
    def enter(self):
        self.difficulty_options = ["Aventura Leve",  "Desafio Justo",  "Provação Maldita",  "Caminho da Dor", "Maldição de Ferro", "Inferno Vivo"]
        
    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== SELECIONE A DIFICULDADE ===")
        print("="*40)
        print("A dificuldade afeta:")
        print("- Dano recebido e causado")
        print("- Experiência e ouro ganhos")
        print("- Efeitos de cura")
        if "Maldição de Ferro" or "Inferno Vivo" in self.difficulty_options:
            print("morte permanente!")
        print("\nOpções:")
        
        for i, diff in enumerate(self.difficulty_options, 1):
            modifiers = DIFFICULTY_MODIFIERS.get(diff, {})
            print(f"{i}. {diff}:")
            
            # Exibe efeitos
            if "damage_received" in modifiers:
                print(f"   Dano recebido: {modifiers['damage_received']}x")
            if "damage_dealt" in modifiers:
                print(f"   Dano causado: {modifiers['damage_dealt']}x")
            if "exp_multiplier" in modifiers:
                print(f"   Experiência: {modifiers['exp_multiplier']}x")
            if "gold_multiplier" in modifiers:
                print(f"   Ouro: {modifiers['gold_multiplier']}x")
            if "healing_received" in modifiers:
                print(f"   Cura recebida: {modifiers['healing_received']}x")
            if "permadeath" in modifiers:
                print("   ⚠️ MORTE PERMANENTE!")
        
        print("\n0. Voltar")
        
    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        if choice == "0":
            self.game.pop_state()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.difficulty_options):
                new_difficulty = self.difficulty_options[idx]
                self.game.player.difficulty = new_difficulty
                
                # Corrigido: Use a função save_character em vez do método save()
                if save_character(self.game.db_conn, self.game.player):
                    print(f"\nDificuldade alterada para: {new_difficulty}")
                else:
                    print("\nErro ao salvar alterações de dificuldade!")
                    
                input("Pressione ENTER para continuar...")
                self.game.pop_state()