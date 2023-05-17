# Page routes for the website

from flask import Flask, request, render_template, redirect, url_for
from flask import current_app as app
from pathlib import Path
import os


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# HOW TO PAGE   
@app.route("/howTo")
def howTo():
    #user_download_path = str(os.path.join(Path.home(), "Downloads"))
    return render_template("howTo.html")#, path=user_download_path


# DASHBOARD  
@app.route("/dashboard")
def dashboard():
          
    path_to_download_folder = str(os.path.join(Path.home(), "Downloads", "NetflixViewingHistory.csv"))

    if (Path(path_to_download_folder).exists()):
        return redirect("/dashapp/")
    else:
        # Redirect user is file not found
        return render_template("howTo.html")


# ROADMAP  
@app.route("/roadmap")
def roadmap():
    return render_template("roadmap.html")
# Known issues
# Advanced show type algorithm
# Discord for help/suggestions
# Future features
    # Filter table
    # Combine datasets
    # Accounts
    # Show data from other APIs
    # Compare with other accounts


# ABOUT 
@app.route("/about")
def about():
    return render_template("about.html")


"""
# UPLOAD PAGE   
# Upload destination folder
path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
app.config["UPLOADS"] = path_to_download_folder
@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        if len(request.files["filename"].filename) > 0:
            file = request.files["filename"]
            file.save(os.path.join(app.config["UPLOADS"], file.filename))
            print("FILE UPLOADED: ", file)
            return redirect(url_for("dashboard"))
        else:
            print("MUST UPLOAD FILE")
            return render_template("upload.html")
    else:
        return render_template("upload.html")"""