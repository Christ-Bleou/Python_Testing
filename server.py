import json
from typing import List, Dict, Any, Optional
from flask import Flask, render_template, request, redirect, flash, url_for

# Types pour l'IDE / Pylance
Club = Dict[str, Any]
Competition = Dict[str, Any]


def loadClubs() -> List[Club]:
    """Charge et normalise les clubs depuis clubs.json"""
    with open("clubs.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    raw = data.get("clubs", [])
    clubs: List[Club] = []
    for c in raw:
        clubs.append({
            "name": c.get("name"),
            "email": c.get("email"),
            # normaliser en int pour faciliter les calculs
            "points": int(c.get("points", 0))
        })
    return clubs


def loadCompetitions() -> List[Competition]:
    """Charge et normalise les competitions depuis competitions.json"""
    with open("competitions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    raw = data.get("competitions", [])
    competitions: List[Competition] = []
    for cp in raw:
        competitions.append({
            "name": cp.get("name"),
            "date": cp.get("date"),
            "numberOfPlaces": int(cp.get("numberOfPlaces", 0))
        })
    return competitions


def saveClubs(clubs: List[Club]) -> None:
    """Écrit les clubs sur le disque (simple pour le TP)."""
    # si tu veux garder le format initial (points en string), adapte ici.
    with open("clubs.json", "w", encoding="utf-8") as f:
        json.dump({"clubs": clubs}, f, indent=4)


def saveCompetitions(comps: List[Competition]) -> None:
    with open("competitions.json", "w", encoding="utf-8") as f:
        json.dump({"competitions": comps}, f, indent=4)


app = Flask(__name__)
app.secret_key = "something_special"

# Charger les données une fois (mémo)
clubs: List[Club] = loadClubs()
competitions: List[Competition] = loadCompetitions()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/welcomeSummary", methods=["POST"])
def welcomeSummary():
    # request.form est un MultiDict ; on utilise .get pour être robuste
    email = request.form.get("email", "").strip().lower()
    # on recherche le club (c est un dict, donc .get est OK)
    club = next((c for c in clubs if (c.get("email") or "").lower() == email), None)

    if club is None:
        flash("Email not found, please try again.")
        return redirect(url_for("index"))

    return render_template("purchasePlaces.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition: str, club: str):
    foundClub = next((c for c in clubs if c.get("name") == club), None)
    foundCompetition = next((c for c in competitions if c.get("name") == competition), None)
    if foundClub and foundCompetition:
        return render_template("booking.html", club=foundClub, competition=foundCompetition)

    flash("Something went wrong - please try again")
    return redirect(url_for("index"))


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    comp_name = request.form.get("competition")
    club_name = request.form.get("club")
    competition = next((c for c in competitions if c.get("name") == comp_name), None)
    club = next((c for c in clubs if c.get("name") == club_name), None)

    if competition is None or club is None:
        flash("Club or competition not found.")
        return redirect(url_for("index"))

    # validation des places demandées
    try:
        placesRequired = int(request.form.get("places", 0))
    except (ValueError, TypeError):
        flash("Invalid number of places.")
        return render_template("welcome.html", club=club, competitions=competitions)

    if placesRequired <= 0:
        flash("You must book at least one place.")
        return render_template("welcome.html", club=club, competitions=competitions)

    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template("welcome.html", club=club, competitions=competitions)

    if competition.get("numberOfPlaces", 0) < placesRequired:
        flash("Not enough places available.")
        return render_template("welcome.html", club=club, competitions=competitions)

    if club.get("points", 0) < placesRequired:
        flash("Not enough points to book these places.")
        return render_template("welcome.html", club=club, competitions=competitions)

    # appliquer les changements en mémoire
    competition["numberOfPlaces"] = competition.get("numberOfPlaces", 0) - placesRequired
    club["points"] = club.get("points", 0) - placesRequired

    # persister (simple save pour le TP)
    saveCompetitions(competitions)
    saveClubs(clubs)

    flash("Great - booking complete!")
    return render_template("welcome.html", club=club, competitions=competitions, placesRequired=placesRequired)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


if __name__ == "__main__":
    # N'exécute flask.run() que si on lance ce fichier directement.
    app.run(debug=True)
