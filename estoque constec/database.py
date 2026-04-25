import sqlite3


def conectar():
    conn = sqlite3.connect("estoque.db")
    conn.row_factory = sqlite3.Row
    return conn


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
    UPDATE produto
    SET quantidade = ?
    WHERE id = ?
    """, (nova_quantidade, id_produto))

    conn.commit()
    conn.close()
    return True


def buscar_por_codigo(codigo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM produto WHERE codigo_barras = ?
    """, (codigo,))

    produto = cursor.fetchone()
    conn.close()
    return produto


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

    conn.commit()
    conn.close()


def remover_produto(id_produto, quantidade_vendida):
    return atualizar_quantidade(id_produto, -quantidade_vendida)


def buscar_produto_por_id(id_produto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produto WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()

    conn.close()
    return produto


if __name__ == "__main__":
    criar_tabela()
    criar_tabela_financeiro()
