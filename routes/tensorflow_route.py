from flask import Blueprint, render_template, jsonify, request
from sklearn.datasets import load_digits, load_iris, load_diabetes
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import accuracy_score, mean_squared_error
import math
import pandas as pd
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import Input
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.models import Model

tensorflow_bp = Blueprint("tensorflow", __name__, template_folder="../templates")

# Load data une seule fois
(X_train, y_train), (X_test, y_test) = mnist.load_data()
num_train = X_train.shape[0]
num_test = X_test.shape[0]
img_height = X_train.shape[1]
img_width = X_train.shape[2]
X_train = X_train.reshape((num_train, img_width * img_height))
X_test = X_test.reshape((num_test, img_width * img_height))

# Normalize data
X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

# Encode data
y_train = to_categorical(y_train, num_classes=10)
y_test = to_categorical(y_test, num_classes=10)

def create_model():
    """Créer un nouveau modèle TensorFlow"""
    num_classes = 10
    xi = Input(shape=(img_height * img_width,))
    x = Dense(num_classes)(xi)
    y = Activation('softmax')(x)
    model = Model(inputs=[xi], outputs=[y])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

@tensorflow_bp.route("/tensorflowML", methods=["GET"])
def tensorflow_route():
    return render_template("tensorflowML.html")

@tensorflow_bp.route("/tensorflow_train", methods=["POST"])
def train():
    data = request.get_json()
    
    batch_size = int(data.get("batchsize", 128))
    epochs = int(data.get("epochs", 5))
    
    # Créer un nouveau modèle pour chaque entraînement
    model = create_model()
    
    # Entraînement
    history = model.fit(
        X_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        verbose=0,
        validation_split=0.1
    )
    
    # Évaluation
    score = model.evaluate(X_test, y_test, verbose=0)
    return jsonify({
        "loss": float(score[0]),
        "accuracy": float(score[1]),
        "history": {
            "loss": [float(l) for l in history.history["loss"]],
            "val_loss": [float(l) for l in history.history["val_loss"]],
            "accuracy": [float(a) for a in history.history["accuracy"]],
            "val_accuracy": [float(a) for a in history.history["val_accuracy"]],
        }
    })

def sensitivity_study_table_tensorflow():
    """Étude de sensibilité pour TensorFlow avec différents batch_size et epochs"""
    batch_sizes = [32, 64, 128, 192, 256]
    epochs_list = [1, 3, 5, 10, 15]
    
    results = []
    
    for batch_size in batch_sizes:
        for epochs in epochs_list:

            model = create_model()
            

            model.fit(
                X_train, y_train,
                batch_size=batch_size,
                epochs=epochs,
                verbose=0,
                validation_split=0.1
            )
            

            score = model.evaluate(X_test, y_test, verbose=0)
            accuracy = score[1]
            
            results.append({
                "batch_size": batch_size,
                "epochs": epochs,
                "accuracy": round(accuracy, 4)
            })
    
    df = pd.DataFrame(results)
    table = df.pivot(index="batch_size", columns="epochs", values="accuracy")
    return table

@tensorflow_bp.route("/tensorflow_sensitivity", methods=["GET"])
def tensorflow_sensitivity():
    """Route pour l'étude de sensibilité TensorFlow"""
    try:
        table = sensitivity_study_table_tensorflow()
        return jsonify(table.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500