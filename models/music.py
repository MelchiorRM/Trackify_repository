import requests
from models.music_model import Music, db
from models.user_media_model import UserMedia
from flask import current_app

def search_music(query, page=1):
    local_music = []
    if query:
        local_music = Music.query.filter(Music.title.contains(query)).all()

    local_results = [{
        "title": music.title,
        "artist": music.artist,
        "genre": music.genre,
        "year": music.year,
        "language": music.language,
        "label": music.label,
        "country": music.country,
        "rating": music.rating,
        "reviews": music.reviews,
        "coverart": music.coverart
        } for music in local_music]
    _music, music_total, _ = search_music_spotify(query, page)
    results = local_results + _music
    results_len = len(local_results) + music_total
    return results, results_len, page

def search_music_spotify(query, page=1):
    client_id = current_app.config.get('SPOTIFY_CLIENT_ID')
    client_secret = current_app.config.get('SPOTIFY_CLIENT_SECRET')
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    })
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    search_url = f'https://api.spotify.com/v1/search?q={query}&type=track&limit=20&offset={20 * (page - 1)}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(search_url, headers=headers)
    data = response.json()
    music = []
    for item in data['tracks']['items']:
        music_data = {
            "title": item.get("name"),
            "artist": ",".join([artist['name'] for artist in item.get("artists", [])]),
            "genre": "Unknown",
            "year": int(item.get("album", {}).get("release_date", "0")[:4]) if item.get("album", {}).get("release_date") else 0,
            "language": "Unknown",
            "label": item.get("album", {}).get("label"),
            "country": "Unknown",
            "rating": item.get("popularity"),
            "coverart": item.get("album", {}).get("images", [{}])[0].get("url")
        }
        music.append(music_data)
    total_results = data.get('tracks', {}).get('total', 0)
    return music, total_results, page

def save_music(music_data, user_id, review=None, rating=None, date_consumed=None):
    from utils.completion import enrich_single_media_item
    existing_music = Music.query.filter_by(title=music_data.get('title')).first()
    if not existing_music:
        music = Music(
            title=music_data.get("title"),
            artist=music_data.get("artist"),
            genre=music_data.get("genre", "Empty"),
            year=music_data.get("year"),
            language=music_data.get("language", "Empty"),
            label=music_data.get("label"),
            country=music_data.get("country", "Empty"),
            description=music_data.get("reviews"),
            coverart=music_data.get("coverart")
        )
        db.session.add(music)
        db.session.flush()
        # Enrich the music data before commit
        enrich_single_media_item(music, "music")
    else:
        music = existing_music
    
    user_media_entry = UserMedia.query.filter_by(user_id=user_id, media_type='music', music_id=music.music_id).first()
    if not user_media_entry:
        user_media_entry = UserMedia(
            user_id=user_id,
            media_type='music',
            music_id=music.music_id,
            review=review,
            rating=float(rating) if rating and rating != 'None' and 0 <= float(rating) <= 10 else None,
            date_consumed=date_consumed if date_consumed and date_consumed != '' else None,
            done=True if date_consumed and date_consumed != '' else False
            )
        db.session.add(user_media_entry)
    else:
        if review:
            user_media_entry.review = review
        if rating and rating != 'None':
            if 0 <= float(rating) <= 10:
                user_media_entry.rating = float(rating)
        if date_consumed and date_consumed != '':
            user_media_entry.date_consumed = date_consumed
            user_media_entry.done = True
    db.session.commit()
    return music
