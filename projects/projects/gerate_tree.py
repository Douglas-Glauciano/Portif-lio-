import os
import ast
import sys
import importlib.util
from collections import defaultdict

# Arvore de arquivos
def print_tree(start_path='.', prefix='', level=0, max_level=3, is_last=False, is_root=True):
    """Imprime estrutura de pastas com arquivos primeiro e cores opcionais"""
    if level > max_level:
        return
        
    try:
        all_entries = sorted(os.listdir(start_path))
    except (PermissionError, FileNotFoundError):
        return
        
    # Filtra diretórios/arquivos indesejados
    ignore = {'.git', '.idea', '__pycache__', '.DS_Store', 'venv', '.venv', '.vscode', 'env'}
    all_entries = [e for e in all_entries if e not in ignore and not e.endswith(('.pyc', '.pyo'))]
    
    # Separar arquivos e diretórios
    files = [e for e in all_entries if os.path.isfile(os.path.join(start_path, e))]
    dirs = [e for e in all_entries if os.path.isdir(os.path.join(start_path, e))]
    
    # Combinar: arquivos primeiro, depois diretórios
    entries = files + dirs
    
    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        is_last_entry = index == len(entries) - 1
        
        # Determinar conectores
        if is_root:
            connector = ''
        else:
            connector = '└── ' if (is_last and is_last_entry) else '├── '
        
        # Cores (opcional - desative se causar problemas)
        if os.path.isdir(path):
            # Azul para diretórios
            entry_str = f"\033[94m{entry}\033[0m"
        elif entry.endswith('.py'):
            # Verde para arquivos Python
            entry_str = f"\033[92m{entry}\033[0m"
        else:
            entry_str = entry
            
        print(prefix + connector + entry_str)
        
        if os.path.isdir(path):
            new_prefix = prefix
            if not is_root:
                new_prefix += '    ' if (is_last and is_last_entry) else '│   '
                
            print_tree(
                path, 
                new_prefix, 
                level + 1, 
                max_level,
                is_last=is_last_entry,
                is_root=False
            )

# Mapeamento completo de módulos para pacotes PyPI
MODULE_TO_PACKAGE = {
    'PIL': 'pillow',
    'bs4': 'beautifulsoup4',
    'sklearn': 'scikit-learn',
    'yaml': 'pyyaml',
    'attr': 'attrs',
    'OpenSSL': 'pyopenssl',
    'cryptography': 'cryptography',
    'IPython': 'ipython',
    'ipywidgets': 'ipywidgets',
    'keyring': 'keyring',
    'redis': 'redis',
    'sphinx': 'sphinx',
    'pyfiglet': 'pyfiglet',
    'colorama': 'colorama',
    'socks': 'PySocks',
    'ntlm': 'requests-ntlm',
    'httplib': None,  # stdlib
    'thread': None,    # stdlib
    'dummy_threading': None,
    'HTMLParser': None,
    'ConfigParser': None,
    'Queue': None,
    'StringIO': None,
    'android': None,
    'jnius': None,
    'java': None,
    'data': None,
    'game': None,
    'states': None,
    'ctags': None,
    'filelock': None,
    'distutils': None,
    'docutils': None,
    'imp': None,
    'pip': None,
    'google': None,
    'urllib2': None,
    'urllib3_secure_extra': None,
    'urlparse': None,
    'xmlrpclib': None,
    'htmlentitydefs': None,
    'dummy_thread': None,
    'data_tuples': None,
    'sqlite3': None,   # stdlib
    'os': None,         # stdlib
    'random': None,     # stdlib
    'time': None,       # stdlib
    'sys': None,        # stdlib
    'json': None,       # stdlib
    'math': None,       # stdlib
    're': None,         # stdlib
    'datetime': None,   # stdlib
    'collections': None,# stdlib
    'itertools': None,  # stdlib
    'functools': None,  # stdlib
    'threading': None,  # stdlib
    'subprocess': None, # stdlib
    'ast': None,        # stdlib
    'importlib': None,  # stdlib
    'pathlib': None,    # stdlib
    'typing': None,     # stdlib
    'logging': None,    # stdlib
    'argparse': None,   # stdlib
    'unittest': None,   # stdlib
    'pkgutil': None,    # stdlib
    'weakref': None,    # stdlib
    'copy': None,       # stdlib
    'pickle': None,     # stdlib
    'hashlib': None,    # stdlib
    'ssl': None,        # stdlib
    'socket': None,     # stdlib
    'selectors': None,  # stdlib
}

