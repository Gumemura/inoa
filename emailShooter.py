'''
Scrip de disparo de email
'''

import mysql.connector
import smtplib
import yfinance as yf

#acessando a base de dados
db = mysql.connector.connect(host = "gumemura.mysql.pythonanywhere-services.com",
                                     database = "gumemura$Inoa",
                                     user = "gumemura",
                                     password="leonscot")

#funcao de dispara o email
def emailShooter(destination, text):
    email_from = "sharetrackerinoa@gmail.com"
    email_to = destination
    smtp = "smtp.gmail.com"

    server = smtplib.SMTP(smtp, 587)
    server.starttls()
    server.login(email_from, '630322na')

    server.sendmail(email_from, email_to, text)
    server.quit()

#acessando a table de shares
shares = db.cursor(buffered=True)
shares.execute('SELECT name, user_id, higherThan, value FROM storedShares;')

userEmail = ''
for share in shares:
    if share[-1] != None:
        shareName = share[0]
        isHigher = share[2]
        shareValue = share[3]

        #pegando o email do usuario
        emails = db.cursor(buffered=True)
        emails.execute('SELECT id, email FROM users;')
        for email in emails:
            if email[0] == share[1]:
                userEmail = email[1]
                break

        #pegando o valor atual da acao
        ticker = yf.Ticker(shareName)
        data = ticker.history()
        last_quote = (data.tail(1)['Close'].iloc[0])

        #determinando o conteudo do email
        subject = 'Informe das acoes ' + shareName
        msg = shareName + "\n\n"
        if isHigher == 1:
            if last_quote > shareValue:
                msg = msg + 'O valor da acao ultrapassou o valor estabelecido!'
                subject = 'O valor de ' + shareName + ' subiu!'
            else:
                msg = msg + 'O valor da acao continua abaixo do valor estabelecido.'
        else:
            if last_quote > shareValue:
                msg = msg + 'O valor da acao continua acima do valor estabelecido.'
            else:
                msg = msg + 'O valor da acao está abaixo do valor estabelecido!'
                subject = 'O valor de ' + shareName + ' caiu!'

        msg = msg + "\n\nValor almejado: " + str(round(shareValue, 2))
        msg = msg + "\nAtual valor: " + str(round(last_quote, 2))

        text = 'Subject: {}\n\n{}'.format(subject, msg)

        #try except caso o usuario tenha inserido um email invalido
        try:
            emailShooter(userEmail, text)
        except:
            print("An exception occurred. Email not send to " + userEmail)




