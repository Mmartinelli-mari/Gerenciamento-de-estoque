# 🏪 CONSTEC — Sistema de Gerenciamento de Estoque

O **CONSTEC** é um sistema web desenvolvido em Python com Flask para gerenciamento de estoque e controle financeiro básico.

O objetivo do sistema é permitir que pequenos comércios controlem seus produtos, entradas, saídas e movimentações financeiras em um único ambiente.

Este projeto foi desenvolvido com foco em aprendizado prático de:

- Python
- Flask
- Banco de dados SQLite
- Estrutura de software
- Backend e Frontend Web

---

# 🎯 Objetivo do Projeto

Desenvolver um sistema web capaz de:

✔ Cadastrar produtos  
✔ Controlar quantidade em estoque  
✔ Registrar entradas e saídas  
✔ Registrar movimentações financeiras  
✔ Exibir estoque em interface web  
✔ Permitir crescimento futuro para vitrine online  

---

# 🧠 Funcionalidades

## 📦 Estoque

- Cadastro de produtos
- Cadastro com ou sem código de barras
- Controle automático de quantidade
- Listagem de produtos cadastrados
- Atualização automática do estoque

## 💰 Financeiro

- Registro de vendas
- Registro de despesas (manutenção)
- Histórico financeiro
- Controle básico de movimentações

## 🌐 Interface Web

- Página inicial
- Cadastro de produtos
- Visualização de estoque
- Visualização financeira

---

# 🏗️ Arquitetura do Projeto

---

# 🗄️ Banco de Dados

O sistema utiliza **SQLite**, com duas tabelas principais:

## 📦 Tabela `produto`

| Campo | Tipo |
|------|------|
| id | INTEGER |
| nome | TEXT |
| codigo_barras | TEXT |
| descricao | TEXT |
| quantidade | INTEGER |
| preco | REAL |
| tipo | TEXT |

---

## 💰 Tabela `financeiro`

| Campo | Tipo |
|------|------|
| id | INTEGER |
| tipo | TEXT |
| descricao | TEXT |
| valor | REAL |
| data | TEXT |

Tipos possíveis:

- VENDA
- DESPESA
- MANUTENÇÃO

---

# 🚀 Como executar o projeto

## 1️⃣ Clonar ou abrir o projeto

```bash
git clone <repositorio>
cd constec
