import requests
from models.cinema_model import Cinema, db
from models.user_media_model import UserMedia
from flask import current_app

def search_cinema(query, page=1):
    local_cinema = []
    if query:
        local_cinema = Cinema.query.filter(Cinema.title.contains(query)).all()
    
    local_results = [{
        "title": cinema.title,
        "genre": cinema.genre,
        "year": cinema.year,
        "country": cinema.country,
        "director": cinema.director,
        "type": cinema.type,
        "language": cinema.language,
        "rating": cinema.rating,
        "reviews": cinema.reviews,
        "coverart": cinema.coverart,
    } for cinema in local_cinema]

    _cinemas, cinema_total, _ = search_tmdb_cinema(query, page)
    results = local_results + _cinemas
    results_len = len(local_results) + cinema_total
    return results, results_len, page

def search_tmdb_cinema(query, page=1):
    api_key = current_app.config.get('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page={page}'
    response = requests.get(url)
    data = response.json()
    cinema = []

    genre_mapping = {
        28: "Action",
        12: "Adventure",
        16: "Animation",
        35: "Comedy",
        80: "Crime",
        99: "Documentary",
        18: "Drama",
        10751: "Family",
        14: "Fantasy",
        36: "History",
        27: "Horror",
        10402: "Music",
        9648: "Mystery",
        10749: "Romance",
        878: "Science Fiction",
        10770: "TV Movie",
        53: "Thriller",
        10752: "War",
        37: "Western"
    }

    for item in data.get("results",[]):
        cinema_data = {
            "title": item.get("title"),
            "genre": ",".join([genre_mapping.get(genre_id, "Unknown") for genre_id in item.get("genre_ids", [])]),
            "year": item.get("release_date")[:4] if item.get("release_date") else 0,
            "country": item.get("production_countries", [{}])[0].get("name", ""),
            "director": "",
            "type": "",
            "language": item.get("original_language"),
            "rating": item.get("vote_average"),
            "reviews": item.get("overview"),
            "coverart": f'https://image.tmdb.org/t/p/w500/{item.get("poster_path")}',
        }
        cinema.append(cinema_data)
    return cinema, data.get("total_results", 0), page

def get_genre_names(genre_ids, api_key):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    genre_dict = {genre['id']: genre['name'] for genre in data.get('genres', [])}
    return [genre_dict.get(genre_id, "Unknown") for genre_id in genre_ids]

def save_cinema(cinema_data, user_id,review=None, rating=None, date_consumed=None):
    existing_cinema = Cinema.query.filter_by(title=cinema_data.get("title")).first()
    if not existing_cinema:
        cinema = Cinema(
            title=cinema_data.get("title"),
            genre=cinema_data.get("genre"),
            year=cinema_data.get("year"),
            country=cinema_data.get("country"),
            director=cinema_data.get("director", "Empty"),
            type=cinema_data.get("type", "Empty"),
            language=cinema_data.get("language"),
            description=cinema_data.get("reviews", "No Description Available"),
            coverart=cinema_data.get("coverart")
        )
        db.session.add(cinema)
        db.session.flush()
    else:
        cinema = existing_cinema

    user_media_entry = UserMedia.query.filter_by(user_id=user_id, media_type='cinema', cinema_id=cinema.cinema_id).first()
    if not user_media_entry:
        user_media_entry = UserMedia(
            user_id=user_id,
            media_type='cinema',
            cinema_id=cinema.cinema_id,
            review=review,
            rating=float(rating) if rating else None,
            date_consumed=date_consumed,
            done=True if date_consumed else False
        )
        db.session.add(user_media_entry)
    else:
        if review:
            user_media_entry.review = review
        if rating:
            user_media_entry.rating = float(rating)
        if date_consumed:
            user_media_entry.date_consumed = date_consumed
        user_media_entry.done = True if date_consumed else False
    db.session.commit()
    return cinema