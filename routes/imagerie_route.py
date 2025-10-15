import os
from flask import Blueprint, render_template, request, jsonify, session
import cv2
import numpy as np
import tensorflow as tf
from src.utils import download_model, read_label_map

imagerie_bp = Blueprint("imagerie", __name__, template_folder="../templates")

# Dossier temporaire pour les uploads
TEMP_FOLDER = "static/temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Modèles disponibles
AVAILABLE_MODELS = [
    "ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8.tar.gz",
    "ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz",
    "ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
]

# Labels COCO par défaut (au cas où le fichier ne se charge pas)
COCO_LABELS = {
    1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane',
    6: 'bus', 7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light',
    11: 'fire hydrant', 13: 'stop sign', 14: 'parking meter', 15: 'bench',
    16: 'bird', 17: 'cat', 18: 'dog', 19: 'horse', 20: 'sheep',
    21: 'cow', 22: 'elephant', 23: 'bear', 24: 'zebra', 25: 'giraffe',
    27: 'backpack', 28: 'umbrella', 31: 'handbag', 32: 'tie', 33: 'suitcase',
    34: 'frisbee', 35: 'skis', 36: 'snowboard', 37: 'sports ball', 38: 'kite',
    39: 'baseball bat', 40: 'baseball glove', 41: 'skateboard', 42: 'surfboard',
    43: 'tennis racket', 44: 'bottle', 46: 'wine glass', 47: 'cup',
    48: 'fork', 49: 'knife', 50: 'spoon', 51: 'bowl', 52: 'banana',
    53: 'apple', 54: 'sandwich', 55: 'orange', 56: 'broccoli', 57: 'carrot',
    58: 'hot dog', 59: 'pizza', 60: 'donut', 61: 'cake', 62: 'chair',
    63: 'couch', 64: 'potted plant', 65: 'bed', 67: 'dining table',
    70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse', 75: 'remote',
    76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
    80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book',
    85: 'clock', 86: 'vase', 87: 'scissors', 88: 'teddy bear',
    89: 'hair drier', 90: 'toothbrush'
}

# Cache pour ne pas recharger les modèles à chaque requête
LOADED_MODELS = {}


def load_model(model_name):
    if model_name not in LOADED_MODELS:
        model_path, labels_path = download_model(model_name)
        model = tf.saved_model.load(model_path)
        
        # Essayer de charger les labels, sinon utiliser COCO par défaut
        try:
            labels = read_label_map(labels_path) if labels_path else COCO_LABELS
            if not labels or len(labels) == 0:
                print("⚠️ Labels vides, utilisation des labels COCO par défaut")
                labels = COCO_LABELS
        except Exception as e:
            print(f"❌ Erreur chargement labels: {e}, utilisation des labels COCO")
            labels = COCO_LABELS
            
        LOADED_MODELS[model_name] = (model, labels)
        print(f"✅ Modèle chargé: {model_name} avec {len(labels)} labels")
    return LOADED_MODELS[model_name]


def process_image(image_path, threshold=0.5, model_name=None):
    model_name = model_name or AVAILABLE_MODELS[0]
    model, labels = load_model(model_name)

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Impossible de lire l'image: {image_path}")
    
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_tensor = np.expand_dims(img_rgb, axis=0)

    # Détection
    resp = model(input_tensor)
    
    detection_count = 0
    for boxes, classes, scores in zip(resp['detection_boxes'].numpy(),
                                      resp['detection_classes'].numpy(),
                                      resp['detection_scores'].numpy()):
        for box, cls, score in zip(boxes, classes, scores):
            if score > threshold:
                detection_count += 1
                
                # Conversion des coordonnées
                ymin = int(box[0] * h)
                xmin = int(box[1] * w)
                ymax = int(box[2] * h)
                xmax = int(box[3] * w)
                
                # Récupération du label (classe commence à 1 dans COCO)
                class_id = int(cls)
                label_text = labels.get(class_id, f"Classe_{class_id}")
                confidence = f"{score:.2f}"
                
                # Couleur aléatoire mais constante par classe
                np.random.seed(class_id)
                color = tuple(map(int, np.random.randint(50, 255, 3)))
                
                # Dessiner le rectangle
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
                
                # Préparer le texte avec fond
                text = f"{label_text} ({confidence})"
                (text_width, text_height), baseline = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                
                # Fond pour le texte
                cv2.rectangle(
                    img,
                    (xmin, ymin - text_height - baseline - 5),
                    (xmin + text_width, ymin),
                    color,
                    -1
                )
                
                # Texte en blanc
                cv2.putText(
                    img,
                    text,
                    (xmin, ymin - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
                
                print(f"🔍 Détecté: {label_text} (score: {confidence})")
    
    print(f"📊 Total détections: {detection_count}")
    cv2.imwrite(image_path, img)


@imagerie_bp.route("/imagerie", methods=["GET"])
def imagerie_route():
    return render_template("imagerie.html", available_models=AVAILABLE_MODELS, score=0.5)


@imagerie_bp.route("/imagerie/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400
    
    filepath = os.path.join(TEMP_FOLDER, file.filename)
    file.save(filepath)
    session['last_uploaded_file'] = filepath

    threshold = float(request.form.get('threshold', 0.5))
    model_name = request.form.get('model_name', AVAILABLE_MODELS[0])
    
    try:
        process_image(filepath, threshold=threshold, model_name=model_name)
        return jsonify({"url": f"{request.url_root}{filepath}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@imagerie_bp.before_app_request
def clean_temp():
    if 'last_uploaded_file' in session:
        last_file = session['last_uploaded_file']
        for filename in os.listdir(TEMP_FOLDER):
            file_path = os.path.join(TEMP_FOLDER, filename)
            if file_path != last_file and os.path.isfile(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print(f"⚠️ Impossible de supprimer {file_path}: {e}")