from flask import Flask, render_template
from tools.experiment import RsModel

app = Flask(__name__)


@app.route("/")
@app.route("/home")
@app.route("/dashboard")
def models():
    return render_template('dashboard.html')


@app.route("/models")
def model():
    rsmodel = RsModel('test.db')
    _models = rsmodel.get_all()
    return render_template('models.html', models=_models)
