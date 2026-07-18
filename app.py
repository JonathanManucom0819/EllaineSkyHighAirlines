from functools import wraps
import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from forms import RegistrationForm, LoginForm, FlightForm

app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY","ellaine-sky-high-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL","sqlite:///airline.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -------------------------
# Database Models
# -------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")

    bookings = db.relationship(
        "Booking",
        backref="customer",
        lazy=True
    )

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash(
                "Please log in to access the administrator area.",
                "warning"
            )
            return redirect(url_for("login"))
        if current_user.role != "admin":
            flash(
                "You do not have permission to access the administrator area.",
                "danger"
            )
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    booking_items = db.relationship(
        "BookingItem",
        backref="flight",
        lazy=True
    )

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    booking_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default="Confirmed"
    )

    items = db.relationship(
        "BookingItem",
        backref="booking",
        lazy=True,
        cascade="all, delete-orphan"
    )

class BookingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("booking.id"),
        nullable=False
    )
    flight_id = db.Column(
        db.Integer,
        db.ForeignKey("flight.id"),
        nullable=False
    )
    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    price = db.Column(
        db.Float,
        nullable=False
    )

# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash(
                "An account with that email address already exists.",
                "danger"
            )
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(
            form.password.data
        )

        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            role="customer"
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful! You can now log in.",
            "success"
        )

        return redirect(url_for("home"))

    return render_template(
        "register.html",
        form=form
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data
        ).first()

        # Email address is not registered
        if not user:
            flash(
                "No account is registered with this email address. "
                "Please register first.",
                "danger"
            )
            return render_template(
                "login.html",
                form=form
            )

        # User exists but password is incorrect
        if not check_password_hash(
            user.password_hash,
            form.password.data
        ):
            flash(
                "Incorrect password. Please try again.",
                "danger"
            )
            return render_template(
                "login.html",
                form=form
            )

        # Login successful
        login_user(user)

        flash(
            "You have successfully logged in.",
            "success"
        )

        # Redirect administrator to CMS
        if user.role == "admin":
            return redirect(
                url_for("admin_dashboard")
            )

        # Redirect customer to home page
        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html",
        form=form
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("home"))

@app.route("/flights")
def flights():
    flight_list = Flight.query.order_by(Flight.departure_time).all()
    return render_template("flights.html", flights=flight_list)

@app.route("/add-to-cart/<int:flight_id>")
@login_required
def add_to_cart(flight_id):
    flight = db.session.get(Flight, flight_id)
    if not flight:
        flash("Flight not found.", "danger")
        return redirect(url_for("flights"))

    if flight.available_seats <= 0:
        flash("Sorry, this flight has no available seats.", "danger")
        return redirect(url_for("flights"))

    cart = session.get("cart", [])

    if flight_id in cart:
        flash("This flight is already in your booking cart.", "warning")
    else:

        cart.append(flight_id)
        session["cart"] = cart
        flash(
            f"Flight {flight.flight_number} was added to your booking cart.",
            "success"
        )

    return redirect(url_for("flights"))

@app.route("/cart")
@login_required
def cart():
    cart_ids = session.get("cart", [])

    if cart_ids:
        cart_flights = Flight.query.filter(Flight.id.in_(cart_ids)).all()
    else:
        cart_flights = []

    total_price = sum(flight.price for flight in cart_flights)

    return render_template(
        "cart.html",
        flights=cart_flights,
        total_price=total_price
    )

@app.route("/remove-from-cart/<int:flight_id>")
@login_required
def remove_from_cart(flight_id):
    cart = session.get("cart", [])

    if flight_id in cart:
        cart.remove(flight_id)
        session["cart"] = cart
        flash("Flight removed from your booking cart.", "success")

    return redirect(url_for("cart"))

@app.route("/confirm-booking", methods=["POST"])
@login_required
def confirm_booking():
    cart_ids = session.get("cart", [])

    if not cart_ids:
        flash("Your booking cart is empty.", "warning")
        return redirect(url_for("cart"))

    cart_flights = Flight.query.filter(
        Flight.id.in_(cart_ids)
    ).all()

    if not cart_flights:
        flash("No valid flights were found in your cart.", "danger")
        session["cart"] = []
        return redirect(url_for("cart"))

    # Check that all selected flights still have available seats
    for flight in cart_flights:
        if flight.available_seats <= 0:
            flash(
                f"Flight {flight.flight_number} is no longer available.",
                "danger"
            )
            return redirect(url_for("cart"))

    # Create the main booking record
    new_booking = Booking(
        user_id=current_user.id,
        status="Confirmed"
    )

    db.session.add(new_booking)

    # Flush so new_booking.id is available
    db.session.flush()

    # Create a BookingItem for every selected flight
    for flight in cart_flights:
        booking_item = BookingItem(
            booking_id=new_booking.id,
            flight_id=flight.id,
            quantity=1,
            price=flight.price
        )

        db.session.add(booking_item)

        # One seat is booked
        flight.available_seats -= 1

    # Save everything
    db.session.commit()

    # Clear the temporary cart
    session["cart"] = []

    flash(
        f"Booking #{new_booking.id} has been confirmed successfully!",
        "success"
    )

    return redirect(url_for("my_bookings"))

