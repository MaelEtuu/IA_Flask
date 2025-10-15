import os, gdown

# Base URL pour les modèles TensorFlow Object Detection
BASE_URL = "http://download.tensorflow.org/models/object_detection/tf2/20200713/"

# URL du label map COCO
LABEL_COCO_URL = "https://gitlab.lst.tfo.upm.es/Plan4Act/trajectory_predictor_with_object_recognition/-/raw/master/research/object_detection/data/mscoco_label_map.pbtxt"

def download_model(model_name: str):
    """
    Télécharge un modèle TensorFlow Object Detection depuis TensorFlow.org
    si il n'existe pas déjà, extrait l'archive et retourne :
        - path_model : chemin vers le dossier 'saved_model'
        - path_labels : chemin vers le label map (None si non COCO)
    """

    # URL complète du modèle
    url = f"{BASE_URL}{model_name}"
    
    # Chemin du fichier .tar.gz
    model_path = f"models/{model_name}"
    
    # Dossier où le modèle sera extrait
    model_dir = model_path.replace(".tar.gz", "")
    
    # Initialisation du chemin labels
    label_path = None

    # Si le modèle n'existe pas, on télécharge et on extrait
    if not os.path.exists(model_dir):
        print(f"Téléchargement du modèle {model_name}...")
        gdown.cached_download(url, model_path, postprocess=gdown.extractall)
        os.remove(model_path)  # supprime le tar.gz après extraction

    # Si c'est un modèle COCO, on télécharge le fichier de labels
    if "coco" in model_name.lower():
        label_path = "models/mscoco_label_map.pbtxt"
        if not os.path.exists(label_path):
            print("Téléchargement du label map COCO...")
            gdown.download(LABEL_COCO_URL, label_path, quiet=False)

    # Chemin final vers saved_model
    saved_model_path = os.path.join(model_dir, "saved_model")
    return saved_model_path, label_path

def read_label_map(label_map_path):
    items = {}
    item_id, item_name = None, None
    with open(label_map_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("id:"):
                item_id = int(line.split(":")[1].strip())
            elif line.startswith("display_name:"): 
                item_name = line.split(":")[-1].replace("\"", "").strip()
            if item_id is not None and item_name is not None:
                items[item_id] = item_name
                item_id, item_name = None, None
    return items
