# game/states/attributes_state.py
from ..base_state import BaseState
from game.utils import modifier, get_display_name
import os

class AttributesState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.tabs = ['Resumo', 'Atributos', 'Equipamentos', 'Perícias', 'Dificuldade']
        self.current_tab = 0
        self.tab_changed = True

    def enter(self):
        self.tab_changed = True

    def render(self):
        if self.tab_changed:
            player = self.game.player
            self.clear_screen()
            
            # Cabeçalho principal
            print("\n" + "=" * 50)
            print(f"📊 ATRIBUTOS DE {player.name.upper()} 📊".center(50))
            print("=" * 50)
            
            # Navegação por abas
            tab_bar = " | ".join(
                [f"{'▶ ' + tab + ' ◀' if i == self.current_tab else tab}" 
                 for i, tab in enumerate(self.tabs)]
            )
            print(f"\n{tab_bar}\n{'═' * 50}\n")
            
            # Renderização da aba atual
            if self.current_tab == 0:
                self._render_summary_tab()
            elif self.current_tab == 1:
                self._render_attributes_tab()
            elif self.current_tab == 2:
                self._render_equipment_tab()
            elif self.current_tab == 3:
                self._render_skills_tab()
            elif self.current_tab == 4:
                self._render_difficulty_tab()
            
            # Instruções de navegação
            print("\n" + "═" * 50)
            print("Navegação: [A] Anterior | [D] Próxima | [Enter] Voltar")
            self.tab_changed = False

    def handle_input(self):
        choice = input().strip().lower()
        
        if choice == 'd':  # Próxima aba
            self.current_tab = (self.current_tab + 1) % len(self.tabs)
            self.tab_changed = True
        elif choice == 'a':  # Aba anterior
            self.current_tab = (self.current_tab - 1) % len(self.tabs)
            self.tab_changed = True
        elif choice == '':  # Voltar
            self.game.pop_state()
        else:
            # Opção inválida, mantém na mesma tela
            self.tab_changed = False


    # =======================================================================
    # Métodos de renderização de abas
    # =======================================================================
    
    def _render_summary_tab(self):
        player = self.game.player
        
        # Informações básicas
        print(f"{'Raça:':<10} {player.race:<20} {'Classe:':<10} {player.char_class}")
        print(f"{'Nível:':<10} {player.level:<20} {'Experiência:':<12} {player.exp}/{player.exp_max}")
        print(f"{'Dificuldade:':<10} {player.difficulty:<20} {'Ouro:':<10} {player.gold}\n")
        
        # Status
        self._render_resource_bar("HP", player.hp, player.hp_max, "❤️", "█", "red")
        if player.mana_max > 0:
            self._render_resource_bar("Mana", player.mana, player.mana_max, "🔵", "▓", "blue")
        
        # Resumo de combate
        print("\n" + "═" * 50)
        print("⚔️ RESUMO DE COMBATE".center(50))
        print("═" * 50)
        
        weapon = next((item for item in player.get_equipped_items() if item['category'] == 'weapon'), None)
        weapon_name = get_display_name(weapon) if weapon else "Nenhuma"
        weapon_damage = f"{player.weapon_dice} {player.damage_type}" if weapon else "1d4 impacto"
        
        print(f"{'Arma:':<15} {weapon_name}")
        print(f"{'Dano:':<15} {weapon_damage}")
        print(f"{'CA:':<15} {player.ac}")
        print(f"{'Res. Física:':<15} {player.get_physical_resistance()} | {'Res. Mágica:':<18} {player.get_magical_resistance()}")

        # Resumo de atributos
        print("\n" + "═" * 50)
        print("📈 ATRIBUTOS".center(50))
        print("═" * 50)
        
        attributes = [
            ("💪 Força", player.get_effective_strength(), modifier(player.get_effective_strength())),
            ("🏹 Destreza", player.get_effective_dexterity(), modifier(player.get_effective_dexterity())),
            ("❤️ Constituição", player.get_effective_constitution(), modifier(player.get_effective_constitution())),
            ("📚 Inteligência", player.get_effective_intelligence(), modifier(player.get_effective_intelligence())),
            ("🔮 Sabedoria", player.get_effective_wisdom(), modifier(player.get_effective_wisdom())),
            ("✨ Carisma", player.get_effective_charisma(), modifier(player.get_effective_charisma()))
        ]
        
        for i in range(0, len(attributes), 2):
            attr1 = attributes[i]
            attr2 = attributes[i+1] if i+1 < len(attributes) else None
            
            line = f"{attr1[0]}: {attr1[1]} ({attr1[2]:+})"
            if attr2:
                line += f" | {attr2[0]}: {attr2[1]} ({attr2[2]:+})"
            print(line)

    def _render_attributes_tab(self):
        player = self.game.player
        
        attributes = [
            ("💪 Força", 
             player.strength, 
             player.get_effective_strength(),
             modifier(player.get_effective_strength()), 
             ["Ataque corpo a corpo", "Testes de força"]),
            
            ("🏹 Destreza", 
             player.dexterity, 
             player.get_effective_dexterity(),
             modifier(player.get_effective_dexterity()), 
             ["CA", "Ataque à distância", "Iniciativa"]),
            
            ("❤️ Constituição", 
             player.constitution, 
             player.get_effective_constitution(),
             modifier(player.get_effective_constitution()), 
             ["Pontos de vida", "Resistência"]),
            
            ("📚 Inteligência", 
             player.intelligence, 
             player.get_effective_intelligence(),
             modifier(player.get_effective_intelligence()), 
             ["Conhecimento", "Magias arcanas"]),
            
            ("🔮 Sabedoria", 
             player.wisdom, 
             player.get_effective_wisdom(),
             modifier(player.get_effective_wisdom()), 
             ["Percepção", "Magias divinas"]),
            
            ("✨ Carisma", 
             player.charisma, 
             player.get_effective_charisma(),
             modifier(player.get_effective_charisma()), 
             ["Persuasão", "Intimidação"])
        ]
        
        for name, base_value, effective_value, mod, uses in attributes:
            reduction = base_value - effective_value
            reduction_text = f" (🔻 Redução: -{reduction})" if reduction > 0 else ""
            
            print(f"\n{name}:")
            print(f"  Base: {base_value}{reduction_text} | Efetivo: {effective_value} | Mod: {mod:+}")
            print(f"  🔹 Usos: {', '.join(uses)}")
            self._render_attribute_bar(effective_value)
            print()

    def _render_equipment_tab(self):
        player = self.game.player
        equipped_items = player.get_equipped_items()
        
        # Arma
        weapon = next((item for item in equipped_items if item['category'] == 'weapon'), None)
        if weapon:
            weapon_name = get_display_name(weapon)
            damage_info = f"{weapon.get('damage_dice', '1d4')} {weapon.get('damage_type', 'impacto')}"
            enhancement = weapon.get('enhancement_level', 0)
            enhancement_str = f" (Aprimoramento +{enhancement})" if enhancement > 0 else ""
            
            print(f"⚔️ ARMA PRINCIPAL:")
            print(f"  {weapon_name}{enhancement_str}")
            print(f"  Dano: {damage_info}")
            print(f"  Atributo: {weapon.get('main_attribute', 'força').capitalize()}")
        else:
            print("⚔️ ARMA PRINCIPAL: Nenhuma equipada")
        
        # Armadura
        armor = next((item for item in equipped_items if item['category'] == 'armor'), None)
        if armor:
            armor_name = get_display_name(armor)
            enhancement = armor.get('enhancement_level', 0)
            enhancement_str = f" (Aprimoramento +{enhancement})" if enhancement > 0 else ""
            
            print("\n🛡️ ARMADURA:")
            print(f"  {armor_name}{enhancement_str}")
            print(f"  Tipo: {armor.get('armor_class', 'leve').capitalize()}")
            print(f"  Bônus de CA: +{armor.get('armor_bonus', 0)}")
            print(f"  Res. Física: +{armor.get('physical_resistance', 0)}")
            print(f"  Res. Mágica: +{armor.get('magical_resistance', 0)}")
        else:
            print("\n🛡️ ARMADURA: Nenhuma equipada")
        
        # Escudo
        shield = next((item for item in equipped_items if item['category'] == 'shield'), None)
        if shield:
            shield_name = get_display_name(shield)
            enhancement = shield.get('enhancement_level', 0)
            enhancement_str = f" (Aprimoramento +{enhancement})" if enhancement > 0 else ""
            
            print("\n🔰 ESCUDO:")
            print(f"  {shield_name}{enhancement_str}")
            print(f"  Bônus de CA: +{shield.get('armor_bonus', 0)}")
            print(f"  Penalidade Destreza: {shield.get('dexterity_penalty', 0)}")
        
        # Acessórios
        accessories = [item for item in equipped_items 
                      if item['category'] in ['ring', 'amulet', 'belt', 'boots']]
        
        if accessories:
            print("\n💍 ACESSÓRIOS:")
            for item in accessories:
                item_name = get_display_name(item)
                slot = item.get('equipped_slot_friendly', 'Equipado')
                effects = []
                
                if 'armor_bonus' in item and item['armor_bonus'] != 0:
                    effects.append(f"CA +{item['armor_bonus']}")
                if 'physical_resistance' in item and item['physical_resistance'] != 0:
                    effects.append(f"Res.Fis +{item['physical_resistance']}")
                if 'magical_resistance' in item and item['magical_resistance'] != 0:
                    effects.append(f"Res.Mag +{item['magical_resistance']}")
                
                effects_str = " | ".join(effects)
                print(f"  {item_name} ({slot}) {effects_str}")
        else:
            print("\n💍 ACESSÓRIOS: Nenhum equipado")

    def _render_skills_tab(self):
        player = self.game.player
        
        try:
            skills = player.get_all_skills()
            if not skills:
                print("❌ Nenhuma perícia disponível")
                return
                
            # Agrupar por atributo
            skills_by_attribute = {}
            for skill in skills:
                attribute = skill.get('attribute', 'none').lower()
                if attribute not in skills_by_attribute:
                    skills_by_attribute[attribute] = []
                skills_by_attribute[attribute].append(skill)
            
            # Ordem de exibição
            attribute_order = ['for', 'des', 'con', 'int', 'sab', 'car', 'none']
            attribute_names = {
                'for': '💪 Força',
                'des': '🏹 Destreza',
                'con': '❤️ Constituição',
                'int': '📚 Inteligência',
                'sab': '🔮 Sabedoria',
                'car': '✨ Carisma',
                'none': '🛠️ Gerais'
            }
            
            for attr in attribute_order:
                if attr in skills_by_attribute and skills_by_attribute[attr]:
                    print(f"\n{attribute_names.get(attr, '🛠️ Gerais')}:")
                    
                    for skill in skills_by_attribute[attr]:
                        skill_name = skill.get('skill_name', 'Desconhecida')
                        level = skill.get('level', 0)
                        current_xp = skill.get('current_xp', 0)
                        max_xp = skill.get('max_xp', 50)
                        
                        percent = min(100, int((current_xp / max_xp) * 100)) if max_xp > 0 else 0
                        bar = f"[{'█' * (percent//5)}{'░' * (20 - percent//5)}]"
                        
                        print(f"  {skill_name} (Nv {level}):")
                        print(f"    XP: {current_xp}/{max_xp} {bar} {percent}%")
        
        except Exception as e:
            print(f"❌ Erro ao carregar perícias: {str(e)}")

    def _render_difficulty_tab(self):
        player = self.game.player
        difficulty_modifiers = player.get_difficulty_modifiers()
        
        # Tabela de modificadores
        print("CONFIGURAÇÃO ATUAL DE DIFICULDADE\n")
        print(f"{'Modificador':<25} {'Efeito':<15}")
        print("-" * 45)
        
        for key, value in difficulty_modifiers.items():
            name = {
                'exp_multiplier': 'Multiplicador de EXP',
                'gold_multiplier': 'Multiplicador de Ouro',
                'damage_received': 'Dano Recebido',
                'damage_dealt': 'Dano Causado',
                'healing_received': 'Cura Recebida',
                'attribute_reduction': 'Redução de Atributos',
                'permadeath': 'Morte Permanente'
            }.get(key, key)
            
            # Formatação dos valores
            if key in ['exp_multiplier', 'gold_multiplier', 'damage_received', 
                      'damage_dealt', 'healing_received']:
                effect = f"{int((value-1)*100)}%"
                effect = f"+{effect}" if value > 1 else effect
            elif key == 'attribute_reduction':
                effect = f"-{value}"
            elif key == 'permadeath':
                effect = "✅ Ativo" if value else "❌ Inativo"
            else:
                effect = str(value)
            
            print(f"{name:<25} {effect:<15}")

    # =======================================================================
    # Métodos auxiliares
    # =======================================================================
    
    def _render_resource_bar(self, name, current, max_value, icon, bar_char, color_code):
        """Renderiza uma barra de recurso (HP ou Mana)"""
        if max_value <= 0: return
            
        percent = min(100, int((current / max_value) * 100))
        filled = percent // 5
        empty = 20 - filled
        
        # Cores ANSI
        colors = {"red": "\033[91m", "green": "\033[92m", 
                 "yellow": "\033[93m", "blue": "\033[94m", "reset": "\033[0m"}
        
        # Escolhe cor baseada na porcentagem
        if percent > 75: color = colors["green"]
        elif percent > 25: color = colors["yellow"]
        else: color = colors["red"]
        
        print(f"{icon} {name}: {current}/{max_value}")
        print(f"{color}[{bar_char * filled}{'░' * empty}]{colors['reset']} {percent}%")
    
    def _render_attribute_bar(self, value):
        """Renderiza uma barra visual para o atributo"""
        bar_length = min(20, max(0, (value - 8) // 2))
        filled = "█" * bar_length
        empty = "░" * (20 - bar_length)
        
        # Escolhe cor baseada no valor
        if value > 16: color = "\033[92m"  # Verde
        elif value > 12: color = "\033[93m"  # Amarelo
        else: color = "\033[91m"  # Vermelho
        
        rating = {
            20: "Lendário", 18: "Heróico", 16: "Excepcional",
            14: "Muito Bom", 12: "Bom", 10: "Médio",
            8: "Abaixo da Média", 0: "Fraco"
        }
        rating_desc = next((v for k, v in rating.items() if value >= k), "Fraco")
        
        print(f"{color}[{filled}{empty}]\033[0m {rating_desc}")