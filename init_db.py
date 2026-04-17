import sys
import os

# Adiciona o diretório atual ao path para importar o db_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    print("Iniciando criação do banco de dados local...")
    db = DatabaseManager()
    
    # O caminho do banco agora é relativo ao diretório do projeto
    print(f"O banco de dados será criado em: {db.db_path}")
    
    try:
        db.inicializar()
        print("Banco de dados inicializado com sucesso!")
        
        if os.path.exists(db.db_path):
            print(f"Arquivo '{os.path.basename(db.db_path)}' criado com sucesso no diretório raiz.")
        else:
            print("Erro: O arquivo do banco de dados não foi encontrado após a inicialização.")
            
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

if __name__ == "__main__":
    main()
