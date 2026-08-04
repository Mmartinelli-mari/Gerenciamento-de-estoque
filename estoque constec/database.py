import sqlite3


def conectar():
    conn = sqlite3.connect("estoque.db")
    conn.row_factory = sqlite3.Row
    return conn

# O módulo database.py é responsável por gerenciar a conexão com o banco de dados SQLite, criar as tabelas necessárias para o funcionamento do sistema e fornecer funções para manipular os dados relacionados a produtos, financeiro e manutenções. Ele inclui funções para criar tabelas, cadastrar produtos, listar produtos, atualizar quantidades, buscar produtos por código ou ID, registrar lançamentos financeiros, listar registros financeiros, deletar lançamentos e registrar manutenções, além de listar e deletar manutenções. O módulo é projetado para ser utilizado pelo app.py para realizar as operações de backend do sistema de estoque e financeiro.
# ─────────────────────────────────────────
# CRIAR TABELAS
# ─────────────────────────────────────────

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        codigo_barras TEXT,
        descricao TEXT,
        quantidade INTEGER NOT NULL,
        preco REAL,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()


def criar_tabela_financeiro():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        descricao TEXT,
        valor REAL NOT NULL,
        data_registro TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("PRAGMA table_info(financeiro)")
    colunas = {coluna["name"] for coluna in cursor.fetchall()}

    if "data_registro" not in colunas:
        cursor.execute("""
        ALTER TABLE financeiro
        ADD COLUMN data_registro TEXT DEFAULT CURRENT_TIMESTAMP
        """)

    if "data" not in colunas:
        cursor.execute("""
        ALTER TABLE financeiro
        ADD COLUMN data TEXT
        """)

    conn.commit()
    conn.close()


def criar_tabela_manutencao():
    """
    Tabela dedicada para manutenções — guarda todos os dados
    do aparelho e do cliente. O valor já é lançado na tabela
    financeiro automaticamente pelo app.py.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manutencao (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente     TEXT,
        telefone    TEXT,
        aparelho    TEXT NOT NULL,
        modelo      TEXT,
        problema    TEXT,
        valor       REAL NOT NULL,
        pagamento   TEXT,
        data_registro TEXT DEFAULT CURRENT_TIMESTAMP,
        id_financeiro INTEGER  -- referência ao lançamento na tabela financeiro
    )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# PRODUTO
# ─────────────────────────────────────────

def cadastrar_produto(nome, codigo_barras, descricao, quantidade, preco, tipo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO produto (nome, codigo_barras, descricao, quantidade, preco, tipo)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, codigo_barras, descricao, quantidade, preco, tipo))

    conn.commit()
    conn.close()


def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produto ORDER BY id DESC")
    produtos = cursor.fetchall()

    conn.close()
    return produtos


def atualizar_quantidade(id_produto, quantidade):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT quantidade FROM produto WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()

    if not produto:
        conn.close()
        return False

    nova_quantidade = produto["quantidade"] + quantidade

    if nova_quantidade < 0:
        conn.close()
        return False

    cursor.execute("""
    UPDATE produto SET quantidade = ? WHERE id = ?
    """, (nova_quantidade, id_produto))

    conn.commit()
    conn.close()
    return True


def buscar_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produto WHERE codigo_barras = ?", (codigo,))
    produto = cursor.fetchone()

    conn.close()
    return produto


def buscar_produto_por_id(id_produto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produto WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()

    conn.close()
    return produto


def remover_produto(id_produto, quantidade_vendida):
    return atualizar_quantidade(id_produto, -quantidade_vendida)


# ─────────────────────────────────────────
# FINANCEIRO
# ─────────────────────────────────────────

def registrar_financeiro(tipo, descricao, valor, data=None):
    conn = conectar()
    cursor = conn.cursor()

    if data is None:
        cursor.execute("""
        INSERT INTO financeiro (tipo, descricao, valor)
        VALUES (?, ?, ?)
        """, (tipo, descricao, valor))
    else:
        cursor.execute("""
        INSERT INTO financeiro (tipo, descricao, valor, data_registro)
        VALUES (?, ?, ?, ?)
        """, (tipo, descricao, valor, data))

    id_inserido = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_inserido   # ← retorna o id para poder linkar com manutenção


def listar_financeiro():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        descricao,
        valor,
        tipo,
        COALESCE(data_registro, data) AS data_registro
    FROM financeiro
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    conn.close()
    return registros


def deletar_lancamento(id_lancamento):
    """Remove um lançamento da tabela financeiro pelo id."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM financeiro WHERE id = ?", (id_lancamento,))

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# MANUTENÇÃO
# ─────────────────────────────────────────

def registrar_manutencao(cliente, telefone, aparelho, modelo,
                          problema, valor, pagamento):
    """
    Salva a manutenção no banco E lança automaticamente
    na tabela financeiro. Retorna o id da manutenção.
    """
    from datetime import datetime
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    descricao_fin = f"Manutenção: {aparelho}" + (f" — {modelo}" if modelo else "")

    # 1) lança no financeiro e pega o id gerado
    id_fin = registrar_financeiro(
        tipo="MANUTENCAO",
        descricao=descricao_fin,
        valor=valor
    )

    # 2) salva detalhes na tabela manutencao
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO manutencao
        (cliente, telefone, aparelho, modelo, problema, valor, pagamento, data_registro, id_financeiro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (cliente, telefone, aparelho, modelo, problema, valor, pagamento, agora, id_fin))

    id_manut = cursor.lastrowid
    conn.commit()
    conn.close()

    return id_manut


def listar_manutencoes():
    """Retorna todas as manutenções em ordem decrescente."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, cliente, telefone, aparelho, modelo,
           problema, valor, pagamento, data_registro, id_financeiro
    FROM manutencao
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    conn.close()
    return registros


def deletar_manutencao(id_manutencao):
    """
    Remove a manutenção e, se houver, o lançamento financeiro vinculado.
    """
    conn = conectar()
    cursor = conn.cursor()

    # descobre o id_financeiro vinculado
    cursor.execute("SELECT id_financeiro FROM manutencao WHERE id = ?", (id_manutencao,))
    row = cursor.fetchone()

    if row and row["id_financeiro"]:
        cursor.execute("DELETE FROM financeiro WHERE id = ?", (row["id_financeiro"],))

    cursor.execute("DELETE FROM manutencao WHERE id = ?", (id_manutencao,))

    conn.commit()
    conn.close()

def criar_tabela_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def buscar_usuario_por_email(email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def criar_usuario(email, senha_hash):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
        (email, senha_hash)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# INIT (execução direta)
# ─────────────────────────────────────────

if __name__ == "__main__":
    criar_tabela()
    criar_tabela_financeiro()
    criar_tabela_manutencao()
    criar_tabela_usuarios()
    print("Tabelas criadas com sucesso.")