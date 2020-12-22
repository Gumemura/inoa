from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
#import yfinance as yf

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username = "gumemura",
    password = "leonscot",
    hostname = "gumemura.mysql.pythonanywhere-services.com",
    databasename = "gumemura$Inoa",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

'''msft = yf.Ticker("MSFT")

tickers = ['MGLU3']

for ticker in tickers:
    ticker_yahoo = yf.Ticker(ticker+'.SA')
    data = ticker_yahoo.history()
    last_quote = (data.tail(1)['Close'].iloc[0])
    print(ticker, last_quote)'''

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(4096))
    shares = db.relationship('SharesTrack', backref = 'user', lazy=True)
    alert = db.relationship('EmailShooter', backref = 'user', lazy=True)

class SharesTrack(db.Model):
    __tablename__ = "storedShares"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096))
    dateFrom = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class EmailShooter(db.Model):
    __tablename__ = "emailAlert"

    id = db.Column(db.Integer, primary_key=True)
    share = db.Column(db.String(4096))
    higher = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_interface.html", users = Users.query.all())

    session['userEmail'] = request.form["userEmail"]

    emailValidator = 0
    for i in range(len(session['userEmail'])):
        if session['userEmail'][i] == '@' and i != 0:
            emailValidator = emailValidator + 1
            aIndex = i
        if emailValidator == 1 and  aIndex + 1 < i < len(session['userEmail']) - 1:
            if session['userEmail'][i] == '.':
                emailValidator = emailValidator + 1
                break

    if emailValidator == 2:
        newUser = True
        users = Users.query.all()

        for user in users:
            if user.email == session['userEmail']:
                newUser = False
                break

        if newUser:
            user = Users(email = session['userEmail'])
            db.session.add(user)
            db.session.commit()

        return redirect(url_for('registerShares'))
    else:
        return render_template("main_interface.html", error=True)

    return redirect(url_for('index'))

@app.route("/register_shares/", methods=["GET", "POST"])
def registerShares():
    if request.method == "GET":
        return render_template("register_shares.html", currentUser = session['userEmail'])

    if request.form["newShare"] != '' and request.form["fromDate"] != '':
        url = "{}/v8/finance/chart/{}".format('https://query1.finance.yahoo.com', request.form["newShare"])
        r = requests.get(url)

        if r.status_code == 404:
            return render_template("register_shares.html", error = "Share's name not valid!", currentUser = session['userEmail'])

        newShare = SharesTrack(
            name = request.form["newShare"],
            dateFrom = request.form["fromDate"]
        )

        currentUserMd = Users.query.filter_by(email = session['userEmail']).first()
        currentUserMd.shares.append(newShare)
        db.session.commit()
    else:
        return render_template("register_shares.html", error = "Invalid input!", currentUser = session['userEmail'])

    return redirect(url_for('registerShares'))

@app.route("/show_shares/", methods=["GET", "POST"])
def showShares():
    return render_template("show_shares.html", currentUser = session['userEmail'])

@app.route("/email_alert/", methods=["GET", "POST"])
def emailAlert():
    return render_template("email_alert.html", currentUser = session['userEmail'])

print("fim")


