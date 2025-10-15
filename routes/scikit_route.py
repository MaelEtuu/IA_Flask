from flask import Blueprint, render_template, jsonify, request
from sklearn.datasets import load_digits, load_iris, load_diabetes
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score, mean_squared_error
import math
import pandas as pd

scikit_bp = Blueprint("scikit", __name__, template_folder="../templates")

digits = load_digits()
print(digits.keys())

# Split data
Xtrain, Xtest, ytrain, ytest = train_test_split(
    digits.data,
    digits.target,
    test_size=0.1
)

# Define model
model = RandomForestClassifier(n_estimators=10)

# Fit Model
model.fit(Xtrain, ytrain)

# Predict model
ypred = model.predict(Xtest)
print(metrics.classification_report(ypred, ytest))

@scikit_bp.route("/scikit", methods=["GET"])
def scikit_route():
    return render_template("scikit.html")


def get_dataset(name):
    if name == "digits":
        data = load_digits()
    elif name == "iris":
        data = load_iris()
    elif name == "diabetes":
        data = load_diabetes()
    else:
        return None
    return data


@scikit_bp.route('/train', methods=['GET'])
def train():
    dataset_name = request.args.get("dataset", default="digits")
    test_size = float(request.args.get("test_size", default=0.2))
    n_estimators = int(request.args.get("n_estimators", default=10))

    dataset = get_dataset(dataset_name)
    if dataset is None:
        return jsonify({"error": "dataset not supported"}), 400

    Xtrain, Xtest, ytrain, ytest = train_test_split(
        dataset.data, dataset.target, test_size=test_size, random_state=42
    )

    # Choix du modèle selon le dataset
    if dataset_name == "diabetes":
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        model.fit(Xtrain, ytrain)
        ypred = model.predict(Xtest)
        metric = mean_squared_error(ytest, ypred)
        result = {"dataset": dataset_name,
                  "test_size": test_size,
                  "n_estimators": n_estimators,
                  "mse": round(math.sqrt(metric), 4)}
    else:
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        model.fit(Xtrain, ytrain)
        ypred = model.predict(Xtest)
        metric = accuracy_score(ytest, ypred)
        result = {"dataset": dataset_name,
                  "test_size": test_size,
                  "n_estimators": n_estimators,
                  "accuracy": round(metric, 4)}

    return jsonify(result)


# ----------- Nouvelle fonction étude de sensibilité -----------
def sensitivity_study_table(dataset_name):
    dataset = get_dataset(dataset_name)
    if dataset is None:
        return None

    test_sizes = [0.1, 0.2, 0.3, 0.4, 0.5]
    n_estimators_list = [5, 10, 20, 50, 100]

    results = []

    for ts in test_sizes:
        for n in n_estimators_list:
            Xtrain, Xtest, ytrain, ytest = train_test_split(
                dataset.data, dataset.target, test_size=ts, random_state=42
            )
            if dataset_name == "diabetes":
                model = RandomForestRegressor(n_estimators=n, random_state=42)
                model.fit(Xtrain, ytrain)
                ypred = model.predict(Xtest)
                metric = mean_squared_error(ytest, ypred)
                score = round(math.sqrt(metric),2)  # RMSE
            else:
                model = RandomForestClassifier(n_estimators=n, random_state=42)
                model.fit(Xtrain, ytrain)
                ypred = model.predict(Xtest)
                score = round(accuracy_score(ytest, ypred),2)

            results.append({
                "test_size": ts,
                "n_estimators": n,
                "score": round(score, 4)
            })

    df = pd.DataFrame(results)
    table = df.pivot(index="test_size", columns="n_estimators", values="score")
    return table



@scikit_bp.route("/sensitivity", methods=["GET"])
def sensitivity():
    dataset_name = request.args.get("dataset", default="digits")
    table = sensitivity_study_table(dataset_name)
    if table is None:
        return jsonify({"error": "dataset not supported"}), 400

    return jsonify(table.to_dict())
