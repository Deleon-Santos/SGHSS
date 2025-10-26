# SGHSS Refatorado


1. Crie um virtualenv e instale dependências:
python -m venv venv
venv\Scripts\activate (Windows)
pip install -r requirements.txt


2. Inicialize banco de dados:
set FLASK_APP=run.py # Windows PowerShell/Command Prompt
flask init-db


3. Rode a aplicação:
python run.py


Endpoints principais:
- POST /consulta -> agendar/solicitar
- PUT /consulta/<id>/cancelar -> cancelar
- PUT /consulta/<id>/realiza -> finalizar consulta
- POST /consulta/<id>/prescreve -> prescrever
- POST /consulta/<id>/solicita_exame -> solicitar exame
- GET /agenda/medico/<id> -> consultar agenda