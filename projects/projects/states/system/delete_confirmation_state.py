# game/states/delete_confirmation_state.py
from ..base_state import BaseState
from game.database import delete_character

class DeleteConfirmationState(BaseState):
    def render(self):
        player = self.game.player
        print("\n" + "=" * 50)
        print(f"CONFIRMAR EXCLUSÃO DE {player.name.upper()}?")
        print("=" * 50)
        print("Tem certeza que deseja excluir este personagem?")
        print("Esta ação é irreversível!\n")
        print("1. Sim, deletar personagem")
        print("2. Não, voltar ao jogo")
        print("=" * 50)

    def handle_input(self):
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            # Chamada corrigida com conexão do banco
            if delete_character(self.game.db_conn, self.game.player.id):
                print("\nPersonagem deletado com sucesso!")
                input("Pressione Enter para voltar ao menu principal...")
                from .main_menu_state import MainMenuState
                self.game.change_state(MainMenuState(self.game))
            else:
                print("\nFalha ao deletar personagem!")
                input("Pressione Enter para continuar...")
                from ..world.gameplay_state import GameplayState
                self.game.change_state(GameplayState(self.game))
        elif choice == "2":
            from ..world.gameplay_state import GameplayState
            self.game.change_state(GameplayState(self.game))