from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import api_routes
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path=""
    )
    CORS(app)

    app.register_blueprint(api_routes)

    @app.route("/")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
