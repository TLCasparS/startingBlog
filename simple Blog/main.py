from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

from datetime import date
def getdate():
    months = ["January", "February", "March", "April", "May", "June", "Juli", "August", "September", "October", "November", "December"]
    month =  months[date.today().month]
    dateString = f"{month} {date.today().day}, {date.today().year} "
    return dateString

print(getdate())
## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
ckeditor = CKEditor()
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor.init_app(app)


#ckeditor.init_app(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/', methods = ["GET", "POST"])
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>",methods = ["GET", "POST"])
def show_post(post_id):
    #requested_post = db.session.query(BlogPost).get(post_id)
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)

@app.route("/author/<name>",methods = ["GET", "POST"])
def show_author(name):
    # alle posts

    author_posts = db.session.query(BlogPost).filter(BlogPost.author == name ).all()


    return render_template("author.html", all_posts=author_posts, author = name)



@app.route("/new-post", methods=['GET', 'POST'])
def newPost():
    blogForm = CreatePostForm()
    if blogForm.validate_on_submit():

        postData = blogForm.data
        title = postData
        print(postData["title"])
        print(postData["subtitle"])
        newPost = BlogPost(title = postData["title"],
            subtitle = postData["subtitle"],
            author= postData["author"],
            img_url=postData["img_url"],
            body = postData["body"],
            date =getdate()
                           )

        db.session.add(newPost)
        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form = blogForm)

@app.route("/delete", methods=['GET', 'DELETE'])
def delete_post():
    ids = int(request.args.get("post_id"))
    post = db.session.query(BlogPost).get(ids)
    db.session.delete(post)
    db.session.commit()
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/edit", methods=['GET', 'PATCH', 'POST'])
def edit_post():
    ids = int(request.args.get("post_id"))
    currentPost = db.session.query(BlogPost).get(ids)

    print(currentPost)
    #ids = db.session.get('post.id')
    blogForm = CreatePostForm(title =currentPost.title,
             subtitle =currentPost.subtitle,
             author = currentPost.author,
             img_url = currentPost.img_url,
             body = currentPost.body,
             date = currentPost.date
             )
    if blogForm.validate_on_submit():
        postData = blogForm.data
        currentPost.title = postData["title"]
        currentPost.subtitle=postData["subtitle"]
        currentPost.author=postData["author"]
        currentPost.img_url=postData["img_url"]
        currentPost.body=postData["body"]
        currentPost.date=getdate()



        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("edit-post.html", form=blogForm)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug = True)

