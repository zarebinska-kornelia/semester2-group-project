from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import UserMixin, current_user, login_user, login_required, logout_user, fresh_login_required, \
    LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, Time, Text
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import re
import uuid
from datetime import timedelta
from flask_migrate import Migrate
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@172.16.1.8:3306/Fonteyn_parks'


app.config['SECRET_KEY'] = 'idkwhatthisis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
bcrypt = Bcrypt(app)
average_output = []
average_final = 0
launch_datetime = datetime.now()
migrate = Migrate(app, db)

API_KEY = os.environ.get('CO2_SIGNAL_API_KEY', 'QXvucMoMfsFVP')

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Database model classes, for SQL alchemy
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    submit = SubmitField('Sign in')
    def is_admin(self):
        return self.admin

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    submit = SubmitField('Submit')

class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    text = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, default=False)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(64), unique=True, nullable=False)
    income = db.Column(db.Float, nullable=False)

    def __init__(self, month, income):
        self.month = month
        self.income = income 

class BowlingBooking(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    people = Column(Integer, nullable=False)
    bowling_lane = Column(String(50), nullable=True)

class AccommodationBooking(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    people = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    room_type = Column(String(50), nullable=True)

class RestaurantBooking(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    people = Column(Integer, nullable=False)
    special_requests = Column(Text, nullable=True)


db.init_app(app)
with app.app_context():
    db.create_all()

def send_email(to_email, subject, body):
    sender_email = "fonteyn.holiday@gmail.com"
    sender_password = os.environ.get('EMAIL_PASSWORD')

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


def get_carbon_intensity(country_code):
    url = 'https://api.co2signal.com/v1/latest'
    headers = {
        'auth-token': API_KEY
    }
    params = {
        'countryCode': country_code
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            carbon_intensity = data['data']['carbonIntensity']
            fossil_fuel_percentage = data['data']['fossilFuelPercentage']
            return {
                'carbonIntensity': carbon_intensity,
                'fossilFuelPercentage': fossil_fuel_percentage
            }
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class LoginForm(FlaskForm):
    username = StringField('', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('', validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).scalar()
        if user is None:
            raise ValidationError("Username does not exist")


class RegisterForm(FlaskForm):
    username = StringField('', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('', validators=[InputRequired(), Length(min=6, max=20)])
    admin = BooleanField('Admin')
    submit = SubmitField('Register')

    def validate_username(self, username):
        exists = User.query.filter_by(username=username.data).first()
        if exists:
            raise ValidationError("Username already exists")


class MessageForm(FlaskForm):
    message = StringField('', validators=[InputRequired(), Length(min=1, max=500)])
    submit = SubmitField('Send')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/managers', methods=['GET', 'POST'])
@login_required
def managers():
    option = request.args.get('option', 'income')  # Default to 'income' if no option is selected

    # Handle form submission for adding income
    if request.method == 'POST' and option == 'income':
        month = request.form.get('month')
        income = request.form.get('income')

        # Check if month and income are provided
        if month and income:
            existing_income = Income.query.filter_by(month=month).first()
            if existing_income:
                flash('Month already exists. Please update the existing month or choose a different month.', 'danger')
                return redirect(url_for('managers', option='income'))
            else:
                try:
                    new_income = Income(month=month, income=float(income))
                    db.session.add(new_income)
                    db.session.commit()
                    flash('Income added successfully!', 'success')
                except ValueError:
                    flash('Invalid income value provided.', 'danger')
                return redirect(url_for('managers', option='income'))
        else:
            flash('Please provide both month and income.', 'danger')
            return redirect(url_for('managers', option='income'))

    
    if option == 'carbon':
        countries = [
            {'name': 'Germany', 'code': 'DE'},
            {'name': 'Netherlands', 'code': 'NL'},
            {'name': 'Belgium', 'code': 'BE'}
        ]

        carbon_data = []
        for country in countries:
            data = get_carbon_intensity(country['code'])
            if data:
                carbon_data.append({
                    'country': country['name'],
                    'carbonIntensity': data['carbonIntensity'],
                    'fossilFuelPercentage': data['fossilFuelPercentage']
                })
            else:
                carbon_data.append({
                    'country': country['name'],
                    'carbonIntensity': None,
                    'fossilFuelPercentage': None
                })

        return render_template('managers.html', option=option, carbon_data=carbon_data)

    elif option == 'income':
        income_data = Income.query.all()
        income_data_serializable = [
            {'month': income.month, 'income': income.income} for income in income_data
        ]
        return render_template('managers.html', option=option, income_data=income_data_serializable)

    return render_template('managers.html', option=option)


@app.route('/add_income', methods=['POST'])
@login_required
def add_income():
    month = request.form.get('month')
    income = request.form.get('income')
    
    if month and income:
        existing_income = Income.query.filter_by(month=month).first()
        if existing_income:
            return jsonify({'status': 'failure', 'message': 'Month already exists'}), 400

        new_income = Income(month=month, income=float(income))
        db.session.add(new_income)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'month': new_income.month,
            'income': new_income.income
        }), 200

    return jsonify({'status': 'failure', 'message': 'Invalid input'}), 400


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            remember_me = request.form.get('remember-me')
            if remember_me:
                login_user(user, remember=True)
            else:
                login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Incorrect password")
    return render_template('sign-in.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password, admin=form.admin.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('sign_in'))
    return render_template('sign-in.html', form=form)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    selected_option = request.args.get('option', 'accommodation')
    if request.method == 'GET':
        return render_template('booking.html', selected_option=selected_option)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        people = request.form.get('people')

        if not all([name, email, date_str, time_str, people]):
            flash("All fields are required!", "danger")
            return redirect(url_for('booking'))

        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            booking_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            flash("Invalid date or time format!", "danger")
            return redirect(url_for('booking'))

        duration = request.form.get('duration')
        room_type = request.form.get('room-type')
        special_requests = request.form.get('special-requests')
        bowling_lane = request.form.get('bowling-lane')

        if selected_option == 'bowling':
            new_booking = BowlingBooking(
                name=name,
                email=email,
                date=booking_date,
                time=booking_time,
                people=int(people),
                bowling_lane=bowling_lane
            )
        elif selected_option == 'accommodation':
            new_booking = AccommodationBooking(
                name=name,
                email=email,
                date=booking_date,
                time=booking_time,
                people=int(people),
                duration=int(duration) if duration else None,
                room_type=room_type
            )
        elif selected_option == 'restaurant':
            new_booking = RestaurantBooking(
                name=name,
                email=email,
                date=booking_date,
                time=booking_time,
                people=int(people),
                special_requests=special_requests
            )

        db.session.add(new_booking)
        db.session.commit()

        email_subject = f"Booking Confirmation for {selected_option.capitalize()}"
        email_body = (
            f"Dear {name},\n\n"
            f"Thank you for your booking.\n\n"
            f"Details:\n"
            f"Date: {booking_date}\n"
            f"Time: {booking_time}\n"
            f"People: {people}\n\n"
            f"We look forward to seeing you!\n"
        )
        send_email(email, email_subject, email_body)

        return render_template('confirmation.html', selected_option=selected_option, name=name, email=email, date=date_str, time=time_str, people=int(people), bowling_lane=bowling_lane, duration=duration, room_type=room_type, special_requests=special_requests)


@app.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('index.html')

@app.route('/workers', methods=['GET'])
def workers():
    if current_user.is_authenticated:
        markers = Marker.query.all()
        messages = Message.query.all()
        return render_template('workers.html', messages=messages, date=datetime.utcnow(), markers=markers, current_User=current_user)
    else:
        return redirect(flask.url_for('sign_in'))


@app.route('/add_marker', methods=['POST'])
def add_marker():
    x = request.form.get('x')
    y = request.form.get('y')
    text = request.form.get('text')

    # Create a new marker object and save it to the database
    new_marker = Marker(x=x, y=y, text=text)
    db.session.add(new_marker)
    db.session.commit()

    return redirect(url_for('workers'))


@app.route('/delete_marker', methods=['POST'])
def delete_marker():
    marker_id = request.form.get('marker_id')
    marker = Marker.query.get(marker_id)
    db.session.delete(marker)
    db.session.commit()
    return redirect(url_for('workers'))


@app.route('/complete_marker/<int:marker_id>', methods=['POST'])
def complete_marker(marker_id):
    if not current_user.is_authenticated or current_user.is_admin():
        return jsonify({"success": False}), 403  # Regular users only

    # Find the marker by its ID
    marker = Marker.query.get(marker_id)
    if not marker:
        return jsonify({"success": False}), 404
    if marker.complete:
        marker.complete = False
    else:
        marker.complete = True
    db.session.commit()
    # Update the marker

    return jsonify({"success": True})


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    #db.session.query(Message).delete(synchronize_session=False)
    #db.session.commit()
    logout_user()
    return redirect(url_for('index'))

# Threading was added here for the add_to_average_power() background process on line 100
if __name__ == '__main__':
    app.run(debug=True)

