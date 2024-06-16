from sqlmodel import Session

from schemas.users import User
from utils.config import settings
from utils.sessions import engine


def add_to_db(session: Session, item) -> None:
    session.add(item)
    session.commit()
    session.refresh(item)


def create_entries(session: Session) -> None:
    user = User(username=settings.AUTH_USER)
    user.set_password(settings.AUTH_PASSWORD)
    add_to_db(session, user)


def add_sample_data():
    with Session(engine) as session:
        create_entries(session)
