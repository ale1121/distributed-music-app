from app import create_app
from app.models import db, Role

def init():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        for r in ["ROLE_USER", "ROLE_ARTIST", "ROLE_ADMIN"]:
            db.session.add(Role(name=r))
        db.session.commit()

        print("db initialised")
        
if __name__ == "__main__":
    init()