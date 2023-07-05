import flask
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userhash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
#with app.app_context():
#   db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#class AddUser(FlaskForm):
#    email = StringField("email adress", validators=[DataRequired()])
#    password = StringField("Password", validators=[DataRequired()])
#    name = StringField("Your NAme", validators=[DataRequired()])


@app.route('/')
def home():
    return render_template("index.html", logged_in = current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        pw = request.form.get('password')
        hash = generate_password_hash(password=pw, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password= hash
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("register.html", logged_in = current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
       mail = request.form.get('email')
       pw = request.form.get('password')
       user = User.query.filter_by(email=mail).first()

       if not user:
           flash("That email does not exist, please try again.")
           return redirect(url_for('login'))

       # check if mail hat einen user
       elif not check_password_hash(pwhash=user.password, password=pw):
           flash('Password incorrect, please try again.')
           log = False
           return redirect(url_for('login'))
       else:
           log = True
           login_user(user)
           return redirect(url_for('secrets'))



    return render_template("login.html", logged_in =current_user.is_authenticated)



@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in =current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return render_template("index.html")


@app.route('/download')
def download():
    return send_from_directory('static', path="files/hello.txt")



if __name__ == "__main__":
    app.run(debug=True)
