def paginate(query, page, per_page=10):
    """Paginate a SQLAlchemy query."""
    total_items = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_items + per_page - 1) // per_page
    return {
        "items": items,
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
    }