from flask import Flask, render_template, send_from_directory
from flask_session import Session
from extensions import db, influxdb
import os

# --- App ---
app = Flask(__name__, static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'table/chinook.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuration InfluxDB
app.config["INFLUXDB_V2_URL"] = "http://192.168.168.88:8086"
app.config["INFLUXDB_V2_ORG"] = "iut"
app.config["INFLUXDB_V2_TOKEN"] = "yUts4Cc11OOkr4JR8PfwIaU9PpPLvfy0LibGFQxDY6bGqM6PWYGKpvx6KEWYgesnCYn-FC_lmIblu4Na4xhxBQ=="

db.init_app(app)
influxdb.init_app(app)

app.secret_key = "e1f9bdf9c89e447a91d8b62736e3a59d9dcbf5e08d2d7f1e2c84b49c2a2d1a77"

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# --- Import & Register Blueprints ---
try:
    from routes.temp_route import temp_bp
    from routes.bd_route import bd_bp
    from routes.bd_question import bdQuestion_bp
    from routes.influxdb_route import influxdb_bp
    from routes.scikit_route import scikit_bp
    from routes.tensorflow_route import tensorflow_bp
    from routes.tensorflowCNN_route import tensorflowcnn_bp
    from routes.imagerie_route import imagerie_bp
    from routes.DLcpp_route import cpp_bp

    app.register_blueprint(temp_bp)
    app.register_blueprint(bd_bp)
    app.register_blueprint(bdQuestion_bp)
    app.register_blueprint(influxdb_bp)
    app.register_blueprint(scikit_bp)
    app.register_blueprint(tensorflow_bp)
    app.register_blueprint(tensorflowcnn_bp)
    app.register_blueprint(imagerie_bp)
    app.register_blueprint(cpp_bp)
    
    print("✅ Tous les blueprints ont été enregistrés avec succès")
    
except Exception as e:
    print(f"❌ Erreur lors de l'enregistrement des blueprints: {e}")
    raise

@app.route("/", methods=["GET"])
def home():
    return render_template("temp.html")


# Gestion d'erreurs globale
@app.errorhandler(404)
def not_found(e):
    return render_template('temp.html'), 404


@app.errorhandler(500)
def server_error(e):
    print(f"❌ Erreur 500: {e}")
    return "Erreur serveur interne", 500


if __name__ == "__main__":
    print("🚀 Démarrage de l'application Flask...")
    print(f"📂 Dossier de base: {basedir}")
    app.run(debug=True, host="0.0.0.0", port=5007)