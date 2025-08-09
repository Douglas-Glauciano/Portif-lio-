# game/states/explore_state.py
from ..base_state import BaseState
from .combat_state import CombatState
from game.utils import roll_dice
import time

class ExploreState(BaseState):
    def enter(self):
        print("\n" + "=" * 50)
        print("EXPLORANDO...")
        print("=" * 50)
        time.sleep(1.2)  # Pequeno delay para dramatismo
        
        # 70% chance de encontro
        if roll_dice("1d100") > 30:
            print("\nVocê encontrou um inimigo!")
            time.sleep(1.2)  # Pequeno delay para dramatismo
            self.encounter = True
        else:
            print("\nVocê explorou a área mas não encontrou nada.")
            self.encounter = False
            input("\nPressione Enter para continuar...")

    def handle_input(self):
        if self.encounter:
            self.game.change_state(CombatState(self.game, self.game.db_conn))
        else:
            from .gameplay_state import GameplayState
            self.game.change_state(GameplayState(self.game))