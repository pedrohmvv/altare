from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///data/altare.db"
    session_cookie_secure: bool = True
