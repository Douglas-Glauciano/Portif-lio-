from ..base_state import BaseState
from states.creation.character_creation_state import CharacterCreationState
from .save_manager_state import SaveManagerState
from game.config import print_path_info, get_db_path

class MainMenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        print("MainMenuState inicializado")
        
    def render(self):
        try:
            print_path_info()
            print(f"Usando banco de dados em: {get_db_path()}")
            print("\n" + "=" * 50)
            print("MENU PRINCIPAL RUST DND DICE")
            print("=" * 50)
            print("1. Continuar")
            print("2. Novo Jogo")
            print("3. Gerenciar saves")
            print("4. Tutorial")
            print("5. Créditos")
            print("6. Configurações")
            print("7. Sair")
            print("=" * 50)
            
            # REMOVA ESTAS LINHA PROBLEMÁTICAS:
            # print("Inicialização completa, exibindo menu principal...")
            # from states.system.main_menu_state import MainMenuState
            # self.change_state(MainMenuState(self))  # <--- ISSO CAUSA O ERRO
            # self.run()
            
        except Exception as e:
            import traceback
            with open("error_log.txt", "w") as f:
                f.write(f"Erro crítico: {str(e)}\n")
                f.write(traceback.format_exc())
            print(f"Ocorreu um erro crítico. Verifique error_log.txt para detalhes.")
    
    def handle_input(self):
        choice = input("\nEscolha uma opção: ").strip()

        if choice == "1":
            print("\nFuncionalidade 'Continuar' ainda não implementada")
            input("Pressione Enter para voltar...")
        elif choice == "2":  # Novo Jogo
            self.game.change_state(CharacterCreationState(self.game))
        elif choice == "3":  # Gerenciar Saves
            self.game.change_state(SaveManagerState(self.game))
        elif choice == "4":
            print("\nFuncionalidade 'Tutorial' ainda não implementada")
            input("Pressione Enter para voltar...")
        elif choice == "5":
            print("\nFuncionalidade 'Créditos' ainda não implementada")
            input("Pressione Enter para voltar...")
        elif choice == "6":
            print("\nFuncionalidade 'Configurações' ainda não implementada")
            input("Pressione Enter para voltar...")
        elif choice == "7":
            print("\nSaindo do jogo... Até sua próxima aventura!")
            self.game.running = False
        else:
            print("\nOpção inválida! Tente novamente.")
            input("Pressione Enter para voltar...")