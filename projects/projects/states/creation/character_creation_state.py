# game/states/character_creation_state.py
import os
import traceback

from game.character import Character
from game.config import DIFFICULTY_MODIFIERS
from game.database import save_character
from game.db_queries import (
    get_background_starting_skills,
    get_item_base_details,
    load_backgrounds,
    load_classes,
    load_races,
)
from game.utils import roll_attribute

from ..base_state import BaseState
from .character_name_creator_state import CharacterNameCreator

# Mapeia as opções de entrada do usuário para os nomes dos atributos
attr_map = {
    "1": "strength", "for": "strength",
    "2": "dexterity", "des": "dexterity",
    "3": "constitution", "con": "constitution",
    "4": "intelligence", "int": "intelligence",
    "5": "wisdom", "sab": "wisdom",
    "6": "charisma", "car": "charisma"
}

def pedir_nome(cultura_padrao='medieval'):
    """
    Função auxiliar para pedir o nome do personagem.
    Utiliza um estado específico para esta tarefa.
    """
    creator = CharacterNameCreator(cultura_padrao)
    return creator.run()

class CharacterCreationState(BaseState):
    """
    Estado de jogo responsável por guiar o usuário através da criação de um novo personagem,
    incluindo nome, dificuldade, raça, classe, antecedente e atributos.
    """

    def enter(self):
        """Inicializa as variáveis do estado ao entrar na tela de criação."""
        self.step = "start"
        self.character_data = {}
        self.races = load_races()
        self.classes = load_classes()
        self.backgrounds = load_backgrounds(self.game.db_conn)
        self.temp_character = None
        self.db_conn = self.game.db_conn
        self.feedback_message = ""
        self.difficulty = "Desafio Justo"
        self.difficulty_options = [
            "Aventura Leve", "Desafio Justo", "Provação Maldita",
            "Caminho da Dor", "Maldição de Ferro", "Inferno Vivo"
        ]

    def render(self):
        """
        Renderiza a tela de criação de personagem com base na etapa atual.
        Apenas exibe as informações, a entrada do usuário é tratada em handle_input().
        """
        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "=" * 40)
        print("=== CRIAÇÃO DE PERSONAGEM ===")
        print("=" * 40)

        if self.feedback_message:
            print(f"\n>>> {self.feedback_message} <<<\n")
            self.feedback_message = ""

        if self.step == "start":
            print("\n1. Começar criação")
            print("2. Voltar")
        
        elif self.step == "difficulty":
            self._render_difficulty_options()
        
        # Nova etapa para selecionar permadeath
        elif self.step == "permadeath_selection":
            self._render_permadeath_options()

        elif self.step == "race":
            self._render_race_options()

        elif self.step == "race_detail":
            self._render_race_details()

        elif self.step == "class":
            self._render_class_options()
        
        elif self.step == "class_detail":
            self._render_class_details()

        elif self.step == "background":
            self._render_background_options()
        
        elif self.step == "background_detail":
            self._render_background_details()

        elif self.step == "attributes":
            self._render_attribute_options()
        
        elif self.step == "attribute_reroll":
            self._render_attribute_reroll_options()
        
        elif self.step == "complete":
            self._render_completion_message()

    def handle_input(self):
        """
        Lida com a entrada do usuário, processando a escolha com base na etapa atual.
        """
        try:
            if self.step == "start":
                self._handle_start_input()
            elif self.step == "name":
                self._handle_name_input()
            elif self.step == "difficulty":
                self._handle_difficulty_input()
            # Novo manipulador de entrada para permadeath
            elif self.step == "permadeath_selection":
                self._handle_permadeath_input()
            elif self.step == "race":
                self._handle_race_input()
            elif self.step == "class":
                self._handle_class_input()
            elif self.step == "background":
                self._handle_background_input()
            elif self.step == "attributes":
                self._handle_attributes_input()
            elif self.step == "attribute_reroll":
                self._handle_attribute_reroll_input()
            elif self.step == "complete":
                self._handle_complete_input()
        except Exception as e:
            # Captura qualquer erro inesperado e exibe para depuração
            self.feedback_message = f"Erro inesperado: {str(e)}. Por favor, reporte este erro."
            traceback.print_exc()
            input("\nPressione ENTER para continuar após o erro...")
            self.step = "start"

    # --- Métodos de Renderização Privados ---
    def _render_difficulty_options(self):
        """Exibe as opções de dificuldade e seus modificadores."""
        print("\n=== SELECIONE A DIFICULDADE ===")
        print("=" * 40)
        print("A dificuldade afeta o jogo inteiro, incluindo:")
        print("- Dano recebido e causado")
        print("- Experiência e ouro ganhos")
        print("- Efeitos de cura")
        print("\nOpções:")
        
        for i, diff in enumerate(self.difficulty_options, 1):
            modifiers = DIFFICULTY_MODIFIERS.get(diff, {})
            print(f"{i}. {diff}:")
            if "damage_received" in modifiers:
                print(f"     Dano recebido: {modifiers['damage_received']}x")
            if "damage_dealt" in modifiers:
                print(f"     Dano causado: {modifiers['damage_dealt']}x")
            if "exp_multiplier" in modifiers:
                print(f"     Experiência: {modifiers['exp_multiplier']}x")
            if "gold_multiplier" in modifiers:
                print(f"     Ouro: {modifiers['gold_multiplier']}x")
        
        print("\n0. Voltar para nome")

    # Novo método de renderização para a seleção de permadeath
    def _render_permadeath_options(self):
        """Exibe as opções para ativar a morte permanente."""
        print("\n=== SELECIONE O MODO DE MORTE PERMANENTE ===")
        print("=" * 40)
        print("A morte permanente significa que, se seu personagem morrer, ele será permanentemente excluído do jogo.")
        print("Esta escolha não pode ser desfeita após a criação.")
        print("\nOpções:")
        print("1. Ativar Morte Permanente")
        print("2. Desativar Morte Permanente")
        print("\n0. Voltar para a dificuldade")


    def _render_race_options(self):
        """Exibe as opções de raça disponíveis."""
        print("\n--- SELECIONE SUA RAÇA ---")
        print("(D) Detalhes das raças")
        print("(V) Voltar para seleção de Morte Permanente")
        print("")
        
        for i, race in enumerate(self.races, 1):
            print(f"{i}. {race.get('name', 'Raça Desconhecida')}")

    def _render_race_details(self):
        """Renderiza o menu para ver detalhes de raças e lida com a entrada."""
        print("\n--- DETALHES DAS RAÇAS ---")
        print("0. Voltar")
        print("")
        
        for i, race in enumerate(self.races, 1):
            print(f"{i}. {race.get('name', 'Raça Desconhecida')}")
        
        choice = input("\nEscolha uma raça para detalhes: ").strip()
        if choice == '0':
            self.step = "race"
        elif choice.isdigit():
            race_idx = int(choice) - 1
            if 0 <= race_idx < len(self.races):
                race = self.races[race_idx]
                self._show_race_info(race)
            else:
                self.feedback_message = "Número inválido!"
        else:
            self.feedback_message = "Escolha inválida!"
    
    def _show_race_info(self, race):
        """Exibe informações detalhadas de uma raça."""
        print(f"\n=== {race.get('name', 'Raça Desconhecida').upper()} ===")
        print(f"\n{race.get('description', 'Sem descrição')}")
        
        print("\nBônus de Atributos:")
        def format_bonus(value):
            return f"+{value}" if value >= 0 else f"{value}"
        
        print(f"Força: {format_bonus(race.get('strength_bonus', 0))}")
        print(f"Destreza: {format_bonus(race.get('dexterity_bonus', 0))}")
        print(f"Constituição: {format_bonus(race.get('constitution_bonus', 0))}")
        print(f"Inteligência: {format_bonus(race.get('intelligence_bonus', 0))}")
        print(f"Sabedoria: {format_bonus(race.get('wisdom_bonus', 0))}")
        print(f"Carisma: {format_bonus(race.get('charisma_bonus', 0))}")
        
        input("\nPressione ENTER para voltar...")
    
    def _render_class_options(self):
        """Exibe as opções de classe disponíveis."""
        print("\n--- SELECIONE SUA CLASSE ---")
        print("(D) Detalhes das classes")
        print("(V) Voltar para raça")
        print("")
        
        for i, cls in enumerate(self.classes, 1):
            print(f"{i}. {cls.get('name', 'Classe Desconhecida')}")

    def _render_class_details(self):
        """Renderiza o menu para ver detalhes de classes e lida com a entrada."""
        print("\n--- DETALHES DAS CLASSES ---")
        print("0. Voltar")
        print("")
        
        for i, cls in enumerate(self.classes, 1):
            print(f"{i}. {cls.get('name', 'Classe Desconhecida')}")
        
        choice = input("\nEscolha uma classe para detalhes: ").strip()
        if choice == '0':
            self.step = "class"
        elif choice.isdigit():
            class_idx = int(choice) - 1
            if 0 <= class_idx < len(self.classes):
                cls = self.classes[class_idx]
                self._show_class_info(cls)
            else:
                self.feedback_message = "Número inválido!"
        else:
            self.feedback_message = "Escolha inválida!"

    def _show_class_info(self, cls):
        """Exibe informações detalhadas de uma classe."""
        print(f"\n=== {cls.get('name', 'Classe Desconhecida').upper()} ===")
        print(f"\n{cls.get('description', 'Sem descrição')}")
        print(f"\nDado de Vida: {cls.get('hit_dice', '1d8')}")
        print(f"Dado de Mana: {cls.get('mana_dice', '1d4')}")
        print(f"CA Base: {cls.get('base_ac', 10)}")

        starting_weapon_id = cls.get('starting_weapon_id')
        if starting_weapon_id:
            weapon_details = get_item_base_details(self.db_conn, starting_weapon_id)
            if weapon_details:
                print(f"\nArma Inicial: {weapon_details.get('name')}")
                print(f"Dano: {weapon_details.get('damage_dice')}")
                print(f"Atributo: {weapon_details.get('main_attribute')}")

        starting_armor_id = cls.get('starting_armor_id')
        if starting_armor_id:
            armor_details = get_item_base_details(self.db_conn, starting_armor_id)
            if armor_details:
                print(f"\nArmadura Inicial: {armor_details.get('name')}")
                print(f"Bônus CA: +{armor_details.get('armor_bonus')}")

        input("\nPressione ENTER para voltar...")

    def _render_background_options(self):
        """Exibe as opções de antecedente disponíveis."""
        print("\n--- SELECIONE SEU ANTECEDENTE ---")
        print("(D) Detalhes dos antecedentes")
        print("(V) Voltar para classe")
        print("")

        for i, bg in enumerate(self.backgrounds, 1):
            print(f"{i}. {bg.get('name', 'Antecedente Desconhecido')}")

    def _render_background_details(self):
        """Renderiza o menu para ver detalhes de antecedentes e lida com a entrada."""
        print("\n--- DETALHES DOS ANTECEDENTES ---")
        print("0. Voltar")
        print("")

        for i, bg in enumerate(self.backgrounds, 1):
            print(f"{i}. {bg.get('name', 'Antecedente Desconhecido')}")

        choice = input("\nEscolha um antecedente para detalhes: ").strip()
        if choice == '0':
            self.step = "background"
        elif choice.isdigit():
            bg_idx = int(choice) - 1
            if 0 <= bg_idx < len(self.backgrounds):
                bg = self.backgrounds[bg_idx]
                self._show_background_info(bg)
            else:
                self.feedback_message = "Número inválido!"
        else:
            self.feedback_message = "Escolha inválida!"

    def _show_background_info(self, background):
        """Exibe informações detalhadas de um antecedente, incluindo suas perícias."""
        print(f"\n=== {background.get('name', 'Antecedente Desconhecido').upper()} ===")
        print(f"\n{background.get('description', 'Sem descrição')}")
        
        print("\nPerícias Iniciais:")
        starting_skills = get_background_starting_skills(self.db_conn, background['id'])
        if starting_skills:
            for skill in starting_skills:
                print(f"- {skill['skill_name']} (Nível Inicial: {skill['starting_level']})")
        else:
            print("- Nenhuma perícia inicial definida para este antecedente.")
        
        input("\nPressione ENTER para voltar...")

    def _render_attribute_options(self):
        """Exibe os atributos atuais e as opções de ação."""
        if not self.temp_character:
            self.feedback_message = "Erro ao criar personagem. Voltando ao início."
            self.step = "start"
            return
        
        print("\n=== ATRIBUTOS DO PERSONAGEM ===")
        self.temp_character.show_attributes()
        
        print("\n" + "=" * 40)
        print("O QUE DESEJA FAZER?")
        print("=" * 40)
        print("1. Manter atributos e finalizar")
        print("2. Rerolar todos os atributos")
        print("3. Rerolar um atributo específico")
        print("4. Voltar para seleção de background")

    def _render_attribute_reroll_options(self):
        """Exibe as opções para rerolar um atributo específico."""
        print("\n" + "=" * 40)
        print("QUAL ATRIBUTO REROLAR?")
        print("=" * 40)
        print("1. Força (for)")
        print("2. Destreza (des)")
        print("3. Constituição (con)")
        print("4. Inteligência (int)")
        print("5. Sabedoria (sab)")
        print("6. Carisma (car)")
        print("\n0. Voltar")

    def _render_completion_message(self):
        """Exibe a mensagem de sucesso e os detalhes finais do personagem."""
        print("\n=== PERSONAGEM CRIADO COM SUCESSO! ===")
        self.game.player.show_attributes()
        print("\nPressione ENTER para começar sua aventura...")

    # --- Métodos de Manipulação de Entrada Privados ---
    def _handle_start_input(self):
        """Processa a entrada na tela inicial."""
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            self.step = "name"
        elif choice == "2":
            from ..system.main_menu_state import MainMenuState
            self.game.change_state(MainMenuState(self.game))
        else:
            self.feedback_message = "Opção inválida!"
    
    def _handle_name_input(self):
        """Processa a entrada de nome."""
        nome = pedir_nome()
        if nome:
            self.character_data["name"] = nome
            self.step = "difficulty"
        else:
            self.feedback_message = "Nome inválido. Tente novamente."
            self.step = "start"

    def _handle_difficulty_input(self):
        """Processa a seleção de dificuldade."""
        choice = input("\nEscolha a dificuldade: ").strip()
        if choice == "0":
            self.step = "name"
        elif choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(self.difficulty_options):
                self.difficulty = self.difficulty_options[choice_idx]
                self.feedback_message = f"Dificuldade definida como: {self.difficulty}"
                self.character_data["difficulty"] = self.difficulty # Salva a dificuldade
                self.step = "permadeath_selection" # Próximo passo é a seleção de permadeath
            else:
                self.feedback_message = "Opção inválida!"
        else:
            self.feedback_message = "Escolha inválida!"

    # Novo manipulador de entrada para permadeath
    def _handle_permadeath_input(self):
        """Processa a seleção de morte permanente."""
        choice = input("\nEscolha: ").strip()
        if choice == "1":
            self.character_data["permadeath"] = 1
            self.feedback_message = "Morte Permanente ATIVADA!"
            self.step = "race"
        elif choice == "2":
            self.character_data["permadeath"] = 0
            self.feedback_message = "Morte Permanente DESATIVADA!"
            self.step = "race"
        elif choice == "0":
            self.step = "difficulty"
        else:
            self.feedback_message = "Opção inválida!"

    def _handle_race_input(self):
        """Processa a seleção de raça."""
        choice = input("\nEscolha uma raça: ").strip().lower()
        if choice == 'd':
            self.step = "race_detail"
        elif choice == 'v':
            self.step = "permadeath_selection" # Volta para a seleção de permadeath
        elif choice.isdigit():
            race_idx = int(choice) - 1
            if 0 <= race_idx < len(self.races):
                race = self.races[race_idx]
                self.character_data["race"] = race.get('name', 'Humano')
                self.feedback_message = f"Raça escolhida: {self.character_data['race']}"
                self.step = "class"
            else:
                self.feedback_message = "Opção inválida!"
        else:
            self.feedback_message = "Escolha inválida!"
    
    def _handle_class_input(self):
        """Processa a seleção de classe."""
        choice = input("\nEscolha uma classe: ").strip().lower()
        if choice == 'd':
            self.step = "class_detail"
        elif choice == 'v':
            self.step = "race"
        elif choice.isdigit():
            class_idx = int(choice) - 1
            if 0 <= class_idx < len(self.classes):
                cls = self.classes[class_idx]
                self.character_data["char_class"] = cls.get('name', 'Guerreiro')
                self.feedback_message = f"Classe escolhida: {self.character_data['char_class']}"
                self.step = "background"
            else:
                self.feedback_message = "Opção inválida!"
        else:
            self.feedback_message = "Escolha inválida!"

    def _handle_background_input(self):
        """Processa a seleção de antecedente."""
        choice = input("\nEscolha um antecedente: ").strip().lower()
        if choice == 'd':
            self.step = "background_detail"
        elif choice == 'v':
            self.step = "class"
        elif choice.isdigit():
            bg_idx = int(choice) - 1
            if 0 <= bg_idx < len(self.backgrounds):
                background = self.backgrounds[bg_idx]
                self.character_data["background"] = background.get('name', 'Nenhum')
                self.feedback_message = f"Antecedente escolhido: {self.character_data['background']}"
                
                # Cria o objeto Character temporário
                self.temp_character = Character(
                    db_connection=self.game.db_conn,
                    name=self.character_data["name"],
                    race=self.character_data["race"],
                    char_class=self.character_data["char_class"],
                    background=self.character_data["background"],
                    difficulty=self.character_data["difficulty"], # Passa a dificuldade
                    permadeath=self.character_data.get("permadeath", 0) # Passa o novo permadeath
                )
                self.temp_character.recalculate()
                self.step = "attributes"
            else:
                self.feedback_message = "Opção inválida!"
        else:
            self.feedback_message = "Escolha inválida!"

    def _handle_attributes_input(self):
        """Processa a entrada para a etapa de atributos."""
        choice = input("\nEscolha: ").strip()

        if choice == "1":
            self._finalize_character()
        elif choice == "2":
            self._reroll_all_attributes()
        elif choice == "3":
            self.step = "attribute_reroll"
        elif choice == "4":
            self.step = "background"
        else:
            self.feedback_message = "Opção inválida!"

    def _finalize_character(self):
        """Salva o personagem, aplica perícias e itens iniciais."""
        try:
            # Salva o personagem no banco para obter um ID
            if not save_character(self.db_conn, self.temp_character):
                self.feedback_message = "Falha ao salvar o personagem inicial."
                return
            
            # Recarrega o personagem para ter o ID válido do banco de dados
            loaded_char = Character.load_character(self.db_conn, self.temp_character.id)
            if not loaded_char:
                self.feedback_message = "Falha ao carregar personagem salvo."
                return
            
            self.temp_character = loaded_char
            
            # Aplica perícias e itens com o personagem já salvo e com ID válido
            self.temp_character.apply_background_skills()
            self.temp_character.equip_starting_items()

            self.game.player = self.temp_character
            self.step = "complete"
        except Exception as e:
            self.feedback_message = f"Erro ao finalizar personagem: {str(e)}"
            traceback.print_exc()

    def _reroll_all_attributes(self):
        """Rerola todos os atributos do personagem temporário."""
        self.temp_character.strength = roll_attribute()
        self.temp_character.dexterity = roll_attribute()
        self.temp_character.constitution = roll_attribute()
        self.temp_character.intelligence = roll_attribute()
        self.temp_character.wisdom = roll_attribute()
        self.temp_character.charisma = roll_attribute()
        self.temp_character.recalculate()
        self.feedback_message = "Atributos rerolados!"
    
    def _handle_attribute_reroll_input(self):
        """Processa a escolha de qual atributo rerolar."""
        choice = input("\nEscolha um atributo para rerolar: ").strip().lower()
        if choice == "0":
            self.step = "attributes"
        elif choice in attr_map:
            attribute_name = attr_map[choice]
            old_value = getattr(self.temp_character, attribute_name)
            new_value = roll_attribute()
            setattr(self.temp_character, attribute_name, new_value)
            self.temp_character.recalculate()
            self.feedback_message = f"Atributo '{attribute_name.capitalize()}' rerolado de {old_value} para {new_value}."
            self.step = "attributes"
        else:
            self.feedback_message = "Escolha inválida!"

    def _handle_complete_input(self):
        """Processa a entrada na tela final, avançando para o próximo estado."""
        input()
        from ..world.gameplay_state import GameplayState
        self.game.change_state(GameplayState(self.game))