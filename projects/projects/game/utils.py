import random
import re
import os
import json
import time
from .config import GAME_SETTINGS, DEFAULT_SETTINGS, SETTINGS_FILE, save_settings # Importa diretamente

def roll_dice(dice_str):
    """Rola dados no formato 'XdY+Z'"""
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str)
    if not match:
        print(f"[WARN] Formato de dado inválido: {dice_str}. Retornando 0.")
        return 0
        
    num = int(match.group(1))
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    total = sum(random.randint(1, sides) for _ in range(num)) + modifier
    return total

def roll_d6():
    """Rola um dado de 6 faces"""
    return random.randint(1, 6)

def roll_attribute():
    """Rola um atributo usando o sistema 4d6 (descarta o menor)"""
    rolls = [roll_d6() for _ in range(4)]
    rolls.sort(reverse=True)
    return sum(rolls[:3])  # Soma os 3 maiores valores

def modifier(score):
    """Calcula modificador de atributo"""
    return (score - 10) // 2

def roll_dice_max(dice_str):
    """Retorna o valor máximo possível para um dado"""
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str)
    if not match:
        print(f"[WARN] Formato de dado inválido para max: {dice_str}. Retornando 0.")
        return 0
        
    num = int(match.group(1))
    sides = int(match.group(2))
    modifier_val = int(match.group(3)) if match.group(3) else 0 # Renomeado para evitar conflito
    
    return (num * sides) + modifier_val

def get_setting(key):
    """Obtém uma configuração do jogo"""
    # A variável GAME_SETTINGS já é carregada no config.py
    return GAME_SETTINGS.get(key, DEFAULT_SETTINGS.get(key))

# Funções save_settings e update_setting já estão em config.py e são importadas.
# Removê-las daqui para evitar duplicação.

