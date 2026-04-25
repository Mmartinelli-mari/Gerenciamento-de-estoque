#from: importar partes especificas de um modulo --
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)
from datetime import date
# importa tudo
import estoque

from database import (
    criar_tabela,
    criar_tabela_financeiro,
    listar_produtos,
    listar_financeiro,
    remover_produto,
    buscar_produto_por_id,
    buscar_por_codigo,
    registrar_financeiro
)
#app var que representa aplicação
app = Flask(__name__) # name informa onde está arquivo que está em execução
app.secret_key = "constec2024" # protege dados do usuario

# Criar tabelas
criar_tabela() #chma função
criar_tabela_financeiro()


def serializar_registro_financeiro(registro):
    return {
        "id": registro["id"],
        "descricao": registro["descricao"],
        "valor": float(registro["valor"] or 0),
        "tipo": registro["tipo"],
        "data_registro": registro["data_registro"]
    }


def criar_registro_financeiro_manual(tipo, descricao, valor):
    tipo_normalizado = (tipo or "").strip().upper()
    descricao_normalizada = (descricao or "").strip()

    if not tipo_normalizado:
        return False, "Informe o tipo do lançamento."

    if not descricao_normalizada:
        return False, "Informe a descrição do lançamento."

    try:
        valor_float = float(valor)
    except (TypeError, ValueError):
        return False, "Informe um valor válido."

    if valor_float <= 0:
        return False, "O valor deve ser maior que zero."

    registrar_financeiro(
        tipo_normalizado,
        descricao_normalizada,
        valor_float,
        date.today().isoformat()
    )

    registro = listar_financeiro()[0]
    return True, serializar_registro_financeiro(registro)


# -------------------------
# HOME
# -------------------------

@app.route("/") # quando colocar no navegador o flask chama --quem chama o que no codigo?
def home(): # define função 
    return render_template("home.html") # a definição

# @ é decorador - age quando uma função será execultada quando a URL for cessada
# -------------------------
# CADASTRAR PRODUTO
# -------------------------

@app.route("/cadastrar", methods=["GET", "POST"])# GET busca info POST envia dados
def cadastrar():

    if request.method == "POST":

        nome = request.form["nome"]
        codigo = request.form["codigo"]
        descricao = request.form["descricao"]
        quantidade = int(request.form["quantidade"])
        preco = float(request.form["preco"])
        tipo = request.form["tipo"]

        estoque.cadastrar_produto_fluxo(
            nome,
            codigo if codigo != "" else None,
            descricao,
            quantidade,
            preco,
            tipo
        )

        flash("Produto cadastrado com sucesso!")# flash recurso flask

        return redirect(url_for("cadastrar"))

    return render_template("cadastrar.html")


# -------------------------
# ESTOQUE
# -------------------------

@app.route("/estoque")
def estoque_view():

    produtos = listar_produtos()

    return render_template(
        "estoque.html",
        produtos=produtos
    )


# -------------------------
# VENDA RAPIDA
# -------------------------

@app.route("/venda-rapida", methods=["GET", "POST"])
def venda_rapida():
    produto = None
    busca_realizada = False
    codigo_buscado = ""

    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        codigo_buscado = codigo
        busca_realizada = True

        if codigo:
            produto = buscar_por_codigo(codigo)

    return render_template(
        "venda_rapida.html",
        produto=produto,
        busca_realizada=busca_realizada,
        codigo_buscado=codigo_buscado
    )


# -------------------------
# FINANCEIRO
# -------------------------

@app.route("/financeiro")
def financeiro():

    registros = listar_financeiro()

    return render_template(
        "financeiro.html",
        registros=registros
    )


@app.route("/api/financeiro", methods=["GET", "POST"])
def api_financeiro():
    if request.method == "GET":
        registros = [
            serializar_registro_financeiro(registro)
            for registro in listar_financeiro()
        ]
        return jsonify({"registros": registros})

    dados = request.get_json(silent=True) or request.form
    sucesso, resposta = criar_registro_financeiro_manual(
        dados.get("tipo"),
        dados.get("descricao"),
        dados.get("valor")
    )

    if not sucesso:
        return jsonify({"erro": resposta}), 400

    return jsonify({
        "mensagem": "Registro financeiro adicionado!",
        "registro": resposta
    }), 201

# Nova rota — vender produto
@app.route("/vender/<int:id_produto>", methods=["POST"])
def vender(id_produto):
    origem = request.form.get("origem", "")
    destino = "venda_rapida" if origem == "venda_rapida" else "estoque_view"

    try:
        quantidade = int(request.form["quantidade"])
    except (TypeError, ValueError):
        flash("Quantidade inválida.")
        return redirect(url_for(destino))

    if quantidade <= 0:
        flash("A quantidade para venda deve ser maior que zero.")
        return redirect(url_for(destino))

    produto = buscar_produto_por_id(id_produto)

    if produto and produto["quantidade"] >= quantidade:
        total = quantidade * (produto["preco"] or 0)
        remover_produto(id_produto, quantidade)
        registrar_financeiro(
            tipo="VENDA",
            descricao=f"Venda de {quantidade}x {produto['nome']}",
            valor=total,
            data=None  # ou use datetime.date.today().isoformat()
        )
        flash(f"Venda registrada! R$ {total:.2f} lançado no financeiro.")
    else:
        flash("Quantidade insuficiente no estoque.")

    return redirect(url_for(destino))


# Nova rota — registrar manutenção ou entrada manual
@app.route("/financeiro/registrar", methods=["POST"])
def registrar_manual():
    sucesso, resposta = criar_registro_financeiro_manual(
        request.form.get("tipo"),
        request.form.get("descricao"),
        request.form.get("valor")
    )

    if not sucesso:
        flash(resposta)
        return redirect(url_for("financeiro"))

    flash("Registro financeiro adicionado!")
    return redirect(url_for("financeiro"))

# -------------------------
# EXECUÇÃO
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
