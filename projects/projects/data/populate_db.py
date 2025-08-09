import os
import sys
import sqlite3

# Adicione o caminho para o diretório pai ao sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Tente importar de game.config, mas com fallback
try:
    from game.config import get_db_path
except ImportError:
    # Fallback para quando estiver rodando como executável
    def get_db_path():
        """Retorna o caminho do banco de dados para executáveis compilados"""
        if getattr(sys, 'frozen', False):
            # Caminho para executáveis PyInstaller
            base_path = os.path.dirname(sys.executable)
            return os.path.join(base_path, 'data', 'database.db')
        else:
            # Caminho para desenvolvimento
            return os.path.join(os.path.dirname(BASE_DIR), 'data', 'database.db')

DB_PATH = get_db_path()
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Importação correta do módulo monster (garantindo que esteja acessível)
try:
    from game.monster import Monster
except ImportError:
    print("Erro: Não foi possível importar 'Monster' de 'game.monster'. Verifique o caminho.")
    sys.exit(1)

def create_connection(db_path):
    """Cria uma conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Erro de banco de dados ao conectar: {e}")
        return None
    
def drop_tables(conn):
    """Apaga todas as tabelas existentes no banco de dados."""
    cursor = conn.cursor()
    
    # 1. Desativa a verificação de chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # 2. Lista de tabelas na ordem correta de exclusão (filhas antes das pais)
    tables = [
        'character_equipment',   # Depende de character_inventory
        'character_inventory',   # Depende de characters e items
        'character_skills',      # Depende de characters e skills
        'background_skills',     # Depende de backgrounds e skills
        'backgrounds',
        'characters',
        'classes',
        'races',
        'monsters',
        'items',
        'name_components',
        'skills'
    ]
    
    print("\nApagando tabelas existentes...")
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Tabela '{table}' apagada.")
        except sqlite3.Error as e:
            print(f"Erro ao apagar tabela '{table}': {e}")
    
    # 3. Reseta a sequência de AUTOINCREMENT
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
        print("Sequência de autoincremento resetada.")
    except sqlite3.Error as e:
        print(f"Erro ao resetar sqlite_sequence: {e}")
    
    # 4. Reativa a verificação de chaves estrangeiras
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    print("Tabelas apagadas com sucesso (se existiam).")


def create_tables(conn):
    """Cria todas as tabelas necessárias no banco de dados."""
    cursor = conn.cursor()

    # Tabela de personagens (SEM ALTERAÇÕES)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        race TEXT NOT NULL,
        class TEXT NOT NULL,
        background TEXT,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        exp_max INTEGER DEFAULT 100,
        hp INTEGER DEFAULT 10,
        hp_max INTEGER DEFAULT 10,
        mana INTEGER DEFAULT 2,
        mana_max INTEGER DEFAULT 2,
        ac INTEGER DEFAULT 10,
        gold INTEGER DEFAULT 0,
        strength INTEGER DEFAULT 10,
        dexterity INTEGER DEFAULT 10,
        constitution INTEGER DEFAULT 10,
        intelligence INTEGER DEFAULT 10,
        wisdom INTEGER DEFAULT 10,
        charisma INTEGER DEFAULT 10,
        difficulty TEXT,
        permadeath INTEGER DEFAULT 0  -- Nova coluna para controle de morte permanente 0 para negativo
    )''')
    
    # Tabela de raças (SEM ALTERAÇÕES)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS races (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        strength_bonus INTEGER DEFAULT 0,
        dexterity_bonus INTEGER DEFAULT 0,
        constitution_bonus INTEGER DEFAULT 0,
        intelligence_bonus INTEGER DEFAULT 0,
        wisdom_bonus INTEGER DEFAULT 0,
        charisma_bonus INTEGER DEFAULT 0,
        description TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL CHECK(category IN (
            'weapon', 'armor', 'shield', 'consumable', 'misc', 'ammo'
        )),
        subcategory TEXT,
        equip_slot TEXT CHECK(equip_slot IN (
            'main_hand', 'off_hand', 'head', 'body', 'hands', 'feet', 'ring', 'amulet'
        )),
        level INTEGER DEFAULT 1,
        description TEXT,
        weight REAL DEFAULT 0,
        value INTEGER DEFAULT 0,
        
        -- Campos específicos para armas
        damage_dice TEXT,
        damage_type TEXT,
        weapon_type TEXT CHECK(weapon_type IN (
            'one_handed', 'two_handed', 'polearm', 'bow', 'crossbow', 'staff', 'unarmed', 'wand'
        )),
        main_attribute TEXT,
        two_handed BOOLEAN DEFAULT 0,
        
        -- Campos específicos para armaduras 
        physical_resistance INTEGER DEFAULT 0,  -- Nova: resistência física
        magical_resistance INTEGER DEFAULT 0,   -- Nova: resistência mágica
        dexterity_penalty INTEGER DEFAULT 0,    -- Nova: penalidade de destreza
        armor_class TEXT CHECK(armor_class IN ('light', 'medium', 'heavy')),
        strength_requirement INTEGER,
        
        -- Campos para escudos (mantém armor_bonus, aumenta a CA)
        armor_bonus INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL, -- Refere-se ao ID do item base na tabela 'items'
        quantity INTEGER DEFAULT 1,
        enhancement_level INTEGER DEFAULT 0,
        enhancement_type TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )''')

    # Tabela de slots de equipamento (AGORA REFERENCIA character_inventory.id)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_equipment (
        character_id INTEGER NOT NULL PRIMARY KEY,
        main_hand_inventory_id INTEGER DEFAULT NULL,
        off_hand_inventory_id INTEGER DEFAULT NULL,
        head_inventory_id INTEGER DEFAULT NULL,
        body_inventory_id INTEGER DEFAULT NULL,
        hands_inventory_id INTEGER DEFAULT NULL,
        feet_inventory_id INTEGER DEFAULT NULL,
        ring1_inventory_id INTEGER DEFAULT NULL,
        ring2_inventory_id INTEGER DEFAULT NULL,
        amulet_inventory_id INTEGER DEFAULT NULL,
        FOREIGN KEY (character_id) REFERENCES characters(id)  ON DELETE CASCADE,
        FOREIGN KEY (main_hand_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (off_hand_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (head_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (body_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (hands_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (feet_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (ring1_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (ring2_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL,
        FOREIGN KEY (amulet_inventory_id) REFERENCES character_inventory(id) ON DELETE SET NULL
    )''')

    # Tabela de classes (SEM ALTERAÇÕES)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        hit_dice TEXT NOT NULL,
        mana_dice TEXT NOT NULL,  
        base_ac INTEGER NOT NULL,
        description TEXT,
        starting_weapon_id INTEGER DEFAULT NULL,
        starting_armor_id INTEGER DEFAULT NULL,
        FOREIGN KEY (starting_weapon_id) REFERENCES items(id),
        FOREIGN KEY (starting_armor_id) REFERENCES items(id)
    )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            level INTEGER NOT NULL,
            hp INTEGER,
            ac INTEGER,
            attack_bonus INTEGER,
            damage_dice TEXT NOT NULL,
            exp_reward INTEGER NOT NULL,
            gold_dice TEXT NOT NULL,
            strength INTEGER DEFAULT 10,
            dexterity INTEGER DEFAULT 10,
            constitution INTEGER DEFAULT 10,
            intelligence INTEGER DEFAULT 10,
            wisdom INTEGER DEFAULT 10,
            charisma INTEGER DEFAULT 10,
            main_attack_attribute TEXT NOT NULL DEFAULT 'strength',
            attack_type TEXT NOT NULL,
            physical_resistance INTEGER DEFAULT 1,
            magical_resistance INTEGER DEFAULT 1
        )''')
    conn.commit()


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS name_components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        culture TEXT NOT NULL,
        gender TEXT, -- 'male', 'female', 'unisex'
        component_type TEXT NOT NULL CHECK(component_type IN ('prefix', 'middle', 'suffix')),
        value TEXT NOT NULL,
        weight INTEGER DEFAULT 1,
        is_required BOOLEAN DEFAULT 0,
        UNIQUE(culture, gender, component_type, value) -- Garante unicidade
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        attribute TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_skills (
        character_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        level INTEGER DEFAULT 0,
        current_xp INTEGER DEFAULT 0,
        max_xp INTEGER DEFAULT 50, -- XP necessário para o próximo nível
        PRIMARY KEY (character_id, skill_id), -- Adicionando PRIMARY KEY composta
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backgrounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS background_skills (
        background_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        starting_level INTEGER DEFAULT 1,
        PRIMARY KEY (background_id, skill_id),
        FOREIGN KEY (background_id) REFERENCES backgrounds(id),
        FOREIGN KEY (skill_id) REFERENCES skills(id)
    )''')

    conn.commit()
    print("Tabelas criadas ou já existentes.")

def insert_race(conn, name, str_bonus, dex_bonus, con_bonus, int_bonus, wis_bonus, cha_bonus, description):
    """Insere uma nova raça se não existir."""
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO races (
            name, strength_bonus, dexterity_bonus, constitution_bonus, 
            intelligence_bonus, wisdom_bonus, charisma_bonus, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, str_bonus, dex_bonus, con_bonus, int_bonus, wis_bonus, cha_bonus, description))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Raça '{name}' adicionada com sucesso!")
    except sqlite3.IntegrityError:
        print(f"Raça '{name}' já existe. Pulando...")
    except sqlite3.Error as e:
        print(f"Erro ao inserir raça '{name}': {e}")

def insert_class(conn, name, hit_dice, mana_dice, base_ac, description, 
                starting_weapon_id=None, starting_armor_id=None):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO classes (
            name, hit_dice, mana_dice, base_ac, description, 
            starting_weapon_id, starting_armor_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, hit_dice, mana_dice, base_ac, description, 
              starting_weapon_id, starting_armor_id))
        
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Classe '{name}' adicionada com sucesso!")
    except sqlite3.IntegrityError:
        print(f"Classe '{name}' já existe. Pulando...")
    except sqlite3.Error as e:
        print(f"Erro ao inserir classe '{name}': {e}")

def insert_monster(conn, monster):
    """Insere um monstro na tabela com os novos campos de resistência."""
    cursor = conn.cursor()
    try:
        # A instrução SQL foi atualizada para incluir os novos campos
        cursor.execute('''
        INSERT OR IGNORE INTO monsters (
            name, level, hp, ac, attack_bonus, damage_dice, 
            exp_reward, gold_dice, strength, dexterity, constitution,
            intelligence, wisdom, charisma, main_attack_attribute, 
            attack_type, physical_resistance, magical_resistance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            monster.name,
            monster.level,
            monster.hp_max,
            monster.ac,
            monster.attack_bonus,
            monster.damage_dice,
            monster.exp_reward,
            monster.gold_dice,
            monster.strength,
            monster.dexterity,
            monster.constitution,
            monster.intelligence,
            monster.wisdom,
            monster.charisma,
            monster.main_attack_attribute,
            monster.attack_type,
            monster.physical_resistance,
            monster.magical_resistance
        ))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Monstro '{monster.name}' inserido com sucesso!")
    except sqlite3.IntegrityError:
        print(f"Monstro '{monster.name}' já existe. Pulando...")
    except sqlite3.Error as e:
        print(f"Erro ao inserir monstro '{monster.name}': {e}")

def insert_component(conn, culture, gender, component_type, value, 
                     weight=1, is_required=0):
    """Insere um novo componente de nome na tabela com validações."""
    cursor = conn.cursor()
    
    # Validação de tipos permitidos
    valid_types = ['prefix', 'middle', 'suffix']
    if component_type not in valid_types:
        print(f"Tipo de componente inválido: {component_type}. Use: {', '.join(valid_types)}")
        return False
    
    try:
        # Verifica se já existe (usando UNIQUE constraint na tabela)
        cursor.execute('''
        INSERT OR IGNORE INTO name_components (
            culture, gender, component_type, value, weight, is_required
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (culture, gender, component_type, value, weight, is_required))
        
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Componente '{value}' adicionado com sucesso!")
            return True
        else:
            print(f"Componente '{value}' já existe para {culture}/{component_type}. Pulando...")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao inserir componente '{value}': {e}")
        return False

def insert_item(conn, item_data):
    cursor = conn.cursor()
    
    # Campos obrigatórios
    item_id = item_data.get('id')
    item_name = item_data.get('name')
    item_category = item_data.get('category')
    equip_slot = item_data.get('equip_slot')
    item_level = item_data.get('level', 1)

    if None in (item_id, item_name, item_category):
        print("Erro: ID, nome e categoria são obrigatórios.")
        return None

    # Verificar se item já existe
    cursor.execute("SELECT id FROM items WHERE id = ? OR name = ?", (item_id, item_name))
    if cursor.fetchone():
        print(f"Item '{item_name}' (ID: {item_id}) já existe. Pulando.")
        return item_id
    
    # Montar query com campos dinâmicos
    columns = ['id', 'name', 'category', 'equip_slot', 'level']
    values = [item_id, item_name, item_category, equip_slot, item_level]
    
    # Campos comuns
    common_fields = ['description', 'weight', 'value', 'subcategory']
    for field in common_fields:
        if field in item_data:
            columns.append(field)
            values.append(item_data[field])
    
    # Campos específicos para armas
    if item_category == 'weapon':
        weapon_fields = [
            'damage_dice', 'damage_type', 'weapon_type', 
            'main_attribute', 'two_handed'
        ]
        for field in weapon_fields:
            if field in item_data:
                columns.append(field)
                # Converter boolean para int
                if field == 'two_handed':
                    values.append(1 if item_data[field] else 0)
                else:
                    values.append(item_data[field])
    
    # Campos específicos para armaduras
    elif item_category == 'armor':
        armor_fields = [
            'physical_resistance', 'magical_resistance', 'dexterity_penalty',
            'armor_class', 'strength_requirement'
        ]
        for field in armor_fields:
            if field in item_data:
                columns.append(field)
                values.append(item_data[field])
    
    # Campos específicos para escudos
    elif item_category == 'shield':
        shield_fields = ['armor_bonus', 'strength_requirement']
        for field in shield_fields:
            if field in item_data:
                columns.append(field)
                values.append(item_data[field])
    
    # Executar inserção
    placeholders = ', '.join(['?'] * len(columns))
    column_names = ', '.join(columns)
    
    try:
        cursor.execute(f"INSERT INTO items ({column_names}) VALUES ({placeholders})", values)
        conn.commit()
        print(f"Item '{item_name}' (ID: {item_id}) adicionado!")
        return item_id
    except sqlite3.Error as e:
        print(f"Erro ao inserir item '{item_name}': {e}")
        return None

        
def insert_skills(conn, name, description, attribute):
    """Insere uma nova perícia se não existir."""
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO skills (name, description, attribute)
        VALUES (?, ?, ?)
        ''', (name, description, attribute))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Perícia '{name}' adicionada com sucesso!")
    except sqlite3.IntegrityError:
        print(f"Perícia '{name}' já existe. Pulando...")
    except sqlite3.Error as e:
        print(f"Erro ao inserir perícia '{name}': {e}")

def insert_background(conn, name, description):
    """Insere um novo antecedente se não existir."""
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO backgrounds (name, description)
        VALUES (?, ?)
        ''', (name, description))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Antecedente '{name}' adicionado com sucesso!")
            return cursor.lastrowid # Retorna o ID do antecedente inserido
    except sqlite3.IntegrityError:
        print(f"Antecedente '{name}' já existe. Pulando...")
        cursor.execute("SELECT id FROM backgrounds WHERE name = ?", (name,))
        return cursor.fetchone()[0] # Retorna o ID do antecedente existente
    except sqlite3.Error as e:
        print(f"Erro ao inserir antecedente '{name}': {e}")
    return None

def add_background_starting_skill(conn, background_id, skill_name, starting_level=1):
    """Adiciona uma perícia inicial a um antecedente."""
    cursor = conn.cursor()
    try:
        # Primeiro, obtenha o skill_id pelo nome da perícia
        cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
        skill_result = cursor.fetchone()
        if not skill_result:
            print(f"Erro: Perícia '{skill_name}' não encontrada.")
            return

        skill_id = skill_result[0]

        cursor.execute('''
        INSERT INTO background_skills (background_id, skill_id, starting_level)
        VALUES (?, ?, ?)
        ''', (background_id, skill_id, starting_level))
        conn.commit()
        print(f"Perícia '{skill_name}' adicionada ao antecedente com ID {background_id} no nível {starting_level}.")
    except sqlite3.IntegrityError:
        print(f"Perícia '{skill_name}' já está associada ao antecedente com ID {background_id}. Pulando...")
    except sqlite3.Error as e:
        print(f"Erro ao adicionar perícia inicial: {e}")
    
def populate_initial_data():
    conn = create_connection(DB_PATH)

    # --------------------------------
    drop_tables(conn)     # Remove tabelas existentes
    create_tables(conn)   # Cria novas tabelas
    # --------------------------------

    # Popule passando as funções de inserção:
    from data_tuples import (
        populate_races, 
        populate_monsters,
        populate_components,
        populate_armors_and_shields,
        populate_weapons,
        populate_classes,
        populate_skills,
        populate_backgrounds
    )

    print("\nPopulando raças...")
    populate_races(conn, insert_race)  # Passe insert_race como argumento

    print("\nPopulando monstros...")
    populate_monsters(conn, insert_monster, Monster)  # Passe insert_monster

    print("\nPopulando componentes...")
    populate_components(conn, insert_component)  # Passe insert_component

    print("\nPopulando itens...")
    populate_weapons(conn, insert_item)  # Passe insert_item
    populate_armors_and_shields(conn, insert_item)  # Passe insert_item

    print("\nPopulando classes...")
    populate_classes(conn, insert_class)  # Passe insert_class

    print("\nPopulando Skills(pericias)...")
    populate_skills(conn, insert_skills)  # Passe insert_skills
    
    print("\nPopulando Antecedentes (Backgrounds)...")
    populate_backgrounds(conn, insert_background, add_background_starting_skill)

if __name__ == "__main__":
    populate_initial_data()

conn = create_connection(DB_PATH)