from flask import Blueprint, request, jsonify

temp_bp = Blueprint("temp", __name__, template_folder="../templates")

def result_to_style(value, min_val=0, max_val=50):
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0, min(1, ratio))

    if ratio < 0.33:
        return "color: #00cc66; font-weight: bold; font-size: 22px;"
    elif ratio < 0.66:
        return ("color: #00cc66; font-weight: bold; font-size: 24px;")
    else:
        return ("color: #00cc66; font-weight: bold; font-size: 32px;"
                "animation: heatPulse .7s infinite alternate;")

@temp_bp.route("/calculateTemp", methods=["POST"])
def calculate():
    result = None
    temp_value = None
    hum_value = None
    styleResult = None

    data = request.get_json()
    try:
        temp = float(data.get("temp", 0))
        hum = float(data.get("hum", 0))
        temp_value = temp
        hum_value = hum
        
        c1 = -8.785
        c2 = 1.611
        c3 = 2.339
        c4 = -0.146
        c5 = -1.231 * 10**-2
        c6 = -1.642 * 10**-2
        c7 = 2.212 * 10**-3
        c8 = 7.255 * 10**-4
        c9 = -3.582 * 10**-6
        
        result = (c1 + c2 * temp + c3 * hum + c4 * temp * hum + 
                    c5 * (temp**2) + c6 * (hum**2) + c7 * (temp**2) * hum + 
                    c8 * temp * (hum**2) + c9 * (temp**2) * (hum**2))
    except ValueError:
        result = "Erreur : entrez des nombres valides"

    styleResult = result_to_style(result, min_val=0, max_val=300)
    return jsonify({"result":round(result, 2), "temp_value":temp_value, "hum_value":hum_value, "styleResult":styleResult})
