from database import (
    buscar_por_codigo,
    cadastrar_produto,
    listar_produtos,
    atualizar_quantidade,
    registrar_financeiro
)

from datetime import date
def cadastrar_produto_fluxo(nome, codigo, descricao, quantidade, preco, tipo):
    
    if codigo:  # se tem código de barras
        produto = buscar_por_codigo(codigo)

        if produto:
            print("Produto já existe → somando quantidade")
            atualizar_quantidade(produto[0], quantidade)
            return

    # se não existe ou não tem código
    cadastrar_produto(nome, codigo, descricao, quantidade, preco, tipo)
    print("Produto cadastrado com sucesso")


def entrada_produto(id_produto, quantidade):
    atualizar_quantidade(id_produto, quantidade)


def saida_produto(id_produto, quantidade):

    produtos = listar_produtos()

    for p in produtos:

        if p[0] == id_produto:

            nome = p[1]
            quantidade_atual = p[4]
            preco = p[5]

            if quantidade_atual >= quantidade:

                # 1 — reduzir estoque
                atualizar_quantidade(id_produto, -quantidade)

                # 2 — calcular valor total
                valor_total = quantidade * preco

                # 3 — registrar financeiro
                registrar_financeiro(
                    tipo="VENDA",
                    descricao=f"Venda: {nome}",
                    valor=valor_total,
                    data=str(date.today())
                )

                print("Saída realizada e venda registrada")

            else:
                print("Estoque insuficiente")

            return

    print("Produto não encontrado")


def mostrar_estoque():
    produtos = listar_produtos()

    for p in produtos:
        print(f"ID: {p[0]} | Nome: {p[1]} | Qtd: {p[4]}")
