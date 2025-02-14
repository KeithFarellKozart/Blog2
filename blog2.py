from sqlite3 import IntegrityError
from flask import Flask, redirect, render_template, request, flash, url_for, session, g, send_from_directory
from utils.database import db_session
from werkzeug.security import check_password_hash, generate_password_hash
from utils.models import User, Post, Comment
from werkzeug.utils import secure_filename
from flask_thumbnails import Thumbnail
import os 
# /home/bigben3/Blog2/media/ -main pwd bigben
# /home/ivan/Blog2/media/ -main pwd home
UPLOAD_FOLDER = "/home/bigben3/Blog2/media/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "webp"}
app = Flask(__name__)
thumb = Thumbnail(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/register/", methods=["GET", "POST"])
def register():
     if request.method == "POST":
          username = request.form.get("username")
          email = request.form.get("email")
          password = request.form.get("password")
          password2 = request.form.get("password2")
          filename = None
          print(request.files)
          if 'file' in request.files:
               file = request.files['file']
               print("help me")
               if file.filename == '':
                    flash('No selected file')
                    print("filename is empty")
                    return redirect(url_for('index'))
               if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
     
          error = ""

          if not username:
               error = "Username is required"
          elif not password:
               error = "Password is required"
          elif not email:
               error = "Email is required"
          elif password != password2:
               error = "Password don't match"
          print(error)

          if error == "":
               user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    avatar=filename,
               )
               try:
                    db_session.add(user)
                    db_session.commit()
               except IntegrityError:
                    error = "Такой пользователь уже существует"
                    print(error)
               else:
                    return redirect(url_for("login"))
          flash(error)
     return render_template("auth/register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
     if request.method == "POST":
          username = request.form.get("username")
          password = request.form.get("password")
          print(password)
          error = None

          user = User.query.filter(User.username == username).first()
          if user is None:
               error = "Не существует такого пользователя"
          elif not check_password_hash(user.password, password):
               error ="Неправильный пароль"

          if error is None:
               session.clear()
               session["user_id"] = user.id
               return redirect(url_for("index"))
          flash(error)
          print(error)
     return render_template("auth/login.html")

@app.route("/", methods=["GET", "POST"])
def index():
     posts = Post.query.all()
     comments = Comment.query.all()
     return render_template("index.html", posts=posts,comments=comments)
# @app.route("/upload",methods=["POST"])


@app.before_request
def load_user() -> None:
     user_id = session.get("user_id")
     if user_id is None:
          g.user = None
     else:
          g.user = User.query.filter(User.id == session["user_id"]).first()


@app.teardown_appcontext
def shutdown_session(exception=None):
     db_session.remove()

@app.post("/create/")
def create():
     title = request.form.get("title")
     text = request.form.get("text")
     filename = None
     if 'file' in request.files:
          file = request.files['file']
          if file.filename == '':
               flash('No selected file')
               print("test")
          if file and allowed_file(file.filename):
               filename = secure_filename(file.filename)
               file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
     
     user = g.user
     post = Post(title, text, user.id, filename)
     if text != "" or text is not None:
          db_session.add(post)
          try:
               db_session.commit()
          except:
               print("help me")
     return redirect(url_for("index"))

@app.route("/edit/<int:id>/", methods=["GET", "POST"])
def edit(id: int):
     post = Post.query.filter(Post.id == id).first()
     if request.method == "POST":
          title = request.form.get("title")
          text = request.form.get("text")

          post.title = title
          post.text = text
          db_session.commit()
          return redirect(url_for("index"))    
     return render_template("edit.html", post=post)

@app.route('/user/<string:name>/', methods=["POST", "GET"])
def profile(name):
     user = User.query.filter(User.username==name).first()
     if request.method == "POST":
          avatar= request.form.get("avatar")
          user.avatar=avatar
          db_session.commit()
          return redirect("profile", name)
     return render_template("profile.html", user=user)

@app.post("/delete/<int:id>/")
def delete(id):
     post = Post.query.get(id)
     db_session.delete(post)
     db_session.commit()
     return redirect(url_for("index"))
def allowed_file(filename):
     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload/", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@app.route("/uploads/<name>")
def download_file(name):
     return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.post("/comment/<int:id>/")
def comment(id):
     title = request.form.get("title")
     text = request.form.get("text")
     filename = None
     if 'file' in request.files:
          file = request.files['file']
          if file.filename == '':
               flash('No selected file')
               print("test")
          if file and allowed_file(file.filename):
               filename = secure_filename(file.filename)
               file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
     user = g.user
     comment = Comment(title, text, user.id, id, filename)
     if text != "" or text is not None:
          db_session.add(comment)
          try:
               db_session.commit()
          except:
               print("help me")
     return redirect(url_for("index"))