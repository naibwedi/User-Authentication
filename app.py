from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

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

if __name__ == '__main__':
    app.run(debug=False, port=5000)
