from flask import Flask
from src.routes import bp   # import the blueprint from your package

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

# For local dev
if __name__ == "__main__":
    create_app().run()
