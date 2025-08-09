import sqlite3
from .character import Character # Importa Character para uso em load_characters
from game.config import get_db_path
DB_PATH = get_db_path()

def save_character(conn, character):
    """
    Salva ou atualiza os dados principais do personagem na tabela 'characters'.
    Inclui o campo 'permadeath'.
    """
    cursor = conn.cursor()
    
    try:
        # 1. Salva/Atualiza os dados da tabela 'characters'
        char_data = (
            character.name, character.race, character.char_class,
            character.background,
            character.level, character.exp, character.exp_max,
            character.hp, character.hp_max, character.mana, character.mana_max,
            character.ac, character.gold, character.strength, character.dexterity,
            character.constitution, character.intelligence, character.wisdom,
            character.charisma, character.difficulty, character.permadeath # Adicionado permadeath aqui
        )
        
        if character.id:
            cursor.execute('''
                UPDATE characters SET
                    name = ?, race = ?, class = ?, background = ?,
                    level = ?, exp = ?, exp_max = ?,
                    hp = ?, hp_max = ?, mana = ?, mana_max = ?, ac = ?, gold = ?, 
                    strength = ?, dexterity = ?, constitution = ?, intelligence = ?, 
                    wisdom = ?, charisma = ?, difficulty = ?, permadeath = ?
                WHERE id = ?
            ''', char_data + (character.id,))
        else:
            cursor.execute('''
                INSERT INTO characters (
                    name, race, class, background,
                    level, exp, exp_max, 
                    hp, hp_max, mana, mana_max, ac, gold, 
                    strength, dexterity, constitution, intelligence, wisdom, charisma, difficulty, permadeath
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', char_data)
            character.id = cursor.lastrowid

        conn.commit()
        print(f"Personagem '{character.name}' salvo com sucesso no banco de dados. ID: {character.id}")
        return True

    except sqlite3.Error as e: # Captura exceções específicas de SQLite
        print(f"Erro no banco de dados ao salvar personagem '{character.name}': {e}")
        conn.rollback()
        return False
    except Exception as e: # Captura outras exceções gerais
        print(f"Erro inesperado ao salvar personagem '{character.name}': {e}")
        conn.rollback()
        return False
    
def load_characters(conn):
    """
    Carrega todos os personagens do banco de dados e os retorna como objetos Character.
    Garanti que os status (como AC) sejam recalculados após o carregamento.
    """
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters')
    characters = []
    
    columns = [description[0] for description in cursor.description]
    
    for row in cursor.fetchall():
        char_data = dict(zip(columns, row))
        
        # Corrige o campo reservado 'class' → 'char_class'
        char_data["char_class"] = char_data.get("class", "Unknown") 
        
        char_data["background"] = char_data.get("background", None) 

        char_data["difficulty"] = char_data.get("difficulty", "Desafio Justo")

        # Adiciona a recuperação do valor de permadeath
        char_data["permadeath"] = char_data.get("permadeath", 0)

        if "class" in char_data:
            del char_data["class"]
        
        char = Character(conn, **char_data)
        characters.append(char)
        
    return characters


def delete_character(conn, character_id):
    """Exclui um personagem e reseta a sequência de IDs se necessário"""
    cursor = conn.cursor()
    try:
        # 1. Exclui o personagem
        cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))
        deleted_count = cursor.rowcount # <-- Armazena o número de linhas afetadas pelo DELETE
        
        # Se nenhuma linha foi excluída, já sabemos que falhou.
        if deleted_count == 0:
            print(f"Aviso: Nenhuma linha encontrada com o ID {character_id} para deletar.")
            conn.rollback()
            return False

        # 2. Verifica se esta foi a última linha da tabela
        cursor.execute("SELECT COUNT(*) FROM characters")
        count = cursor.fetchone()[0]
        
        # 3. Se a tabela estiver vazia, reseta a sequência de autoincremento
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'characters'")
            print("Sequência de IDs resetada para personagens.")
        
        conn.commit()
        return True # <-- Retorna True se a contagem foi maior que zero
        
    except sqlite3.Error as e:
        print(f"Erro ao deletar personagem: {e}")
        conn.rollback()
        return False
    
def rename_character(conn, character_id, new_name):
    """Renomeia um personagem no banco de dados"""
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE characters SET name = ? WHERE id = ?", (new_name, character_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Personagem ID {character_id} renomeado para '{new_name}'.")
            return True
        else:
            print(f"Nenhum personagem encontrado com ID {character_id} para renomear.")
            return False
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao renomear personagem com ID {character_id}: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Erro inesperado ao renomear personagem com ID {character_id}: {e}")
        conn.rollback()
        return False