def rows_to_dicts(cursor):
    """Converte os resultados de uma consulta SQL em dicionários"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_display_name(item):
    """Retorna o nome do item com informações de melhoria"""
    name = item['name']
    
    enhancement_level = item.get('enhancement_level', 0)
    enhancement_type = item.get('enhancement_type')
    
    if enhancement_level > 0:
        name += f" +{enhancement_level}"
    
    if enhancement_type:
        # Adiciona um emoji baseado no tipo de melhoria
        type_emojis = {
            'fire': '🔥',
            'ice': '❄️',
            'lightning': '⚡',
            'poison': '☠️',
            'holy': '✨',
            'sharp': '🔪',
            'durable': '🛡️',
            'lucky': '🍀',
            'normal': ''
        }
        emoji = type_emojis.get(enhancement_type, '')
        name += f" {emoji}"
    
    return name

def calculate_enhanced_value(item):
    """Calcula o valor aprimorado do item"""
    base_value = item.get('value', 0)
    enhancement_level = item.get('enhancement_level', 0)
    
    # Valor aumenta 50% por nível de melhoria
    return int(base_value * (1 + 0.5 * enhancement_level))

def calculate_enhanced_damage(item):
    """Calcula o dano aprimorado para armas"""
    base_dice = item.get('damage_dice', '1d4')
    enhancement_level = item.get('enhancement_level', 0)
    
    # Para armas: cada nível de aprimoramento adiciona +1 de dano fixo
    # e +1d2 nos níveis ímpares (1, 3, 5)
    bonus_dice = ""
    
    # Adiciona dados de dano extra para níveis ímpares
    for level in range(1, enhancement_level + 1):
        if level % 2 == 1:  # Níveis ímpares
            if bonus_dice:
                bonus_dice += f"+1d{2 * level}"
            else:
                bonus_dice = f"1d{2 * level}"
    
    # Combina o dano base com os bônus
    if bonus_dice:
        return f"{base_dice}+{bonus_dice}"
    
    return base_dice

def calculate_enhanced_resistances(item):
    """Calcula as resistências aprimoradas para armaduras."""
    phys_res = item.get('physical_resistance', 0)
    mag_res = item.get('magical_resistance', 0)
    enhancement_level = item.get('enhancement_level', 0)
    
    # Cada nível de aprimoramento aumenta ambas as resistências em 1
    return {
        'physical_resistance': phys_res + enhancement_level,
        'magical_resistance': mag_res + enhancement_level
    }

def calculate_enhanced_armor_bonus(item):
    """Calcula o bônus de armadura aprimorado para escudos"""
    base_bonus = item.get('armor_bonus', 0)
    enhancement_level = item.get('enhancement_level', 0)
    
    # Cada nível de aprimoramento adiciona +1 ao bônus de armadura
    return base_bonus + enhancement_level

def calculate_attack_bonus(item):
    """Calcula o bônus de ataque para armas aprimoradas"""
    enhancement_level = item.get('enhancement_level', 0)
    
    # Para armas: cada nível par de aprimoramento adiciona +1 de bônus de ataque
    attack_bonus = 0
    for level in range(1, enhancement_level + 1):
        if level % 2 == 0:  # Níveis pares
            attack_bonus += 1
    
    return attack_bonus

def can_enhance(item):
    """Verifica se um item pode ser melhorado"""
    return item.get('category') in ['weapon', 'armor', 'shield']

# game/utils.py
def is_weapon(item):
    return item.get('category') == 'weapon'

def is_armor(item):
    return item.get('category') == 'armor'

def is_shield(item):
    return item.get('category') == 'shield'

'''
def show_settings():
    """Menu de configurações do jogo"""
    from .interface import print_centered_menu
    from .menus import main_menu
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Obter velocidade atual
        current_speed = get_setting("text_speed")
        
        # Título com animação usando a velocidade atual
        animate_text(C_TITLE + "\n⚙️ CONFIGURAÇÕES")
        
        # Menu de opções
        menu_options = [
            ("⏩", f"1. Velocidade de texto: {current_speed}s", C_MINT),
            ("🔊", "2. Volume de som", C_BABY_BLUE),
            ("🎨", "3. Esquema de cores", C_LAVENDER),
            ("🔙", "4. Voltar", C_PINK)
        ]
        
        print_centered_menu(menu_options, border_color=C_PINK)
        
        choice = input(C_PROMPT + "\n✨ Escolha: " + Style.RESET_ALL).strip()
        
        if choice == '1':
            # Submenu de velocidade
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                animate_text(C_TITLE + "\n⏩ VELOCIDADE DE TEXTO")
                
                speed_options = [
                    ("🐇", "1. Rápido (0.01s)", C_MINT),
                    ("🚶", "2. Normal (0.03s)", C_BABY_BLUE),
                    ("🐢", "3. Lento (0.05s)", C_LAVENDER),
                    ("🎚️", "4. Personalizar", C_PEACH),
                    ("🔙", "5. Voltar", C_PINK)
                ]
                
                print_centered_menu(speed_options, border_color=C_MINT)
                
                speed_choice = input(C_PROMPT + "\n✨ Escolha: " + Style.RESET_ALL).strip()
                
                if speed_choice == "1":
                    update_setting("text_speed", 0.01)
                    animate_text(C_SUCCESS + "\n✅ Velocidade definida para RÁPIDO!")
                    time.sleep(1)
                    save_settings()
                elif speed_choice == "2":
                    update_setting("text_speed", 0.03)
                    animate_text(C_SUCCESS + "\n✅ Velocidade definida para NORMAL!")
                    time.sleep(1)
                    save_settings()
                elif speed_choice == "3":
                    update_setting("text_speed", 0.05)
                    animate_text(C_SUCCESS + "\n✅ Velocidade definida para LENTO!")
                    time.sleep(1)
                    save_settings()
                elif speed_choice == "4":
                    try:
                        new_speed = float(input(C_PROMPT + "Digite a nova velocidade (ex: 0.02): " + Style.RESET_ALL))
                        if new_speed > 0:
                            update_setting("text_speed", new_speed)
                            animate_text(C_SUCCESS + f"\n✅ Velocidade definida para {new_speed}s!")
                            save_settings()
                        else:
                            animate_text(C_WARN + "\n⚠️ A velocidade deve ser maior que 0!")
                        time.sleep(1.5)
                    except ValueError:
                        animate_text(C_WARN + "\n⚠️ Valor inválido! Use números (ex: 0.03).")
                        time.sleep(1.5)
                # Dentro do while True do submenu de velocidade:
                elif speed_choice == "5":
                    break  # Sai do submenu e volta ao menu principal
                else:
                    animate_text(C_WARN + "\n⚠️ Opção inválida!")
                    time.sleep(1)

        elif choice == '2':
            # Implementar lógica real aqui
            animate_text(C_WARN + "\n⚠️ Funcionalidade em desenvolvimento!")
            time.sleep(1)
        elif choice == '3':
            # Implementar lógica real aqui
            animate_text(C_WARN + "\n⚠️ Funcionalidade em desenvolvimento!")
            time.sleep(1)
        elif choice == '4':
            return  # Sai completamente do menu de configurações

def show_tutorial():
    """Tutorial completo baseado em D&D com design fofo"""
    sections = [
        {
            "title": "📚 INTRODUÇÃO AO SISTEMA D&D",
            "content": f"""
{C_TITLE}Como funciona o Rust Dice?{Style.RESET_ALL}

