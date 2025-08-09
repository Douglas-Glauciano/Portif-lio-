import sqlite3
import sys
import os

def get_application_base_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Se estiver em um executável PyInstaller, usa o caminho _MEIPASS.
        return sys._MEIPASS
    else:
        # Se estiver rodando o script Python diretamente,
        # retorna o diretório do script principal (main.py).
        # sys.argv[0] contém o caminho para o script que foi executado.
        return os.path.dirname(os.path.abspath(sys.argv[0])) # <--- LINHA ALTERADA AQUI
                                                             #      Isso garante que o base_path
                                                             #      seja o diretório do main.py
                                                             #      que é 'C:\Users\Usuario\Desktop\rust dice pré pericias\'
                                                             #      no seu caso.

# O restante do código permanece igual
# Constrói o caminho completo para o banco de dados.
# db_queries.py
from game.config import get_db_path
DB_PATH = get_db_path()

def get_connection():
    print(f"Tentando conectar ao banco de dados em: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def get_all_classes():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        c.id, c.name, c.hit_dice, c.mana_dice, c.base_ac, c.description,
        w.id AS weapon_id, w.name AS weapon_name, w.damage_dice, w.main_attribute, w.weapon_type,
        a.id AS armor_id, a.name AS armor_name, 
        a.physical_resistance,
        a.magical_resistance,
        a.dexterity_penalty,
        a.armor_class
    FROM classes c
    LEFT JOIN items w ON c.starting_weapon_id = w.id
    LEFT JOIN items a ON c.starting_armor_id = a.id
    ''')
    
    classes = []
    for row in cursor.fetchall():
        class_data = {
            'id': row[0],
            'name': row[1],
            'hit_dice': row[2],
            'mana_dice': row[3],
            'base_ac': row[4],
            'description': row[5],
            'starting_weapon': {
                'id': row[6],
                'name': row[7],
                'damage_dice': row[8],
                'main_attribute': row[9],
                'weapon_type': row[10]
            } if row[6] else None,
            'starting_armor': {
                'id': row[11],
                'name': row[12],
                'physical_resistance': row[13],
                'magical_resistance': row[14],
                'dexterity_penalty': row[15],
                'armor_class': row[16]
            } if row[11] else None
        }
        classes.append(class_data)
    
    conn.close()
    return classes

def get_class_by_name(conn, class_name):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT 
        c.id, c.name, c.hit_dice, c.mana_dice, c.base_ac, c.description,
        w.id AS weapon_id, w.name AS weapon_name, w.damage_dice, w.main_attribute, w.weapon_type,
        a.id AS armor_id, a.name AS armor_name, 
        a.physical_resistance,
        a.magical_resistance,
        a.dexterity_penalty,
        a.armor_class
    FROM classes c
    LEFT JOIN items w ON c.starting_weapon_id = w.id
    LEFT JOIN items a ON c.starting_armor_id = a.id
    WHERE c.name = ?
    ''', (class_name,))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    class_data = {
        'id': row[0],
        'name': row[1],
        'hit_dice': row[2],
        'mana_dice': row[3],
        'base_ac': row[4],
        'description': row[5],
        'starting_weapon': {
            'id': row[6],
            'name': row[7],
            'damage_dice': row[8],
            'main_attribute': row[9],
            'weapon_type': row[10]
        } if row[6] else None,
        'starting_armor': {
            'id': row[11],
            'name': row[12],
            'physical_resistance': row[13],
            'magical_resistance': row[14],
            'dexterity_penalty': row[15],
            'armor_class': row[16]
        } if row[11] else None
    }
    return class_data
def get_race_by_name(conn, name):
    """
    Retorna os dados de uma raça específica pelo nome.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM races WHERE name = ?", (name,))
    race_data = cursor.fetchone()
    
    if race_data:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, race_data))
    return None

def load_races():
    """
    Carrega todos os dados de raças do banco de dados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM races")
    
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    races = []
    for row in rows:
        race = dict(zip(columns, row))
        races.append(race)
    
    conn.close()
    return races

