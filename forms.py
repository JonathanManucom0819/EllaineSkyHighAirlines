import re
from wtforms.validators import ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DecimalField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Login")

class FlightForm(FlaskForm):
    flight_number = StringField(
        "Flight Number",
        validators=[
            DataRequired(),
            Length(max=20)
        ],
        render_kw={"placeholder": "ESH 101"}
    )

    origin = StringField(
        "Origin",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    destination = StringField(
        "Destination",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    departure_time = DateTimeLocalField(
        "Departure Date and Time",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )

    available_seats = IntegerField(
        "Available Seats",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    price = DecimalField(
        "Fare",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    submit = SubmitField("Save")

    def validate_flight_number(self, field):
        value = field.data.strip().upper().replace(" ", "")

        match = re.fullmatch(r"([A-Z]{2,3})(\d{3})", value)

        if not match:
            raise ValidationError(
                "Flight number must be in the format 'ESH 101'."
            )

        # Save in a consistent format
        field.data = f"{match.group(1)} {match.group(2)}"