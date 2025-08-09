📁 Estrutura do projeto:
README.md
Rust_Dice.spec
a.py
build.bat
error_log.txt
fim.html
game_settings.json
gerate_tree.py
main.py
requirements.txt
build
├── Rust_Dice
│   ├── Analysis-00.toc
│   ├── PKG-00.toc
│   ├── PYZ-00.pyz
│   ├── PYZ-00.toc
│   ├── Rust_Dice.pkg
│   ├── base_library.zip
│   ├── warn-Rust_Dice.txt
│   ├── xref-Rust_Dice.html
│   └── localpycs
data
├── __init__.py
├── data_tuples.py
├── database.db
├── populate_db.py
dist
├── Rust_Dice.exe
├── data
│   ├── database.db
├── documentacao
│   ├── change_log.md
│   └── tutorial.md
documentacao
├── change_log.md
├── tutorial.md
game
├── __init__.py
├── character.py
├── combat.py
├── config.py
├── database.py
├── db_queries.py
├── menus.py
├── monster.py
├── name_generator.py
├── utils.py
states
├── __init__.py
├── base_state.py
├── character
│   ├── __init__.py
│   ├── attributes_state.py
│   ├── inventory_state.py
├── city
│   ├── __init__.py
│   ├── blacksmith_state.py
│   ├── city_hub_base.py
│   ├── inn_state.py
│   ├── shop_state.py
│   ├── lindenrock
│   │   ├── hub.py
│   ├── vallengar
│   │   └── hub.py
├── creation
│   ├── __init__.py
│   ├── character_creation_state.py
│   ├── character_name_creator_state.py
├── system
│   ├── __init__.py
│   ├── delete_confirmation_state.py
│   ├── difficulty_state.py
│   ├── main_menu_state.py
│   ├── save_manager_state.py
│   ├── settings_state.py
└── world
    ├── __init__.py
    ├── combat_state.py
    ├── explore_state.py
    ├── gameplay_state.py
    └── rest_state.py

# Rust Dice: Echoes of Prometheus - RPG por Turnos (Com exe funcional)
**Versão:** 1.0.0  
**Inspirações:** D&D, Skyrim, Dragon's Dogma  
**Status:** Desenvolvimento em Progresso  

## Visão Geral
Rust Dice é um RPG por turnos em terminal que recria a experiência clássica de RPGs de mesa e videogame. O jogo oferece criação de personagem profunda, combate tático baseado em atributos, exploração de mundo e progressão de personagem.

## Funcionalidades Implementadas

### 🧙 Sistema de Criação de Personagem
- **Gênero e Nome**: 
  - Escolha manual ou geração aleatória baseada em gênero e cultura
- **Raças**: 
  - Modificadores nos 6 atributos básicos: Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma
- **Classes**: 
  - Valores iniciais de Vida/Mana
  - Armadura e item inicial
- **Antecedentes**: 
  - Modificadores em perícias (sistema em desenvolvimento)
- **Rolagem de Atributos**:
  - Rerolagem total ou individual
- **Dificuldade**: 
  - Vinculada ao permadeath (opções futuras: separação)

### 🎮 Menu Principal
- Gerenciamento de Saves:
  - Carregar, Deletar, Renomear personagens
- Opções: 
  - Novo Jogo, Sair

### 🌍 Gameplay Principal
- **Exploração**:
  - Encontros aleatórios com inimigos
  - Eventos de "nada acontece"
- **Descanso**:
  - Recuperação de vida com modificadores de atributos
  - Risco de emboscada
- **Viagem**:
  - Movimento entre cidades (Vallengar e Lindenrock)

### 📊 Menu do Personagem (Sempre Acessível)
1. **Atributos**: Visualização detalhada
2. **Inventário**:
   - Visualização de itens equipados
   - Sistema de equipar/desequipar
3. **Opções**:
   - Alterar dificuldade
   - Salvar e continuar
   - Salvar e sair
   - Deletar personagem

### ⚔️ Sistema de Combate (Turn-based)
- **Mecânicas**:
  - X1 contra monstros nivelados
  - Ataque = Atributo da arma + modificador vs CA do monstro
  - Dano = Valor da arma - Defesa física
  - Opções: Atacar ou Fugir
- **Consequências**:
  - **Vitória**: Ouro, XP + chance de item aleatório
  - **Derrota**: Perda de ouro + chance de perder item + revive com 1 HP

### 🏙️ Cidades (Vallengar & Lindenrock)
- **Lojas**:
  - 3 tipos com itens especializados
- **Estalagem**:
  - Cura completa mediante pagamento
- **Ferraria**:
  - Melhoria de equipamentos

## Próximos Passos (To-Do)
| Módulo           | Tarefas Pendentes                         | Prioridade |
|------------------|-------------------------------------------|------------|
| Sistema Perícias | Finalizar vinculação com antecedentes     | Alta       | 
| Combate          | Implementar resistência mágica            | Média      | ✅
| Dificuldade      | Separar permadeath de níveis de desafio   | Média      | ✅
| NPCs             | Implementar diálogos básicos              | Baixa      | ✅

## Como Executar

### Para executar pelo terminal:
```bash
python main.py
```

### Para criar o executável:
```bash
.\build.bat
```

### Outros comandos úteis:
```bash
# Gerar árvore de diretórios
python gerate_tree.py

# Popular banco de dados
python data/populate_db.py
```