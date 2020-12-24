'''
TO DO
Limitar a data inicial para hoje
Exibir os alertas registrados
Permitir que os alertas registrados sejam alterados (deletados e ter a data inicial alterada)
Botao de logout
Alerta caso email nao tenha sido disparado (email errado)
'''

from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
import yfinance as yf

#Instanciando o flask
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #propriedade necessaria por alguns metodos de flask

#Configurando a base de dados SQL
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

#CRIANDO MODELOS
class Users(db.Model):
    '''Modelo principal
    id - código unico de cada usuario
    email - email do usuario usado para identifica-lo e para realizar o disparo de email
    shares - acoes registradas pelo usuario
    '''
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(4096))
    shares = db.relationship('SharesTrack', backref = 'user', lazy=True)

class SharesTrack(db.Model):
    '''Modelo das acoes
    id - codigo unico de identificacao
    name = nome da acao
    user_id - id do usuario que a cadastrou
    higherThan - boolean que indica se o usuario quer que seja disparado o email caso o valor seja maior ou menor que o definido
    value - valor paradgima
    '''
    __tablename__ = "storedShares"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096))
    dateFrom = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    higherThan = db.Column(db.Boolean)
    value = db.Column(db.Integer)

#criando as tables
with app.app_context():
    db.create_all()

#pagina principal, onde o usuario ira inserir seu email
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_interface.html", users = Users.query.all())

    session['userEmail'] = request.form["userEmail"] #"variavel global" que aramzena o email do usuario ativo
 
    #validando o email inserido. pre requisito é ter um @ precedido de um .
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

        #verificando se o usuario ja é cadastrado
        for user in users:
            if user.email == session['userEmail']:
                newUser = False
                break

        #registrando novo usuario
        if newUser:
            user = Users(email = session['userEmail'])
            db.session.add(user)
            db.session.commit()

        return redirect(url_for('registerShares'))
    else:
        return render_template("main_interface.html", error=True)

    return redirect(url_for('index'))

#pagina onde usuario ira cadastrar novas acoes para serem acompanhadas
@app.route("/register_shares/", methods=["GET", "POST"])
def registerShares():
    currentUser = Users.query.filter_by(email = session['userEmail']).first()
    if request.method == "GET":
        return render_template("register_shares.html", currentUser = currentUser)

    if request.form["newShare"] != '' and request.form["fromDate"] != '':
        url = "{}/v8/finance/chart/{}".format('https://query1.finance.yahoo.com', request.form["newShare"]) # API da yahoo finance aqui usada para checar se o nome da acao é valido
        r = requests.get(url)

        #se a api retornar 404 com o dado nome, erro
        if r.status_code == 404:
            return render_template("register_shares.html", error = "Share's name not valid!", currentUser = currentUser)

        # verificando se a acao já esta registrada
        for share in currentUser.shares:
            if share.name == request.form["newShare"]:
                return render_template("register_shares.html", error = "Share already registered!", currentUser = currentUser)

        #criando nova instancia da acao registrada
        newShare = SharesTrack(
            name = request.form["newShare"],
            dateFrom = request.form["fromDate"]
        )

        #adicionando a nova acao ao usuario
        currentUser.shares.append(newShare)
        db.session.commit()
        return render_template("register_shares.html", success = "Share registered!", currentUser = currentUser)
    else:
        return render_template("register_shares.html", error = "Invalid input!", currentUser = currentUser)

    return redirect(url_for('registerShares'))

# pagina em que é exibida as acoes
@app.route("/show_shares/", methods=["GET", "POST"])
def showShares():
    currentUser = Users.query.filter_by(email = session['userEmail']).first()
    if request.method == "GET":
        return render_template("show_shares.html", currentUser = currentUser)

    #pegando a data inicial
    fromDate = ""
    for share in currentUser.shares:
        if share.name == request.form["sharesSelect"]:
            fromDate = share.dateFrom

    #exibindo a tabela por meio de converdsao de dataframe a versao html
    msft = yf.Ticker(request.form["sharesSelect"])
    sharesHistoric = msft.history(request.form["sharesSelect"], start = fromDate)
    return render_template("show_shares.html", currentUser = currentUser, displayedShare = request.form["sharesSelect"],
        tables=[sharesHistoric.to_html(
            classes='data',
            col_space = '100px',
            float_format='{:10.2f}'.format,
            justify='center')],
        titles=sharesHistoric.columns.values
    )

#pagina de registro de email
@app.route("/email_alert/", methods=["GET", "POST"])
def emailAlert():
    currentUser = Users.query.filter_by(email = session['userEmail']).first()
    if request.method == "GET":
        return render_template("email_alert.html", currentUser = currentUser)

    for share in currentUser.shares:
        if share.name == request.form["shareToKeepTrack"]:
            share.higherThan = (request.form["highOrLow"] == 'higher')
            share.value = request.form["valueAlert"]
            break
    db.session.commit()

    return render_template("email_alert.html", currentUser = currentUser, success = "Alert registered!")