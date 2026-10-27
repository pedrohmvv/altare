from fastapi import FastAPI

from wedding.platform.http.app import create_app


def build_app() -> FastAPI:
    return create_app()
