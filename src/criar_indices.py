from db import get_database

# Conecta ao banco
db = get_database()

if db is not None:
    print("🔄 Reiniciando índices Full Text Search...")

    # --- 1. Índice para VAGAS ---
    try:
        # Tenta apagar o índice antigo se ele existir
        db.vagas.drop_index("search_index_vagas")
        print("🗑️ Índice antigo de Vagas removido.")
    except Exception:
        pass # Se não existir, segue a vida

    try:
        # Cria o novo
        db.vagas.create_index([
            ("titulo", "text"),
            ("descricao", "text"),
            ("requisitos", "text"),
            ("skills", "text")
        ], name="search_index_vagas")
        print("✅ Novo índice de VAGAS criado!")
    except Exception as e:
        print(f"❌ Erro ao criar índice de vagas: {e}")


    # --- 2. Índice para CANDIDATOS ---
    try:
        # Tenta apagar o índice antigo
        db.candidatos.drop_index("search_index_candidatos")
        print("🗑️ Índice antigo de Candidatos removido.")
    except Exception:
        pass

    try:
        # Cria o novo
        db.candidatos.create_index([
            ("resumo", "text"),
            ("skills", "text"),
            ("experiencia", "text"),
            ("formacao", "text"),
            ("nome", "text")
        ], name="search_index_candidatos")
        print("✅ Novo índice de CANDIDATOS criado!")
    except Exception as e:
        print(f"❌ Erro ao criar índice de candidatos: {e}")

else:
    print("Erro de conexão. Verifique o secrets.toml")