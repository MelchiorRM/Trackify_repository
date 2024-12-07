#DATABASE MODEL
USE trackifydb;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cinema (
    cinema_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    genre VARCHAR(100),
    year INT,
    country VARCHAR(100),
    director VARCHAR(255),
    type VARCHAR(100),
    language VARCHAR(100),
    rating DECIMAL(3,1),
    reviews TEXT,
    description TEXT,
    coverart VARCHAR(255)
);

CREATE TABLE music (
    music_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    artist VARCHAR(255),
    genre VARCHAR(100),
    year INT,
    language VARCHAR(100),
    label VARCHAR(100),
    country VARCHAR(100),
    rating DECIMAL(3,1),
    reviews TEXT,
    coverart VARCHAR(255)
);

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(100),
    year INT,
    language VARCHAR(100),
    publisher VARCHAR(100),
    country VARCHAR(100),
    rating DECIMAL(3,1),
    reviews TEXT,
    coverart VARCHAR(255)
);

CREATE TABLE user_media (
    user_media_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cinema_id INT,
    music_id INT,
    book_id INT,
    media_type ENUM('cinema', 'music', 'book') NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    planned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (cinema_id) REFERENCES cinema(cinema_id) ON DELETE CASCADE,
    FOREIGN KEY (music_id) REFERENCES music(music_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE user_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cinema_id INT,
    music_id INT,
    book_id INT,
    media_type ENUM('cinema', 'music', 'book') NOT NULL,
    review TEXT,
    rating DECIMAL(3,1),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (cinema_id) REFERENCES cinema(cinema_id) ON DELETE CASCADE,
    FOREIGN KEY (music_id) REFERENCES music(music_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE user_media_consumption (
    consumption_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cinema_id INT,
    music_id INT,
    book_id INT,
    media_type ENUM('cinema', 'music', 'book'),
    done BOOLEAN DEFAULT FALSE,
    planned BOOLEAN DEFAULT FALSE,
    consumption_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (cinema_id) REFERENCES cinema(cinema_id) ON DELETE CASCADE,
    FOREIGN KEY (music_id) REFERENCES music(music_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

CREATE TABLE user_statistics (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_movies INT,
    total_books INT,
    total_music INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
