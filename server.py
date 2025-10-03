import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         data = json.load(c)
         clubs_list = data.get('clubs')
         for club in clubs_list:
             # normaliser les points en int
             club['points'] = int(club.get('points', 0))
         return clubs_list


def loadCompetitions():
    with open('competitions.json') as comps:
         data = json.load(comps)
         competitions_list = data.get('competitions', [])
         for comp in competitions_list:
             # normaliser le nombre de places en int
             comp['numberOfPlaces'] = int(comp.get('numberOfPlaces', 0))
         return competitions_list

# Save clubs to file
def saveClubs():
    with open ('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f, indent=4)

# Save competitions to file
def saveCompetitions():
    with open('competitions.json', 'w') as f:
        json.dump({'competitions': competitions}, f, indent=4)

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    # Get email from form and normalize it
    email = request.form.get('email', '').strip().lower()
    # Find club by email
    club = next((c for c in clubs if c.get('email', '').lower() == email), None)
    
    if club is None:
        flash("Email not found, please try again.")
        return redirect(url_for('index'))
    
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = next((c for c in  competitions if c['name'] == request.form.get('competition')), None)
    club = next((c for c in  clubs if c['name'] == request.form.get('club')), None)
    
    if competition is None or club is None:
        flash("Club or competition not found.")
        return redirect(url_for('index'))
    
    try:
        placesRequired = int(request.form.get('places', 0))
    except ValueError:
        flash("Invalid number of places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    if placesRequired <= 0:
        flash("You must book at least one place.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    available = int(competition['numberOfPlaces'])
    if placesRequired > available:
        flash("Not enough places available.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    competition['numberOfPlaces'] = available - placesRequired

    if club['points'] < placesRequired:
        flash("Not enough points to book these places.")
        # restaurer le nombre de places si moins de points
        return render_template('welcome.html', club=club, competitions=competitions)
    
    club['points'] -= placesRequired

    # persister les changements
    saveCompetitions()
    saveClubs()

    flash('Great - booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)