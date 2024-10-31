# User Authentication Project
This project demonstrates a user authentication system with features like basic authentication, database integration, protection against brute force attacks, Two-Factor Authentication (2FA), and an OAuth2 integration.

# Features
Database Integration: Uses SQLite to persistently store user and blog post data.
User Authentication: Implements standard username-password login with hashed credentials using bcrypt.
Brute Force Protection: Rate-limiting and timeout features to prevent repetitive login attempts.
Two-Factor Authentication (2FA): TOTP-based 2FA for additional security, compatible with Google Authenticator.
OAuth2 Implementation: Authorization Code Flow for OAuth2 support, enabling secure user authentication with external providers.

#Project Structure

```php
User Authentication/
├── .venv/                  # Virtual environment files
├── static/                 # Static assets (CSS, JS)
├── templates/              # HTML templates for the application
├── app.py                  # Main application logic
├── config.py               # Configuration settings
├── Dockerfile              # Docker setup for containerizing the application
├── docker-compose.yml      # Compose file to set up Docker services
├── requirements.txt        # Python dependencies
└── app.db                  # SQLite database
```
# Prerequisites
Docker and Docker Compose must be installed on your system.
Python (for local development) and Flask installed if you are not using Docker.
## Setup and Usage
Running with Docker Compose

### Clone the repository:
```bash
git clone https://github.com/yourusername/your-repo.git
cd "User Authentication"
```
### Run with Docker Compose:

```bash
docker-compose up --build
```
### Access the application:

Open your browser and go to http://localhost:5000.

# Usage Guide
Register: Go to /register to create a new account. A QR code will be displayed for setting up TOTP with an authenticator app.
Login: Go to /login and enter your username, password, and TOTP code from the authenticator app.
Add a Blog Post: After logging in, add a new post with the /add_post endpoint.
OAuth2 Authentication: The app supports OAuth2 login. You can initiate it from the /auth route.



# Technologies Used
Flask: Web framework for Python.
SQLite: Database for data persistence.
bcrypt: Library for password hashing.
pyotp: Used to generate TOTP for 2FA.
qrcode: For generating QR codes for TOTP setup.
Docker & Docker Compose: For containerizing and running the app.
## Notes
Ensure that the CLIENT_ID and CLIENT_SECRET values in app.py are replaced with actual OAuth2 credentials.
Security: Follow best practices for securing sensitive data in production, such as setting up environment variables and using HTTPS.

## Known Issues
The project setup assumes you have configured the OAuth2 provider and client credentials correctly.
# License
This project is licensed under the MIT License.

