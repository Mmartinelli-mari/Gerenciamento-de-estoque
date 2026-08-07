from werkzeug.security import generate_password_hash
from database import criar_usuario, criar_tabela_usuarios

criar_tabela_usuarios()

email = "admin@constec.com"
senha = "constec2024"  # troque por uma senha forte depois

criar_usuario(email, generate_password_hash(senha))
print(f"Usuário {email} criado com sucesso!")