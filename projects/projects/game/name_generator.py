import sqlite3
import random
from pathlib import Path

class NameGenerator:
    def __init__(self, db_path=None):
        # Define o caminho padrão para o banco de dados na pasta data
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            self.db_path = base_dir / 'data' / 'database.db'
        else:
            self.db_path = db_path
            
        self.conn = None
        print(f"Usando banco de dados: {self.db_path}")  # Para depuração
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            # Habilita o acesso por nome de coluna
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close_connection(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Para suportar o protocolo 'with'"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que a conexão será fechada ao sair do bloco with"""
        self.close_connection()
        return False  # Não suprime exceções

    def listar_culturas(self):
        """Retorna todas as culturas disponíveis no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT culture FROM name_components")
            culturas = [row['culture'] for row in cursor.fetchall()]
            return culturas
        except sqlite3.Error as e:
            print(f"Erro ao buscar culturas: {e}")
            return ['medieval']  # Fallback padrão
        finally:
            # Não fechar a conexão aqui! 
            pass
        
    def get_components(self, gender, component_type, culture='medieval'):
        """Busca componentes priorizando gênero, depois cultura"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT value, weight, is_required 
            FROM name_components 
            WHERE gender IN (?, 'unisex') 
            AND component_type = ?
            AND culture = ?
            '''
            cursor.execute(query, (gender, component_type, culture))
            results = cursor.fetchall()
            
            # Separa obrigatórios e opcionais
            required = []
            optional = []
            
            for row in results:
                if row['is_required']:
                    required.append((row['value'], row['weight']))
                else:
                    optional.append((row['value'], row['weight']))
            
            return required, optional
    
        except sqlite3.Error as e:
            print(f"Erro no banco de dados: {e}")
            return [], []  # Retorna listas vazias para evitar quebra
        finally:
            # Não fechar a conexão aqui!
            pass

    def select_component(self, components):
        """Seleciona um componente considerando seu peso"""
        if not components:
            return ""
        
        weighted_list = []
        for value, weight in components:
            weighted_list.extend([value] * weight)
        
        return random.choice(weighted_list)
    
    def insert_component(conn, culture, gender, component_type, value, 
                        weight=1, is_required=0):
        """Insere um novo componente de nome na tabela com validações"""
        cursor = conn.cursor()
        
        # Validação de tipos permitidos
        valid_types = ['prefix', 'middle', 'suffix', 'title']
        if component_type not in valid_types:
            print(f"Tipo de componente inválido: {component_type}. Use: {', '.join(valid_types)}")
            return False
        
        try:
            # Verifica se já existe (usando a ordem correta)
            query = '''
            SELECT 1 FROM name_components 
            WHERE culture = ? AND gender IS ? AND component_type = ? AND value = ?
            '''
            cursor.execute(query, (culture, gender, component_type, value))
            
            if cursor.fetchone():
                print(f"Componente '{value}' já existe para {culture}/{component_type}. Pulando...")
                return False
            
            # Insere novo componente
            cursor.execute('''
            INSERT INTO name_components (
                culture, gender, component_type, value, weight, is_required
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (culture, gender, component_type, value, weight, is_required))
            
            conn.commit()
            print(f"Componente '{value}' adicionado com sucesso!")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir componente: {e}")
            return False

    def gerar_nome_base(self, genero='masc', cultura='medieval'):
        """Gera apenas o nome base (sem título)"""
        parts = {
            'prefix': "",
            'middle': "",
            'suffix': ""
        }
        
        try:
            for part in parts.keys():
                required, optional = self.get_components(genero, part, cultura)
                
                if required:
                    parts[part] = self.select_component(required)
                
                if optional and random.random() > 0.5:
                    parts[part] = self.select_component(optional)
        
        except Exception as e:
            print(f"Erro ao gerar nome base: {e}")
            fallback_names = {
                'masc': ['Geralt', 'Aragorn', 'Conan', 'Arthur'],
                'fem': ['Yennefer', 'Galadriel', 'Ciri', 'Guinevere'],
                'neutro': ['Robin', 'Taylor', 'Alex', 'Jordan']
            }
            return random.choice(fallback_names.get(genero, fallback_names['neutro']))
        
        name_parts = [parts['prefix'], parts['middle'], parts['suffix']]
        core_name = ' '.join(filter(None, name_parts))
        return ' '.join(core_name.split())  # Remove espaços extras
    
    def gerar_titulo(self, genero='masc', cultura='medieval'):
        """Gera apenas o título"""
        try:
            required, optional = self.get_components(genero, 'title', cultura)
            titulo = ""
            
            # Componente obrigatório
            if required:
                titulo = self.select_component(required)
            
            # Componente opcional (50% de chance)
            if optional and random.random() > 0.5:
                if titulo:
                    # Adiciona um segundo título
                    titulo += " " + self.select_component(optional)
                else:
                    titulo = self.select_component(optional)
            
            return titulo
        
        except Exception as e:
            print(f"Erro ao gerar título: {e}")
            # Fallback para títulos
            fallback_titles = {
                'medieval': ['o Bravo', 'o Sábio', 'o Magnífico'],
                'nórdica': ['o Destemido', 'o Implacável', 'Lobo do Inverno'],
                'élfica': ['da Floresta', 'da Lua Prateada', 'das Estrelas'],
                'indian': ['o Grande', 'o Sábio', 'o Valente'],
                'japanese': ['o Samurai', 'o Honorável', 'o Sábio']
            }
            # Usar fallback específico para a cultura ou medieval como padrão
            return random.choice(fallback_titles.get(cultura, fallback_titles['medieval']))
    
    # Métodos de conveniência simplificados
    def gerar_nome(self, genero='masc', cultura='medieval'):
        return self.generate_name(genero, cultura)
    
    def gerar_nome_masculino(self, cultura='medieval'):
        return self.generate_name('masc', cultura)
    
    def gerar_nome_feminino(self, cultura='medieval'):
        return self.generate_name('fem', cultura)
    
    def gerar_nome_neutro(self, cultura='medieval'):
        return self.generate_name('neutro', cultura)
    
class UniversalNameGenerator:
    def __init__(self, db_path='rpg_data.db'):
        self.db_path = db_path
        self.conn = None
    
    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_components(self, gender, component_type):
        """Busca componentes de TODAS as culturas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT value, weight, is_required 
        FROM name_components 
        WHERE gender = ? OR gender IS NULL
          AND component_type = ?
        '''
        cursor.execute(query, (gender, component_type))
        results = cursor.fetchall()
        
        required = []
        optional = []
        for value, weight, is_required in results:
            if is_required:
                required.append((value, weight))
            else:
                optional.append((value, weight))
        
        return required, optional
    
    def select_component(self, components):
        if not components:
            return ""
        
        weighted_list = []
        for value, weight in components:
            weighted_list.extend([value] * weight)
        
        return random.choice(weighted_list)
    
    def generate_name(self, gender='masc'):
        parts = {
            'prefix': "",
            'middle': "",
            'suffix': "",
            'title': ""
        }
        
        try:
            for part in parts.keys():
                required, optional = self.get_components(gender, part)
                
                if required:
                    parts[part] = self.select_component(required)
                
                if optional and random.random() > 0.5:
                    parts[part] = self.select_component(optional)
        
        except Exception as e:
            print(f"Erro ao gerar nome: {e}")
            return f"{gender.capitalize()}_{random.randint(1, 100)}"
        
        finally:
            self.close_connection()
        
        # Monta o nome combinando partes de diferentes culturas
        name_parts = [parts['prefix'], parts['middle'], parts['suffix']]
        core_name = ' '.join(filter(None, name_parts))
        
        if parts['title'] and random.random() > 0.3:  # 70% de chance de título
            return f"{core_name} {parts['title']}"
        return core_name
    
    def gerar_nome_masculino(self):
        return self.generate_name('masc')
    
    def gerar_nome_feminino(self):
        return self.generate_name('fem')
    
    def gerar_nome_neutro(self):
        return self.generate_name('neutro')

