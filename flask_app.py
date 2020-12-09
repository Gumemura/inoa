from flask import Flask, redirect, render_template, request, url_for
import yfinance as yf

app = Flask(__name__)
app.config["DEBUG"] = True

'''msft = yf.Ticker("MSFT")

tickers = ['MGLU3']

for ticker in tickers:
    ticker_yahoo = yf.Ticker(ticker+'.SA')
    data = ticker_yahoo.history()
    last_quote = (data.tail(1)['Close'].iloc[0])
    print(ticker, last_quote)'''

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("main_interface.html")
print('asd')


