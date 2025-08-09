#game/states/base_states.py
class BaseState:
    def __init__(self, game, title="RUST DICE"):
        self.game = game
        self.title = title
        self.needs_render = True 
    
    @property
    def player(self):
        return self.game.player
    
    def enter(self):
        """Executado ao entrar neste estado"""
        pass
    
    def clear_screen(self):
        """Limpa a tela de forma cross-platform"""
        print("\033[H\033[J", end="")  # Códigos ANSI para limpar tela
    
    def display_title(self):
        pass
    
    def exit(self):
        """Executado ao sair deste estado"""
        pass
    
    def render(self):
        """Mostra o conteúdo na tela"""
        pass
    
    def handle_input(self):
        """Processa a entrada do usuário"""
        pass