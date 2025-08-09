from states.system.main_menu_state import MainMenuState
from game.config import load_settings, get_db_path
import sqlite3
import os
import sys

# Adiciona o diretório raiz ao PATH do Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

class Game:
    def __init__(self):
        self.running = True
        self.states = []  # Pilha de estados
        self.player = None
        self.db_conn = None
        self.needs_render = True 
        print(f"Usando banco de dados em: {get_db_path()}")

    def change_state(self, new_state):
        """Substitui toda a pilha por um novo estado"""
        while self.states:
            state = self.states.pop()
            state.exit()
        self.push_state(new_state)

    def push_state(self, state):
        """Adiciona um novo estado à pilha"""
        if self.states:
            self.states[-1].exit()
        self.states.append(state)
        state.enter()

    def pop_state(self):
        """Remove o estado atual da pilha"""
        if self.states:
            state = self.states.pop()
            state.exit()
        if self.states:
            self.states[-1].enter()

    def current_state(self):
        """Retorna o estado atual"""
        if self.states:
            return self.states[-1]
        return None

    def run(self):
        try:
            
            # Configurações e conexão
            load_settings()
            self.db_conn = sqlite3.connect(get_db_path())
            
            # Estado inicial
            self.change_state(MainMenuState(self))

            # Loop principal
            while self.running:
                current_state = self.current_state()
                if current_state:
                    current_state.render()
                    current_state.handle_input()

        except KeyboardInterrupt:
            self.running = False
            print("\n\nObrigado por jogar! Até à sua próxima aventura!")
        except Exception as e:
            print(f"Erro crítico: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.db_conn:
                self.db_conn.close()
    
    def quit(self):
        self.running = False

if __name__ == "__main__":
    game = Game()
    game.run()