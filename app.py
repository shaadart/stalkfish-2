from flask import Flask
from src.routes import bp   # import the blueprint from your package

app = Flask(__name__)  # Define the app variable at the module level
app.register_blueprint(bp)

# For local dev
if __name__ == "__main__":
    app.run(
        debug=True,
    )
