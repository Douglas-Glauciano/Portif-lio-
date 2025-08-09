from .utils import roll_dice, modifier  # Certifique-se que modifier está importado
import random
import re

class Monster:
    def __init__(self, id=None, name="", level=1, hp=None, hp_max=None, ac=None, 
                 attack_bonus=None, damage_dice="1d6", exp_reward=0, gold_dice="1d4",
                 strength=10, dexterity=10, constitution=10, intelligence=10, 
                 wisdom=10, charisma=10, main_attack_attribute="strength", attack_type="physical",
                 physical_resistance=1, magical_resistance=1):
        
        self.id = id
        self.name = name
        self.level = level
        self.damage_dice = damage_dice
        self.exp_reward = exp_reward
        self.gold_dice = gold_dice
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.main_attack_attribute = main_attack_attribute
        self.attack_type = attack_type
        self.physical_resistance = physical_resistance
        self.magical_resistance = magical_resistance
        
        if hp_max is None or ac is None:
            raise ValueError("hp_max (base HP) and ac must be provided when creating a Monster.")
            
        # Calcula HP máximo com modificador de Constituição
        self.hp_max = hp_max + modifier(self.constitution)
        self.hp = self.hp_max
        
        if attack_bonus is None:
            self.calculate_attack_bonus()
        else:
            self.attack_bonus = attack_bonus
        self.ac = ac  # Usa AC fornecido diretamente
            
    def calculate_attack_bonus(self):
        """Calcula bônus de ataque usando atributo principal"""
        main_attr = getattr(self, self.main_attack_attribute)
        self.attack_bonus = modifier(main_attr) + self.level // 2
        
    def attack(self):
        """Realiza um ataque retornando [total, crítico, rolagem]"""
        roll = random.randint(1, 20)
        is_critical = (roll == 20)
        is_fumble = (roll == 1)
        
        total = roll + self.attack_bonus
        return total, is_critical, roll

    def calculate_damage(self, crit=False):
        """Calcula dano baseado na arma e atributo principal"""
        base_damage = roll_dice(self.damage_dice)
        
        main_attr = getattr(self, self.main_attack_attribute)
        damage = base_damage + modifier(main_attr)
        
        if crit:
            damage += roll_dice(self.damage_dice)  # Dano extra no crítico
            
        return max(1, damage)

    def take_damage(self, damage, damage_type):
        """Aplica dano considerando resistências"""
        if damage_type == "physical":
            damage = max(1, damage - self.physical_resistance)
        elif damage_type == "magical":
            damage = max(1, damage - self.magical_resistance)
        
        self.hp -= damage
        return self.hp <= 0

    def get_gold_reward(self):
        """Calcula a recompensa em ouro"""
        return roll_dice(self.gold_dice)