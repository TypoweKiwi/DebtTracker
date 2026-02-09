import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database config
use_sqlite = os.getenv("USE_SQLITE", "").strip().lower() in {"1", "true", "yes"}
database_url = os.getenv("DATABASE_URL")

if use_sqlite or not database_url:
    sqlite_path = Path(__file__).parent / "dev.db"
    database_url = f"sqlite:///{sqlite_path}"
    if use_sqlite:
        print("Using SQLite for local development (USE_SQLITE=1)")
    else:
        print("DATABASE_URL not set - falling back to SQLite for local development")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# Enable CORS for development
CORS(app, origins=["http://localhost:3000", "http://localhost:5000"])

# Initialize DB and auth blueprint
from models import db
from routes.auth import auth_bp
from routes.debts import debts_bp
from routes.debt_participants import debt_participants_bp

# Initialize extensions
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(debts_bp)
app.register_blueprint(debt_participants_bp)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"}), 200

# Index page
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "DebtTracker API"}), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created")
        except Exception as e:
            print(f"Could not create tables: {e}")
            print("(Database connection will be established when needed)")

    # For now: Run plain Flask without SocketIO (eventlet has compatibility issues with Python 3.10)
    # SocketIO will be added later when we upgrade dependencies
    print("Starting Flask on http://0.0.0.0:5000")
    print("Backend is ready")
    app.run(debug=True, host="0.0.0.0", port=5000)