def load_classes():
    """
    Carrega todos os dados de classes do banco de dados (dados base, sem itens).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes")
    
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    classes = []
    for row in rows:
        cls = dict(zip(columns, row))
        classes.append(cls)
    
    conn.close()
    return classes

def load_monsters():
    """
    Carrega todos os dados de monstros do banco de dados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monsters")
    
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    monsters = []
    for row in rows:
        monsters.append(dict(zip(columns, row)))
    
    conn.close()
    
    return monsters

def load_monsters_by_level(conn, player_level, tolerance=2):    
    """
    Carrega monstros dentro de uma faixa de nível em relação ao nível do jogador.
    """
    cursor = conn.cursor()
    
    min_level = max(1, player_level - tolerance)
    max_level = player_level + tolerance
    
    cursor.execute('''
        SELECT * FROM monsters
        WHERE level BETWEEN ? AND ?
    ''', (min_level, max_level))
    
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    monsters = [dict(zip(columns, row)) for row in rows]
    
    return monsters

def get_character_by_id(conn, character_id):
    """
    Obtém os dados de um personagem pelo ID como um dicionário.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
    row = cursor.fetchone()
    
    if not row:
        return None

    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def add_item_to_inventory(conn, character_id, item_id, quantity=1, enhancement_level=0, enhancement_type=None):
    """
    Adiciona um item ao inventário de um personagem.
    Se um item com o mesmo ID base, nível de aprimoramento e tipo de aprimoramento
    já existir no inventário, a quantidade é atualizada. Caso contrário, um novo
    registro de item é criado no inventário.
    Retorna o inventory_id do item adicionado/atualizado.
    """
    cursor = conn.cursor()
    
    # Verifica se já existe uma instância EXATAMENTE igual no inventário
    # (mesmo item_id, enhancement_level e enhancement_type) para empilhar.
    # O tratamento de NULL para enhancement_type é crucial aqui.
    cursor.execute('''
        SELECT id, quantity FROM character_inventory
        WHERE character_id = ? AND item_id = ? AND enhancement_level = ? 
        AND (enhancement_type = ? OR (enhancement_type IS NULL AND ? IS NULL))
    ''', (character_id, item_id, enhancement_level, enhancement_type, enhancement_type))
    existing_item = cursor.fetchone()

    inventory_item_id = None

    if existing_item:
        # Se existe, atualiza a quantidade
        inventory_item_id, current_quantity = existing_item
        new_quantity = current_quantity + quantity
        cursor.execute('''
            UPDATE character_inventory
            SET quantity = ?
            WHERE id = ?
        ''', (new_quantity, inventory_item_id))
    else:
        # Se não existe, insere uma nova entrada no inventário
        cursor.execute('''
            INSERT INTO character_inventory (character_id, item_id, quantity, enhancement_level, enhancement_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (character_id, item_id, quantity, enhancement_level, enhancement_type))
        inventory_item_id = cursor.lastrowid # Pega o ID da nova entrada no inventário
    
    conn.commit()
    return inventory_item_id

def get_character_equipment(conn, character_id):
    cursor = conn.cursor()
    
    # Primeiro verifique se o personagem existe
    cursor.execute("SELECT id FROM characters WHERE id = ?", (character_id,))
    char_exists = cursor.fetchone()
    
    if not char_exists:
        print(f"[ERRO] Personagem com ID {character_id} não existe!")
        return {
            'character_id': character_id,
            'main_hand_inventory_id': None,
            'off_hand_inventory_id': None,
            'head_inventory_id': None,
            'body_inventory_id': None,
            'hands_inventory_id': None,
            'feet_inventory_id': None,
            'ring1_inventory_id': None,
            'ring2_inventory_id': None,
            'amulet_inventory_id': None
        }
    
    # Agora verifique o equipamento
    cursor.execute("SELECT * FROM character_equipment WHERE character_id = ?", (character_id,))
    row = cursor.fetchone()
    
    if row:
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
    else:
        # Usar INSERT OR IGNORE para evitar duplicatas
        cursor.execute("""
            INSERT OR IGNORE INTO character_equipment (character_id) 
            VALUES (?)
        """, (character_id,))
        conn.commit()
        
        # Buscar novamente após a inserção
        cursor.execute("SELECT * FROM character_equipment WHERE character_id = ?", (character_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        else:
            print(f"[ERRO] Falha ao criar registro de equipamento para char_id={character_id}")
            return {
                'character_id': character_id,
                'main_hand_inventory_id': None,
                'off_hand_inventory_id': None,
                'head_inventory_id': None,
                'body_inventory_id': None,
                'hands_inventory_id': None,
                'feet_inventory_id': None,
                'ring1_inventory_id': None,
                'ring2_inventory_id': None,
                'amulet_inventory_id': None
            }

def get_item_base_details(conn, item_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if row:
        columns = [col[0] for col in cursor.description]
        item_details = dict(zip(columns, row))
        return item_details
    return None

def get_equipped_items_for_character(conn, character_id):
    cursor = conn.cursor()
    slot_mapping = {
        'main_hand_inventory_id': "Mão Principal",
        'off_hand_inventory_id': "Mão Secundária",
        'head_inventory_id': "Cabeça",
        'body_inventory_id': "Corpo",
        'hands_inventory_id': "Mãos",
        'feet_inventory_id': "Pés", 
        'ring1_inventory_id': "Anel 1",
        'ring2_inventory_id': "Anel 2",
        'amulet_inventory_id': "Amuleto"
    }

    equipped_items_details = []
    equipped_slots_map = get_character_equipment(conn, character_id)
    
    if not equipped_slots_map or all(value is None for key, value in equipped_slots_map.items() if key != 'character_id'):
        return []

    for slot_technical, inventory_id in equipped_slots_map.items():
        if slot_technical == 'character_id':
            continue

        if inventory_id is not None:
            cursor.execute('''
                SELECT 
                    ci.id AS inventory_id,
                    ci.quantity,
                    ci.enhancement_level,
                    ci.enhancement_type,
                    i.id AS item_base_id,
                    i.name,
                    i.category,
                    i.subcategory,
                    i.equip_slot,
                    i.level,
                    i.description,
                    i.weight,
                    i.value,
                    i.damage_dice,
                    i.damage_type,
                    i.weapon_type,
                    i.main_attribute,
                    i.two_handed,
                    i.physical_resistance,  -- Novo campo
                    i.magical_resistance,   -- Novo campo
                    i.dexterity_penalty,    -- Novo campo
                    i.armor_bonus,          -- Mantido para escudos
                    i.armor_class,
                    i.strength_requirement
                FROM character_inventory ci
                JOIN items i ON ci.item_id = i.id
                WHERE ci.id = ?
            ''', (inventory_id,))
            
            item_full_details = cursor.fetchone()

            if item_full_details:
                columns = [description[0] for description in cursor.description]
                item_data = dict(zip(columns, item_full_details))
                
                item_data['equipped_slot_technical'] = slot_technical
                item_data['equipped_slot_friendly'] = slot_mapping.get(slot_technical, slot_technical)
                
                equipped_items_details.append(item_data)
    
    return equipped_items_details
    
    
def unequip_item_from_character(conn, character_id, slot_name):
    """
    Desequipa um item de um slot específico do personagem e o move para o inventário.
    Retorna True e uma mensagem de sucesso, ou False e uma mensagem de erro.
    """
    cursor = conn.cursor()
    
    # CORREÇÃO: slot_name JÁ DEVE VIR COM '_inventory_id' se for um slot de equipamento
    # Se slot_name já é 'main_hand_inventory_id', não adicione '_inventory_id' novamente.
    # Assumimos que slot_name já é o nome da coluna no DB (ex: 'main_hand_inventory_id')
    db_slot_name = slot_name 

    try:
        # Pega o inventory_id do item atualmente equipado no slot
        cursor.execute(f'''
            SELECT {db_slot_name} FROM character_equipment
            WHERE character_id = ?
        ''', (character_id,))
        result = cursor.fetchone()
        inventory_id_to_unequip = result[0] if result else None
        
        if not inventory_id_to_unequip:
            return False, "Nenhum item equipado neste slot."
        
        # Atualiza a quantidade do item no inventário para 1 (tornando-o disponível novamente)
        cursor.execute('''
            UPDATE character_inventory
            SET quantity = quantity + 1 -- Incrementa a quantidade, pois o item estava 'removido' do inventário
            WHERE id = ?
        ''', (inventory_id_to_unequip,))

        # Define o slot de equipamento como NULL
        cursor.execute(f'''
            UPDATE character_equipment
            SET {db_slot_name} = NULL
            WHERE character_id = ?
        ''', (character_id,))
        
        conn.commit()

        # Opcional: Obter o nome do item para a mensagem de sucesso
        cursor.execute('''
            SELECT i.name FROM character_inventory ci
            JOIN items i ON ci.item_id = i.id
            WHERE ci.id = ?
        ''', (inventory_id_to_unequip,))
        item_name_result = cursor.fetchone()
        item_name = item_name_result[0] if item_name_result else f"Item (ID de Inventário: {inventory_id_to_unequip})"

        # A mensagem agora usa o nome amigável do slot, não o nome técnico do DB
        # Para isso, precisamos do mapeamento.
        # Poderíamos passar o nome amigável como parâmetro ou re-mapear aqui.
        # Por simplicidade, vamos usar o slot_name que veio, mas é o slot técnico.
        return True, f"'{item_name}' desequipado do slot '{slot_name.replace('_inventory_id', '').replace('_', ' ').capitalize()}' e movido para a mochila."
        
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Erro ao desequipar item: {e}"

def get_character_inventory(conn, character_id):
    cursor = conn.cursor()
    query = """
    SELECT 
        ci.id AS inventory_id,
        ci.quantity,
        ci.enhancement_level,
        ci.enhancement_type,
        i.id AS item_base_id,
        i.name,
        i.category,
        i.subcategory,
        i.equip_slot,
        i.level,
        i.description,
        i.weight,
        i.value,
        i.damage_dice,
        i.damage_type,
        i.weapon_type,
        i.main_attribute,
        i.two_handed,
        i.physical_resistance,  -- Novo campo
        i.magical_resistance,   -- Novo campo
        i.dexterity_penalty,    -- Novo campo
        i.armor_bonus,          -- Mantido para escudos
        i.armor_class,
        i.strength_requirement
    FROM character_inventory ci
    JOIN items i ON ci.item_id = i.id
    WHERE ci.character_id = ? AND ci.quantity > 0
    """
    cursor.execute(query, (character_id,))
    columns = [col[0] for col in cursor.description]
    inventory_items = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return inventory_items

def get_class_starting_items(conn, class_name):
    """
    Obtém os IDs dos itens iniciais (arma e armadura base) para uma classe.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT starting_weapon_id, starting_armor_id 
        FROM classes 
        WHERE name = ?
    ''', (class_name,))
    row = cursor.fetchone()
    return row if row else (None, None)

def remove_item_from_inventory(conn, inventory_id, quantity=1):
    """
    Remove uma quantidade especificada de um item do inventário
    (identificado pelo inventory_id). Se a quantidade for maior ou igual
    à quantidade existente, o item é removido completamente.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM character_inventory WHERE id = ?", (inventory_id,))
    result = cursor.fetchone()

    if not result:
        return False

    current_quantity = result[0]
    if current_quantity > quantity:
        new_quantity = current_quantity - quantity
        cursor.execute("UPDATE character_inventory SET quantity = ? WHERE id = ?", (new_quantity, inventory_id))
    else:
        cursor.execute("DELETE FROM character_inventory WHERE id = ?", (inventory_id,))
    
    conn.commit()
    return True

def equip_item_from_inventory(conn, character_id, inventory_id):
    """
    Equipa um item do inventário de um personagem em seu slot apropriado.
    Se um item já estiver equipado no slot, ele é desequipado e movido
    de volta para o inventário do personagem.
    Retorna True e uma mensagem de sucesso, ou False e uma mensagem de erro.
    """
    cursor = conn.cursor()
    
    # 1. Obter detalhes do item do inventário (incluindo o item_id base e o slot de equipamento)
    cursor.execute('''
        SELECT ci.item_id, i.equip_slot, i.name
        FROM character_inventory ci
        JOIN items i ON ci.item_id = i.id
        WHERE ci.id = ? AND ci.character_id = ? AND ci.quantity > 0
    ''', (inventory_id, character_id))
    result = cursor.fetchone()
    
    if not result:
        return False, "Item não encontrado no inventário ou não pertence a este personagem."
    
    item_base_id, declared_equip_slot, item_name = result

    if not declared_equip_slot:
        return False, "Este item não pode ser equipado."
    
    # Determinar o slot real a ser usado (especialmente para anéis)
    slot_to_equip_db_name = None
    if declared_equip_slot == 'ring':
        cursor.execute("SELECT ring1_inventory_id, ring2_inventory_id FROM character_equipment WHERE character_id = ?", (character_id,))
        ring_slots = cursor.fetchone()
        
        if not ring_slots or (ring_slots[0] is None and ring_slots[1] is None):
            # Garante que o registro de equipamento existe e o busca
            # Esta chamada a get_character_equipment já garante a criação e busca do registro
            equipment_data = get_character_equipment(conn, character_id)
            ring_slots = (equipment_data.get('ring1_inventory_id'), equipment_data.get('ring2_inventory_id'))

        if ring_slots and ring_slots[0] is None:
            slot_to_equip_db_name = 'ring1_inventory_id'
        elif ring_slots and ring_slots[1] is None:
            slot_to_equip_db_name = 'ring2_inventory_id'
        else:
            return False, "Ambos os slots de anel estão ocupados. Desequipe um primeiro."
    else:
        slot_to_equip_db_name = f"{declared_equip_slot}_inventory_id"
    
    # 2. Verificar se já existe um item equipado no slot de destino
    cursor.execute(f"SELECT {slot_to_equip_db_name} FROM character_equipment WHERE character_id = ?", (character_id,))
    currently_equipped_inventory_id_tuple = cursor.fetchone()
    currently_equipped_inventory_id = currently_equipped_inventory_id_tuple[0] if currently_equipped_inventory_id_tuple else None
    
    # 3. Se houver um item equipado, desequipá-lo (movê-lo de volta para o inventário)
    if currently_equipped_inventory_id is not None:
        # Incrementa a quantidade do item desequipado no inventário
        cursor.execute('''
            UPDATE character_inventory
            SET quantity = quantity + 1
            WHERE id = ?
        ''', (currently_equipped_inventory_id,))
        
        # Opcional: obter o nome do item desequipado para a mensagem
        cursor.execute('''
            SELECT i.name FROM character_inventory ci
            JOIN items i ON ci.item_id = i.id
            WHERE ci.id = ?
        ''', (currently_equipped_inventory_id,))
        unequipped_item_name_result = cursor.fetchone()
        unequipped_item_name = unequipped_item_name_result[0] if unequipped_item_name_result else "Item Desconhecido"
        print(f"'{unequipped_item_name}' desequipado e retornado ao inventário.")

    # 4. Equipar o novo item (atualizar o slot na tabela character_equipment)
    # Usamos INSERT OR REPLACE para garantir que o registro de equipamento exista
    # e para atualizar o slot corretamente.
    sql_query = f"UPDATE character_equipment SET {slot_to_equip_db_name} = ? WHERE character_id = ?"
    sql_params = (inventory_id, character_id)
    cursor.execute(sql_query, sql_params)

    # 5. Reduzir a quantidade do item equipado no inventário para 0 (ou remover)
    # Optamos por definir a quantidade como 0 para manter o registro do item no inventário
    # mesmo quando equipado, facilitando a re-adição ao desequipar.
    cursor.execute("UPDATE character_inventory SET quantity = 0 WHERE id = ?", (inventory_id,))
    
    conn.commit()

    return True, f"'{item_name}' equipado com sucesso no slot '{declared_equip_slot}'."

def get_item_by_id(conn, item_id):
    """
    Esta função agora é um alias para get_item_base_details,
    pois 'get_item_details' não é mais o nome mais preciso.
    """
    return get_item_base_details(conn, item_id)

def update_character_gold(conn, character_id, new_gold):
    """
    Atualiza a quantidade de ouro de um personagem.
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE characters SET gold = ? WHERE id = ?", (new_gold, character_id))
    conn.commit()

def enhance_inventory_item(conn, inventory_id, new_enhancement_level, new_enhancement_type):
    """
    Aprimora um item específico no inventário (identificado pelo inventory_id).
    Atualiza seu nível e tipo de aprimoramento.
    """
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE character_inventory
            SET enhancement_level = ?, enhancement_type = ?
            WHERE id = ?
        ''', (new_enhancement_level, new_enhancement_type, inventory_id))
        conn.commit()
        return True, f"Item de inventário {inventory_id} aprimorado para Nível {new_enhancement_level} ({new_enhancement_type})."
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Erro ao aprimorar item: {e}"

