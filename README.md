# EllaineSkyHighAirlines

A full-stack airline reservation web application developed using Python and Flask. The system provides customers with an online interface for browsing flights, making reservations, managing bookings, and maintaining their profiles, together with administrative functions for managing airline operations.

## Project Overview

EllaineSkyHighAirlines was developed as a cloud-oriented web application demonstrating the design and deployment of a database-driven airline reservation system.

The application separates the presentation, application, authentication, database, and deployment concerns to provide a practical example of a modern Python web application.

## Features

### Customer Features

- Customer registration and login
- Secure user authentication
- Browse available flights
- Select flights for reservation
- Create flight bookings
- View booking confirmation
- View booking history
- Cancel reservations
- Manage customer profile
- Logout functionality

### Administrative Features

- Administrative authentication
- Manage flight information
- Manage customer accounts
- Manage bookings and reservations
- View and maintain airline operational data

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Flask |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Password Security | Werkzeug password hashing |
| Development Database | SQLite |
| Production Database | PostgreSQL |
| Production Database Platform | Neon PostgreSQL |
| Database Driver | psycopg2-binary |
| Configuration | Environment Variables / python-dotenv |
| Production Web Server | Gunicorn |
| Cloud Deployment | Microsoft Azure App Service / Render |
| Source Control | Git / GitHub |

## Application Architecture

The application follows a web application architecture consisting of:

```text
User
  |
  v
Web Browser
  |
  v
Flask Application
  |
  +---- Authentication & Authorization
  |
  +---- Flight Management
  |
  +---- Booking Management
  |
  +---- Customer Profile Management
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL Database