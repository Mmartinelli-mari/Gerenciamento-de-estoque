 # chamar banco de dados
from database import criar_tabela
import estoque
#criar menu

def menu():
    print("\n===== SISTEMA DE ESTOQUE =====")
    print("1 - Cadastrar produto")
    print("2 - Listar estoque")
    print("3 - Entrada de produto")
    print("4 - Saída de produto")
    print("0 - Sair")


def main():
    criar_tabela()

    while True:
        menu()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\n--- Cadastro de Produto ---")
            nome = input("Nome: ")
            codigo = input("Código de barras (ou Enter): ")
            descricao = input("Descrição: ")
            quantidade = int(input("Quantidade: "))
            preco = float(input("Preço: "))
            tipo = input("Tipo: ")
        
            estoque.cadastrar_produto_fluxo(
                nome,
                codigo if codigo != "" else None,
                descricao,
                quantidade,
                preco,
                tipo
            )

        elif opcao == "2":
            print("\n--- Estoque ---")
            estoque.mostrar_estoque()

        elif opcao == "3":
            print("\n--- Entrada de Produto ---")
            id_produto = int(input("ID do produto: "))
            quantidade = int(input("Quantidade: "))

            estoque.entrada_produto(id_produto, quantidade)

        elif opcao == "4":
            print("\n--- Saída de Produto ---")
            id_produto = int(input("ID do produto: "))
            quantidade = int(input("Quantidade: "))

            estoque.saida_produto(id_produto, quantidade)

        elif opcao == "0":
            print("Saindo do sistema...")
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()