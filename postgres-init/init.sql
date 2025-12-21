CREATE TABLE users (
        id SERIAL NOT NULL,
        keycloak_id VARCHAR(64) NOT NULL,
        email VARCHAR(255),
        username VARCHAR(255),
        display_name VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (keycloak_id),
        UNIQUE (email)
);



CREATE TABLE artists (
        id INTEGER NOT NULL,
        avatar_path VARCHAR(255),
        PRIMARY KEY (id),
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
);



CREATE TABLE artist_requests (
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL,
        PRIMARY KEY (user_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);


CREATE TABLE albums (
        id SERIAL NOT NULL,
        title VARCHAR(255) NOT NULL,
        cover_path VARCHAR(255),
        release_year INTEGER,
        artist_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (artist_id) REFERENCES artists (id) ON DELETE CASCADE
);


CREATE TABLE songs (
        id SERIAL NOT NULL,
        title VARCHAR(255) NOT NULL,
        genre VARCHAR(100),
        audio_path VARCHAR(255) NOT NULL,
        album_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (album_id) REFERENCES albums (id) ON DELETE CASCADE
);


CREATE TABLE plays (
        id SERIAL NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        song_id INTEGER NOT NULL,
        user_id INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);


CREATE INDEX IF NOT EXISTS idx_albums_artist
ON albums (artist_id);


CREATE INDEX IF NOT EXISTS idx_songs_album
ON songs (album_id);
