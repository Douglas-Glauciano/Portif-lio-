from game.utils import roll_dice, modifier, roll_attribute, get_setting
from game.character import Character
from game.combat import Combat
from game.db_queries import get_class_by_name, get_item_details # Adicionado get_item_details para mostrar info de itens

def show_race_options(races):
    """Mostra opções de raça disponíveis com formatação de tabela aprimorada"""
    print("\n" + "=" * 80)
    print("ESCOLHA SUA RAÇA".center(80))
    print("=" * 80)
    
    # Cabeçalho da tabela
    print(f"{'Nº':<3} {'Raça':<15} {'For':<4} {'Des':<4} {'Con':<4} {'Int':<4} {'Sab':<4} {'Car':<4} {'Tier':<5} {'Descrição'}")
    print("-" * 80)
    
    for i, race_data in enumerate(races, 1):
        # Extrai os valores dos atributos (substitui None por 0)
        # Assumindo que race_data é um dicionário agora
        attrs = [
            race_data.get('strength_bonus', 0),
            race_data.get('dexterity_bonus', 0),
            race_data.get('constitution_bonus', 0),
            race_data.get('intelligence_bonus', 0),
            race_data.get('wisdom_bonus', 0),
            race_data.get('charisma_bonus', 0)
        ]
        
        # Formata os bônus com sinal de + se positivo
        formatted_attrs = []
        for val in attrs:
            if val > 0:
                formatted_attrs.append(f"+{val}")
            else:
                formatted_attrs.append(str(val))
        
        # Formata a linha da raça
        print(f"{i:<3} {race_data['name']:<15} " +
              f"{formatted_attrs[0]:<4} {formatted_attrs[1]:<4} " +
              f"{formatted_attrs[2]:<4} {formatted_attrs[3]:<4} " +
              f"{formatted_attrs[4]:<4} {formatted_attrs[5]:<4} " +
              f"{race_data.get('description', '')[:30]}...") # Limita descrição
    
    print("-" * 80)
    print("D. Ver detalhes de uma raça")
    print("V. Voltar ao menu anterior")
    print("=" * 80)
    
def show_race_details(race_data):
    """Mostra detalhes de uma raça específica com formatação aprimorada"""
    # race_data agora é um dicionário
    title = f"DETALHES: {race_data['name']}"
    title_len = len(title)
    
    print("\n" + "=" * title_len)
    print(title)
    print("=" * title_len)
    
    # Atributos com bônus
    print("\nBônus de Atributos:")
    print("-" * 30)
    attributes = ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"]
    attr_keys = ['strength_bonus', 'dexterity_bonus', 'constitution_bonus', 
                 'intelligence_bonus', 'wisdom_bonus', 'charisma_bonus']
    for idx, attr in enumerate(attributes):
        bonus = race_data.get(attr_keys[idx], 0)
        print(f"{attr:<15} {f'+{bonus}' if bonus > 0 else bonus}")
    
    # Descrição formatada
    print("\nDescrição:")
    print("-" * 30)
    desc = race_data.get('description', '')
    if desc:
        for i in range(0, len(desc), 70): # Quebra a descrição em linhas de no máximo 70 caracteres
            print(desc[i:i+70])
    else:
        print("Nenhuma descrição disponível.")
    
    print("\n" + "=" * title_len)

def show_class_options(classes):
    """Mostra opções de classe disponíveis"""
    print("\n" + "=" * 80)
    print("ESCOLHA SUA CLASSE".center(80))
    print("=" * 80)
    
    print(f"{'Nº':<3} {'Classe':<15} {'Dado de Vida':<12} {'CA Base':<9} {'Arma Inicial':<15} {'Armadura Inicial':<18}")
    print("-" * 80)
    for i, class_data in enumerate(classes, 1):
        weapon_name = "Nenhuma"
        # Usar get_connection() para obter uma conexão temporária
        conn = get_connection() 
        if class_data.get('starting_weapon_id'):
            weapon_details = get_item_details(conn, class_data['starting_weapon_id'])
            if weapon_details:
                weapon_name = weapon_details['name']
        
        armor_name = "Nenhuma"
        if class_data.get('starting_armor_id'):
            armor_details = get_item_details(conn, class_data['starting_armor_id'])
            if armor_details:
                armor_name = armor_details['name']
        conn.close() # Fechar a conexão

        print(f"{i:<3} {class_data['name']:<15} {class_data['hit_dice']:<12} {class_data['base_ac']:<9} {weapon_name:<15} {armor_name:<18}")
    
    print("-" * 80)
    print("D. Ver detalhes de uma classe")
    print("V. Voltar ao menu anterior")
    print("=" * 80)

