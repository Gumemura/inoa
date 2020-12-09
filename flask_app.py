from flask import Flask, redirect, render_template, request, url_for
import yfinance as yf

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []

msft = yf.Ticker("MSFT")

tickers = ['MGLU3']

for ticker in tickers:
    ticker_yahoo = yf.Ticker(ticker+'.SA')
    data = ticker_yahoo.history()
    last_quote = (data.tail(1)['Close'].iloc[0])
    print(ticker, last_quote)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=comments)

    comments.append(request.form["contents"])
    print(comments)
    return redirect(url_for('index'))

@app.route('/vmd_timestamp')
def test():
    return render_template('main_interface.html')