def get_background_by_name(conn, background_name):
    """
    Retorna os dados de um background específico pelo nome.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backgrounds WHERE name = ?", (background_name,))
    background_data = cursor.fetchone()

    if background_data:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, background_data))
    return None

def get_background_starting_skills(conn, background_id):
    """
    Obtém as habilidades iniciais concedidas por um background específico.
    Retorna uma lista de dicionários, cada um contendo os detalhes de uma habilidade.
    Assume uma tabela 'background_skills' que liga 'backgrounds' a 'skills'.
    """
    cursor = conn.cursor()
    query = """
    SELECT
        s.id AS skill_id,
        s.name AS skill_name,
        s.attribute,
        bs.starting_level -- <--- ADD THIS LINE! You need to select it from the background_skills table
    FROM background_skills bs
    JOIN skills s ON bs.skill_id = s.id
    WHERE bs.background_id = ?
    """
    cursor.execute(query, (background_id,))
    
    columns = [col[0] for col in cursor.description]
    skills = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return skills

def add_character_skill(conn, character_id, skill_id, initial_level=1):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM character_skills
            WHERE character_id = ? AND skill_id = ?
        ''', (character_id, skill_id))
        existing_skill = cursor.fetchone()

        if existing_skill:
            return False, f"Personagem {character_id} já possui a habilidade {skill_id}."
        else:
            # Corrigido: inserir apenas as colunas existentes
            cursor.execute('''
                INSERT INTO character_skills (character_id, skill_id, level, current_xp, max_xp)
                VALUES (?, ?, ?, 0, ?)
            ''', (character_id, skill_id, initial_level, 50)) # max_xp inicial 50
        
        conn.commit()
        return True, f"Habilidade {skill_id} adicionada ao personagem {character_id} com sucesso."
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Erro ao adicionar habilidade ao personagem: {e}"
    
def get_character_skills(conn, character_id):
    """
    Obtém todas as perícias de um personagem específico, incluindo o nível atual e XP.
    Retorna uma lista de dicionários, cada um contendo os detalhes da perícia.
    """
    cursor = conn.cursor()
    query = """
    SELECT
        cs.skill_id,
        s.name AS skill_name,
        s.description,  -- Mudado de skill_description para description
        s.attribute,
        cs.level,
        cs.current_xp,
        cs.max_xp
    FROM character_skills cs
    JOIN skills s ON cs.skill_id = s.id
    WHERE cs.character_id = ?
    ORDER BY s.name ASC
    """
    cursor.execute(query, (character_id,))
    
    columns = [col[0] for col in cursor.description]
    skills = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return skills

def get_skill_by_name(conn, skill_name):
    """
    Obtém os detalhes de uma habilidade base pelo nome.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skills WHERE name = ?", (skill_name,))
    skill_data = cursor.fetchone()

    if skill_data:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, skill_data))
    return None

def get_skill_by_id(conn, skill_id):
    """
    Obtém os detalhes de uma habilidade base pelo ID.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
    skill_data = cursor.fetchone()

    if skill_data:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, skill_data))
    return None

def load_backgrounds(conn):
    """
    Carrega todos os dados de antecedentes do banco de dados.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backgrounds")
    
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    backgrounds = []
    for row in rows:
        backgrounds.append(dict(zip(columns, row)))
    
    return backgrounds

def get_all_skills(conn):
    """
    Retorna todas as habilidades base do sistema.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skills")
    
    columns = [col[0] for col in cursor.description]
    skills = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return skills