{C_BABY_BLUE}Rust Dice é baseado no sistema de Dungeons & Dragons (D&D),{Style.RESET_ALL}
{C_MINT}um famoso jogo de RPG de mesa. As principais mecânicas incluem:

{C_PINK}• Dados Poliédricos: {Style.RESET_ALL}d4, d6, d8, d10, d12 e d20
{C_PINK}• Atributos: {Style.RESET_ALL}Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma
{C_PINK}• Testes de Habilidade: {Style.RESET_ALL}Rolagens contra uma dificuldade (DC)
{C_PINK}• Combate por Turnos: {Style.RESET_ALL}Iniciativa, ataques e dano
{C_PINK}• Progressão de Nível: {Style.RESET_ALL}Ganho de habilidades e pontos de vida
"""
        },
        {
            "title": "🎲 ENTENDENDO OS DADOS",
            "content": f"""
{C_TITLE}O coração do sistema D&D{Style.RESET_ALL}

{C_BABY_BLUE}Os dados são usados para determinar quase tudo no jogo:
{Style.RESET_ALL}
{C_PINK}1. d20 (20 faces):{Style.RESET_ALL} 
   • Testes de habilidade
   • Ataques
   • Defesas
   • Exemplo: Rolar 1d20 + modificador

{C_PINK}2. Dados de dano:{Style.RESET_ALL}
   • d4, d6, d8, d10, d12
   • Determinam o dano das armas
   • Exemplo: Espada curta = 1d6 + Força

{C_PINK}3. Dados de vida:{Style.RESET_ALL}
   • Determinam PV ao subir de nível
   • Exemplo: Nível 2 = 1d8 + CON
"""
        },
        {
            "title": "💪 ATRIBUTOS E MODIFICADORES",
            "content": f"""
{C_TITLE}Seus pontos fortes e fracos{Style.RESET_ALL}

{C_BABY_BLUE}Os 6 atributos principais definem suas capacidades:{Style.RESET_ALL}

{C_PINK}• Força (FOR):{Style.RESET_ALL} 
   - Ataques corpo-a-corpo
   - Testes físicos brutos
   - Exemplo: Arrombar portas

{C_PINK}• Destreza (DES):{Style.RESET_ALL} 
   - Armadura (CA)
   - Ataques à distância
   - Exemplo: Escapar de armadilhas

{C_PINK}• Constituição (CON):{Style.RESET_ALL} 
   - Pontos de Vida (PV)
   - Resistência a venenos
   - Exemplo: Suportar ferimentos

{C_PINK}• Inteligência (INT):{Style.RESET_ALL} 
   - Conhecimento arcano
   - Lembrar informações
   - Exemplo: Decifrar feitiços

{C_PINK}• Sabedoria (SAB):{Style.RESET_ALL} 
   - Percepção
   - Intuição
   - Exemplo: Detectar mentiras

{C_PINK}• Carisma (CAR):{Style.RESET_ALL} 
   - Persuasão
   - Intimidação
   - Exemplo: Negociar preços

{C_MINT}Modificadores:{Style.RESET_ALL}
Valor  Mod
8-9:   -1
10-11: +0
12-13: +1
14-15: +2
16-17: +3
18-19: +4
20:    +5
"""
        },
        {
            "title": "⚔️ SISTEMA DE COMBATE",
            "content": f"""
{C_TITLE}Como as batalhas funcionam{Style.RESET_ALL}

{C_BABY_BLUE}1. Iniciativa:{Style.RESET_ALL}
   • Todos rolam 1d20 + DES
   • Ordem decrescente determina os turnos