def show_class_details(class_data):
    """Mostra detalhes de uma classe específica"""
    # class_data agora é um dicionário
    from game.db_queries import get_item_details, get_connection # Importa aqui para evitar circular
    
    title = f"DETALHES: {class_data['name']}"
    title_len = len(title)

    print("\n" + "=" * title_len)
    print(title)
    print("=" * title_len)
    print(f"Descrição: {class_data.get('description', 'Sem descrição')}")
    print(f"Dado de Vida: {class_data.get('hit_dice', 'N/A')}")
    print(f"CA Base: {class_data.get('base_ac', 'N/A')}")

    # Detalhes da arma inicial
    starting_weapon_id = class_data.get('starting_weapon_id')
    if starting_weapon_id:
        conn = get_connection() # Abre conexão temporária
        weapon_details = get_item_details(conn, starting_weapon_id)
        conn.close() # Fecha conexão
        if weapon_details:
            print(f"Arma Inicial: {weapon_details.get('name')} (Dano: {weapon_details.get('damage_dice')}, Atributo: {weapon_details.get('main_attribute')})")
        else:
            print("Arma Inicial: ID não encontrado.")
    else:
        print("Arma Inicial: Nenhuma.")

    # Detalhes da armadura inicial
    starting_armor_id = class_data.get('starting_armor_id')
    if starting_armor_id:
        conn = get_connection() # Abre conexão temporária
        armor_details = get_item_details(conn, starting_armor_id)
        conn.close() # Fecha conexão
        if armor_details:
            print(f"Armadura Inicial: {armor_details.get('name')} (Bônus CA: {armor_details.get('armor_bonus')})")
        else:
            print("Armadura Inicial: ID não encontrado.")
    else:
        print("Armadura Inicial: Nenhuma.")

    print("\n" + "=" * title_len)


def game_menu(player):
    from game.database import save_character, delete_character
    from game.db_queries import get_connection # Importa get_connection para usar aqui

    """Menu principal do jogo (versão simplificada)"""
    if not hasattr(player, 'name') or not isinstance(player.name, str):
        print("Erro: Objeto de personagem inválido!")
        return
    while True:
        player.recalculate() # Garante que os status estão atualizados no menu
        print("\n" + "=" * 50)
        print(f"AVENTURA DE {player.name.upper()}")
        print("=" * 50)
        print(f"Nível: {player.level} | Exp: {player.exp}/{player.exp_max}")
        print(f"HP: {player.hp}/{player.hp_max} | AC: {player.ac} | Ouro: {player.gold}")
        print("-" * 50)
        print("1. Explorar")
        print("2. Descansar")
        print("3. Ver Atributos")
        print("4. Inventário") # Adicionado
        print("5. Salvar e Continuar")
        print("6. Salvar e Sair")
        print("7. Deletar Personagem")
        print("=" * 50)
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            explore(player)
        elif choice == "2":
            rest(player)
        elif choice == "3":
            show_attributes_full(player) # Renomeado para evitar conflito e mostrar mais detalhes
        elif choice == "4": # Novo: Menu de Inventário
            from states.character.inventory_state import InventoryState
            # Assumindo que game.py tem uma forma de mudar o estado
            # Se não, você precisará passar o game object ou refatorar
            # Por enquanto, apenas printa uma mensagem
            print("\nMenu de Inventário (funcionalidade a ser implementada via estados).")
            input("Pressione Enter para continuar...")
            # self.game.change_state(InventoryState(self.game, player)) # Exemplo de como seria com states
        elif choice == "5":
            save_character(player.conn, player) # Passa a conexão
            print("\nJogo salvo!")
            input("Pressione Enter para continuar...")
        elif choice == "6":
            save_character(player.conn, player) # Passa a conexão
            return
        elif choice == "7":
            confirm = input(f"Tem certeza que deseja deletar {player.name}? (s/N): ").lower().strip()
            if confirm == 's':
                if delete_character(player.conn, player.id): # Passa a conexão
                    print("\nPersonagem deletado!")
                    input("Pressione Enter para continuar...")
                    return "deleted" # Retorna algo para indicar que o personagem foi deletado
            else:
                print("\nOperação cancelada.")
                input("Pressione Enter para continuar...")

def explore(player):
    from game.database import save_character
    from game.db_queries import get_connection # Importa get_connection
    """Ação de explorar (versão simplificada)"""
    print("\n" + "=" * 50)
    print("EXPLORANDO...")
    print("=" * 50)
    
    # 70% chance de encontro
    if roll_dice("1d10") > 3:
        print("\nVocê encontrou um inimigo!")
        combat = Combat(player, get_connection()) # Passa a conexão
        combat_result = combat.start()
        save_character(player.conn, player) # Salva após o combate
    else:
        print("\nVocê explorou a área mas não encontrou nada.")
    
    input("\nPressione Enter para continuar...")

def rest(player):
    from game.database import save_character
    from game.db_queries import get_connection # Importa get_connection
    """Ação de descansar (versão simplificada)"""
    print("\n" + "=" * 50)
    print("DESCANSANDO...")
    print("=" * 50)
    
    # 30% chance de encontro durante descanso
    if roll_dice("1d10") > 7:
        print("\nUm monstro te surpreendeu durante o descanso!")
        combat = Combat(player, get_connection()) # Passa a conexão
        combat_result = combat.start()
        save_character(player.conn, player) # Salva após o combate
    else:
        heal_amount = roll_dice("1d8") + modifier(player.constitution)
        player.hp = min(player.hp + heal_amount, player.hp_max)
        print(f"\nVocê descansou e recuperou {heal_amount} de HP!")
        print(f"HP atual: {player.hp}/{player.hp_max}")
        save_character(player.conn, player) # Salva após o descanso
        input("\nPressione Enter para continuar...")

def show_attributes_full(player): # Renomeado para diferenciar da versão simplificada
    """Exibe atributos do personagem (versão completa e atualizada)"""
    # O método show_attributes da classe Character já faz o recalculo e formatação
    if player:
        player.show_attributes()
    else:
        print("\nErro: Personagem não carregado ou inválido.")
    input("\nPressione Enter para voltar...")

# Importa get_connection aqui para que as funções de menu possam usá-lo
from game.db_queries import get_connection
