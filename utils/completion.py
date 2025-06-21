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
    Fetch all media items from the database.
    Returns a dictionary containing lists of books, movies, and music items.
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
    Detect missing fields in the media item and return a dictionary of missing fields.
    """
    missing = {}
    if media_type == "book":
        fields = ["author", "genre", "title", "year", "language", "publisher", "country", "description"]
    elif media_type == "movie":
        fields = ["director", "genre", "title", "year", "country", "type", "language", "description"]
    elif media_type == "music":
        fields = ["artist", "genre", "title", "year", "language", "label", "country", "description"]
    else:
        return missing

    for field in fields:
        value = getattr(media_item, field, None)
        if not value or (isinstance(value, str) and value.strip() == ""):
            missing[field] = None
    return missing

def build_enrichment_prompt(media_type, title, missing_fields):
    """
    Build a prompt to ask Gemini to enrich missing fields for a media item.
    """
    prompt = (
        f"The following {media_type} titled '{title}' has missing information for these fields: "
        f"{', '.join(missing_fields)}. "
        f"Please provide the missing details. Return ONLY a valid JSON object where keys are the field names "
        f"and values are the corresponding information. If information for a field cannot be found, omit the key or return null for its value. "
        f"Do not include any explanatory text or markdown."
    )
    return prompt

def build_validation_prompt(media_type, media_data):
    """
    Build a prompt for Gemini to verify the metadata of a media item.
    """
    return (
        f"Please verify the following metadata for a {media_type}. "
        f"Return ONLY a valid JSON object listing inaccurate fields with corrected suggestions if applicable.\n\n"
        f"Metadata:\n{json.dumps(media_data, indent=2)}\n\n"
        f"Example output:\n"
        f'{{"author": "Correct Author", "year": "Correct Year"}}\n\n'
        f"Do NOT include markdown or explanations."
    )

def call_gemini_api(prompt):
    """
    Call the Gemini API with the given prompt and return the response.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Gemini API key not configured")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[len("```json"):]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[len("```"):]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-len("```")]
        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            return {}

        enriched_data = json.loads(cleaned_text)
        if isinstance(enriched_data, dict):
            return enriched_data
        else:
            return {}

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {}

def generate_tags_for_media(media_type, title, description):
    """
    Generate relevant tags for a given media item using Gemini AI.
    """
    prompt = (
        f"Please generate relevant tags for the following {media_type}:\n\n"
        f"Title: {title}\nDescription: {description}\n\n"
        f"Return ONLY a valid JSON array of tags. Tags should be related to the genre, themes, or style of the {media_type}. "
        f"Do NOT include any explanations or extra text."
    )
    return call_gemini_api(prompt)

def update_media_item(media_item, media_type, enriched_data):
    """
    Update a media item in the database with the enriched data.
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

def validate_media_item(media_item, media_type):
    """
    Validate a media item by checking its metadata and correcting any inaccuracies.
    """
    media_data = {
        field: getattr(media_item, field, None)
        for field in ["title", "author", "genre", "year", "language", "publisher", "country",
                      "director", "type", "artist", "label", "description"]
        if hasattr(media_item, field)
    }
    prompt = build_validation_prompt(media_type, media_data)
    corrected_fields = call_gemini_api(prompt)
    if corrected_fields:
        updated = False
        for field, corrected_value in corrected_fields.items():
            if hasattr(media_item, field) and corrected_value:
                current_value = getattr(media_item, field)
                if current_value != corrected_value:
                    setattr(media_item, field, corrected_value)
                    updated = True
        if updated:
            db.session.add(media_item)
            db.session.commit()
            return True
    return False

def enrich_single_media_item(media_item, media_type):
    """
    Enrich a single media item by filling missing fields and generating tags.
    Returns the generated tags list.
    """
    missing_fields = detect_missing_fields(media_item, media_type)

    # Enrich missing fields first
    if missing_fields:
        prompt = build_enrichment_prompt(media_type, media_item.title or "Unknown Title", missing_fields.keys())
        enriched_data = call_gemini_api(prompt)
        if enriched_data:
            updated = update_media_item(media_item, media_type, enriched_data)
            if updated:
                db.session.commit()
    
    # Generate tags for the media with error handling and type check
    description = getattr(media_item, 'description', "") or ""
    tags = generate_tags_for_media(media_type, media_item.title or "Unknown Title", description)
    clean_tags = []
    if tags and isinstance(tags, list):
        try:
            # Ensure tags is a list of strings
            clean_tags = [str(tag) for tag in tags if isinstance(tag, (str, int, float))]
            if hasattr(media_item, 'tags'):
                media_item.tags = clean_tags
                db.session.commit()
        except Exception as e:
            print(f"Error assigning tags: {e}")

    return clean_tags

def enrich_all_media():
    """
    Enrich all media items in the database by detecting missing fields, validating metadata, and generating tags.
    """
    media = fetch_all_media()
    total_updated = 0
    for media_type, items in media.items():
        for item in items:
            if enrich_single_media_item(item, media_type):
                total_updated += 1
    if total_updated > 0:
        db.session.commit()
    return total_updated
