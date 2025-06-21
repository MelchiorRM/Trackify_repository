import random
import json
from sqlalchemy import or_
from flask import current_app
import google.generativeai as genai
from models.book_model import Book
from models.music_model import Music
from models.cinema_model import Cinema
from models.user_media_model import UserMedia
from models.social_model import Follow
from utils.pagination import paginate

def get_user_consumption(user_id, db_session):
    return {
        "books": Book.query.join(UserMedia, Book.book_id == UserMedia.book_id).filter(UserMedia.user_id == user_id).all(),
        "movies": Cinema.query.join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id).filter(UserMedia.user_id == user_id).all(),
        "music": Music.query.join(UserMedia, Music.music_id == UserMedia.music_id).filter(UserMedia.user_id == user_id).all(),
    }

def recommend_cross_art(consumed_books, consumed_movies, consumed_music, page=1, per_page=10):
    authors = set(b.author for b in consumed_books if b.author)
    book_genres = set(g for b in consumed_books for g in (b.genre or "").split(",") if g and g != "Unknown")
    directors = set(m.director for m in consumed_movies if m.director)
    movie_genres = set(g for m in consumed_movies for g in (m.genre or "").split(",") if g)
    artists = set(m.artist for m in consumed_music if m.artist)
    music_genres = set(g for m in consumed_music for g in (m.genre or "").split(",") if g and g != "Unknown")

    countries = set()
    years = set()
    languages = set()
    labels = set()
    types = set()

    for item in consumed_books + consumed_movies + consumed_music:
        if hasattr(item, "country") and item.country:
            countries.add(item.country)
        if hasattr(item, "year") and item.year:
            years.add(str(item.year))
        if hasattr(item, "language") and item.language:
            languages.add(item.language)
        if hasattr(item, "label") and item.label:
            labels.add(item.label)
        if hasattr(item, "type") and item.type:
            types.add(item.type)

    recom_books_query = Book.query.join(UserMedia, Book.book_id == UserMedia.book_id).filter(
        or_(
            Book.author.in_(authors),
            *[Book.genre.like(f"%{genre.strip()}%") for genre in book_genres],
            Book.country.in_(countries) if countries else False,
            Book.year.in_(years) if years else False,
            Book.language.in_(languages) if languages else False,
            *[UserMedia.tags.contains([tag]) for tag in labels] if labels else [],
        ),
        ~Book.book_id.in_([b.book_id for b in consumed_books])
    )

    recom_movies_query = Cinema.query.join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id).filter(
        or_(
            Cinema.director.in_(directors),
            *[Cinema.genre.like(f"%{genre.strip()}%") for genre in movie_genres],
            Cinema.country.in_(countries) if countries else False,
            Cinema.year.in_(years) if years else False,
            Cinema.language.in_(languages) if languages else False,
            Cinema.type.in_(types) if types else False,
            *[UserMedia.tags.contains([tag]) for tag in labels] if labels else [],
        ),
        ~Cinema.cinema_id.in_([m.cinema_id for m in consumed_movies])
    )

    recom_music_query = Music.query.join(UserMedia, Music.music_id == UserMedia.music_id).filter(
        or_(
            *[Music.artist.like(f"%{artist.strip()}%") for artist in artists],
            *[Music.genre.like(f"%{genre.strip()}%") for genre in music_genres],
            Music.country.in_(countries) if countries else False,
            Music.year.in_(years) if years else False,
            Music.language.in_(languages) if languages else False,
            Music.label.in_(labels) if labels else False,
            *[UserMedia.tags.contains([tag]) for tag in labels] if labels else [],
        ),
        ~Music.music_id.in_([m.music_id for m in consumed_music])
    )

    recom_books_paginated = paginate(recom_books_query, page, per_page)
    recom_movies_paginated = paginate(recom_movies_query, page, per_page)
    recom_music_paginated = paginate(recom_music_query, page, per_page)

    combined_recommendations = []
    for b in recom_books_paginated["items"]:
        combined_recommendations.append({"item": b, "type": "book"})
    for m in recom_movies_paginated["items"]:
        combined_recommendations.append({"item": m, "type": "cinema"})
    for mu in recom_music_paginated["items"]:
        combined_recommendations.append({"item": mu, "type": "music"})

    return {
        "recommendations": combined_recommendations,
        "total_pages": max(recom_books_paginated["total_pages"], recom_movies_paginated["total_pages"], recom_music_paginated["total_pages"]),
        "current_page": page
    }

def collaborative_filtering(user_id, consumed_books, consumed_movies, consumed_music, page=1, per_page=10):
    similar_users = [
        f.followed_id for f in Follow.query.filter_by(follower_id=user_id).all()
    ]

    commun_books_query = Book.query.join(UserMedia, Book.book_id == UserMedia.book_id).filter(
        UserMedia.user_id.in_(similar_users),
        ~UserMedia.book_id.in_([b.book_id for b in consumed_books])
    )

    commun_movies_query = Cinema.query.join(UserMedia, Cinema.cinema_id == UserMedia.cinema_id).filter(
        UserMedia.user_id.in_(similar_users),
        ~UserMedia.cinema_id.in_([m.cinema_id for m in consumed_movies])
    )

    commun_music_query = Music.query.join(UserMedia, Music.music_id == UserMedia.music_id).filter(
        UserMedia.user_id.in_(similar_users),
        ~UserMedia.music_id.in_([m.music_id for m in consumed_music])
    )

    commun_books_paginated = paginate(commun_books_query, page, per_page)
    commun_movies_paginated = paginate(commun_movies_query, page, per_page)
    commun_music_paginated = paginate(commun_music_query, page, per_page)

    combined_collaborative = []
    for b in commun_books_paginated["items"]:
        combined_collaborative.append({"item": b, "type": "book"})
    for m in commun_movies_paginated["items"]:
        combined_collaborative.append({"item": m, "type": "cinema"})
    for mu in commun_music_paginated["items"]:
        combined_collaborative.append({"item": mu, "type": "music"})

    return {
        "recommendations": combined_collaborative,
        "total_pages": max(commun_books_paginated["total_pages"], commun_movies_paginated["total_pages"], commun_music_paginated["total_pages"]),
        "current_page": page
    }

