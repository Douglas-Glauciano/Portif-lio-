# game/states/settings_state.py
from ..base_state import BaseState
from game.database import save_character
import os

class SettingsState(BaseState):
    def enter(self):
        self.options = [
            ("Alterar Dificuldade", "change_difficulty"),
            ("Voltar", "back"),
            ("Salvar e continuar", "Save and continnue"),
            ("Salvar e sair", "Save and exit"),
            ("Deletar personagem", "Delete character")
        ]
        
    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== CONFIGURAÇÕES ===")
        print("="*30)
        
        for i, (name, _) in enumerate(self.options, 1):
            print(f"{i}. {name}")
        
    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            self.change_difficulty()
        elif choice == "2":
            from ..world.gameplay_state import GameplayState
            self.game.change_state(GameplayState(self.game))
        elif choice == "3":
            save_character(self.game.db_conn, self.game.player)
            print("\nJogo salvo com sucesso! ✅")
            input("Pressione Enter para continuar...")
        elif choice == "4":
            save_character(self.game.db_conn, self.game.player)
            print("\nProgresso salvo. Até a próxima aventura! 👋")
            from .main_menu_state import MainMenuState
            self.game.change_state(MainMenuState(self.game))
        elif choice == "5":
            from .delete_confirmation_state import DeleteConfirmationState
            self.game.change_state(DeleteConfirmationState(self.game))
    
    def change_difficulty(self):
        from .difficulty_state import DifficultyState
        self.game.push_state(DifficultyState(self.game))