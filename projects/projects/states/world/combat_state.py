# game/states/combat_state.py
import time
import os

from ..base_state import BaseState
from game.combat import Combat
from game.database import save_character
from .gameplay_state import GameplayState

class CombatState(BaseState):
    def __init__(self, game, db_conn):
        super().__init__(game)
        self.conn = db_conn

    def enter(self):
        """Prepara o estado de combate ao ser iniciado."""
        self.combat = Combat(self.game.player, self.conn)
        self.result = None

    def render(self):
        """Renderiza a tela inicial do combate"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Preparando para o combate...")

    def handle_input(self):
        """Inicia e gerencia o combate"""
        # Inicia o combate e obtém o resultado
        self.result = self.combat.start()

        # Processa o resultado
        self._handle_combat_result()

    def _handle_combat_result(self):
        """Processa o resultado final do combate"""
        os.system('cls' if os.name == 'nt' else 'clear')

        if self.result == "victory":
            # A chamada para self.combat.victory() foi removida daqui.
            # O método victory() já foi executado dentro da classe Combat.
            save_character(self.conn, self.game.player)
            print("\n[Pressione Enter para continuar sua aventura...]")
            input()
            self.game.change_state(GameplayState(self.game))

        elif self.result == "defeat":
            # Processar derrota normal (não permanente)
            self.combat.defeat()
            gold_lost = self.game.player.gold // 2
            self.game.player.gold -= gold_lost
            print(f"Você perdeu {gold_lost} moedas de ouro...")
            save_character(self.conn, self.game.player)
            print("\n[Pressione Enter para retornar a um lugar seguro...]")
            input()
            self.game.change_state(GameplayState(self.game))

        elif self.result == "permadeath":
            # Processar morte permanente (Hardcore)
            self._handle_permadeath()

        elif self.result == "fled":
            print("\nVocê escapou por pouco...")
            print("[Pressione Enter para continuar...]")
            input()
            self.game.change_state(GameplayState(self.game))

    def _handle_permadeath(self):
        """Lida com morte permanente no modo Hardcore"""
        from ..system.delete_confirmation_state import DeleteConfirmationState

        print("\n☠️☠️☠️ VOCÊ MORREU! ☠️☠️☠️")
        print("Nos modos mais dificeis a morte é permanente.")
        print(f"{self.game.player.name} será apagado para sempre.")

        # Mostrar personagem pela última vez
        self.game.player.show_attributes()

        # Confirmar exclusão do personagem
        print("\nPressione Enter para confirmar...")
        input()

        # Excluir personagem
        from game.database import delete_character
        delete_character(self.conn, self.game.player.id)

        # Voltar ao menu principal
        from ..system.main_menu_state import MainMenuState
        self.game.change_state(MainMenuState(self.game))