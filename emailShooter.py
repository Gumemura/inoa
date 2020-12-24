import mysql.connector
import smtplib
import yfinance as yf

db = mysql.connector.connect(host = "gumemura.mysql.pythonanywhere-services.com",
                                     database = "gumemura$Inoa",
                                     user = "gumemura",
                                     password="leonscot")

def emailShooter(destination, text):
    email_from = "sharetrackerinoa@gmail.com"
    email_to = destination
    smtp = "smtp.gmail.com"

    server = smtplib.SMTP(smtp, 587)
    server.starttls()
    server.login(email_from, '630322na')

    server.sendmail(email_from, email_to, text)
    server.quit()

shares = db.cursor()
shares.execute('SELECT name, user_id, higherThan, value FROM storedShares;')

for share in shares:
    if share[-1] != None:
        shareName = share[0]
        isHigher = share[2]
        shareValue = share[3]

        emails = db.cursor()
        emails.execute('SELECT id, email FROM users;')
        for email in emails:
            if email[0] == share[1]:
                userEmail = email[1]
                break

        ticker = yf.Ticker(shareName)
        data = ticker.history()
        last_quote = (data.tail(1)['Close'].iloc[0])

        subject = 'Informe das acoes ' + shareName
        msg = shareName + "\n\n"
        if isHigher == 1:
            if last_quote > shareValue:
                msg = 'O valor da acao ultrapassou o valor estabelecido!'
                subject = 'O valor de ' + shareName + ' subiu!'
            else:
                msg = 'O valor da acao continua abaixo do valor estabelecido.'
        else:
            if last_quote > shareValue:
                msg = 'O valor da acao acima do valor estabelecido.'
            else:
                msg = 'O valor da acao está abaixo do valor estabelecido!'
                subject = 'O valor de ' + shareName + ' caiu!'

        msg = msg + "\n\nValor almejado: " + str(round(shareValue, 2))
        msg = msg + "\nAtual valor: " + str(round(last_quote, 2))

        text = 'Subject: {}\n\n{}'.format(subject, msg)

        emailShooter(userEmail, text)

print(msg)



