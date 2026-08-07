from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory,
    session
)
from flask import Flask, request, render_template
import sqlite3

# flask é o microframework web usado para criar a aplicação. Ele fornece ferramentas para lidar com rotas, templates, requisições e respostas HTTP, entre outras funcionalidades essenciais para o desenvolvimento web.
from datetime import date
# datetime é uma biblioteca padrão do Python que fornece classes para manipulação de datas e horas. Aqui, estamos importando a classe date, que representa uma data (ano, mês e dia) sem informações de tempo. Ela é usada para registrar a data de um lançamento financeiro ou manutenção.
import estoque
# estoque é um módulo local (provavelmente um arquivo estoque.py) que contém funções relacionadas à gestão de produtos em estoque, como cadastrar produtos, listar produtos, remover produtos, etc. Ele é importado para ser utilizado nas rotas que lidam com o estoque de produtos.
from werkzeug.security import check_password_hash
from database import (
    criar_tabela,
    criar_tabela_financeiro,
    criar_tabela_manutencao, 
    criar_tabela_usuarios,     # ← 
    listar_produtos,
    listar_financeiro,
    listar_manutencoes,           # ← 
    remover_produto,
    buscar_produto_por_id,
    buscar_por_codigo,
    registrar_financeiro,
    registrar_manutencao,         # ← 
    deletar_lancamento, 
    buscar_usuario_por_email,          # ← 
    deletar_manutencao            # ← 
)
# database é um módulo local (provavelmente um arquivo database.py) que contém funções para interagir com o banco de dados SQLite. Ele inclui funções para criar tabelas, listar registros, inserir novos registros e deletar registros tanto para o financeiro quanto para as manutenções.
from database import criar_tabela, criar_tabela_financeiro

criar_tabela()
criar_tabela_financeiro()
print("Tabelas criadas!")
app = Flask(__name__)
# Flask é a classe principal do framework Flask. Criamos uma instância dela chamada app, que representa a aplicação web. Essa instância é usada para definir rotas, configurar a aplicação e executar o servidor web.
app.secret_key = "constec2024"
# A secret key é usada pelo Flask para criptografar sessões e mensagens flash. Ela deve ser mantida em segredo em um ambiente de produção, mas para fins de desenvolvimento, uma string simples pode ser usada.

@app.errorhandler(404)
def not_found(_):
    return render_template("home.html"), 404


# ─── Criar tabelas ao iniciar ───────────────
criar_tabela()
criar_tabela_financeiro()
criar_tabela_manutencao()    
criar_tabela_usuarios()     
# Essas funções garantem que as tabelas necessárias para a aplicação existam no banco de dados. Se as tabelas já existirem, elas não serão recriadas, evitando perda de dados.

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def serializar_registro_financeiro(registro):
    return {
        "id":            registro["id"],
        "descricao":     registro["descricao"],
        "valor":         float(registro["valor"] or 0),
        "tipo":          registro["tipo"],
        "data_registro": registro["data_registro"]
    }
# Essa função é um helper que recebe um registro financeiro (provavelmente um dicionário ou objeto retornado do banco de dados) e o transforma em um formato mais adequado para ser enviado como resposta JSON. Ela garante que o valor seja convertido para float e que as chaves estejam padronizadas.


def criar_registro_financeiro_manual(tipo, descricao, valor):
    tipo_normalizado      = (tipo or "").strip().upper()
    descricao_normalizada = (descricao or "").strip()
    # O valor é validado e convertido para float, garantindo que seja um número válido e positivo.

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
# Se todas as validações passarem, o lançamento é registrado no banco de dados usando a função registrar_financeiro. A data do lançamento é definida como a data atual usando date.today().isoformat().
    registrar_financeiro(
        tipo_normalizado,
        descricao_normalizada,
        valor_float,
        date.today().isoformat()
    )

    registro = listar_financeiro()[0]
    return True, serializar_registro_financeiro(registro)
