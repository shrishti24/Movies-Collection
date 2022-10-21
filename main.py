from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "278dd8c3bb1ee1eca0e406490a5e4e18"
API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyNzhkZDhjM2JiMWVlMWVjYTBlNDA2NDkwYTVlNGUxOCIsInN1YiI6IjYzNTI0OTRmODgwYzkyMDA3OTZjZTI0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.7TUWGRmJFU7ot-imaBgmAZBgYt1x2JZx8ojqf_zVHH0"

Headers = {
    'api_key': API_KEY,
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json;charset=utf-8'
}
API_SEARCH_URL = "https://api.themoviedb.org/3/search/movie?"
API_FIND_URL = "https://api.themoviedb.org/3/movie/"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = "$%^ambhjk)**?!@~bl"
Bootstrap(app)

app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie_collections.db"
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)


class Add_Movie(FlaskForm):
    new_movie = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class Edit_Movie(FlaskForm):
    new_rating = StringField("Your Rating Out Of 10 e.g.7.5", validators=[DataRequired()])
    new_review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField('Submit')


db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    #This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    movie = Add_Movie()
    if request.method == "POST":
        title = request.form["new_movie"].title()
        url_get = requests.get(f"{API_SEARCH_URL}query={title}", headers=Headers)
        url_response = url_get.json()
        return render_template("select.html", movie_list=url_response["results"])

    return render_template("add.html", movie=movie)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{API_FIND_URL}{movie_api_id}"
        response = requests.get(movie_api_url, headers=Headers)
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            # The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )

        db.session.add(new_movie)
        print(new_movie.id)
        db.session.commit()
        return redirect(url_for('update', id=new_movie.id))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def update(id):
    movie_form = Edit_Movie()
    movie = Movie.query.get(id)
    print(movie.title)
    if request.method == 'POST':
        movie.rating = request.form['new_rating']
        movie.review = request.form['new_review']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', movie_form=movie_form)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
