import json
import requests
from models.book_model import Book
from models.cinema_model import Cinema
from models.music_model import Music
from models.user_media_model import UserMedia
from models.user_model import db
from flask import current_app
import google.generativeai as genai

def fetch_all_media():
    """
    Fetch all user-added media items: books, movies, music.
    Returns dict with lists of media objects.
    """
    books = Book.query.all()
    movies = Cinema.query.all()
    music = Music.query.all()
    return {
        "books": books,
        "movies": movies,
        "music": music
    }

def detect_missing_fields(media_item, media_type):
    """
    Detect missing or empty fields in a media item based on type.
    Returns a dict of missing fields with None or empty values.
    """
    missing = {}
    if media_type == "book":
        fields = ["author", "genre", "title", "year", "language", "publisher", "country"]
        for field in fields:
            value = getattr(media_item, field, None)
            if not value or (isinstance(value, str) and value.strip() == ""):
                missing[field] = None
    elif media_type == "movie":
        fields = ["director", "genre", "title", "year", "country", "type", "language"]
        for field in fields:
            value = getattr(media_item, field, None)
            if not value or (isinstance(value, str) and value.strip() == ""):
                missing[field] = None
    elif media_type == "music":
        fields = ["artist", "genre", "title", "year", "language", "label", "country"]
        for field in fields:
            value = getattr(media_item, field, None)
            if not value or (isinstance(value, str) and value.strip() == ""):
                missing[field] = None
    return missing

def enrich_single_media_item(media_item, media_type):
    """
    Enrich a single media item by detecting missing fields and using Gemini to complete them.
    Updates the media item in the database if enriched.
    """
    missing_fields = detect_missing_fields(media_item, media_type)
    if not missing_fields:
        return False  # No enrichment needed

    prompt = build_gemini_prompt(media_type, media_item.title or "Unknown Title", missing_fields.keys())
    enriched_data = call_gemini_api(prompt)
    if enriched_data:
        updated = update_media_item(media_item, media_type, enriched_data)
        if updated:
            db.session.commit()
            return True
    return False

def build_gemini_prompt(media_type, title, missing_fields):
    """
    Build a prompt for Gemini to complete missing fields for a media item.
    """
    prompt = (
        f"The following {media_type} titled '{title}' has missing information for these fields: "
        f"{', '.join(missing_fields)}. "
        f"Please provide the missing details. Return ONLY a valid JSON object where keys are the field names "
        f"and values are the corresponding information. For example, if 'author' and 'genre' are missing for a book, "
        f"return: {{\"author\": \"Author Name\", \"genre\": \"Genre Name\"}}. "
        f"If information for a field cannot be found, omit the key or return null for its value. "
        f"Do not include any explanatory text or markdown."
    )
    return prompt

def call_gemini_api(prompt):
    """
    Call the Gemini API with the given prompt and return parsed JSON response.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Gemini API key not configured")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(prompt)
        
        print(f"Gemini Raw Response Text (Completion): {response.text}")

        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[len("```json"):]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[len("```"):] 
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-len("```")]   
        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            print("Error: Gemini returned an empty response after cleaning (Completion).")
            return {}
            
        enriched_data = json.loads(cleaned_text)
        if isinstance(enriched_data, dict):
            return enriched_data
        else:
            print(f"Error: Gemini response was not a JSON object as expected (Completion). Got: {type(enriched_data)}")
            return {}
            
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from Gemini response (Completion). Response: '{response.text if 'response' in locals() else 'N/A'}'. Error: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred with Gemini API (Completion): {e}")
        return {}

def update_media_item(media_item, media_type, enriched_data):
    """
    Update the media item with enriched data from Gemini.
    """
    updated = False
    for field, value in enriched_data.items():
        if hasattr(media_item, field) and value:
            current_value = getattr(media_item, field)
            if not current_value or current_value.strip() == "":
                setattr(media_item, field, value)
                updated = True
    if updated:
        db.session.add(media_item)
    return updated

def enrich_all_media():
    """
    Main function to enrich all media items with missing data using Gemini.
    """
    media = fetch_all_media()
    total_updated = 0

    for media_type, items in media.items():
        for item in items:
            missing_fields = detect_missing_fields(item, media_type)
            if missing_fields:
                prompt = build_gemini_prompt(media_type, item.title or "Unknown Title", missing_fields.keys())
                enriched_data = call_gemini_api(prompt)
                if enriched_data:
                    updated = update_media_item(item, media_type, enriched_data)
                    if updated:
                        total_updated += 1
    if total_updated > 0:
        db.session.commit()
    return total_updated