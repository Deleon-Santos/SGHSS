from app import create_app
from flask_cors import CORS

app = create_app()
#A API está liberada para todas as origens 
CORS(app)

if __name__ == '__main__':
	app.run(debug=True)