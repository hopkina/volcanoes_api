import flask

app = flask.Flask(__name__)
conn_string = 'postgresql://park:life@localhost:5432/hawthorn'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_string	
app.config['SECRET_KEY'] = "SECRET_KEY"
app.config['DEBUG'] = True

import application.views
