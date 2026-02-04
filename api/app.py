from flask import Flask
# SocketIO import deferred

# Initialize DB and auth blueprint
from api.models import db
from api.routes.auth import auth_bp

app = Flask(__name__)
# Load config from env if desired
app.config.from_envvar("API_CONFIG_FILE", silent=True)

# Initialize extensions
db.init_app(app)
# SocketIO is initialized when running directly

# Register blueprints
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return "Index Page API"

if __name__ == "__main__":
    import eventlet
    from flask_socketio import SocketIO

    eventlet.monkey_patch()

    io = SocketIO()
    io.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    @io.on("connect")
    def socketio_hello():
        if not hasattr(app, "_connect_count"):
            app._connect_count = 0
        app._connect_count += 1
        io.send(app._connect_count, broadcast=True)

    with app.app_context():
        db.create_all()
    io.run(app, debug=True)
