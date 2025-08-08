from flask import Blueprint, request, render_template, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.book_model import Book, db
from models.music_model import Music
from models.cinema_model import Cinema
from models.books import search_books, save_books
from models.cinema import search_cinema, save_cinema
from models.music import search_music, save_music
from models.user_media_model import UserMedia
from models.social_model import Follow, Like, Notification, List, Comment
from models.user_model import User
from datetime import datetime

media_routes = Blueprint('media_routes', __name__)

@media_routes.route("/search", methods=["GET"])
@login_required
def search():
    search_query = request.args.get('search_query')
    media_type = request.args.get('media_type')
    if media_type == "books":
        return redirect(url_for('media_routes.books', search_query=search_query, page=1))
    elif media_type == "music":
        return redirect(url_for('media_routes.music', search_query=search_query, page=1))
    elif media_type == "cinema":
        return redirect(url_for('media_routes.cinema', search_query=search_query, page=1))
    else:
        flash("Invalid media type", "danger")
        return redirect(url_for('main_routes.home'))

@media_routes.route("/books", methods=["GET", "POST"])
@login_required
def books():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for('media_routes.books', search_query=search_query, page=1))
        else:
            book_data = {
                "title": request.form["title"],
                "author": request.form["author"],
                "genre": request.form["genre"],
                "year": request.form["year"],
                "language": request.form["language"],
                "publisher": request.form["publisher"],
                "country": request.form["country"],
                "coverart": request.form["coverart"],
            }
            review = request.form.get("reviews")
            rating = request.form.get("rating")
            date_consumed = request.form.get("date_consumed")
            user_id = current_user.user_id
            book = save_books(book_data, user_id, review, rating, date_consumed)
            flash("Book added to library!", "success")
            return redirect(url_for("media_routes.media", media_id=book.book_id, media_type='book'))
    
    search_query = request.args.get('search_query','')
    page = int(request.args.get('page', 1))
    if search_query:
        books, total_results, current_page = search_books(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_books = books[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='book').all()
        paged_books = [Book.query.get(entry.book_id) for entry in user_media_entries if entry.book_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("book.html", books=paged_books, search_query=search_query, page=current_page, has_next=has_next, has_prev=has_prev)

@media_routes.route("/music", methods=["GET", "POST"])
@login_required
def music():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for("media_routes.music", search_query=search_query, page=1))
        else:
            music_data = {
                "title": request.form.get("title"),
                "artist": request.form.get("artist"),
                "genre": request.form.get("genre"),
                "year": request.form.get("year"),
                "language": request.form.get("language"),
                "label": request.form.get("label"),
                "country": request.form.get("country"),
                "coverart": request.form.get("coverart")
            }
            review = request.form.get("reviews")
            rating = request.form.get("rating")
            date_consumed = request.form.get("date_consumed")
            user_id = current_user.user_id
            music = save_music(music_data, user_id, review, rating, date_consumed)
            flash("Music added to library!", "success")
            return redirect(url_for("media_routes.media", media_id=music.music_id, media_type='music'))
    
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    if search_query:
        music, total_results, current_page = search_music(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_music = music[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='music').all()
        paged_music = [Music.query.get(entry.music_id) for entry in user_media_entries if entry.music_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("music.html", search_query=search_query, music=paged_music, page=current_page, has_next=has_next, has_prev=has_prev)

@media_routes.route("/cinema", methods=["GET", "POST"])
@login_required
def cinema():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        if search_query:
            return redirect(url_for("media_routes.cinema", search_query=search_query, page=1))
        else:
            cinema_data = {
                "title": request.form.get("title"),
                "genre": request.form.get("genre"),
                "year": request.form.get("year"),
                "country": request.form.get("country"),
                "director": request.form.get("director"),
                "type": request.form.get("type", ""), 
                "language": request.form.get("language"),
                "coverart": request.form.get("coverart")
            }
            review = request.form.get("reviews")
            rating = request.form.get("rating")
            date_consumed = request.form.get("date_consumed")
            user_id = current_user.user_id
            cinema = save_cinema(cinema_data, user_id, review, rating, date_consumed)
            flash("Cinema added to library!", "success")
            return redirect(url_for("media_routes.media", media_id=cinema.cinema_id, media_type='cinema'))
    
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    if search_query:
        cinema, total_results, current_page = search_cinema(search_query, page)
        results_per_page = 20
        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paged_cinema = cinema[start_index:end_index]
        has_next = end_index < total_results
        has_prev = current_page > 1
    else:
        user_media_entries = UserMedia.query.filter_by(user_id=current_user.user_id, media_type='cinema').all()
        paged_cinema = [Cinema.query.get(entry.cinema_id) for entry in user_media_entries if entry.cinema_id]
        has_next = False
        has_prev = False
        current_page = 1
    return render_template("cinema.html", cinema=paged_cinema, search_query=search_query, page=current_page, has_next=has_next, has_prev=has_prev)

@media_routes.route("/media/<media_type>/<int:media_id>")
@login_required
def media(media_type, media_id):
    if media_type == 'book':
        media = Book.query.get_or_404(media_id)
    elif media_type == 'music':
        media = Music.query.get_or_404(media_id)
    elif media_type == 'cinema':
        media = Cinema.query.get_or_404(media_id)
    else:
        flash("Invalid media type", "danger")
        return redirect(url_for('main_routes.home'))
    
    # Get user media entry
    user_media = UserMedia.query.filter_by(
        user_id=current_user.user_id,
        media_type=media_type,
        **{f"{media_type}_id": media_id}
    ).first()
    
    # Get network activity
    planned_by = UserMedia.query.filter_by(
        media_type=media_type,
        planned=True,
        **{f"{media_type}_id": media_id}
    ).all()
    
    consumed_by = UserMedia.query.filter_by(
        media_type=media_type,
        done=True,
        **{f"{media_type}_id": media_id}
    ).all()
    
    # Add user information to the queries
    for entry in planned_by + consumed_by:
        entry.user = User.query.get(entry.user_id)
    
    return render_template("media.html", 
                         media=media,
                         media_type=media_type,
                         user_media=user_media,
                         planned_by=planned_by,
                         consumed_by=consumed_by)

@media_routes.route("/feed", methods=["GET"])
@login_required
def feed():
    followed_id = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.user_id).all()]
    followed_id.append(current_user.user_id)
    user_media_entries = UserMedia.query.filter(UserMedia.user_id.in_(followed_id))\
                             .order_by(UserMedia.date_consumed.desc())\
                             .limit(50).all()
    media_items = []
    for entry in user_media_entries:
        item = (Book.query.get(entry.book_id) if entry.book_id else
                Music.query.get(entry.music_id) if entry.music_id else
                Cinema.query.get(entry.cinema_id))
        if not item:
            continue
        user = User.query.get(entry.user_id)
        likes = Like.query.filter_by(user_media_id=entry.user_media_id).count()
        comments = Comment.query.filter_by(user_media_id=entry.user_media_id).order_by(Comment.created_at.desc()).all()
        liked_by_me = Like.query.filter_by(user_id=current_user.user_id, user_media_id=entry.user_media_id).first()
        media_items.append({
            "item": item,
            "entry": entry,
            "user": user,
            "likes": likes,
            "comments": comments,
            "liked_by_me": liked_by_me
            })
    return render_template("feed.html", media_items=media_items)

@media_routes.route("/lists", methods=["GET", "POST"])
@login_required
def lists():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        new_list = List(user_id=current_user.user_id, name=name, description=description)
        db.session.add(new_list)
        db.session.commit()
        flash("List created!", "success")
        return redirect(url_for("media_routes.lists"))
    user_lists = List.query.filter_by(user_id=current_user.user_id).all()
    return render_template("lists.html", lists=user_lists)

@media_routes.route("/notifications")
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.user_id)\
                               .order_by(Notification.created_at.desc())\
                               .limit(20).all()
    return render_template("notifications.html", notifications=notifs)

