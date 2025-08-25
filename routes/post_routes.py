from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.social_model import Post, Like, Comment
from models.user_model import db, User
from models.books import Book
from models.music import Music
from models.cinema import Cinema
from datetime import datetime

post_routes = Blueprint('post_routes', __name__)

@post_routes.route('/posts', methods=['GET'])
@login_required
def posts():
    """Main posts feed page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get posts from followed users and current user
    followed_ids = [f.followed_id for f in current_user.following]
    followed_ids.append(current_user.user_id)
    
    posts = Post.query.filter(Post.user_id.in_(followed_ids))\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
    
    # Add media info and check if current user liked each post
    for post in posts.items:
        if post.media_type and post.media_id:
            if post.media_type == 'book':
                post.media = Book.query.get(post.media_id)
            elif post.media_type == 'music':
                post.media = Music.query.get(post.media_id)
            elif post.media_type == 'cinema':
                post.media = Cinema.query.get(post.media_id)
        
        # Check if current user liked this post
        post.is_liked_by_current_user = Like.query.filter_by(
            user_id=current_user.user_id, 
            post_id=post.post_id
        ).first() is not None
    
    return render_template('posts.html', posts=posts)

@post_routes.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        media_type = request.form.get('media_type')
        media_id = request.form.get('media_id')
        
        if not content:
            flash('Post content is required', 'error')
            return redirect(url_for('post_routes.create_post'))
        
        # Create the post
        post = Post(
            user_id=current_user.user_id,
            content=content,
            media_type=media_type if media_type else None,
            media_id=int(media_id) if media_id else None
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('post_routes.posts'))
    
    # Pre-fill media info if coming from media page
    media_type = request.args.get('media_type')
    media_id = request.args.get('media_id')
    media = None
    
    if media_type and media_id:
        if media_type == 'book':
            media = Book.query.get(media_id)
        elif media_type == 'music':
            media = Music.query.get(media_id)
        elif media_type == 'cinema':
            media = Cinema.query.get(media_id)
    
    return render_template('create_post.html', media=media, media_type=media_type, media_id=media_id)

@post_routes.route('/post/<int:post_id>', methods=['GET'])
@login_required
def view_post(post_id):
    """View a specific post"""
    post = Post.query.get_or_404(post_id)
    
    # Get media info if post has media
    media = None
    if post.media_type and post.media_id:
        if post.media_type == 'book':
            media = Book.query.get(post.media_id)
        elif post.media_type == 'music':
            media = Music.query.get(post.media_id)
        elif post.media_type == 'cinema':
            media = Cinema.query.get(post.media_id)
    
    # Check if current user liked this post
    post.is_liked_by_current_user = Like.query.filter_by(
        user_id=current_user.user_id, 
        post_id=post.post_id
    ).first() is not None
    
    return render_template('view_post.html', post=post, media=media)

@post_routes.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.user_id != current_user.user_id:
        flash('You can only edit your own posts', 'error')
        return redirect(url_for('post_routes.view_post', post_id=post_id))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('Post content is required', 'error')
            return redirect(url_for('post_routes.edit_post', post_id=post_id))
        
        post.content = content
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post_routes.view_post', post_id=post_id))
    
    return render_template('edit_post.html', post=post)

@post_routes.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.user_id != current_user.user_id:
        flash('You can only delete your own posts', 'error')
        return redirect(url_for('post_routes.view_post', post_id=post_id))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('post_routes.posts'))

# API endpoints for AJAX interactions

@post_routes.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/unlike a post"""
    post = Post.query.get_or_404(post_id)
    
    existing_like = Like.query.filter_by(
        user_id=current_user.user_id, 
        post_id=post_id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        # Like
        like = Like(user_id=current_user.user_id, post_id=post_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    like_count = post.likes.count()
    
    return jsonify({
        'success': True,
        'action': action,
        'like_count': like_count
    })

@post_routes.route('/api/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    """Add a comment to a post"""
    post = Post.query.get_or_404(post_id)
    content = request.json.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'error': 'Comment content is required'}), 400
    
    comment = Comment(
        user_id=current_user.user_id,
        post_id=post_id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.comment_id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'user': {
                'username': current_user.username,
                'profile_picture': current_user.profile_picture
            }
        }
    })

@post_routes.route('/api/post/<int:post_id>/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(post_id, comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user owns the comment
    if comment.user_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'You can only delete your own comments'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'success': True})

@post_routes.route('/api/post/<int:post_id>/share', methods=['POST'])
@login_required
def share_post(post_id):
    """Share a post to direct message"""
    post = Post.query.get_or_404(post_id)
    recipient_id = request.json.get('recipient_id')
    
    if not recipient_id:
        return jsonify({'success': False, 'error': 'Recipient is required'}), 400
    
    # Create a message with the post content
    from models.social_model import Message
    
    share_content = f"Check out this post from {post.user.username}:\n\n{post.content}"
    if post.media_type and post.media_id:
        share_content += f"\n\nMedia: {post.media_type.title()} (ID: {post.media_id})"
    
    message = Message(
        sender_id=current_user.user_id,
        recipient_id=recipient_id,
        content=share_content
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post shared successfully!'})

@post_routes.route('/api/post/<int:post_id>/repost', methods=['POST'])
@login_required
def repost(post_id):
    """Repost a post"""
    original_post = Post.query.get_or_404(post_id)
    
    # Create a new post that references the original
    repost_content = f"Reposted from @{original_post.user.username}:\n\n{original_post.content}"
    
    new_post = Post(
        user_id=current_user.user_id,
        content=repost_content,
        media_type=original_post.media_type,
        media_id=original_post.media_id
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post reposted successfully!'})