def build_prompt(consumed_books, consumed_movies, consumed_music):
    format_items = "\n".join([
        f'- {type(item).__name__}: "{item.title}" by {getattr(item, "author", getattr(item, "director", getattr(item, "artist", "Unknown")))} (genre: {getattr(item, "genre", "Unknown")})'
        for item in consumed_books + consumed_movies + consumed_music
    ])
    return f"""
The user has consumed the following media items:
{format_items}

Please recommend 10 culturally, thematically, or stylistically connected titles across books, music, or movies that the user might enjoy.

Return only a JSON array of objects with "title" and "type" fields, where "type" is one of "book", "movie", or "music".

Example:
[
  {{"title": "Example Book Title", "type": "book"}},
  {{"title": "Example Movie Title", "type": "movie"}},
  {{"title": "Example Music Title", "type": "music"}}
]

Only return the JSON array, no additional text.
""".strip()

def call_gemini_api(prompt):
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not configured.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        print(f"Gemini Raw Response Text (Recommendations): {response.text}")
        # Added debug log of raw response
        print(f"Raw Gemini Response: {response.text}")
        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[len("```json"):]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[len("```"):]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-len("```")]

        cleaned_text = cleaned_text.strip()
        if not cleaned_text:
            print("Error: Gemini returned an empty response after cleaning.")
            return []
        gemini_recom = json.loads(cleaned_text)
        if isinstance(gemini_recom, list):
            return gemini_recom
        else:
            print(f"Error: Gemini response was not a JSON list as expected. Got: {type(gemini_recom)}")
            return []
    except json.JSONDecodeError as e:
        print("Gemini API error:", e)
        return []

def get_gemini_recommendations(gemini_recom):
    import re
    gemini_combined = []
    if isinstance(gemini_recom, list):
        for item in gemini_recom:
            if isinstance(item, dict) and "title" in item and "type" in item:
                title, mtype = item["title"], item["type"].lower()
                # Remove trailing type annotation in parentheses, e.g. "Harry Potter (Book)" -> "Harry Potter"
                title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
                if mtype == "book":
                    b = Book.query.filter_by(title=title).first()
                    if b:
                        gemini_combined.append({"item": b, "type": "book"})
                        print(f"Gemini recommendation found in DB: {title}")
                    else:
                        print(f"Gemini recommendation NOT found in DB: {title}")
                        gemini_combined.append({"item": {"title": title}, "type": "book"})
                elif mtype == "movie":
                    m = Cinema.query.filter_by(title=title).first()
                    if m:
                        gemini_combined.append({"item": m, "type": "cinema"})
                        print(f"Gemini recommendation found in DB: {title}")
                    else:
                        print(f"Gemini recommendation NOT found in DB: {title}")
                        gemini_combined.append({"item": {"title": title}, "type": "cinema"})
                elif mtype == "music":
                    mu = Music.query.filter_by(title=title).first()
                    if mu:
                        gemini_combined.append({"item": mu, "type": "music"})
                        print(f"Gemini recommendation found in DB: {title}")
                    else:
                        print(f"Gemini recommendation NOT found in DB: {title}")
                        gemini_combined.append({"item": {"title": title}, "type": "music"})
    return gemini_combined

def combine_and_randomize_recommendations(user_id, consumed_books, consumed_movies, consumed_music, page=1, per_page=10):
    cross_art_data = recommend_cross_art(consumed_books, consumed_movies, consumed_music, page, per_page)
    collaborative_data = collaborative_filtering(user_id, consumed_books, consumed_movies, consumed_music, page, per_page)

    prompt = build_prompt(consumed_books, consumed_movies, consumed_music)
    gemini_recom = call_gemini_api(prompt)
    gemini_recs = get_gemini_recommendations(gemini_recom)

    combined = cross_art_data["recommendations"] + collaborative_data["recommendations"] + gemini_recs

    # Remove duplicates based on item id and type
    seen = set()
    unique_recs = []
    for rec in combined:
        key = (rec["type"], getattr(rec["item"], f"{rec['type']}_id", None))
        if key not in seen:
            seen.add(key)
            unique_recs.append(rec)

    # Randomize with slight bias towards cross_art_recs (first part of list)
    def weighted_shuffle(items, weight=0.7):
        # weight: probability to keep order, else shuffle
        import random
        if random.random() > weight:
            random.shuffle(items)
        return items

    randomized_recs = weighted_shuffle(unique_recs)

    return {
        "recommendations": randomized_recs,
        "current_page": page,
        "total_pages": max(cross_art_data["total_pages"], collaborative_data["total_pages"])
    }
