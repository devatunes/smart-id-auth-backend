from fastapi import UploadFile


class InvalidImageError(ValueError):
    pass


def ensure_image_file(file: UploadFile) -> None:
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise InvalidImageError("Invalid file type. Only image files are allowed.")