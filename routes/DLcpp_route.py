from flask import Blueprint, render_template, send_from_directory
import os

cpp_bp = Blueprint("cpp", __name__, template_folder="../templates")

@cpp_bp.route("/DLcpp", methods=["GET"])
def DLcpp():
    return render_template("DLcpp.html")


@cpp_bp.route("/download_dl_cpp")
def download_dl_cpp():
    return send_from_directory(
        os.path.join(app.static_folder, "IA"),
        "build_for_windows.zip",
        as_attachment=True
    )

@cpp_bp.route("/download_dl_cpp_mac")
def download_dl_mac():
    return send_from_directory(
        os.path.join(app.static_folder, "IA"),
        "build_for_mac.zip",
        as_attachment=True
    )