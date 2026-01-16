from sqlalchemy import select
from app.database.db import Session
from app.database.models import User, Artist
from app.opensearch import opensearch


def sync_user_db(decoded_token):
    """
    Update or create user in db with token details
    """

    sub = decoded_token.get('sub')
    email = decoded_token.get('email')
    username = decoded_token.get('preferred_username')
    display_name = decoded_token.get('display_name')

    # index/reindex artist, if the user is an artist and details changed
    index_artist = False
    
    user = Session.scalar(select(User).where(User.keycloak_id == sub))
    if not user:
        user = User(
            keycloak_id=sub,
            email=email,
            username=username,
            display_name=display_name,
        )
        Session.add(user)
    else:
        if user.email != email:
            user.email = email
        if user.display_name != display_name:
            user.display_name = display_name
            index_artist = True  # display name changed, must reindex if artist

    Session.commit()
    Session.refresh(user)

    if 'ROLE_ARTIST' in decoded_token.get('realm_access', {}).get('roles', []):
        artist = Session.get(Artist, user.id)
        if not artist:
            index_artist = True  # new artist, must index
            artist = Artist(id=user.id)
            Session.add(artist)
    else:
        index_artist = False  # user is not an artist

    Session.commit()
    Session.refresh(user)

    if index_artist:
        opensearch.index_artist(user)
    
    return user
