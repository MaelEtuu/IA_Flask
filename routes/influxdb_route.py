from flask import Blueprint, render_template, jsonify, request, session
from extensions import influxdb
import numpy as np

influxdb_bp = Blueprint("influxdb", __name__, template_folder="../templates")

@influxdb_bp.route("/influxdb", methods=["GET"])
def influxdb_route():
    response = influxdb.connection.ping()

    buckets_api = influxdb.connection.buckets_api()
    buckets = buckets_api.find_buckets().buckets

    query_api = influxdb.connection.query_api()
    query = '''
    from(bucket: "AnnecyWeather")
        |> range(start: -1w)
        |> filter(fn: (r) => r._measurement == "weather")
        |> filter(fn: (r) => r._field == "temperature_2m")
    '''
    tables = query_api.query(org="iut", query=query)

    # Récupération des données brutes
    data = []
    for table in tables:
        for record in table.records:
            val = record.values.get("_value")
            if val is not None:
                data.append(val)

    # Stocker les données brutes dans la session
    session["influx_data"] = data  

    # Entraînement du modèle ML avec fenêtre = 2
    window_size = 2
    theta_final, cost_history = train(data, window_size=window_size)

    # Sauvegarder les paramètres en session
    session["theta_final"] = theta_final.tolist()
    session["cost_history"] = cost_history.tolist()

    # Créer X/Y avec la même fenêtre que l'entraînement
    X = [data[i:i+window_size] for i in range(len(data)-window_size)]
    Y = [data[i+window_size] for i in range(len(data)-window_size)]

    # Ajouter colonne de biais pour le modèle
    X_b = np.hstack((X, np.ones((len(X), 1))))

    # Prédictions avec le bon modèle
    predictions = model(X_b, theta_final).flatten().tolist()

    return render_template("influxdb.html",
                           response=response,
                           buckets=buckets,
                           X=X,
                           Y=Y,
                           predictions=predictions,
                           cost_history=cost_history.tolist())

@influxdb_bp.route("/influxdb_connect", methods=["POST"])
def influxdb_test_connect():
    response = influxdb.connection.ping()
    return jsonify({"response": response})

@influxdb_bp.route("/influxdb_get_buckets", methods=["POST"])
def influxdb_get_buckets():
    buckets_api = influxdb.connection.buckets_api()
    buckets = buckets_api.find_buckets().buckets
    buckets_list = [{"name": b.name} for b in buckets]
    return jsonify({"buckets": buckets_list})

@influxdb_bp.route("/influxdb_window", methods=["POST"])
def influxdb_update_table():
    try:
        window_size = int(request.json.get("window_size", 3))
        if window_size < 1:
            window_size = 1

        # Récupérer les données depuis la session
        data = session.get("influx_data", [])
        if not data:
            return jsonify({"error": "Pas de données en session. Rechargez la page."})

        if len(data) <= window_size:
            return jsonify({"X": [], "Y": []})

        X_new = [data[i:i+window_size] for i in range(len(data)-window_size)]
        Y_new = [data[i+window_size] for i in range(len(data)-window_size)]

        return jsonify({"X": X_new, "Y": Y_new})

    except Exception as e:
        return jsonify({"error": str(e)})

@influxdb_bp.route("/influxdb_ml_predict", methods=["POST"])
def influxdb_ml():
    try:
        X_new = request.json.get("X_new", [])
        if not X_new:
            return jsonify({"error": "Pas de données envoyées"})

        # numpy array, et forcer en 2D
        X_new = np.array(X_new).reshape(1, -1)

        theta_final = session.get("theta_final", None)
        if theta_final is None:
            return jsonify({"error": "Le modèle n'est pas encore entraîné"})

        prediction = model(X_new, np.array(theta_final))

        return jsonify({"predict": prediction.flatten().tolist()})

    except Exception as e:
        return jsonify({"error": str(e)})

# === Machine Learning ===

def train(data, window_size=2):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])   # features = dernières valeurs
        y.append(data[i+window_size])     # label = valeur suivante

    X = np.array(X)
    y = np.array(y).reshape(-1, 1)

    # Ajouter colonne de biais
    X_b = np.hstack((X, np.ones((X.shape[0], 1))))

    # Initialiser paramètres
    theta = np.random.randn(X_b.shape[1], 1)

    # Entraînement
    theta_final, cost_history = gradient_descent(X_b, y, theta, 0.001, 100)
    return theta_final, cost_history

def model(X, theta):
    return X.dot(theta)

def cost_function(X, y, theta):
    m = len(y)
    return 1/(2*m) * np.sum((model(X, theta) - y)**2)

def grad(X, y, theta):
    m = len(y)
    return 1/m * X.T.dot(model(X, theta) - y)

def gradient_descent(X, y, theta, learning_rate, n_iterations):
    cost_history = np.zeros(n_iterations)
    for i in range(n_iterations):
        theta = theta - learning_rate * grad(X, y, theta)
        cost_history[i] = cost_function(X, y, theta)
    return theta, cost_history