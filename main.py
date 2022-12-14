from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
# On official doc, ".query." is missing!


app.config['SECRET_KEY'] = os.environ['SEC_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if db.session.query(User).filter_by(email=request.form.get("email")).first():
            flash("You've already sign-up with that email, please log in!")
            return redirect(url_for("login"))
        else:
            user = User()
            user.name = request.form.get("name")
            user.email = request.form.get("email")
            plain_pass = request.form.get("password")
            user.password = generate_password_hash(plain_pass, method='pbkdf2:sha256', salt_length=8)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" and "email" in request.form:
        log_email = request.form.get("email")
        log_password = request.form.get("password")
        log_user = db.session.query(User).filter_by(email=log_email).first()
        if log_user:
            if check_password_hash(log_user.password, log_password):
                login_user(log_user)
                return redirect(url_for("secrets"))
        flash("Wrong email or password, please try again.")
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
@login_required
def download():
    if current_user.is_authenticated:
        return send_from_directory('static/files/', 'cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
