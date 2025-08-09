import random
import time
import os
from .character import Character
from .monster import Monster
from .db_queries import load_monsters_by_level, add_item_to_inventory, remove_item_from_inventory
from .utils import modifier, roll_dice, get_display_name, calculate_enhanced_damage, calculate_enhanced_armor_bonus
from .config import DIFFICULTY_MODIFIERS
from .database import delete_character

class Combat:
    def __init__(self, player: Character, db_connection):
        self.player = player
        self.conn = db_connection
        self.difficulty_modifiers = DIFFICULTY_MODIFIERS.get(player.difficulty, DIFFICULTY_MODIFIERS["Desafio Justo"])
        self.monster = self.generate_monster()
        self.permadeath_active = player.permadeath
        player.recalculate()
        print(f"\nUm {self.monster.name} selvagem aparece!")
        time.sleep(2)

    def generate_monster(self) -> Monster:
        """Gera um monstro apropriado para o nível do jogador."""
        valid_monsters = load_monsters_by_level(self.conn, self.player.level)

        if not valid_monsters:
            print("Aviso: Nenhum monstro válido encontrado no DB. Usando um Rato Gigante como padrão.")
            return Monster(
                name="Rato Gigante", 
                level=1, 
                hp_max=10, 
                ac=10, 
                damage_dice="1d4", 
                exp_reward=5, 
                gold_dice="1d2",
                attack_type="physical"
            )

        monster_data = random.choice(valid_monsters)
        
        # Aplicar o multiplicador de HP do monstro com base na dificuldade
        hp_max = int(monster_data.get('hp', 10) * self.difficulty_modifiers.get("monster_hp_multiplier", 1.0))
        ac = monster_data.get('ac', 10)
        
        return Monster(
            name=monster_data['name'],
            level=monster_data['level'],
            hp_max=hp_max,
            ac=ac,
            attack_bonus=monster_data.get('attack_bonus', 0),
            damage_dice=monster_data['damage_dice'],
            exp_reward=monster_data['exp_reward'],
            gold_dice=monster_data['gold_dice'],
            strength=monster_data.get('strength', 10),
            dexterity=monster_data.get('dexterity', 10),
            constitution=monster_data.get('constitution', 10),
            intelligence=monster_data.get('intelligence', 10),
            wisdom=monster_data.get('wisdom', 10),
            charisma=monster_data.get('charisma', 10),
            main_attack_attribute=monster_data.get('main_attack_attribute', 'strength'),
            attack_type=monster_data.get('attack_type', 'physical'),
            physical_resistance=monster_data.get('physical_resistance', 0),
            magical_resistance=monster_data.get('magical_resistance', 0)
        )
    
    def start(self):
        """Inicia e gerencia o combate até sua conclusão"""
        print(f"\n{'='*50}")
        print(f"     ☠ BATALHA CONTRA {self.monster.name.upper()} ☠")
        print(f"{'='*50}")
        
        while True:
            # Turno do jogador
            self.display_status()
            choice = input("\n1. Atacar\n2. Fugir\nEscolha: ").strip()
            
            if choice == "1":
                monster_dead = self.player_attack()
                if monster_dead:
                    self.victory()
                    return "victory"
            elif choice == "2":
                if self.attempt_flee():
                    print("\nVocê fugiu com sucesso!")
                    return "fled"
            else:
                print("Opção inválida!")
                time.sleep(1)
                continue
            
            # Turno do monstro, apenas se o monstro não estiver morto
            if not self.monster.hp <= 0:
                player_dead = self.monster_attack()
                if player_dead:
                    permadeath_result = self.defeat()
                    return "permadeath" if permadeath_result else "defeat"
            
    def display_status(self):
        """Mostra status do combate com informações de resistências."""
        os.system('cls' if os.name == 'nt' else 'clear')
        border = "═" * 52
        separator = "─" * 52
        skull = "☠"
        heart_drop = "❤️ "
        mana_drop = "🔷"
        shield = "🛡"

        physical_res = self.player.physical_resistance
        magical_res = self.player.magical_resistance
        dex_penalty = self.player.dexterity_penalty

        player_hp_percent = min(100, int((self.player.hp / self.player.hp_max) * 100))
        monster_hp_percent = min(100, int((self.monster.hp / self.monster.hp_max) * 100))
        
        player_mana_info = ""
        if self.player.mana_max > 0:
            mana_percent = min(100, int((self.player.mana / self.player.mana_max) * 100))
            player_mana_info = f"\n  {mana_drop} Mana: {self.player.mana}/{self.player.mana_max}"
            player_mana_info += f"\n      [{'▓' * (mana_percent // 5)}{'░' * (20 - (mana_percent // 5))}] {mana_percent}%"

        print(f"\n{border}")
        print(f"    {skull} BATALHA CONTRA {self.monster.name.upper()} {skull}")
        print(f"{border}")
        print(f"\n👤 {self.player.name} [Lvl {self.player.level}]")
        print(f"  {heart_drop} Vida: {self.player.hp}/{self.player.hp_max}")
        print(f"      [{'█' * (player_hp_percent // 5)}{'░' * (20 - (player_hp_percent // 5))}] {player_hp_percent}%")
        
        if player_mana_info:
            print(player_mana_info)
            
        print(f"  {shield} Armadura: {self.player.ac}")
        print(f"  🛡️ Resistência Física: {physical_res}")
        print(f"  ✨ Resistência Mágica: {magical_res}")
        print(f"  ⚠️ Penalidade Destreza: -{dex_penalty}")
        
        equipped_items = self.player.get_equipped_items()
        weapon = next((item for item in equipped_items if item['category'] == 'weapon' and item.get('equip_slot') == 'main_hand'), None)
        shield_item = next((item for item in equipped_items if item['category'] == 'shield'), None)
        
        if weapon:
            display_name = get_display_name(weapon)
            enhanced_damage_str = calculate_enhanced_damage(weapon)
            damage_type = weapon.get('damage_type', 'physical')
            damage_info = f"{enhanced_damage_str} {damage_type}"
            enhancement_level = weapon.get('enhancement_level', 0)
            enhancement_str = f" (+{enhancement_level})" if enhancement_level > 0 else ""
            print(f"  ⚔️ Arma: {display_name} ({damage_info}{enhancement_str})")
        else:
            print("  ⚔️ Arma: Punhos (1d4 physical)")
        
        if shield_item:
            shield_bonus = calculate_enhanced_armor_bonus(shield_item)
            print(f"  🛡️ Escudo: {get_display_name(shield_item)} (+{shield_bonus} AC)")
        
        print(f"\n{separator}")
        print(f"👹 {self.monster.name} [Lvl {self.monster.level}]")
        print(f"  {heart_drop} Vida: {self.monster.hp}/{self.monster.hp_max}")
        print(f"      [{'█' * (monster_hp_percent // 5)}{'░' * (20 - (monster_hp_percent // 5))}] {monster_hp_percent}%")
        print(f"  {shield} Armadura: {self.monster.ac}")
        print(f"  🛡️ Resistência Física: {self.monster.physical_resistance}")
        print(f"  ✨ Resistência Mágica: {self.monster.magical_resistance}")
        print(f"  ⚔️ Tipo de Ataque: {self.monster.attack_type}")
        print(f"{border}\n")


    def player_attack(self):
        """Ataque do jogador com feedback melhorado."""
        self.player.recalculate()
        attack_roll, critical, dice_roll = self.player.attack()
        
        print(f"\nSua rolagem de ataque: {attack_roll} (Dado: {dice_roll} + Bônus: {attack_roll - dice_roll})")
        time.sleep(1.2)

        if critical:
            print("⚡ CRÍTICO! Dano dobrado!")
            time.sleep(1)

        if attack_roll >= self.monster.ac or critical:
            # Agora calculate_damage retorna (dano, tipo_de_dano)
            damage, damage_type = self.player.calculate_damage(critical)
            
            # Aplica modificador de dificuldade ao dano causado pelo jogador
            damage = int(damage * self.difficulty_modifiers.get("damage_dealt", 1.0))
            
            # Adicione o dano critico se o inimigo tiver chance de critico
            if critical and "enemy_crit_chance_bonus" in self.difficulty_modifiers:
                damage += damage * 0.15

            # Aplica a resistência do monstro ao dano
            if damage_type == "physical":
                damage_after_resistance = max(1, damage - self.monster.physical_resistance)
            else:
                damage_after_resistance = max(1, damage - self.monster.magical_resistance)
                
            # Reduz o HP do monstro
            self.monster.hp -= damage_after_resistance
            
            # Exibe informações detalhadas
            print(f"🔥 Você acerta o {self.monster.name} causando {damage_after_resistance} de dano {damage_type}!")
            
            if damage > damage_after_resistance:
                resistance_value = damage - damage_after_resistance
                print(f"  🛡️ Resistência do monstro reduziu {resistance_value} de dano!")
            
            time.sleep(1.5)
            
            # Verifica se o monstro morreu
            return self.monster.hp <= 0
        else:
            print(f"Você erra o ataque! O {self.monster.name} tinha {self.monster.ac} de AC.")
            time.sleep(1.5)
            return False

    def monster_attack(self):
        """Ataque do monstro com feedback visual aprimorado."""
        # Se houver chance de crítico extra para inimigos, aplica aqui
        crit_bonus_chance = self.difficulty_modifiers.get("enemy_crit_chance_bonus", 0)
        is_crit_bonus_active = random.random() < crit_bonus_chance

        attack_roll, critical, dice_roll = self.monster.attack()
        attack_bonus = attack_roll - dice_roll

        # Verifica se o crítico adicional foi ativado
        if is_crit_bonus_active:
            critical = True

        print(f"\n{self.monster.name} ataca!")
        time.sleep(1)
        
        print(f"Rolagem do monstro: {dice_roll} (dado) + {attack_bonus} (bônus) = {attack_roll}")
        time.sleep(1.2)

        if critical:
            print("☠️  CRÍTICO DO MONSTRO! Você sente a dor profunda!")
            time.sleep(1.5)

        if attack_roll >= self.player.ac or critical:
            # O monstro calcula o dano (sem tipo, pois o tipo já está definido)
            raw_damage = self.monster.calculate_damage(critical)
            
            # Aplica modificador de dificuldade ao dano recebido pelo jogador
            modified_damage = int(raw_damage * self.difficulty_modifiers.get("damage_received", 1.0))
            
            # O jogador toma dano com o tipo correto
            is_player_dead, actual_damage, damage_reduced = self.player.take_damage(
                modified_damage, 
                self.monster.attack_type
            )
            
            print(f"💥 O ataque ACERTOU!")
            print(f"  Tipo de dano: {self.monster.attack_type}")
            print(f"  Dano bruto: {modified_damage}")
            
            if damage_reduced > 0:
                print(f"  🛡️ Sua resistência reduziu {damage_reduced} de dano!")
                
            print(f"  Dano efetivo: {actual_damage}")
            time.sleep(3.5)
            return is_player_dead
        else:
            print(f"🛡️ O ataque ERROU!")
            print(f"  Sua AC: {self.player.ac}")
            print(f"  Ataque necessário: {self.player.ac} (rolagem: {attack_roll})")
            time.sleep(1.3)
            return False
            
    def attempt_flee(self):
        """Tentativa de fuga com teste de destreza."""
        print("\nVocê tenta fugir...")
        time.sleep(0.5)

        self.player.recalculate()
        
        player_roll = roll_dice("1d20") + modifier(self.player.get_effective_intelligence())
        monster_roll = roll_dice("1d20") + modifier(self.monster.dexterity)

        print(f"Seu teste de fuga: {player_roll} vs. Teste do monstro: {monster_roll}")
        time.sleep(1.5)

        if player_roll > monster_roll:
            return True
        else:
            print("A fuga falhou! O monstro bloqueia seu caminho!")
            time.sleep(1)
            return False

    def get_random_item(self):
        """Retorna um item aleatório apropriado para o nível do jogador."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM items 
            WHERE category IN ('weapon', 'armor', 'shield', 'consumable', 'misc')
            ORDER BY RANDOM() 
            LIMIT 1
        ''')
        item = cursor.fetchone()
        if not item:
            return None
            
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, item))
    
    def lose_random_item(self):
        """Remove um item aleatório do inventário do jogador."""
        inventory = self.player.get_inventory()
        unequipped_items = [item for item in inventory if item.get('quantity', 0) > 0]

        if not unequipped_items:
            print("\nVocê não tem itens na mochila para perder!")
            return
            
        item_to_lose = random.choice(unequipped_items)
        success = remove_item_from_inventory(self.conn, item_to_lose['inventory_id'], quantity=1)
        
        if success:
            print(f"\n⚠️ Você perdeu '{get_display_name(item_to_lose)}' durante a batalha!")
        else:
            print(f"\nNão foi possível remover '{get_display_name(item_to_lose)}' do seu inventário.")
        time.sleep(1.5)

    def victory(self):
        """Recompensas por vitória com itens aleatórios."""
        border = "═" * 52
        chest = "📦"
        star = "✦"
        coin = "🪙"
        heart_drop = "❤️ "
        mana_drop = "🔷"

        exp_earned = int(self.monster.exp_reward * self.difficulty_modifiers.get("exp_multiplier", 1.0))
        base_gold = self.monster.get_gold_reward()
        gold_earned = int(base_gold * self.difficulty_modifiers.get("gold_multiplier", 1.0))

        print(f"\n{border}")
        print(f" O {self.monster.name} desaba sem vida. A vitória é sua.")
        print(f"{border}")
        
        print(f"\n{heart_drop} Vida: {self.player.hp}/{self.player.hp_max}")
        if self.player.mana_max > 0:
            print(f"{mana_drop} Mana: {self.player.mana}/{self.player.mana_max}")
        
        print(f"  🛡️ Resistência Física: {self.player.physical_resistance}")
        print(f"  ✨ Resistência Mágica: {self.player.magical_resistance}")
 
        print(f"\n{chest} Recompensas:")
        print(f"  {star} EXP Ganha: +{exp_earned}")
        print(f"  {coin} Ouro Encontrado: +{gold_earned}")

        if random.random() < 0.4:
            item_base_data = self.get_random_item()
            if item_base_data:
                try:
                    add_item_to_inventory(self.conn, self.player.id, item_base_data['id'], quantity=1, enhancement_level=0, enhancement_type=None)
                    print(f"  🎁 Item Encontrado: '{get_display_name(item_base_data)}'!")
                except Exception as e:
                    print(f"ERRO ao adicionar item: {str(e)}")
            else:
                print("  Nenhum item encontrado.")
        else:
            print("  Nenhum item encontrado.")

        self.player.gain_exp(exp_earned)
        self.player.gold += gold_earned
        
        from game.db_queries import update_character_gold
        update_character_gold(self.conn, self.player.id, self.player.gold)

        self.player.recalculate()
        
        print(f"\n{border}")
        input("Pressione Enter para continuar...")

    def defeat(self):
        """Derrota com perda de itens e tratamento de permadeath."""
        border = "═" * 52
        skull = "☠"

        print(f"\n{border}")
        print(f" {skull} Você foi derrotado...")
        print(f" {skull} Sua visão escurece enquanto o {self.monster.name} ruge em triunfo.")
        print(f"{border}")

        # Verifica se o modo permadeath está ativo (0 para não, 1 para sim)
        if self.player.permadeath == 1:
            self.player.hp = 0
            print(f"\n{skull*3} A MORTE É PERMANENTE! {skull*3}")
            print(f"{skull} Seu personagem {self.player.name} será apagado para sempre.")
            
            success = delete_character(self.conn, self.player.id)
            
            if success:
                print("Personagem deletado com sucesso do banco de dados.")
            else:
                print("Houve um erro ao deletar o personagem do banco de dados.")
                
            input("Pressione Enter para encerrar...")
            return True
        else:
            if random.random() < 0.3:
                self.lose_random_item()
            
            # Multiplicador de cura recebida também afeta a cura ao ser derrotado
            recovery_hp = int(self.player.hp_max * 0.1 * self.difficulty_modifiers.get("healing_received", 1.0))
            self.player.hp = max(1, recovery_hp)
            
            self.player.recalculate()
            
            print(f"\nPor um triz, você sobrevive e acorda horas depois, com o corpo dolorido.")
            input("Pressione Enter para continuar...")
        
        return False # Retorna False se o personagem não tiver permadeath