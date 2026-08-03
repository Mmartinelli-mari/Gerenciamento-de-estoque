# ============================================================
# 1. ADICIONE NO app.py
# ============================================================
# Cole essas duas rotas junto com as outras rotas do app.py

@app.route("/venda-rapida", methods=["GET", "POST"])
def venda_rapida():
    produto = None
    busca_realizada = False
    codigo_buscado = ""

    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        codigo_buscado = codigo
        busca_realizada = True
        produto = buscar_por_codigo(codigo)

    return render_template(
        "venda_rapida.html",
        produto=produto,
        busca_realizada=busca_realizada,
        codigo_buscado=codigo_buscado
    )


# ============================================================
# 2. ATUALIZE a rota /vender no app.py
# ============================================================
# Troque o return final da função vender() para redirecionar
# de volta para venda_rapida se a venda veio de lá:

@app.route("/vender/<int:id_produto>", methods=["POST"])
def vender(id_produto):
    quantidade = int(request.form["quantidade"])
    origem = request.form.get("origem", "")
    produto = buscar_produto_por_id(id_produto)

    if produto and produto[4] >= quantidade:
        total = quantidade * produto[5]
        remover_produto(id_produto, quantidade)
        registrar_financeiro(
            tipo="VENDA",
            descricao=f"Venda de {quantidade}x {produto[1]}",
            valor=total,
            data=None
        )
        flash(f"Venda registrada! R$ {total:.2f} lançado no financeiro.")
    else:
        flash("Quantidade insuficiente no estoque.")

    # Redireciona de volta para onde veio
    if origem == "venda_rapida":
        return redirect(url_for("venda_rapida"))
    return redirect(url_for("estoque_view"))


# ============================================================
# 3. ADICIONE NO base.html — dentro da <nav>, em nav-links
# ============================================================
# Adicione essa linha junto com os outros links do menu:

# <a href="/venda-rapida">Venda Rápida</a>

# Exemplo de como ficará o bloco nav-links no base.html:
# <div class="nav-links">
#     <a href="/">Início</a>
#     <a href="/cadastrar">Cadastrar</a>
#     <a href="/estoque">Estoque</a>
#     <a href="/venda-rapida">Venda Rápida</a>
#     <a href="/financeiro">Financeiro</a>
# </div>
