# render_template: renderizar as páginas html dentro do diretório templates
#request: Possibilitar o uso das requests GET e POST
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def principal():
    return render_template("index.html")

