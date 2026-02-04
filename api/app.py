from flask import Flask
from flask_socketio import SocketIO

# Initialize DB and auth blueprint
from api.models import db
from api.routes.auth import auth_bp

import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
# Load config from env if desired
app.config.from_envvar("API_CONFIG_FILE", silent=True)

# Initialize extensions
db.init_app(app)
io = SocketIO()
io.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

# Register blueprints
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return "Index Page API"

n = 0

@io.on("connect")
def socketio_hello():
    global n 
    n+=1
    io.send(n, broadcast=True)

if __name__ == "__main__":
    # Create tables if running locally for convenience
    with app.app_context():
        db.create_all()
    io.run(app, debug=True)
