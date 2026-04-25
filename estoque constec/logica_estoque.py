#logica de estoque 
import uuid
class produto:
    def __init__(self, nome,codigo_barras,preço,quantidade,categoria):
        self.nome = nome
        self.codigo_barras = codigo_barras
        self.preço = preço
        self.quantidade =quantidade
        self.categoria = categoria
        self.id = str(uuid.uuid4()) # Id Automatico

class Estoque:
    def __init__(self):
        self.produtos_por_codigo = {}
        self.produtos_por_id = {}

        def cadastrar_produtos(self, pprduto):
            #pra sempre salvar por id
            self.produtos_por_id[produto.id]=produto

            # se tiver código de barras slava tambem 
            if produto.codigo_barras:
                if produto.codigo_barras in self.produtos_por_codigo:
                    self.produtos_por_codigo[produto.codigo_barras].quantidade += produto.quantidade
                else:
                    self.produtos_por_codigo[produto.codigo_barras]=produto
                