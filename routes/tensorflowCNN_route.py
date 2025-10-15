from flask import Blueprint, render_template, jsonify, request
from tensorflow.keras.datasets import cifar100
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.losses import sparse_categorical_crossentropy
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
import matplotlib.pyplot as plt
import io, base64

tensorflowcnn_bp = Blueprint("tensorflowcnn", __name__, template_folder="../templates")

# Charger CIFAR-100
""" (input_train, target_train), (input_test, target_test) = cifar100.load_data()
input_train, input_test = input_train.astype("float32") / 255.0, input_test.astype("float32") / 255.0
img_shape = (32, 32, 3)
num_classes = 100 """


def build_model(optimizer):
    """Construction du modèle CNN"""
    model = Sequential([
        Conv2D(32, (3, 3), activation="relu", input_shape=img_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation="relu"),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation="relu"),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(256, activation="relu"),
        Dense(128, activation="relu"),
        Dense(num_classes, activation="softmax")
    ])
    model.compile(loss=sparse_categorical_crossentropy, optimizer=optimizer, metrics=["accuracy"])
    return model


@tensorflowcnn_bp.route("/tensorflowCNN", methods=["GET"])
def tensorflowCnn():
    return render_template("tensorflowCNN.html")


@tensorflowcnn_bp.route("/train_cnn", methods=["POST"])
def train_cnn():
    """Entraînement avec hyper-paramètres personnalisés"""
    data = request.get_json() or request.form

    batch_size = int(data.get("batch_size", 50))
    epochs = int(data.get("epochs", 5))
    lr = float(data.get("learning_rate", 0.001))
    optimizer_choice = data.get("optimizer", "adam").lower()

    if optimizer_choice == "sgd":
        optimizer = SGD(learning_rate=lr)
    elif optimizer_choice == "rmsprop":
        optimizer = RMSprop(learning_rate=lr)
    else:
        optimizer = Adam(learning_rate=lr)

    model = build_model(optimizer)
    history = model.fit(
        input_train, target_train,
        batch_size=batch_size,
        epochs=epochs,
        verbose=1,
        validation_split=0.2
    )

    score = model.evaluate(input_test, target_test, verbose=0)

    # Génération du graphique
    plt.plot(history.history["accuracy"], label="Train Accuracy")
    plt.plot(history.history["val_accuracy"], label="Val Accuracy")
    plt.xlabel("Époques")
    plt.ylabel("Précision")
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    return jsonify({
        "test_loss": float(score[0]),
        "test_accuracy": float(score[1]),
        "plot": plot_base64
    })
