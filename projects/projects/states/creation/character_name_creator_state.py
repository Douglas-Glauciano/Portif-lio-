import random
import time
import sqlite3
from game.config import culturas_comuns, culturas_fantasiosas
from game.name_generator import NameGenerator

class CharacterNameCreator:
    def __init__(self, cultura_padrao='medieval'):
        self.cultura_padrao = cultura_padrao
        self.generator = NameGenerator()
        self.generos = {
            '1': 'masc',
            '2': 'fem',
            '3': 'neutro'
        }
        self.genero = None
        self.cultura_selecionada = None
        self.culturas_disponiveis = []
        self.culturas_comuns_filtradas = []
        self.culturas_fantasiosas_filtradas = []

        self.setup_cultures()
        

    def get_components(self, gender, component_type, culture='medieval'):
        """Busca componentes priorizando gênero, depois cultura"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Atualizado para tratar NULL como unisex
            query = '''
            SELECT value, weight, is_required 
            FROM name_components 
            WHERE (gender = ? OR gender = 'unisex' OR gender IS NULL)
            AND component_type = ?
            AND LOWER(culture) = LOWER(?)
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

    def setup_cultures(self):
        """Configura as listas de culturas disponíveis"""
        self.culturas_disponiveis = self.generator.listar_culturas()
        
        if not self.culturas_disponiveis:
            print("Nenhuma cultura encontrada no banco de dados. Usando padrão.")
            self.culturas_disponiveis = ['medieval']
        
        # Normalizar nomes para minúsculas para comparação
        culturas_disponiveis_lower = [c.lower() for c in self.culturas_disponiveis]
        
        def encontrar_nome_original(nome_base):
            for c in self.culturas_disponiveis:
                if c.lower() == nome_base.lower():
                    return c
            return nome_base
        
        # Filtrar e manter a capitalização original
        self.culturas_comuns_filtradas = []
        for c in culturas_comuns:
            if c.lower() in culturas_disponiveis_lower:
                self.culturas_comuns_filtradas.append(encontrar_nome_original(c))
        
        self.culturas_fantasiosas_filtradas = []
        for c in culturas_fantasiosas:
            if c.lower() in culturas_disponiveis_lower:
                self.culturas_fantasiosas_filtradas.append(encontrar_nome_original(c))
        
        # Adicionar culturas não classificadas como fantasiosas
        for c in self.culturas_disponiveis:
            c_lower = c.lower()
            if (c_lower not in [c2.lower() for c2 in self.culturas_comuns_filtradas] and 
                c_lower not in [c2.lower() for c2 in self.culturas_fantasiosas_filtradas]):
                self.culturas_fantasiosas_filtradas.append(c)
    
    def select_gender(self):
        """Seleciona o gênero do personagem"""
        while True:
            print("\n" + "="*50)
            print("ESCOLHA O GÊNERO DO PERSONAGEM")
            print("="*50)
            print("1. Masculino\n2. Feminino\n3. Não binário/Outro")
            print("4. Voltar ao menu principal")
            print("-"*50)
            
            escolha = input("Escolha (1/2/3/4): ").strip()
            
            if escolha == '4':
                return False  # Indica que deve voltar
            
            self.genero = self.generos.get(escolha)
            if self.genero:
                return True
            
            print("Opção inválida! Tente novamente.")
    
    def select_culture(self):
        """Seleciona a cultura do nome"""
        while True:
            print("\n" + "="*50)
            print("ESCOLHA A CULTURA DO NOME")
            print("="*50)
            print(f"1. Usar cultura padrão ({self.cultura_padrao})")
            print("2. Escolher uma cultura comum")
            print("3. Escolher uma cultura fantástica")
            print("4. Aleatório (qualquer cultura)")
            print("5. Voltar (escolher outro gênero)")
            print("6. Voltar ao menu principal")
            print("-"*50)
            
            escolha_cultura = input("Escolha (1-6): ").strip()
            
            if escolha_cultura == '1':
                self.cultura_selecionada = self.cultura_padrao
                return True
            elif escolha_cultura == '2':
                return self.handle_common_cultures()
            elif escolha_cultura == '3':
                return self.handle_fantasy_cultures()
            elif escolha_cultura == '4':
                self.cultura_selecionada = None  # Indicador de cultura aleatória
                return True
            elif escolha_cultura == '5':
                return False  # Voltar para seleção de gênero
            elif escolha_cultura == '6':
                return None  # Voltar ao menu principal
            else:
                print("Opção inválida! Tente novamente.")
    
    def handle_common_cultures(self):
        """Lida com a seleção de culturas comuns"""
        if not self.culturas_comuns_filtradas:
            print("\nNão há culturas comuns disponíveis.")
            return False
            
        print("\nCULTURAS COMUNS:")
        for idx, cultura in enumerate(self.culturas_comuns_filtradas, 1):
            print(f"{idx}. {cultura}")
        
        escolha_num = input("\nEscolha o número da cultura: ").strip()
        try:
            idx = int(escolha_num) - 1
            if 0 <= idx < len(self.culturas_comuns_filtradas):
                self.cultura_selecionada = self.culturas_comuns_filtradas[idx]
                return True
            print("Número fora do intervalo válido!")
        except ValueError:
            print("Entrada inválida! Digite um número.")
        return False
    
    def handle_fantasy_cultures(self):
        """Lida com a seleção de culturas fantasiosas"""
        if not self.culturas_fantasiosas_filtradas:
            print("\nNão há culturas fantasiosas disponíveis.")
            return False
            
        print("\nCULTURAS FANTÁSTICAS:")
        known_fantasy = self.culturas_fantasiosas_filtradas[:len(culturas_fantasiosas)]
        other_fantasy = self.culturas_fantasiosas_filtradas[len(culturas_fantasiosas):]
        
        for idx, cultura in enumerate(known_fantasy, 1):
            print(f"{idx}. {cultura}")
        
        if other_fantasy:
            print("-"*30)
            print("OUTRAS CULTURAS FANTÁSTICAS:")
            start_idx = len(known_fantasy) + 1
            for i, cultura in enumerate(other_fantasy, start_idx):
                print(f"{i}. {cultura}")
        
        escolha_num = input("\nEscolha o número da cultura: ").strip()
        try:
            idx = int(escolha_num) - 1
            if 0 <= idx < len(self.culturas_fantasiosas_filtradas):
                self.cultura_selecionada = self.culturas_fantasiosas_filtradas[idx]
                return True
            print("Número fora do intervalo válido!")
        except ValueError:
            print("Entrada inválida! Digite um número.")
        return False
    
    def select_name(self):
        """Seleciona o nome do personagem (SEM TÍTULOS)"""
        while True:
            print("\n" + "="*50)
            print("ESCOLHA O NOME DO PERSONAGEM")
            print("="*50)
            entrada = input("Digite seu nome ou ENTER para gerar: ").strip()
            
            if entrada:
                return entrada  # Aceita diretamente o nome digitado
            
            # Determinar cultura para esta geração
            if self.cultura_selecionada is None:
                cultura_ativa = random.choice(self.culturas_disponiveis)
            else:
                cultura_ativa = self.cultura_selecionada
            
            # Gerar apenas o nome base
            try:
                nome_base = self.generator.gerar_nome_base(self.genero, cultura_ativa)
                print(f"\nNome gerado ({cultura_ativa}): {nome_base}")
            except Exception as e:
                print(f"\nErro ao gerar nome: {e}")
                nome_base = "Nome Desconhecido"
            
            # Opções simplificadas (sem títulos)
            print("\n1. Usar este nome")
            print("2. Gerar outro nome")
            print("3. Digitar nome manualmente")
            print("4. Voltar (escolher cultura/gênero)")
            
            escolha = input("\nEscolha: ").strip()
            
            if escolha == '1':
                return nome_base
            elif escolha == '2':
                continue
            elif escolha == '3':
                novo_nome = input("Digite o nome: ").strip()
                if novo_nome:
                    return novo_nome
                print("Nome inválido. Tente novamente.")
            elif escolha == '4':
                return None  # Voltar
            else:
                print("Opção inválida! Tente novamente.")
                time.sleep(1)
    
    def run(self):
        """Executa o fluxo completo de criação de nome (SEM TÍTULOS)"""
        # Selecionar gênero
        if not self.select_gender():
            return None
        
        # Selecionar cultura
        while True:
            result = self.select_culture()
            if result is None:  # Voltar ao menu principal
                return None
            elif result:  # Cultura selecionada com sucesso
                break
            # Caso contrário, continua no loop
        
        # Selecionar nome
        while True:
            nome = self.select_name()
            if nome is not None:
                return nome
            # Se voltar, reinicia o processo
            return self.run()