def is_stdlib_module(module_name):
    """Verificação robusta de módulos da stdlib"""
    # Primeiro verifica no dicionário de mapeamento
    if module_name in MODULE_TO_PACKAGE and MODULE_TO_PACKAGE[module_name] is None:
        return True
        
    # Verifica built-in modules
    if module_name in sys.builtin_module_names:
        return True
        
    # Verifica stdlib para Python 3.10+
    if sys.version_info >= (3, 10):
        if module_name in sys.stdlib_module_names:
            return True
            
    # Obter caminhos da stdlib de forma segura
    stdlib_paths = []
    
    # Caminho do módulo os
    try:
        stdlib_paths.append(os.path.dirname(os.__file__))
    except AttributeError:
        pass
        
    # Caminho da instalação do Python
    try:
        if hasattr(sys, 'base_prefix'):
            stdlib_paths.append(os.path.join(sys.base_prefix, 'Lib'))
    except AttributeError:
        pass
        
    # Se não encontrou caminhos, usa fallback
    if not stdlib_paths:
        # Tentativa de fallback para localização padrão
        python_path = sys.executable
        if python_path:
            lib_path = os.path.join(os.path.dirname(python_path), 'Lib')
            if os.path.exists(lib_path):
                stdlib_paths.append(lib_path)
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
            
        if spec.origin is None:  # Built-in module
            return True
            
        # Verifica se a origem está em um dos caminhos da stdlib
        for path in stdlib_paths:
            if path and spec.origin.startswith(path):
                return True
    except (ImportError, AttributeError, TypeError):
        pass
        
    return False

def is_project_module(module_name, project_dir):
    """Verifica se é um módulo local do projeto"""
    # Ignorar módulos muito curtos (provavelmente não são locais)
    if len(module_name) < 3:
        return False
        
    # Verifica arquivo .py
    py_file = os.path.join(project_dir, *module_name.split('.')) + ".py"
    if os.path.exists(py_file):
        return True
        
    # Verifica pacote (diretório com __init__.py)
    package_dir = os.path.join(project_dir, *module_name.split('.'))
    if os.path.isdir(package_dir):
        init_py = os.path.join(package_dir, "__init__.py")
        if os.path.exists(init_py):
            return True
            
    return False

def analyze_imports(filepath, project_dir):
    """Analisa imports com detecção de contexto aprimorada"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            try:
                tree = ast.parse(file.read(), filename=filepath)
            except (SyntaxError, UnicodeDecodeError, TypeError):
                return set()
    except (FileNotFoundError, PermissionError, OSError):
        return set()

    imports = set()
    for node in ast.walk(tree):
        # Import padrão: import lib
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                if module_name:
                    imports.add(module_name)
        
        # Import absoluto: from lib import module
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            module_name = node.module.split('.')[0]
            if module_name:
                imports.add(module_name)
    
    return imports

def scan_project(directory):
    """Varredura inteligente com múltiplas camadas de filtro"""
    project_dir = os.path.abspath(directory)
    found_imports = defaultdict(int)
    
    for root, _, files in os.walk(project_dir):
        # Ignorar diretórios irrelevantes
        ignore_dirs = ['venv', '.venv', '.git', '.idea', '__pycache__', 'env']
        if any(ignore_dir in root for ignore_dir in ignore_dirs):
            continue
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                modules = analyze_imports(filepath, project_dir)
                
                for module in modules:
                    # Ignorar módulos privados
                    if module.startswith('_'):
                        continue
                        
                    # Pular módulos da stdlib
                    if is_stdlib_module(module):
                        continue
                        
                    # Pular módulos do próprio projeto
                    if is_project_module(module, project_dir):
                        continue
                        
                    found_imports[module] += 1
    
    # Aplicar mapeamento
    dependencies = set()
    for module in found_imports:
        package = MODULE_TO_PACKAGE.get(module, module)
        
        # Se o pacote está marcado como None (stdlib), ignorar
        if package is None:
            continue
            
        dependencies.add(package)
    
    return dependencies

def generate_requirements(dependencies, output_file="requirements.txt"):
    """Gera o arquivo requirements.txt"""
    if not dependencies:
        print("\n⚠️ Nenhuma dependência externa identificada!")
        return None
        
    with open(output_file, "w") as f:
        for package in sorted(dependencies):
            f.write(f"{package}\n")
            
    print(f"\n✅ {len(dependencies)} dependências salvas em {output_file}")
    return os.path.abspath(output_file)

if __name__ == "__main__":
    print("🔍 Analisador de Dependências de Projeto Python")
    project_dir = input("\nCaminho do projeto [Enter para diretório atual]: ").strip() or "."
    
    print("\n📁 Estrutura do projeto:")
    print_tree(project_dir, max_level=3)
    
    print("\n⏳ Analisando dependências...")
    try:
        dependencies = scan_project(project_dir)
    except Exception as e:
        print(f"\n❌ Erro durante a análise: {e}")
        dependencies = set()
    
    if dependencies:
        print("\n📦 Dependências identificadas:")
        for dep in sorted(dependencies):
            print(f" - {dep}")
    else:
        print("\n🔍 Nenhuma dependência externa encontrada")
    
    req_file = generate_requirements(dependencies)
    
    # Sugestão para instalação
    if req_file:
        print("\n💡 Sugestão para instalar as dependências:")
        print(f"pip install -r {req_file}")