@media_routes.route("/planner", methods=['GET'])
@login_required
def planner():
    planned_items = UserMedia.query.filter_by(user_id=current_user.user_id, planned=True).all()
    return render_template("planner.html", planned_items=planned_items)

@media_routes.route("/media/add/planned", methods=["POST"])
@login_required
def add_to_planner():
    title = request.form.get("title")
    media_type = request.form.get("media_type")
    if title and media_type:
        existing_media = UserMedia.query.filter_by(user_id=current_user.id, title=title).first()
        if existing_media:
            flash('Media already exists in your planner or library.', 'warning')
        else:
            new_media = UserMedia(user_id=current_user.id, title=title, media_type=media_type, planned=True)
            db.session.add(new_media)
            db.session.commit()
            flash('Media added to planner!', 'success')
    else:
        flash('Invalid input. Please provide a title and media type.', 'danger')
    return redirect(url_for('media_routes.planner'))

@media_routes.route('/add', methods=['POST'])
@login_required
def add_media():
    # ... existing code ...
    return redirect(url_for('main_routes.home'))

@media_routes.route("/media/save_external", methods=["POST"])
@login_required
def save_external_media():
    """Save external API media to database and redirect to media detail page"""
    data = request.get_json()
    media_type = data.get('media_type')
    media_data = data.get('media_data')
    
    if not media_type or not media_data:
        return jsonify({'success': False, 'message': 'Missing required data'}), 400
    
    try:
        if media_type == 'book':
            # Check if book already exists
            existing_book = Book.query.filter_by(
                title=media_data['title'], 
                author=media_data['author']
            ).first()
            
            if existing_book:
                book = existing_book
            else:
                # Create new book
                book = Book(
                    title=media_data['title'],
                    author=media_data['author'],
                    genre=media_data.get('genre', 'Unknown'),
                    year=media_data.get('year'),
                    language=media_data.get('language', 'Unknown'),
                    publisher=media_data.get('publisher'),
                    country=media_data.get('country'),
                    description=media_data.get('reviews'),
                    coverart=media_data.get('coverart')
                )
                db.session.add(book)
                db.session.flush()  # Get the book_id
            
            # Check if user already has this book in their library
            existing_user_media = UserMedia.query.filter_by(
                user_id=current_user.user_id,
                book_id=book.book_id,
                media_type='book'
            ).first()
            
            if not existing_user_media:
                # Create user media entry (not consumed, not planned)
                user_media = UserMedia(
                    user_id=current_user.user_id,
                    book_id=book.book_id,
                    media_type='book',
                    done=False,
                    planned=False
                )
                db.session.add(user_media)
            
        elif media_type == 'music':
            # Check if music already exists
            existing_music = Music.query.filter_by(
                title=media_data['title'], 
                artist=media_data['artist']
            ).first()
            
            if existing_music:
                music = existing_music
            else:
                # Create new music
                music = Music(
                    title=media_data['title'],
                    artist=media_data['artist'],
                    genre=media_data.get('genre', 'Unknown'),
                    year=media_data.get('year'),
                    language=media_data.get('language', 'Unknown'),
                    label=media_data.get('label'),
                    country=media_data.get('country'),
                    reviews=media_data.get('reviews'),
                    coverart=media_data.get('coverart')
                )
                db.session.add(music)
                db.session.flush()  # Get the music_id
            
            # Check if user already has this music in their library
            existing_user_media = UserMedia.query.filter_by(
                user_id=current_user.user_id,
                music_id=music.music_id,
                media_type='music'
            ).first()
            
            if not existing_user_media:
                # Create user media entry (not consumed, not planned)
                user_media = UserMedia(
                    user_id=current_user.user_id,
                    music_id=music.music_id,
                    media_type='music',
                    done=False,
                    planned=False
                )
                db.session.add(user_media)
            
        elif media_type == 'cinema':
            # Check if cinema already exists
            existing_cinema = Cinema.query.filter_by(
                title=media_data['title'], 
                director=media_data['director']
            ).first()
            
            if existing_cinema:
                cinema = existing_cinema
            else:
                # Create new cinema
                cinema = Cinema(
                    title=media_data['title'],
                    director=media_data['director'],
                    genre=media_data.get('genre', 'Unknown'),
                    year=media_data.get('year'),
                    language=media_data.get('language', 'Unknown'),
                    type=media_data.get('type', 'movie'),
                    country=media_data.get('country'),
                    reviews=media_data.get('reviews'),
                    coverart=media_data.get('coverart')
                )
                db.session.add(cinema)
                db.session.flush()  # Get the cinema_id
            
            # Check if user already has this cinema in their library
            existing_user_media = UserMedia.query.filter_by(
                user_id=current_user.user_id,
                cinema_id=cinema.cinema_id,
                media_type='cinema'
            ).first()
            
            if not existing_user_media:
                # Create user media entry (not consumed, not planned)
                user_media = UserMedia(
                    user_id=current_user.user_id,
                    cinema_id=cinema.cinema_id,
                    media_type='cinema',
                    done=False,
                    planned=False
                )
                db.session.add(user_media)
        
        db.session.commit()
        
        # Return success with redirect URL
        if media_type == 'book':
            redirect_url = url_for('media_routes.media', media_type='book', media_id=book.book_id)
        elif media_type == 'music':
            redirect_url = url_for('media_routes.media', media_type='music', media_id=music.music_id)
        elif media_type == 'cinema':
            redirect_url = url_for('media_routes.media', media_type='cinema', media_id=cinema.cinema_id)
        
        return jsonify({
            'success': True, 
            'message': f'{media_type.title()} added to library!',
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@media_routes.route("/media/add_to_library", methods=["POST"])
@login_required
def add_to_library():
    media_type = request.form.get("media_type")
    media_id = request.form.get("media_id")
    rating = request.form.get("rating")
    date_consumed = request.form.get("date_consumed")

    if not media_type or not media_id:
        flash("Invalid request.", "danger")
        return redirect(url_for("main_routes.home"))

    # Check if it's already in the library
    user_media = UserMedia.query.filter_by(
        user_id=current_user.user_id,
        media_type=media_type,
        **{f"{media_type}_id": media_id}
    ).first()

    if user_media:
        flash("This item is already in your library.", "warning")
    else:
        new_user_media = UserMedia(
            user_id=current_user.user_id,
            media_type=media_type,
            rating=rating if rating else None,
            date_consumed=datetime.strptime(date_consumed, '%Y-%m-%d').date() if date_consumed else None,
            **{f"{media_type}_id": media_id}
        )
        db.session.add(new_user_media)
        db.session.commit()
        flash("Successfully added to your library!", "success")

    return redirect(url_for("media_routes.media", media_type=media_type, media_id=media_id))

@media_routes.route("/api/media/<int:media_id>/plan", methods=["POST"])
@login_required
def add_to_planner_api():
    """Add media to planner via API"""
    data = request.get_json()
    media_id = request.view_args.get('media_id')
    media_type = data.get('media_type')
    
    if not media_type:
        return jsonify({'success': False, 'message': 'Media type is required'}), 400
    
    try:
        # Find the user media entry
        user_media = UserMedia.query.filter_by(
            user_id=current_user.user_id,
            media_type=media_type,
            **{f"{media_type}_id": media_id}
        ).first()
        
        if not user_media:
            # Create new user media entry
            user_media = UserMedia(
                user_id=current_user.user_id,
                media_type=media_type,
                planned=True,
                done=False,
                **{f"{media_type}_id": media_id}
            )
            db.session.add(user_media)
        else:
            # Update existing entry
            user_media.planned = True
            user_media.done = False
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Added to planner!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@media_routes.route("/api/media/<int:media_id>/remove", methods=["POST"])
@login_required
def remove_from_planner_api():
    """Remove media from planner via API"""
    data = request.get_json()
    media_id = request.view_args.get('media_id')
    media_type = data.get('media_type')
    
    if not media_type:
        return jsonify({'success': False, 'message': 'Media type is required'}), 400
    
    try:
        # Find the user media entry
        user_media = UserMedia.query.filter_by(
            user_id=current_user.user_id,
            media_type=media_type,
            **{f"{media_type}_id": media_id}
        ).first()
        
        if user_media:
            user_media.planned = False
            db.session.commit()
            return jsonify({'success': True, 'message': 'Removed from planner!'})
        else:
            return jsonify({'success': False, 'message': 'Media not found in planner'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@media_routes.route("/api/media/<int:media_id>/consume", methods=["POST"])
@login_required
def mark_as_consumed_api():
    """Mark media as consumed via API"""
    data = request.get_json()
    media_id = request.view_args.get('media_id')
    media_type = data.get('media_type')
    
    if not media_type:
        return jsonify({'success': False, 'message': 'Media type is required'}), 400
    
    try:
        # Find the user media entry
        user_media = UserMedia.query.filter_by(
            user_id=current_user.user_id,
            media_type=media_type,
            **{f"{media_type}_id": media_id}
        ).first()
        
        if not user_media:
            # Create new user media entry
            user_media = UserMedia(
                user_id=current_user.user_id,
                media_type=media_type,
                done=True,
                planned=False,
                date_consumed=datetime.now(),
                **{f"{media_type}_id": media_id}
            )
            db.session.add(user_media)
        else:
            # Update existing entry
            user_media.done = True
            user_media.planned = False
            user_media.date_consumed = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Marked as consumed!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500