{C_BABY_BLUE}2. Seu turno:{Style.RESET_ALL}
   • Ação principal (atacar, lançar feitiço)
   • Movimento
   • Ação bônus (se disponível)

{C_BABY_BLUE}3. Realizar um ataque:{Style.RESET_ALL}
   a. Rolar 1d20 + modificador de ataque
   b. Se ≥ CA do alvo, acerta!
   c. Role o dado de dano da arma + modificador

{C_BABY_BLUE}4. Dano e Morte:{Style.RESET_ALL}
   • Quando PV chegam a 0, você cai inconsciente
   • Testes de morte a cada turno (1d20)
   • 3 sucessos antes de 3 falhas = estável
   • 3 falhas = morte!
"""
        },
        {
            "title": "📈 PROGRESSÃO E XP",
            "content": f"""
{C_TITLE}Evoluindo seu personagem{Style.RESET_ALL}

{C_BABY_BLUE}Ganho de Experiência (XP):{Style.RESET_ALL}
• Derrotar monstros
• Completar objetivos
• Resolver situações criativamente

{C_BABY_BLUE}Subindo de Nível:{Style.RESET_ALL}
• Ao atingir XP necessário
• Ganha novos recursos da classe
• Aumenta pontos de vida
• Pode aprender novos feitiços

{C_BABY_BLUE}Exemplo de Progressão:{Style.RESET_ALL}
Nível  XP necessário
1     0
2     300
3     900
4     2700
5     6500
"""
        },
        {
            "title": "🏆 DICAS PARA INICIANTES",
            "content": f"""
{C_TITLE}Como ter sucesso em suas aventuras{Style.RESET_ALL}

{C_PINK}1. Conheça seu personagem:{Style.RESET_ALL}
   • Habilidades de classe
   • Fraquezas e forças

{C_PINK}2. Trabalhe em equipe:{Style.RESET_ALL}
   • Combine habilidades com colegas
   • Proteja os membros mais fracos

{C_PINK}3. Seja criativo:{Style.RESET_ALL}
   • Use o ambiente a seu favor
   • Nem tudo se resolve com combate

{C_PINK}4. Gerencie recursos:{Style.RESET_ALL}
   • Poções são limitadas
   • Feitiços têm usos por dia
   • Equipamentos podem quebrar

{C_PINK}5. Roleplay!:{Style.RESET_ALL}
   • Atue como seu personagem
   • Faça escolhas baseadas na personalidade
   • Divirta-se criando uma história épica!
"""
        }
    ]
    
    current_index = 0
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        section = sections[current_index]
        
        # Título animado
        animate_text(C_TITLE + "\n" + section["title"] + Style.RESET_ALL, delay=0.03)
        
        # Conteúdo
        print(section["content"])
        
        # Navegação
        nav_options = []
        if current_index > 0:
            nav_options.append(f"{C_PINK}1. Anterior{Style.RESET_ALL}")
        if current_index < len(sections) - 1:
            nav_options.append(f"{C_BABY_BLUE}2. Próximo{Style.RESET_ALL}")
        nav_options.append(f"{C_MINT}3. Voltar ao menu{Style.RESET_ALL}")
        
        # Criar tabela de navegação
        nav_table = PrettyTable()
        nav_table.header = False
        nav_table.border = False
        nav_table.horizontal_char = "─"
        nav_table.vertical_char = "│"
        nav_table.junction_char = "┼"
        
        for option in nav_options:
            nav_table.add_row([option])
        
        # Personalizar tabela
        nav_str = nav_table.get_string()
        nav_str = nav_str.replace('─', C_LAVENDER + '─' + Style.RESET_ALL)
        nav_str = nav_str.replace('│', C_LAVENDER + '│' + Style.RESET_ALL)
        nav_str = nav_str.replace('┼', C_LAVENDER + '┼' + Style.RESET_ALL)
        
        print("\n" + nav_str)
        
        choice = input(C_PROMPT + "\n🌸 Escolha: " + Style.RESET_ALL).strip()
        
        if choice == "1" and current_index > 0:
            current_index -= 1
        elif choice == "2" and current_index < len(sections) - 1:
            current_index += 1
        elif choice == "3":
            return
        else:
            animate_text(C_WARN + "⚠️ Opção inválida! Tente novamente." + Style.RESET_ALL, delay=0.03)
            time.sleep(1.5)
'''