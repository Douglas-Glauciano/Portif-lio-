from ..base_state import BaseState
from .combat_state import CombatState
from game.utils import roll_dice, modifier
from game.database import save_character

class RestState(BaseState):
    def enter(self):
        print("\n" + "=" * 50)
        print("DESCANSANDO...")
        print("=" * 50)
        
        # 30% chance de encontro
        if roll_dice("1d100") > 70:
            print("\nUm monstro te surpreendeu durante o descanso!")
            self.encounter = True
        else:
            self.encounter = False
            player = self.game.player
            
            # Obtém modificadores de dificuldade
            difficulty_modifiers = player.get_difficulty_modifiers()
            healing_multiplier = difficulty_modifiers.get("healing_received", 1.0)
            
            # Usa atributos EFETIVOS (com redução de dificuldade)
            effective_con = player.get_effective_constitution()
            effective_int = player.get_effective_intelligence()
            
            # Calcula modificadores a partir dos atributos efetivos
            con_mod = modifier(effective_con)
            int_mod = modifier(effective_int)
            
            print(f"Constituição Efetiva: {effective_con} (Mod: {con_mod:+.0f})")
            print(f"Inteligência Efetiva: {effective_int} (Mod: {int_mod:+.0f})")
            
            # Escolhe o maior modificador
            chosen_mod = max(con_mod, int_mod)
            print(f"Modificador escolhido: {chosen_mod:+.0f}")
            
            # Rola a cura base
            dice_roll_heal = roll_dice("1d8")
            base_heal = max(1, dice_roll_heal + chosen_mod)  # Mínimo 1 HP
            print(f"Cura base (1d8 + mod): {dice_roll_heal} + {chosen_mod} = {base_heal}")
            
            # Aplica multiplicador de dificuldade
            heal_amount = max(1, int(base_heal * healing_multiplier))
            print(f"Multiplicador de cura ({player.difficulty}): x{healing_multiplier}")
            print(f"Cura final: {base_heal} x {healing_multiplier} = {heal_amount}")
            
            # Aplica a cura
            player.hp = min(player.hp + heal_amount, player.hp_max)
            print(f"\nVocê descansou e recuperou {heal_amount} de HP!")
            print(f"HP atual: {player.hp}/{player.hp_max}")
            
            save_character(self.game.db_conn, player)
            input("\nPressione Enter para continuar...")

    def handle_input(self):
        if self.encounter:
            self.game.change_state(CombatState(self.game, self.game.db_conn))
        else:
            from .gameplay_state import GameplayState
            self.game.change_state(GameplayState(self.game))