@app.route("/my-bookings")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

@app.route("/admin")
@admin_required
def admin_dashboard():

    flight_list = Flight.query.order_by(
        Flight.departure_time
    ).all()

    return render_template(
        "admin_dashboard.html",
        flights=flight_list
    )

@app.route("/admin/flights/add", methods=["GET", "POST"])
@admin_required
def add_flight():
    
    form = FlightForm()
    form.submit.label.text = "Add Flight"

    if form.validate_on_submit():

        existing_flight = Flight.query.filter_by(
            flight_number=form.flight_number.data
        ).first()

        if existing_flight:
            flash(
                "A flight with this flight number already exists.",
                "danger"
            )
            return render_template(
                "admin_add_flight.html",
                form=form
            )

        new_flight = Flight(
            flight_number=form.flight_number.data,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data,
            available_seats=form.available_seats.data,
            price=float(form.price.data)
        )

        db.session.add(new_flight)
        db.session.commit()

        flash(
            f"Flight {new_flight.flight_number} added successfully.",
            "success"
        )

        return redirect(url_for("admin_dashboard"))
    return render_template(
        "admin_add_flight.html",
        form=form
    )

@app.route("/admin/flights/edit/<int:flight_id>", methods=["GET", "POST"])
@admin_required
def edit_flight(flight_id):
    flight = db.session.get(Flight, flight_id)

    if not flight:
        flash("Flight not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    form = FlightForm(obj=flight)
    form.submit.label.text = "Update Flight"

    if form.validate_on_submit():

        existing_flight = Flight.query.filter(
            Flight.flight_number == form.flight_number.data,
            Flight.id != flight.id
        ).first()

        if existing_flight:
            flash(
                f"Flight number {form.flight_number.data} already exists. "
                "Please enter a different flight number.",
                "danger"
            )

            return render_template(
                "admin_edit_flight.html",
                form=form,
                flight=flight
            )

        flight.flight_number = form.flight_number.data
        flight.origin = form.origin.data
        flight.destination = form.destination.data
        flight.departure_time = form.departure_time.data
        flight.available_seats = form.available_seats.data
        flight.price = float(form.price.data)

        db.session.commit()

        flash(
            f"Flight {flight.flight_number} updated successfully.",
            "success"
        )

        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_edit_flight.html",
        form=form,
        flight=flight
    )

@app.route("/admin/flights/delete/<int:flight_id>", methods=["POST"])
@admin_required
def delete_flight(flight_id):
    flight = db.session.get(Flight, flight_id)

    if not flight:
        flash(
            "Flight not found.",
            "danger"
        )
        return redirect(url_for("admin_dashboard"))

    flight_number = flight.flight_number

    # Prevent deletion if the flight is already part of a booking
    if flight.booking_items:
        flash(
            f"Flight {flight_number} cannot be deleted because "
            "it is associated with an existing customer booking.",
            "danger"
        )
        return redirect(url_for("admin_dashboard"))

    db.session.delete(flight)
    db.session.commit()

    flash(
        f"Flight {flight_number} deleted successfully.",
        "success"
    )

    return redirect(url_for("admin_dashboard"))


# -------------------------
# Create Database
# -------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if Flight.query.count() == 0:
            sample_flights = [
                Flight(
                    flight_number="ESH101",
                    origin="Auckland",
                    destination="Sydney",
                    departure_time=datetime(2026, 7, 20, 9, 0),
                    available_seats=50,
                    price=320.00
                ),
                Flight(
                    flight_number="ESH205",
                    origin="Auckland",
                    destination="Melbourne",
                    departure_time=datetime(2026, 7, 21, 14, 30),
                    available_seats=40,
                    price=295.00
                ),
                Flight(
                    flight_number="ESH310",
                    origin="Wellington",
                    destination="Brisbane",
                    departure_time=datetime(2026, 7, 22, 11, 15),
                    available_seats=35,
                    price=360.00
                )
            ]

            db.session.add_all(sample_flights)
            db.session.commit()

    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=True
)
