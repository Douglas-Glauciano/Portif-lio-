from .utils import roll_dice, modifier, roll_attribute, roll_dice_max, calculate_attack_bonus
from .config import DIFFICULTY_MODIFIERS
from .db_queries import (
    get_race_by_name, 
    get_class_by_name, 
    get_character_inventory,
    get_equipped_items_for_character,
    add_item_to_inventory,
    equip_item_from_inventory,
    unequip_item_from_character,
    get_background_by_name,
    get_background_starting_skills,
    add_character_skill,
    get_character_equipment,
    get_item_by_id
)
from .utils import calculate_enhanced_damage, calculate_enhanced_value



attr_map = {
    "for": "strength",
    "des": "dexterity",
    "con": "constitution",
    "int": "intelligence",
    "sab": "wisdom",
    "car": "charisma"
}

class Character:
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, int(value)) if value is not None else 0

    @property
    def hp_max(self):
        return self._hp_max

    @hp_max.setter
    def hp_max(self, value):
        try:
            self._hp_max = max(1, int(value)) if value is not None else 10
        except (TypeError, ValueError):
            self._hp_max = 10

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, value):
        self._mana = max(0, int(value)) if value is not None else 0

    @property
    def mana_max(self):
        return self._mana_max

    @mana_max.setter
    def mana_max(self, value):
        try:
            self._mana_max = max(0, int(value)) if value is not None else 0
        except (TypeError, ValueError):
            self._mana_max = 0

    def __init__(self, db_connection, id=None, name="", race="", char_class="", background="", level=1, exp=0, exp_max=100, hp=None, hp_max=None, mana=None, mana_max=None, gold=0, strength=None, dexterity=None,
                 constitution=None, intelligence=None, wisdom=None, charisma=None, ac=10, difficulty='Desafio Justo', permadeath=0):
        self.conn = db_connection
        self.id = id
        self.name = name
        self.race = race
        self.char_class = char_class
        self.background = background
        self.level = level
        self.exp = exp
        self.exp_max = exp_max
        self.gold = gold
        self.difficulty = difficulty
        self.permadeath = permadeath
        self.temporary_modifiers = {}
        self.location = "forest"
        self.last_wilderness = self.location

        self.strength = strength if strength is not None else roll_attribute()
        self.dexterity = dexterity if dexterity is not None else roll_attribute()
        self.constitution = constitution if constitution is not None else roll_attribute()
        self.intelligence = intelligence if intelligence is not None else roll_attribute()
        self.wisdom = wisdom if wisdom is not None else roll_attribute()
        self.charisma = charisma if charisma is not None else roll_attribute()

        # Resistências iniciais (serão recalculadas com equipamentos)
        self.physical_resistance = 0
        self.magical_resistance = 0
        self.dexterity_penalty = 0
        
        if not self.id and race:
            self.apply_race_bonus()

        self.ac = ac
        self.hp_max = hp_max if hp_max is not None else self.calculate_hp()
        self.hp = hp if hp is not None else self.hp_max
        self.mana_max = mana_max if mana_max is not None else self.calculate_mana()
        self.mana = mana if mana is not None else self.mana_max

        self.weapon_dice = '1d4'
        self.damage_type = 'physical'  # Padrão para dano físico
        self.main_attack_attribute = 'strength'
        
        if self.id:
            self.recalculate()
        else:
            self.ac = self.calculate_ac()
        self.skills = [] 
        if self.id:
            self._load_skills()

    def is_permadeath_enabled(self):
        """Retorna True se a morte permanente estiver ativada."""
        return self.permadeath == 1

    def handle_death(self):
        """Lida com a morte do personagem."""
        if self.is_permadeath_enabled():
            print(f"O personagem {self.name} morreu. Fim de jogo.")
            # Lógica para remover o personagem ou marcar como morto no DB
        else:
            print(f"O personagem {self.name} desmaiou e foi levado de volta ao acampamento.")
            # Lógica para reviver o personagem

    def get_effective_attribute(self, attribute_name):
        """Retorna o valor efetivo do atributo, considerando modificadores temporários, de dificuldade e penalidades de equipamento"""
        base_value = getattr(self, attribute_name)
        
        # Aplica modificadores de dificuldade
        if "attribute_reduction" in self.get_difficulty_modifiers():
            reduction = self.get_difficulty_modifiers()["attribute_reduction"]
            base_value = max(1, base_value - reduction)
        
        # Aplica penalidade de destreza do equipamento se for o atributo de destreza
        if attribute_name == "dexterity":
            penalty = self.get_dexterity_penalty()
            base_value = max(1, base_value - penalty)
        
        return base_value
    
    get_effective_xp_multiplier = 1 
    
    def get_effective_strength(self):
        return self.get_effective_attribute("strength")
    
    def get_effective_dexterity(self):
        return self.get_effective_attribute("dexterity")
    
    def get_effective_constitution(self):
        return self.get_effective_attribute("constitution")
    
    def get_effective_intelligence(self):
        return self.get_effective_attribute("intelligence")
    
    def get_effective_wisdom(self):
        return self.get_effective_attribute("wisdom")
    
    def get_effective_charisma(self):
        return self.get_effective_attribute("charisma")
    
    def apply_difficulty_modifiers(self):
        """Aplica os modificadores de dificuldade aos atributos do personagem"""
        pass

    def get_difficulty_modifiers(self):
        """Retorna os modificadores ativos para a dificuldade atual"""
        return DIFFICULTY_MODIFIERS.get(self.difficulty, {})
    
    @property
    def strength_modifier(self):
        return modifier(self.get_effective_strength())

    @property
    def dexterity_modifier(self):
        return modifier(self.get_effective_dexterity())

    @property
    def constitution_modifier(self):
        return modifier(self.get_effective_constitution())

    @property
    def intelligence_modifier(self):
        return modifier(self.get_effective_intelligence())

    @property
    def wisdom_modifier(self):
        return modifier(self.get_effective_wisdom())

    @property
    def charisma_modifier(self):
        return modifier(self.get_effective_charisma())
    
    def get_physical_resistance(self):
        return self.physical_resistance

    def get_magical_resistance(self):
        return self.magical_resistance

    def get_dexterity_penalty(self):
        return self.dexterity_penalty

    def apply_race_bonus(self):
        """Aplica os bônus de atributo da raça ao personagem."""
        race_data = get_race_by_name(self.conn, self.race)
        if not race_data: return
        
        self.strength += race_data.get("strength_bonus", 0)
        self.dexterity += race_data.get("dexterity_bonus", 0)
        self.constitution += race_data.get("constitution_bonus", 0)
        self.intelligence += race_data.get("intelligence_bonus", 0)
        self.wisdom += race_data.get("wisdom_bonus", 0)
        self.charisma += race_data.get("charisma_bonus", 0)

    def apply_background_skills(self):
        """
        Aplica as perícias iniciais definidas pelo antecedente do personagem.
        """
        if not self.id or not self.background:
            return

        background_data = get_background_by_name(self.conn, self.background)
        if not background_data:
            print(f"Aviso: Antecedente '{self.background}' não encontrado.")
            return

        background_id = background_data['id']
        starting_skills = get_background_starting_skills(self.conn, background_id)

        print(f"\nAplicando perícias iniciais do antecedente '{self.background}':")
        for skill_info in starting_skills:
            skill_id = skill_info['skill_id']
            skill_name = skill_info['skill_name']
            starting_level = skill_info['starting_level']
            
            # Adiciona a perícia ao personagem
            success = add_character_skill(self.conn, self.id, skill_id, starting_level)
            if success:
                print(f"- Perícia '{skill_name}' adicionada no nível {starting_level}.")
            else:
                print(f"- Erro ao adicionar perícia '{skill_name}'")
        
        # ATUALIZAÇÃO CRÍTICA: Recarrega as perícias após adicionar
        self._load_skills()

    def calculate_hp(self):
        """Calcula o HP máximo do personagem com base na classe e nível."""
        class_data = get_class_by_name(self.conn, self.char_class)
        hit_dice = class_data["hit_dice"] if class_data else "1d8"
        
        # Para nível 1: sempre usa o máximo do dado
        hp_base = roll_dice_max(hit_dice)
        
        # Para níveis acima de 1: usa a média arredondada para cima
        if self.level > 1:
            dice_size = int(hit_dice.split('d')[1])
            average_roll = (dice_size + 1) // 2  # Média arredondada para cima
            hp_base += average_roll * (self.level - 1)
            
        con_mod = modifier(self.get_effective_constitution())
        return max(1, hp_base + con_mod)

    def calculate_mana(self):
        """Calcula o Mana máximo do personagem com base na classe e nível."""
        class_data = get_class_by_name(self.conn, self.char_class)
        mana_dice = class_data["mana_dice"] if class_data else "1d2"
        
        # Para nível 1: sempre usa o máximo do dado
        mana_base = roll_dice_max(mana_dice)
        
        # Para níveis acima de 1: usa a média arredondada para cima
        if self.level > 1:
            dice_size = int(mana_dice.split('d')[1])
            average_roll = (dice_size + 1) // 2  # Média arredondada para cima
            mana_base += average_roll * (self.level - 1)
        
        # Usa o maior modificador entre Inteligência e Sabedoria
        int_mod = modifier(self.get_effective_intelligence())
        wis_mod = modifier(self.get_effective_wisdom())
        mental_mod = max(int_mod, wis_mod)
        
        return max(0, mana_base + mental_mod)

    def calculate_ac(self):
        """
        Calcula a Classe de Armadura (AC) do personagem, considerando
        a CA base da classe, bônus de destreza (com penalidades já aplicadas) e escudos.
        """
        # CA base da classe
        class_data = get_class_by_name(self.conn, self.char_class)
        base_ac_from_class = class_data.get('base_ac', 10) if class_data else 10
        
        # O valor de 'dexterity_penalty' já é recalculado em self.recalculate()
        # A penalidade é subtraída diretamente da destreza
        effective_dex = self.dexterity - self.dexterity_penalty
        
        # O bônus de destreza pode ter um teto, dependendo do tipo de armadura.
        # Por exemplo, armaduras pesadas não dão bônus de destreza.
        # Essa lógica é mais avançada, mas o código atual funciona bem para a maioria dos casos.
        dex_mod = modifier(effective_dex)
        
        current_ac = base_ac_from_class + dex_mod

        # Adiciona bônus de escudo dos itens equipados
        for item in self.get_equipped_items():
            if item.get('category') == 'shield' and item.get('armor_bonus') is not None:
                current_ac += item['armor_bonus']
                current_ac += item.get('enhancement_level', 0)
        
        return current_ac
    
    def recalculate(self):
        """
        Recalcula todos os atributos derivados do personagem,
        incluindo AC, dano da arma e atributo de ataque principal,
        com base nos itens equipados e seus aprimoramentos.
        """
        if not self.id:
            return

        # Recalcula HP e Mana máximos (podem mudar com nível, raça, etc.)
        self.hp_max = self.calculate_hp()
        self.mana_max = self.calculate_mana()

        # Resetar resistências e penalidades
        self.physical_resistance = 0
        self.magical_resistance = 0
        self.dexterity_penalty = 0
        
        equipped_items = get_equipped_items_for_character(self.conn, self.id)
        
        # Calcular resistências e penalidades
        for item in equipped_items:
            if item.get('category') == 'armor':
                # Aplica redução de penalidade com aprimoramento
                penalty_reduction = item.get('enhancement_level', 0) // 3
                self.dexterity_penalty += max(0, item.get('dexterity_penalty', 0) - penalty_reduction)
                
                # Calcula resistências aprimoradas
                phys_res = item.get('physical_resistance', 0)
                mag_res = item.get('magical_resistance', 0)
                enhancement_level = item.get('enhancement_level', 0)
                
                self.physical_resistance += phys_res + enhancement_level
                self.magical_resistance += mag_res + enhancement_level
            elif item.get('category') == 'shield' or item.get('category') == 'armor':
                # Escudos também podem fornecer resistências
                self.physical_resistance += item.get('physical_resistance', 0)
                self.magical_resistance += item.get('magical_resistance', 0)
        
        # Recalcula AC com base nos itens equipados
        self.ac = self.calculate_ac()
        
        # Resetar arma e tipo de dano para valores padrão antes de aplicar itens
        self.weapon_dice = '1d4'
        self.damage_type = 'physical'  # Padrão para dano físico
        self.main_attack_attribute = 'strength'
        
        equipped_items = get_equipped_items_for_character(self.conn, self.id)
        
        # Encontra a arma principal equipada (se houver)
        equipped_weapon = None
        for item in equipped_items:
            if item.get('category') == 'weapon' and item.get('equip_slot') == 'main_hand':
                equipped_weapon = item
                break
        
        if equipped_weapon:
            # Usa o dano aprimorado da arma
            self.weapon_dice = calculate_enhanced_damage(equipped_weapon)
            self.damage_type = equipped_weapon.get('damage_type', 'physical')
            self.main_attack_attribute = equipped_weapon.get('main_attribute', 'strength')
        
    def attack(self):
        """
        Calcula o resultado de um ataque, incluindo bônus de atributo,
        """
        self.recalculate() # Garante que os atributos estão atualizados antes do ataque
        
        # Obtém a arma equipada (já com detalhes de aprimoramento)
        weapon = None
        equipped_items = self.get_equipped_items()
        for item in equipped_items:
            if item['category'] == 'weapon' and item.get('equip_slot') == 'main_hand':
                weapon = item
                break
        
        roll = roll_dice("1d20")
        is_critical = (roll == 20)
        
        # CORREÇÃO: Usa o valor efetivo do atributo de ataque para o cálculo do bônus
        effective_attack_attribute = self.get_effective_attribute(self.main_attack_attribute)
        attack_attr_mod = modifier(effective_attack_attribute)
        
        # Adiciona bônus de aprimoramento da arma (se houver)
        enhancement_bonus = 0
        if weapon:
            # calculate_attack_bonus deve ser uma função utilitária que usa o enhancement_level
            enhancement_bonus = calculate_attack_bonus(weapon) 
        
        attack_bonus = attack_attr_mod + enhancement_bonus
        
        return roll + attack_bonus, is_critical, roll

    def calculate_damage(self, critical=False):
        """Calcula o dano causado, considerando a arma equipada e aprimoramentos."""
        # Obtém a arma equipada (já com detalhes de aprimoramento)
        weapon = None
        equipped_items = self.get_equipped_items()
        for item in equipped_items:
            if item['category'] == 'weapon' and item.get('equip_slot') == 'main_hand':
                weapon = item
                break
        
        if not weapon:
            # Se não tiver arma equipada, usa dano desarmado
            base_damage = roll_dice("1d4")
            return base_damage, "physical"  # Retorna dano e tipo
        
        # Calcula o dano base da arma usando a função de utilidade que já considera aprimoramento
        dice_to_roll = calculate_enhanced_damage(weapon)
        
        # Rola os dados de dano
        total_damage = roll_dice(dice_to_roll)
        
        # CORREÇÃO: Usa o valor efetivo do atributo de ataque para o cálculo do bônus
        effective_attack_attribute = self.get_effective_attribute(self.main_attack_attribute)
        total_damage += modifier(effective_attack_attribute)

        # Se for crítico, dobra o dano
        if critical:
            total_damage *= 2
        
        return max(1, total_damage), self.damage_type  # Retorna dano e tipo

    def take_damage(self, damage, damage_type="physical"):
        """
        Aplica dano ao personagem, reduzindo pela resistência apropriada.
        damage_type: "physical" ou "magical"
        Retorna: (is_dead, actual_damage_taken, damage_reduced)
        """
        # Garante que os valores de resistência estão atualizados
        self.recalculate()
        
        resistance = 0
        if damage_type == "physical":
            resistance = self.physical_resistance
        elif damage_type == "magical":
            resistance = self.magical_resistance
        
        # Reduz o dano pela resistência
        # Se o dano for menor ou igual à resistência, o dano real é 0.
        # Caso contrário, o dano real é a diferença.
        actual_damage = max(0, damage - resistance)
        damage_reduced = damage - actual_damage
        
        self.hp -= actual_damage
        
        is_dead = self.hp <= 0
        
        return is_dead, actual_damage, damage_reduced
    
    def gain_exp(self, amount):
        """Adiciona experiência e verifica subida de nível"""
        self.exp += amount
        
        # Verificar se subiu de nível múltiplas vezes se ganhou muita XP
        while self.exp >= self.exp_max:
            # Calcular XP excedente para o próximo nível
            excess = self.exp - self.exp_max
            self.level_up()
            self.exp = excess  # Aplicar excedente ao próximo nível

    def level_up(self, use_average=True):
        """
        Aumenta o nível do personagem, recalcula HP/Mana e oferece
        escolha de atributos a cada 2 níveis.
        """
        self.level += 1
        self.exp_max = int(self.exp_max * 1.5) # Aumenta o XP necessário para o próximo nível
        
        class_data = get_class_by_name(self.conn, self.char_class)
        hit_dice = class_data["hit_dice"] if class_data else "1d8"
        mana_dice = class_data["mana_dice"] if class_data else "1d2" # Pega o dado de mana da classe

        # Ganho de HP
        if use_average:
            dice_size = int(hit_dice.split('d')[1])
            roll_hp = (dice_size // 2) + 1
        else:
            roll_hp = roll_dice(hit_dice)
        
        con_mod = modifier(self.get_effective_constitution())
        hp_gain = max(1, roll_hp + con_mod)
        self.hp_max += hp_gain
        self.hp = self.hp_max  # cura completamente
        
        # Ganho de Mana
        mana_gain = 0
        if mana_dice != "1d2": # Se a classe tem um dado de mana significativo
            if use_average:
                dice_size = int(mana_dice.split('d')[1])
                roll_mana = (dice_size // 2) + 1
            else:
                roll_mana = roll_dice(mana_dice)
            
            int_mod = modifier(self.get_effective_intelligence())
            wis_mod = modifier(self.get_effective_wisdom())
            mental_mod = max(int_mod, wis_mod) # Usa o maior modificador mental
            
            mana_gain = max(0, roll_mana + mental_mod)
            self.mana_max += mana_gain
            self.mana = self.mana_max
        
        # Aumento de atributos a cada 2 níveis
        attributes_increased = []
        if self.level % 2 == 0:
            print("\n🎉 Você ganhou pontos de atributo! Escolha 3 atributos para aumentar em +1 🎉")
            attributes = {
                "1": "strength", "2": "dexterity", "3": "constitution",
                "4": "intelligence", "5": "wisdom", "6": "charisma"
            }
            
            attribute_names = {
                "strength": "Força", "dexterity": "Destreza", "constitution": "Constituição",
                "intelligence": "Inteligência", "wisdom": "Sabedoria", "charisma": "Carisma"
            }
            
            print("\nAtributos atuais:")
            for idx, attr in attributes.items():
                attr_name = attributes[idx]
                print(f"{idx}. {attribute_names[attr_name]}: {getattr(self, attr_name)}")
            
            choices = []
            for i in range(1, 4):
                while True:
                    choice = input(f"\nEscolha o {i}º atributo para aumentar (1-6): ")
                    if choice in attributes and attributes[choice] not in choices:
                        choices.append(attributes[choice])
                        break
                    else:
                        print("Escolha inválida ou atributo já selecionado. Tente novamente.")
            
            for attr in choices:
                current_value = getattr(self, attr)
                setattr(self, attr, current_value + 1)
                attributes_increased.append(f"{attribute_names[attr]} +1")
            
            print("\nAtributos aumentados:", ", ".join(attributes_increased))
        
        return hp_gain, mana_gain, attributes_increased
    
    # --- Métodos de Inventário e Itens (Refatorados) ---
    def get_inventory(self):
        """Retorna a lista de itens no inventário do personagem, com detalhes de aprimoramento."""
        return get_character_inventory(self.conn, self.id) if self.id else []
    
    def get_equipped_items(self):
        """Retorna a lista de itens equipados pelo personagem, com detalhes de aprimoramento."""
        if self.id:
            return get_equipped_items_for_character(self.conn, self.id)
        return []  # Retorna lista vazia se não tiver ID

    def equip_item(self, inventory_id):
        success, message = equip_item_from_inventory(self.conn, self.id, inventory_id)
        if success:
            self.recalculate()  # Já está presente
        return success, message

    def unequip_item(self, slot_technical_name):
        success, message = unequip_item_from_character(self.conn, self.id, slot_technical_name)
        if success:
            self.recalculate()  # Já está presente
        return success, message

    def equip_starting_items(self):
        if not self.id:
            return

        class_data = get_class_by_name(self.conn, self.char_class)
        if not class_data: 
            return

        # Cria o registro de equipamento apenas uma vez
        get_character_equipment(self.conn, self.id)

        # ... resto do código para equipar itens ...
        print(f"Equipando itens iniciais para classe: {self.char_class}")
        
        weapon_data = class_data.get('starting_weapon')
        if weapon_data:
            weapon_id = weapon_data.get('id')
            print(f" - Arma inicial: {weapon_data.get('name')} (ID: {weapon_id})")
            if weapon_id:
                inventory_id = add_item_to_inventory(self.conn, self.id, weapon_id, quantity=1, enhancement_level=0)
                if inventory_id:
                    success, msg = self.equip_item(inventory_id)
                    print(f"   - Equipado: {msg}")
                else:
                    print("   - Falha ao adicionar arma ao inventário")
        else:
            print(" - Nenhuma arma inicial definida para esta classe")

        armor_data = class_data.get('starting_armor')
        if armor_data:
            armor_id = armor_data.get('id')
            print(f" - Armadura inicial: {armor_data.get('name')} (ID: {armor_id})")
            if armor_id:
                inventory_id = add_item_to_inventory(self.conn, self.id, armor_id, quantity=1, enhancement_level=0)
                if inventory_id:
                    success, msg = self.equip_item(inventory_id)
                    print(f"   - Equipado: {msg}")
                else:
                    print("   - Falha ao adicionar armadura ao inventário")
        else:
            print(" - Nenhuma armadura inicial definida para esta classe")

        self.recalculate()
    
    def get_enhancement_benefits(self, item, new_level):
        """
        Retorna uma lista de strings descrevendo os benefícios do próximo nível
        de aprimoramento para um item dado.
        """
        benefits = []
        
        # Obter a perícia associada ao item
        skill_name = self.get_associated_skill(item)
        
        if item['category'] == 'weapon':
            # Benefícios de dano baseados na perícia
            skill_level = self.skills.get(skill_name, 0)
            damage_bonus = skill_level * 0.1  # +10% de dano por nível de perícia
            benefits.append(f"- Dano: +{damage_bonus:.1f}% por nível de {skill_name}")
            
            # Benefícios específicos por tipo de arma
            weapon_type = item.get('weapon_type', '')
            if weapon_type in ['bow', 'crossbow']:
                if new_level % 2 == 0:  # Níveis pares
                    benefits.append("- Alcance: +10%")
            elif weapon_type in ['polearm']:
                if new_level % 3 == 0:  # Cada 3 níveis
                    benefits.append("- Chance de atordoamento: +5%")
        
        elif item['category'] == 'armor':
            # Benefícios baseados na perícia
            armor_class = item.get('armor_class', '')
            skill_name = {
                'light': "Armaduras Leves",
                'medium': "Armaduras Médias",
                'heavy': "Armaduras Pesadas"
            }.get(armor_class, "Armaduras")
            
            skill_level = self.skills.get(skill_name, 0)
            resistance_bonus = skill_level * 0.05  # +5% de resistência por nível
            
            # Benefícios diretos do aprimoramento
            benefits.append(f"- Resistência Física: +1")
            benefits.append(f"- Resistência Mágica: +1")
            benefits.append(f"- Eficiência: +{resistance_bonus:.1f}% por nível de {skill_name}")
            
            # Redução de penalidade a cada 3 níveis
            if new_level % 3 == 0 and item.get('dexterity_penalty', 0) > 0:
                benefits.append("- Penalidade de Destreza: -1")

        elif item['category'] in ['shield']:
            # Benefícios de defesa baseados na perícia
            skill_name = "Armaduras Leves" if item.get('armor_class') == 'light' else \
                         "Armaduras Médias" if item.get('armor_class') == 'medium' else \
                         "Armaduras Pesadas" if item.get('armor_class') == 'heavy' else "Escudos"
            
            skill_level = self.skills.get(skill_name, 0)
            defense_bonus = skill_level * 0.05  # +5% de defesa por nível de perícia
            benefits.append(f"- Defesa: +{defense_bonus:.1f}% por nível de {skill_name}")
            
            # Benefícios específicos para escudos
            if item['category'] == 'shield' and new_level % 2 == 0:
                benefits.append("- Chance de bloqueio: +5%")
        
        return benefits
    

    # --- MÉTODOS DE PERICIAS ---
    def get_associated_skill(self, item):
        """Retorna a perícia associada a um item equipado"""
        skill_map = {
            # Armas
            'one_handed': "Armas de Uma Mão",
            'two_handed': "Armas de Duas Mãos",
            'polearm': "Armas de Haste",
            'bow': "Arquearia",
            'crossbow': "Bestas",
            'throwing': "Armas de Arremesso",
            'unarmed': "Briga",
            
            # Armaduras
            'light': "Armaduras Leves",
            'medium': "Armaduras Médias",
            'heavy': "Armaduras Pesadas",
            
            # Escudos
            'shield': "Escudos"
        }
        
        if item['category'] == 'weapon':
            return skill_map.get(item.get('weapon_type', 'unarmed'), "Briga")
        
        elif item['category'] == 'armor':
            return skill_map.get(item.get('armor_class', 'light'), "Resiliência")
        
        elif item['category'] == 'shield':
            return "Escudos"
        
        return None
    
    def update_passive_skills(self):
        """Atualiza perícias passivas baseadas no equipamento"""
        passive_skills = {
            "Armaduras Leves": 0,
            "Armaduras Médias": 0,
            "Armaduras Pesadas": 0,
            "Escudos": 0
        }
        
        # Verificar itens equipados
        for item in self.get_equipped_items():
            if item['category'] == 'armor':
                armor_class = item.get('armor_class', 'light')
                if armor_class == 'light':
                    passive_skills["Armaduras Leves"] += 1
                elif armor_class == 'medium':
                    passive_skills["Armaduras Médias"] += 1
                elif armor_class == 'heavy':
                    passive_skills["Armaduras Pesadas"] += 1
            elif item['category'] == 'shield':
                passive_skills["Escudos"] += 1
        
        # Atualizar níveis de perícia (simulação de progressão)
        for skill, level in passive_skills.items():
            if skill in self.skills:
                self.skills[skill] = max(self.skills[skill], level)
            else:
                self.skills[skill] = level

    def get_all_skills(self):
        """
        Retorna todas as perícias disponíveis, garantindo que as do personagem mantenham seus níveis reais
        """
        from .db_queries import get_character_skills, get_all_skills as get_all_base_skills
        
        try:
            if not self.id:
                return []
            
            # Carrega as perícias do personagem
            character_skills = get_character_skills(self.conn, self.id)
            # Carrega todas as perícias base do sistema
            all_base_skills = get_all_base_skills(self.conn)
            
            # Cria um dicionário de perícias do personagem por ID
            char_skills_dict = {skill['skill_id']: skill for skill in character_skills}
            
            all_skills = []
            for base_skill in all_base_skills:
                skill_id = base_skill['id']
                
                # Verifica se o personagem tem esta perícia
                if skill_id in char_skills_dict:
                    # Usa os dados REAIS do personagem
                    skill_data = char_skills_dict[skill_id]
                    skill_data['skill_name'] = base_skill['name']  # Garante o nome correto
                    skill_data['description'] = base_skill['description']
                    skill_data['attribute'] = base_skill['attribute']
                    all_skills.append(skill_data)
                else:
                    # Perícia que o personagem não possui
                    all_skills.append({
                        'skill_id': skill_id,
                        'skill_name': base_skill['name'],
                        'description': base_skill['description'],
                        'attribute': base_skill['attribute'],
                        'level': 0,
                    })
            return all_skills
        except Exception as e:
            print(f"Erro ao carregar perícias: {e}")
            return []
    
    def _load_skills(self):
        """
        Carrega as perícias do personagem do banco de dados para o objeto
        """
        from .db_queries import get_character_skills
        skills_list = get_character_skills(self.conn, self.id)
        self.skills = {skill['skill_name']: skill['level'] for skill in skills_list}

    # --- MÉTODOS DE EXIBIÇÃO (UI) ---
    def show_attributes(self):
        """Exibe os atributos e status atuais do personagem de forma visual."""
        if self.id:
            self.recalculate()
        
        # Dados básicos
        print(f"\n{'='*50}")
        print(f"ATRIBUTOS DE {self.name.upper()}".center(50))
        print(f"{'='*50}")
        print(f"Raça: {self.race} | Classe: {self.char_class} | Nível: {self.level}")
        print(f"Experiência: {self.exp}/{self.exp_max} | Ouro: {self.gold}")
        print(f"{'-'*50}")
        
        # Barra de HP e Mana
        hp_percent = min(100, int((self.hp / self.hp_max) * 100))
        mana_percent = min(100, int((self.mana / self.mana_max) * 100)) if self.mana_max > 0 else 0
        
        print(f"HP: {self.hp}/{self.hp_max}")
        print(f"[{'█' * (hp_percent // 5)}{'░' * (20 - (hp_percent // 5))}] {hp_percent}%")
        
        if self.mana_max > 0:
            print(f"\nMana: {self.mana}/{self.mana_max}")
            print(f"[{'▓' * (mana_percent // 5)}{'░' * (20 - (mana_percent // 5))}] {mana_percent}%")

        print(f"Dificuldade: {self.difficulty}")

        if self.id:
            print(f"\nResistência Física: {self.physical_resistance}")
            print(f"Resistência Mágica: {self.magical_resistance}")
            print(f"Penalidade de Destreza: -{self.dexterity_penalty}")
            
            # Exibe a arma com dano aprimorado
            weapon_desc = ""
            equipped_weapon = None
            for item in self.get_equipped_items():
                if item.get('category') == 'weapon' and item.get('equip_slot') == 'main_hand':
                    equipped_weapon = item
                    break
        
            if equipped_weapon:
                # Usa o dano calculado pela função utilitária (já inclui aprimoramento)
                weapon_desc = f"{calculate_enhanced_damage(equipped_weapon)} {equipped_weapon.get('damage_type', 'physical')}"
                enhancement_level = equipped_weapon.get('enhancement_level', 0)
                if enhancement_level > 0:
                    weapon_desc += f" (+{enhancement_level})" # Adiciona o nível de aprimoramento na exibição
                print(f"Arma: {weapon_desc} (Atributo: {self.main_attack_attribute})")
            else:
                print(f"Arma: Punhos (1d4 physical) (Atributo: strength)") # Dano desarmado padrão
                
        print(f"{'-'*50}")
        
        # Atributos com barras de progresso
        attributes = [
            ("Força", self.get_effective_strength(), "💪"),
            ("Destreza", self.get_effective_dexterity(), "🏹"),
            ("Constituição", self.get_effective_constitution(), "❤️"),
            ("Inteligência", self.get_effective_intelligence(), "📚"),
            ("Sabedoria", self.get_effective_wisdom(), "🔮"),
            ("Carisma", self.get_effective_charisma(), "✨")
        ]
        
        print("\nAtributos:")
        print("Atributo      | Valor | Mod | Barra")
        print(f"{'-'*50}")
        
        for name, value, icon in attributes:
            mod = modifier(value)
            bar_length = min(20, max(1, (value - 8) // 2))  # Ajuste a escala da barra conforme necessário
            bar = f"[{icon * bar_length}{' ' * (20 - bar_length)}]"
            
            print(f"{name:<12} | {value:<5} | {mod:>+2} | {bar}")
        
        print(f"{'='*50}")
        
    @staticmethod
    def load_character(conn, character_id):
        """
        Carrega um único personagem do banco de dados pelo seu ID.
        """
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()

        if not row:
            return None

        columns = [description[0] for description in cursor.description]
        char_data = dict(zip(columns, row))
        
        char_data["char_class"] = char_data.get("class", "Unknown") 
        char_data["background"] = char_data.get("background", None) 
        char_data["difficulty"] = char_data.get("difficulty", "Desafio Justo")
        char_data["permadeath"] = char_data.get("permadeath", 0)

        if "class" in char_data:
            del char_data["class"]
        
        return Character(conn, **char_data)