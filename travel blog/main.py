from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField

from datetime import date
def getdate():
    months = ["January", "February", "March", "April", "May", "June", "Juli", "August", "September", "October", "November", "December"]
    month = months[date.today().month]
    dateString = f"{month} {date.today().day}, {date.today().year} "
    return dateString


app = Flask(__name__)
ckeditor = CKEditor()
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor.init_app(app)



Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Travell.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class TravelPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    start = db.Column(db.String(250), nullable=False)
    end = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class DayPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journey = db.Column(db.Integer)
    title = db.Column(db.String(250), unique=False, nullable=False)
    subtitle = db.Column(db.String(250), nullable=True)
    start = db.Column(db.String(250), nullable=True)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=True)





with app.app_context():
    db.create_all()
    db.session.commit()

##WTForm
class CreateJourneyForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    start = StringField("Start of the Journey")
    end = StringField("End of the Journey")
    img_url = StringField("Thumbnail Image URL", validators=[URL()])
    body = CKEditorField("Description of the Journey, give more details", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class AddDay(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    author = StringField("Author")
    start = StringField("Data of the day")

    img_url = StringField("Thumbnail Image URL", validators=[URL()])
    body = CKEditorField("What happend on that day, what is the plan for the day?, give more details")
    submit = SubmitField("Submit Day")


@app.route("/gallery",methods = ["GET", "POST"])
def show_gallery():
    main = db.session.query(TravelPost).all()
    sub = db.session.query(DayPost).all()
    return render_template("gallery.html", sub = sub, main = main)
@app.route('/', methods = ["GET", "POST"])
def get_all_posts():
    posts = db.session.query(TravelPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>",methods = ["GET", "POST"])
def show_post(post_id):
    #requested_post = db.session.query(BlogPost).get(post_id)
    requested_post = TravelPost.query.get(post_id)
    posts = db.session.query(DayPost).filter(DayPost.journey == post_id).all()
    return render_template("post.html", post=requested_post, all_posts=posts, count = 1)

@app.route("/author/<name>",methods = ["GET", "POST"])
def show_author(name):
    # alle posts

    author_posts = db.session.query(TravelPost).filter(TravelPost.author == name).all()


    return render_template("author.html", all_posts=author_posts, author = name)



@app.route("/new-post", methods=['GET', 'POST'])
def newPost():
    blogForm = CreateJourneyForm()
    if blogForm.validate_on_submit():

        postData = blogForm.data
        title = postData
        print(postData["title"])
        print(postData["subtitle"])
        newPost = TravelPost(title = postData["title"],
            subtitle = postData["subtitle"],
            author= postData["author"],
            img_url=postData["img_url"],
            body = postData["body"],
            start=postData["start"],
            end = postData["end"],
                           )

        db.session.add(newPost)
        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form = blogForm)

@app.route("/delete", methods=['GET', 'DELETE'])
def delete_post():
    ids = int(request.args.get("post_id"))
    if request.args.get("blog") == "Day":
        post = db.session.query(DayPost).get(ids)
    else:
        post = db.session.query(TravelPost).get(ids)
    db.session.delete(post)
    db.session.commit()
    posts = db.session.query(TravelPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/edit", methods=['GET', 'PATCH', 'POST'])
def edit_post():
    ids = int(request.args.get("post_id"))
    currentPost = db.session.query(TravelPost).get(ids)

    print(currentPost)
    #ids = db.session.get('post.id')
    blogForm = CreateJourneyForm(title =currentPost.title,
             subtitle =currentPost.subtitle,
             author = currentPost.author,
             img_url = currentPost.img_url,
             body = currentPost.body,
             start=currentPost.start,
             end=currentPost.end
             )
    if blogForm.validate_on_submit():
        postData = blogForm.data
        currentPost.title = postData["title"]
        currentPost.subtitle=postData["subtitle"]
        currentPost.author=postData["author"]
        currentPost.img_url=postData["img_url"]
        currentPost.body=postData["body"]
        currentPost.start = postData["start"]
        currentPost.end = postData["end"]




        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template("edit-post.html", form=blogForm)




@app.route("/day/<int:post_id>",methods = ["GET", "POST"])
def show_day(post_id):
    #requested_post = db.session.query(BlogPost).get(post_id)
    requested_post = TravelPost.query.get(post_id)
    posts = db.session.query(DayPost).all()
    return render_template("post.html", post=requested_post, all_posts=posts, count = 1)


@app.route("/add-day", methods=['GET', 'PATCH', 'POST'])
def add_day():
    ids = int(request.args.get("post_id"))
    currentPost = db.session.query(TravelPost).get(ids)

    journeyId = currentPost.id
    print(journeyId)

    blogForm = AddDay(
             author = currentPost.author,
             img_url = currentPost.img_url,
             start=currentPost.start,

             )
    if blogForm.validate_on_submit():
        postData = blogForm.data
        newDay = DayPost(title=postData["title"],
                          journey = ids,
                          subtitle=postData["subtitle"],
                          start=postData["start"],
                          body=postData["body"],
                          author=postData["author"],
                          img_url=postData["img_url"],

                          )
        db.session.add(newDay)
        db.session.commit()


        #posts = db.session.query(DayPost).all()
        return redirect(url_for('show_post', post_id = journeyId))
        #return render_template("post.html", post=current_post, all_posts=posts, count=1)

        return redirect(url_for('get_all_posts'))

    return render_template("add-day.html", form=blogForm)




@app.route("/edit-day", methods=['GET', 'PATCH', 'POST'])
def edit_day():
    ids = int(request.args.get("post_id"))
    currentPost = db.session.query(DayPost).get(ids)
    journey.id = db.session.get()

    print(currentPost)
    #ids = db.session.get('post.id')
    blogForm = AddDay(title =currentPost.title,
                      journey = ids,
             subtitle =currentPost.subtitle,
             author = currentPost.author,
             img_url = currentPost.img_url,
             body = currentPost.body,
             start=currentPost.start,

             )
    if blogForm.validate_on_submit():
        postData = blogForm.data
        currentPost.title = postData["title"]
        currentPost.subtitle=postData["subtitle"]

        currentPost.author=postData["author"]
        currentPost.img_url=postData["img_url"]
        currentPost.body=postData["body"]
        currentPost.start = postData["start"]





        db.session.commit()

        return redirect(url_for('show_post', post_id = currentPost.journey ))

    return render_template("edit-post.html", form=blogForm)





@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug = True)

