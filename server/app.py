from flask import Flask
from flask_cors import CORS

from routes.user import user_bp
from routes.ingredient import ingredient_bp

app = Flask(__name__)
CORS(app)


app.register_blueprint(user_bp)
app.register_blueprint(ingredient_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)