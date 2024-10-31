from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pyotp
import qrcode
from io import BytesIO
import base64
import os
import requests
from config import Config  # Ensure Config is imported



app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])
migrate = Migrate(app, db)

# Model for Blog Posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


# Model for Comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)


# Model for Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    totp_secret = db.Column(db.String(16))


# Route to view all blog posts and set a session cookie
@app.route('/')
def index():
    session['user'] = 'victim_user'  # This sets a session cookie
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


# Route to add a new post
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            new_post = Post(title=title, content=content)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!')
            return redirect(url_for('index'))
        flash('Title and Content are required!')
    return render_template('add_post.html')


# Route to view a specific post and add a comment
@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_comment = Comment(post_id=post.id, content=content)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully!')
            return redirect(url_for('post_detail', post_id=post_id))
        flash('Comment cannot be empty!')

    return render_template('post.html', post=post, comments=comments)


# Route for User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']

        # Hash the password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Generate TOTP secret
        totp_secret = pyotp.random_base32()

        new_user = User(username=username, password_hash=password_hash, totp_secret=totp_secret)
        db.session.add(new_user)
        db.session.commit()

        # Generate QR code for TOTP
        totp = pyotp.TOTP(totp_secret)
        qr_code_uri = totp.provisioning_uri(username, issuer_name="YourAppName")
        img = qrcode.make(qr_code_uri)
        buf = BytesIO()
        img.save(buf, format="PNG")
        img_str = base64.b64encode(buf.getvalue()).decode('ascii')

        flash('User registered successfully')
        return render_template('qr_code.html', qr_code=img_str)  # Render the QR code page

    return render_template('register.html')


# Route for User Login
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']
        totp_code = data['totp_code']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            totp = pyotp.TOTP(user.totp_secret)
            if totp.verify(totp_code):
                session['user'] = username
                flash('Login successful')
                return redirect(url_for('index'))
            else:
                flash('Invalid TOTP code')
        else:
            flash('Invalid credentials')

    return render_template('login.html')


# **OAuth2 Implementation**

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
AUTH_CODES = {}
TOKENS = {}


@app.route("/auth", methods=["GET"])
def auth():
    auth_url = f"https://example.com/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=read"
    return redirect(auth_url)


@app.route("/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    session['auth_code'] = code
    return redirect("/token")


@app.route("/token", methods=["GET", "POST"])
def token():
    code = session.get('auth_code')
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400

    token_response = requests.post("https://example.com/oauth/token", data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    token_json = token_response.json()
    session['access_token'] = token_json['access_token']
    return jsonify(token_json)


@app.route("/protected_resource", methods=["GET"])
def protected_resource():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Access token not found'}), 400

    resource_response = requests.get("https://example.com/api/resource", headers={
        'Authorization': f"Bearer {access_token}"
    })

    return jsonify(resource_response.json())


if __name__ == "__main__":
    app.run(debug=True, port=5000)