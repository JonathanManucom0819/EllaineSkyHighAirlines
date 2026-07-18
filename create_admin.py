from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():

    existing_admin = User.query.filter_by(
        email="admin@ellaineskyhigh.com"
    ).first()

    if existing_admin:
        print("Admin account already exists.")

    else:
        admin = User(
            full_name="System Administrator",
            email="admin@ellaineskyhigh.com",
            password_hash=generate_password_hash("Admin123!"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")
