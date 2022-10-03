from flask import Flask, render_template, request, flash, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
import pywhatkit as kt



app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///automation_whats.sqlite3"
db = SQLAlchemy(app)

class pessoas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    telefone = db.Column(db.String(14))

    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone

class mensagens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    mensagem = db.Column(db.String(500))

    def __init__(self, tipo, mensagem):
        self.tipo = tipo
        self.mensagem = mensagem


@app.route("/", methods=["GET", "POST"])
def principal():
   
    pessoa = pessoas.query.with_entities(pessoas.nome).all()
    mensagem = mensagens.query.order_by(mensagens.mensagem).all()


    if 'Enviar mensagem' in request.form:

        nomes = request.form.getlist('nome_select')
        list_tel = []

        for nome in nomes:
            list_tel.append(pessoas.query.with_entities(pessoas.telefone).filter_by(nome=nome).all())
            out = [item for t in list_tel for item in t]
            tel = [item for t in out for item in t]

        mensagem = request.form.get('mensagem_select')
        mensagem_inicial = 'Olá, NOME.'
        index = 0

        for item in tel:

            nova_mensagem_inicial = mensagem_inicial.replace('NOME', str(nomes[index]))
            mensagem_padrao = '{}\n\n {}'.format(nova_mensagem_inicial, mensagem)
            kt.sendwhatmsg_instantly(item, mensagem_padrao, 15, True, 3)
            nova_mensagem_inicial = mensagem_inicial
            index += 1

    return render_template("index.html", pessoas=pessoa, mensagens=mensagem)






#BANCO DE DADOS: PESSOAS CRUD

@app.route("/Consultar/Pessoas", methods=["GET", "POST"])
def consultar_pessoas():
    return render_template("consultar_pessoas.html", pessoas=pessoas.query.all())


@app.route("/Cadastrar/Pessoas", methods=["GET", "POST"])
def cadastrar_pessoas():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')

    if request.method == 'POST':
        if not nome or not telefone:
            flash('Preencha todos os campos do formulário.', 'error')
        else:
            pessoa = pessoas(nome, telefone)
            db.session.add(pessoa)
            db.session.commit()
            return redirect(url_for('consultar_pessoas'))
    return render_template("cadastrar_pessoas.html")


@app.route("/Consultar/<int:id>/atualizar_pessoas", methods=["GET", "POST"])
def atualizar_pessoas(id):
    pessoa = pessoas.query.filter_by(id=id).first()

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']

        pessoas.query.filter_by(id=id).update({"nome":nome, "telefone":telefone})
        db.session.commit()
        return redirect(url_for('consultar_pessoas'))

    return render_template("atualizar_pessoas.html", pessoa=pessoa)


@app.route("/Consultar/<int:id>/excluir_pessoas", methods=["GET", "POST"])
def excluir_pessoas(id):
    pessoa = pessoas.query.filter_by(id=id).first()
    db.session.delete(pessoa)
    db.session.commit()
    return redirect(url_for('consultar_pessoas'))



#BANCO DE DADOS: MENSAGENS CRUD


@app.route("/Consultar/Mensagens", methods=["GET", "POST"])
def consultar_mensagens():
    return render_template("consultar_mensagens.html", mensagens=mensagens.query.all())


@app.route("/Cadastrar/Mensagens", methods=["GET", "POST"])
def cadastrar_mensagens():
    tipo = request.form.get('tipo')
    mensagem = request.form.get('mensagem')

    if request.method == 'POST':
        if not tipo or not mensagem:
            flash('Preencha todos os campos do formulário.', 'error')
        else:
            mensagem = mensagens(tipo, mensagem)
            db.session.add(mensagem)
            db.session.commit()
            return redirect(url_for('consultar_mensagens'))
    return render_template("cadastrar_mensagens.html")


@app.route("/Consultar/<int:id>/atualizar_mensagens", methods=["GET", "POST"])
def atualizar_mensagens(id):
    mensagem = mensagens.query.filter_by(id=id).first()

    if request.method == 'POST':
        tipo = request.form['tipo']
        mensagem = request.form['mensagem']

        mensagens.query.filter_by(id=id).update({"tipo":tipo, "mensagem":mensagem})
        db.session.commit()
        return redirect(url_for('consultar_mensagens'))

    return render_template("atualizar_mensagens.html", mensagem=mensagem)


@app.route("/Consultar/<int:id>/excluir_mensagens", methods=["GET", "POST"])
def excluir_mensagens(id):
    mensagem = mensagens.query.filter_by(id=id).first()
    db.session.delete(mensagem)
    db.session.commit()
    return redirect(url_for('consultar_mensagens'))



@app.route("/Logs", methods=["GET", "POST"])
def logs():

    contents = []

    with open('PyWhatKit_DB.txt') as f:
        for line in f.readlines():
            a = line.strip()
            contents.append(a)

    
    return render_template('logs.html', logs=contents)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000)
