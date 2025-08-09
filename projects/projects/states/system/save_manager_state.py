# game/states/save_manager_state.py
from ..base_state import BaseState
from game.database import load_characters, delete_character, rename_character
from states.world.gameplay_state import GameplayState
from states.creation.character_creation_state import CharacterCreationState

class SaveManagerState(BaseState):
    def enter(self):
        self.step = "main"
        self.message = None
        self.characters = load_characters(self.game.db_conn)
        self.selected_char_id = None
        self.selected_char_name = None
        self.pending_action = None
    
    def _reload_characters(self):
        self.characters = load_characters(self.game.db_conn)
        self.selected_char_id = None
        self.selected_char_name = None
        self.pending_action = None
    
    def render(self):
        if self.message:
            print(f"\n{self.message}\n")
            import time
            time.sleep(1.5)
            self.message = None

        if self.step == "main":
            self._render_main()
        elif self.step == "select_character":
            if self.pending_action == "load":
                print("\nDigite o ID do personagem para CARREGAR:")
            elif self.pending_action == "delete":
                print("\nDigite o ID do personagem para EXCLUIR:")
            elif self.pending_action == "rename":
                print("\nDigite o ID do personagem para RENOMEAR:")
        elif self.step == "delete":
            print(f"\nTem certeza que deseja excluir '{self.selected_char_name}'? (s/n)")
        elif self.step == "rename":
            print(f"\nDigite o novo nome para '{self.selected_char_name}':")
    
    def _render_main(self):
        print("\n" + "=" * 70)
        print(" GERENCIADOR DE SAVES ".center(70, '='))
        print("=" * 70)
        
        if not self.characters:
            print("\nNenhum personagem salvo!")
            print("\n1. Voltar ao menu principal")
            print("2. Criar novo personagem")
            return
        
        print("\nPERSONAGENS SALVOS:")
        print("-" * 70)
        print(f"{'ID':<4} {'Nome':<20} {'Raça':<15} {'Classe':<15} {'Nível':<6} {'Ouro':<10} {'Dificuldade':<12}")
        print("-" * 70)
        
        for char in self.characters:
            print(f"{char.id:<4} {char.name:<20} {char.race:<15} {char.char_class:<15} {char.level:<6} {char.gold:<10} {char.difficulty:<12}")
        
        print("\n" + "=" * 70)
        print(" OPÇÕES DISPONÍVEIS ".center(70, '='))
        print("=" * 70)
        print("1. Carregar jogo")
        print("2. Excluir save")
        print("3. Renomear personagem")
        print("4. Voltar ao menu principal")
        print("=" * 70)
        
    def handle_input(self):
        if self.step == "main":
            self._handle_main_input()
        elif self.step == "select_character": 
            self._handle_select_character_input()  # Corrigido
        elif self.step == "delete":
            self._handle_delete_input()
        elif self.step == "rename":
            self._handle_rename_input()

    def _handle_main_input(self):
        choice = input("\nEscolha uma opção: ").strip()
        
        if not self.characters:
            if choice == "1":
                from .main_menu_state import MainMenuState
                self.game.change_state(MainMenuState(self.game))
            elif choice == "2":
                self.game.change_state(CharacterCreationState(self.game))
            else:
                self.message = "Opção inválida!"
            return
        
        if choice == "1":
            self.step = "select_character"
            self.pending_action = "load"
        elif choice == "2":
            self.step = "select_character"
            self.pending_action = "delete"
        elif choice == "3":
            self.step = "select_character"
            self.pending_action = "rename"
        elif choice == "4":
            from .main_menu_state import MainMenuState
            self.game.change_state(MainMenuState(self.game))
        else:
            self.message = "Opção inválida!"

    def _handle_select_character_input(self):  # Novo método
        input_str = input("> ").strip()
        
        try:
            char_id = int(input_str)
            selected_char = next((c for c in self.characters if c.id == char_id), None)
            
            if not selected_char:
                self.message = "ID inválido! Tente novamente."
                return
            
            self.selected_char_id = char_id
            self.selected_char_name = selected_char.name
            
            if self.pending_action == "load":
                self._load_character(selected_char)
            elif self.pending_action == "delete":
                self.step = "delete"
            elif self.pending_action == "rename":
                self.step = "rename"
                
        except ValueError:
            self.message = "Digite um número válido!"

    def _handle_load_input(self):  # Vamos renomear para melhor refletir
        input_str = input("> ").strip()
        
        try:
            char_id = int(input_str)
            selected_char = next((c for c in self.characters if c.id == char_id), None)
            
            if not selected_char:
                self.message = "ID inválido! Tente novamente."
                return
            
            self.selected_char_id = char_id
            self.selected_char_name = selected_char.name
            
            if self.pending_action == "load":
                self._load_character(selected_char)
            elif self.pending_action == "delete":
                self.step = "delete"
            elif self.pending_action == "rename":
                self.step = "rename"
                
        except ValueError:
            self.message = "Digite um número válido!"

    def _handle_delete_input(self):
        choice = input("> ").strip().lower()
        if choice == 's':
            # Chamada corrigida com conexão do banco
            if delete_character(self.game.db_conn, self.selected_char_id):
                self.message = f"'{self.selected_char_name}' foi excluído com sucesso!"
                self._reload_characters()
                self.step = "main"
            else:
                self.message = "Falha ao excluir personagem!"
        elif choice == 'n':
            self.step = "main"
        else:
            self.message = "Opção inválida! Digite 's' ou 'n'."

    def _handle_rename_input(self):
        new_name = input("> ").strip()
        if new_name:
            # Chamada corrigida com conexão do banco
            if rename_character(self.game.db_conn, self.selected_char_id, new_name):
                self.message = f"Personagem renomeado para '{new_name}'!"
                self._reload_characters()
                self.step = "main"
            else:
                self.message = "Falha ao renomear personagem!"
        else:
            self.message = "Nome não pode ser vazio!"
    
    def _load_character(self, character):
        """Carrega o personagem e inicia o jogo"""
        if character.hp <= 0:
            character.hp = character.hp_max
        
        self.game.player = character
        self.game.change_state(GameplayState(self.game))