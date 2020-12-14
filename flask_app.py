from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username = "gumemura",
    password = "leonscot",
    hostname = "gumemura.mysql.pythonanywhere-services.com",
    databasename = "gumemura$users",
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
    userEmail = db.Column(db.String(4096))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_interface.html", users = Users.query.all())

    email = request.form["userEmail"]
    emailValidator = 0
    for i in range(len(email)):
        if email[i] == '@' and i != 0:
            emailValidator = emailValidator + 1
            aIndex = i
        if emailValidator == 1 and  aIndex + 1 < i < len(email) - 1:
            if email[i] == '.':
                emailValidator = emailValidator + 1
                break

    if emailValidator == 2:
        user = Users(userEmail = request.form["userEmail"])
        db.session.add(user)
        db.session.commit()
    else:
        flash("Insert valid e-mail!")

    return redirect(url_for('index'))



