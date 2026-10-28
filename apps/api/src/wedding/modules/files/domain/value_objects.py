from enum import StrEnum


class FileKind(StrEnum):
    PDF = "application/pdf"
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"
