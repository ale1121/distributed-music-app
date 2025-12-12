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
        artist_id INTEGER NOT NULL,
        PRIMARY KEY (artist_id),
        FOREIGN KEY(artist_id) REFERENCES users (id) ON DELETE CASCADE
);



CREATE TABLE artist_requests (
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL,
        PRIMARY KEY (user_id),
        FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);