# A função retorna uma tupla onde o primeiro elemento é um booleano indicando o sucesso da operação e o segundo elemento é a mensagem de erro ou o registro criado, dependendo do resultado da validação.

# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")
# A rota "/" é a página inicial da aplicação. Quando um usuário acessa essa rota, a função home() é chamada, que renderiza o template "home.html". Esse template provavelmente contém a interface principal do sistema, com links para as outras funcionalidades como estoque, vendas rápidas, financeiro e manutenções.

@app.route('/static/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def service_worker():
    """Disponibiliza o SW na raiz para que ele controle todo o site."""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = buscar_usuario_por_email(email)

        if usuario and check_password_hash(usuario["senha"], senha):
            session["admin"] = True
            flash("Login realizado com sucesso!")
            return redirect("/estoque")
        else:
            flash("Email ou senha inválidos.")
            return redirect("/login")

    return render_template("login.html")

    

# ─────────────────────────────────────────────
# CADASTRAR PRODUTO
# ─────────────────────────────────────────────

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome       = request.form["nome"]
        codigo     = request.form["codigo"]
        descricao  = request.form["descricao"]
        quantidade = int(request.form["quantidade"])
        preco      = float(request.form["preco"])
        tipo       = request.form["tipo"]
# O código de barras é opcional, mas se for fornecido, ele é incluído no cadastro do produto. A função estoque.cadastrar_produto_fluxo é chamada para adicionar o produto ao banco de dados e atualizar o estoque.
        estoque.cadastrar_produto_fluxo(
            nome,
            codigo if codigo != "" else None,
            descricao,
            quantidade,
            preco,
            tipo
        )
# Após o cadastro, uma mensagem de sucesso é exibida usando flash e o usuário é redirecionado de volta para a página de cadastro.
        flash("Produto cadastrado com sucesso!")
        return redirect(url_for("cadastrar"))

    return render_template("cadastrar.html")
# Se a requisição for GET, o template "cadastrar.html" é renderizado, exibindo o formulário para cadastro de um novo produto.

# ─────────────────────────────────────────────
# ESTOQUE
# ─────────────────────────────────────────────

@app.route("/estoque")
def estoque_view():
    produtos = listar_produtos()
    return render_template("estoque.html", produtos=produtos)

# A rota "/estoque" exibe a página de estoque, onde a função estoque_view() é chamada. Ela obtém a lista de produtos do banco de dados usando listar_produtos() e passa essa lista para o template "estoque.html", que é responsável por exibir os produtos em uma tabela ou formato adequado.
# ─────────────────────────────────────────────
# VENDA RÁPIDA
# ─────────────────────────────────────────────

@app.route("/venda-rapida", methods=["GET", "POST"])
def venda_rapida():
    produto         = None
    busca_realizada = False
    codigo_buscado  = ""
# A rota "/venda-rapida" permite que o usuário busque um produto pelo código de barras e realize uma venda rápida. Se a requisição for POST, o código de barras é obtido do formulário; se for GET, ele pode ser passado como parâmetro na URL. O produto correspondente é buscado no banco de dados usando buscar_por_codigo() e as informações são passadas para o template "venda_rapida.html" para exibição.
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
    else:
        codigo = request.args.get("codigo", "").strip()

    if codigo:
        codigo_buscado  = codigo
        busca_realizada = True
        produto         = buscar_por_codigo(codigo)

    return render_template(
        "venda_rapida.html",
        produto=produto,
        busca_realizada=busca_realizada,
        codigo_buscado=codigo_buscado
    )

# A página de venda rápida é projetada para facilitar a venda de produtos usando o código de barras, permitindo que o usuário encontre rapidamente o produto e registre a venda sem precisar navegar pelo estoque completo.
@app.route("/cadastrar-rapido", methods=["POST"])
def cadastrar_rapido():
    nome      = request.form.get("nome",      "").strip()
    codigo    = request.form.get("codigo",    "").strip()
    descricao = request.form.get("descricao", "").strip()
    tipo      = request.form.get("tipo",      "").strip()
# O código de barras é opcional, mas se for fornecido, ele é incluído no cadastro do produto. A função estoque.cadastrar_produto_fluxo é chamada para adicionar o produto ao banco de dados e atualizar o estoque.
    try:
        quantidade = int(request.form.get("quantidade", ""))
        preco      = float(request.form.get("preco", ""))
    except (TypeError, ValueError):
        flash("Quantidade e preço precisam ser válidos.")
        return redirect(url_for("venda_rapida", codigo=codigo))
# Validações básicas para garantir que os campos obrigatórios sejam preenchidos e que quantidade e preço sejam números válidos. Se alguma validação falhar, uma mensagem de erro é exibida e o usuário é redirecionado de volta para a página de venda rápida com o código de barras preenchido para facilitar a correção.
    if not nome or not tipo:
        flash("Nome e tipo são obrigatórios para o cadastro rápido.")
        return redirect(url_for("venda_rapida", codigo=codigo))
# Validações para garantir que quantidade e preço sejam positivos. Se alguma dessas condições falhar, uma mensagem de erro é exibida e o usuário é redirecionado de volta para a página de venda rápida.
    if quantidade < 0:
        flash("A quantidade não pode ser negativa.")
        return redirect(url_for("venda_rapida", codigo=codigo))

    if preco < 0:
        flash("O preço não pode ser negativo.")
        return redirect(url_for("venda_rapida", codigo=codigo))
# O código de barras é opcional, mas se for fornecido, ele é incluído no cadastro do produto. A função estoque.cadastrar_produto_fluxo é chamada para adicionar o produto ao banco de dados e atualizar o estoque.
    estoque.cadastrar_produto_fluxo(
        nome,
        codigo if codigo != "" else None,
        descricao,
        quantidade,
        preco,
        tipo
    )
# Após o cadastro, uma mensagem de sucesso é exibida usando flash e o usuário é redirecionado de volta para a página de venda rápida, com o código de barras preenchido para facilitar a venda do produto recém-cadastrado.
    flash("Produto cadastrado com sucesso na venda rápida!") 
    return redirect(url_for("venda_rapida", codigo=codigo)) 
# A rota "/cadastrar-rapido" é usada para cadastrar um produto diretamente da página de venda rápida. Ela processa os dados do formulário, realiza as validações necessárias e, se tudo estiver correto, cadastra o produto e redireciona o usuário de volta para a página de venda rápida com uma mensagem de sucesso.

# ─────────────────────────────────────────────
# VENDER (descontar estoque + lançar financeiro) 
# ─────────────────────────────────────────────

@app.route("/vender/<int:id_produto>", methods=["POST"])
def vender(id_produto):
    origem  = request.form.get("origem", "")
    destino = "venda_rapida" if origem == "venda_rapida" else "estoque_view"
# A função vender() é responsável por processar a venda de um produto. Ela recebe o ID do produto a ser vendido e a quantidade desejada. A função verifica se a quantidade solicitada está disponível em estoque, calcula o valor total da venda, atualiza o estoque e registra a venda no financeiro. Se a venda for realizada a partir da página de venda rápida, o usuário é redirecionado de volta para essa página; caso contrário, ele é redirecionado para a página de estoque.  
    try:
        quantidade = int(request.form["quantidade"])
    except (TypeError, ValueError):
        flash("Quantidade inválida.")
        return redirect(url_for(destino))

    if quantidade <= 0:
        flash("A quantidade para venda deve ser maior que zero.")
        return redirect(url_for(destino))

    produto        = buscar_produto_por_id(id_produto)
    codigo_retorno = produto["codigo_barras"] if produto else ""

    if produto and produto["quantidade"] >= quantidade:
        total = quantidade * (produto["preco"] or 0)
        remover_produto(id_produto, quantidade)
        registrar_financeiro(
            tipo="VENDA",
            descricao=f"Venda de {quantidade}x {produto['nome']}",
            valor=total,
            data=None
        )
        # O valor total da venda é calculado multiplicando a quantidade vendida pelo preço do produto. O estoque é atualizado removendo a quantidade vendida e o lançamento financeiro é registrado com o tipo "VENDA", uma descrição detalhada e o valor total da venda. Após a venda, uma mensagem de sucesso é exibida usando flash, indicando o valor que foi lançado no financeiro.
        flash(f"Venda registrada! R$ {total:.2f} lançado no financeiro.")
    else:
        flash("Quantidade insuficiente no estoque.")

    if origem == "venda_rapida" and codigo_retorno:
        return redirect(url_for("venda_rapida", codigo=codigo_retorno))

    return redirect(url_for(destino))

# A rota "/vender/<int:id_produto>" é usada para processar a venda de um produto específico. Ela espera uma requisição POST com a quantidade a ser vendida e, opcionalmente, a origem da venda (para redirecionamento). A função realiza as validações necessárias, atualiza o estoque, registra a venda no financeiro e redireciona o usuário para a página apropriada com mensagens de sucesso ou erro.
# ─────────────────────────────────────────────
# FINANCEIRO — página
# ─────────────────────────────────────────────

@app.route("/financeiro")
def financeiro():
    return render_template("financeiro.html")
    # A tabela é carregada via fetch('/api/financeiro') pelo JS do template
# A rota "/financeiro" exibe a página do financeiro, onde o template "financeiro.html" é renderizado. Esse template provavelmente contém uma tabela ou interface para exibir os lançamentos financeiros, que são carregados dinamicamente usando JavaScript através de uma requisição para a API "/api/financeiro".

# ─────────────────────────────────────────────
# API FINANCEIRO — GET / POST
# ─────────────────────────────────────────────

@app.route("/api/financeiro", methods=["GET", "POST"])
def api_financeiro():

    if request.method == "GET":
        registros = [
            serializar_registro_financeiro(r)
            for r in listar_financeiro()
        ]
        return jsonify({"registros": registros})

    # POST — lançamento manual (entrada ou saída)
    dados   = request.get_json(silent=True) or request.form
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
# A rota "/api/financeiro" é uma API RESTful que suporta tanto requisições GET quanto POST. O método GET retorna a lista de registros financeiros em formato JSON, enquanto o método POST permite criar um novo lançamento financeiro manualmente, recebendo os dados no corpo da requisição. A função criar_registro_financeiro_manual é usada para validar e criar o lançamento, e a resposta JSON indica o sucesso ou erro da operação.

# ─────────────────────────────────────────────
# API FINANCEIRO — DELETE  ← NOVO
# ─────────────────────────────────────────────

@app.route("/api/financeiro/<int:id_lancamento>", methods=["DELETE"])
def api_financeiro_delete(id_lancamento):
    """Remove um lançamento da tabela financeiro pelo id."""
    try:
        deletar_lancamento(id_lancamento)
        return jsonify({"mensagem": "Lançamento removido.", "id": id_lancamento})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
# A rota "/api/financeiro/<int:id_lancamento>" com o método DELETE permite remover um lançamento financeiro específico pelo seu ID. A função deletar_lancamento é chamada para realizar a remoção no banco de dados, e a resposta JSON indica se a operação foi bem-sucedida ou se ocorreu um erro.

# ─────────────────────────────────────────────
# API MANUTENÇÃO — GET / POST  ← NOVO
# ─────────────────────────────────────────────

@app.route("/api/manutencao", methods=["GET", "POST"])
def api_manutencao():

    if request.method == "GET":
        registros = []
        for r in listar_manutencoes():
            registros.append({
                "id":            r["id"],
                "cliente":       r["cliente"] or "",
                "telefone":      r["telefone"] or "",
                "aparelho":      r["aparelho"],
                "modelo":        r["modelo"] or "",
                "problema":      r["problema"] or "",
                "valor":         float(r["valor"] or 0),
                "pagamento":     r["pagamento"] or "",
                "data_registro": r["data_registro"],
                "id_financeiro": r["id_financeiro"]
            })
        return jsonify({"manutencoes": registros})
# A rota "/api/manutencao" com o método GET retorna a lista de manutenções registradas em formato JSON, incluindo detalhes como cliente, telefone, aparelho, modelo, problema, valor, pagamento, data de registro e o ID do lançamento financeiro vinculado.
    # POST — nova manutenção
    dados = request.get_json(silent=True) or {}

    aparelho = (dados.get("aparelho") or "").strip()
    problema = (dados.get("problema") or "").strip()
# O valor é validado e convertido para float, garantindo que seja um número válido e positivo. Se alguma validação falhar, uma resposta JSON com o erro correspondente é retornada.
    try:
        valor = float(dados.get("valor", 0))
    except (TypeError, ValueError):
        return jsonify({"erro": "Valor inválido."}), 400

    if not aparelho or not problema or valor <= 0:
        return jsonify({"erro": "Aparelho, problema e valor são obrigatórios."}), 400

    id_manut = registrar_manutencao(
        cliente   = (dados.get("cliente")   or "").strip(),
        telefone  = (dados.get("telefone")  or "").strip(),
        aparelho  = aparelho,
        modelo    = (dados.get("modelo")    or "").strip(),
        problema  = problema,
        valor     = valor,
        pagamento = (dados.get("pagamento") or "").strip()
    )
# Se o registro for criado com sucesso, uma resposta JSON é retornada contendo uma mensagem de sucesso e o ID da manutenção recém-criada. Essa resposta pode ser usada pelo frontend para atualizar a interface do usuário ou fornecer feedback ao usuário.
    return jsonify({
        "mensagem":    "Manutenção registrada e lançada no financeiro!",
        "id_manutencao": id_manut
    }), 201

# A rota "/api/manutencao" suporta tanto requisições GET para listar as manutenções quanto POST para criar uma nova manutenção. O método POST espera receber os dados da manutenção no corpo da requisição em formato JSON, realiza as validações necessárias e, se tudo estiver correto, registra a manutenção e o lançamento financeiro correspondente, retornando uma resposta JSON com o resultado da operação.
# ─────────────────────────────────────────────
# API MANUTENÇÃO — DELETE  ← NOVO
# ─────────────────────────────────────────────

@app.route("/api/manutencao/<int:id_manutencao>", methods=["DELETE"])
def api_manutencao_delete(id_manutencao):
    """
    Remove a manutenção e o lançamento financeiro vinculado.
    """
    try:
        deletar_manutencao(id_manutencao)
        return jsonify({"mensagem": "Manutenção removida.", "id": id_manutencao})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# A rota "/api/manutencao/<int:id_manutencao>" com o método DELETE permite remover uma manutenção específica pelo seu ID, bem como o lançamento financeiro vinculado a essa manutenção. A função deletar_manutencao é chamada para realizar a remoção no banco de dados, e a resposta JSON indica se a operação foi bem-sucedida ou se ocorreu um erro.
# ─────────────────────────────────────────────
# FINANCEIRO — formulário sem JS (fallback)
# ─────────────────────────────────────────────

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

# A rota "/financeiro/registrar" é um fallback para registrar um lançamento financeiro manualmente usando um formulário HTML sem JavaScript. Ela processa os dados do formulário, chama a função criar_registro_financeiro_manual para validar e criar o lançamento, e usa flash para exibir mensagens de sucesso ou erro antes de redirecionar o usuário de volta para a página do financeiro.
# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    # O modo debug é ativado para facilitar o desenvolvimento, permitindo que o servidor reinicie automaticamente quando mudanças no código forem detectadas e exibindo mensagens de erro detalhadas no navegador.                                                                                                                         
