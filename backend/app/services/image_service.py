# =====================================================================
# FILE: backend/app/services/image_service.py
# DESCRIPTION: Service layer for validating, identifying MIME type, and
#              reading crop leaf images safely.
# =====================================================================

# We import 'os' to interact with the filesystem (like checking file sizes).
import os

# We import 'logging' to capture info, warnings, and errors in a structured way.
import logging

# We import 'Path' from 'pathlib' to handle cross-platform file paths cleanly.
from pathlib import Path

# We import 'Optional' for optional parameter typing.
from typing import Optional

# We import 'Image' from the Pillow library (PIL) to perform image integrity checks.
from PIL import Image

# Setup a module-level logger. Its name will match the module path: app.services.image_service.
logger = logging.getLogger(__name__)

# Define the set of allowed image extensions. We keep them in lowercase for case-insensitive matching.
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Map lowercase extensions to their formal MIME (Multipurpose Internet Mail Extensions) type string.
MIME_TYPE_MAPPING = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp"
}

# The maximum file size limit in bytes. 10MB is exactly 10 * 1024 KB * 1024 Bytes = 10,485,760 bytes.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
BACKEND_DIR = Path(__file__).resolve().parents[2]

class ImageServiceError(Exception):
    """
    Custom exception class designed specifically for the Image Service.
    Inheriting from Python's base 'Exception' allows us to raise and catch
    specific errors related to image validation, format, and reading.
    """
    pass

def resolve_image_path(image_path: str) -> Path:
    """Resolve upload paths consistently regardless of the server working directory."""
    file_path = Path(image_path)
    if file_path.is_absolute() or file_path.exists():
        return file_path
    backend_relative = BACKEND_DIR / file_path
    if backend_relative.exists():
        return backend_relative
    return file_path

def validate_image(image_path: str) -> Path:
    """
    Validates that a file at the given path exists, is a file, has a valid
    extension, is under 10MB, and is a valid (non-corrupted) image.

    Parameters:
        image_path (str): The file path of the image.

    Returns:
        Path: A pathlib.Path object representing the validated file.

    Raises:
        ImageServiceError: If any of the validation steps fail.
    """
    # 1. Logging the start of validation to trace execution.
    logger.info(f"Validating image file path: {image_path}")

    # 2. Check if the path argument is a non-empty string.
    if not image_path or not isinstance(image_path, str):
        logger.error("The provided image path is empty or not of type string.")
        raise ImageServiceError("Image path must be a non-empty string.")

    # 3. Instantiate a Path object which provides cross-platform path handling.
    file_path = resolve_image_path(image_path)

    # 4. Check if the path exists on the disk.
    if not file_path.exists():
        logger.error(f"Image path does not exist on disk: {file_path}")
        raise ImageServiceError(f"Image file not found at path: '{file_path}'")

    # 5. Verify that the path points to an actual file, not a directory folder.
    if not file_path.is_file():
        logger.error(f"Image path is not a file: {file_path}")
        raise ImageServiceError(f"The path does not point to a valid file: '{file_path}'")

    # 6. Extract the file suffix/extension and convert it to lowercase for safety.
    extension = file_path.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        logger.error(f"Extension '{extension}' is not allowed for path: {file_path}")
        raise ImageServiceError(
            f"Invalid image extension '{extension}'. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 7. Check the file size in bytes using os.path.getsize.
    try:
        file_size = os.path.getsize(file_path)
        if file_size >= MAX_FILE_SIZE_BYTES:
            logger.error(f"File size of {file_size} bytes exceeds the 10MB limit ({MAX_FILE_SIZE_BYTES} bytes).")
            raise ImageServiceError(
                f"File size exceeds the 10MB limit. Current size is {file_size / (1024 * 1024):.2f} MB."
            )
    except OSError as e:
        logger.error(f"Failed to read file size for {file_path}: {e}")
        raise ImageServiceError(f"Could not read the file size on disk. Details: {e}")

    # 8. Verify the structural integrity of the image using the Pillow library (PIL).
    try:
        # Open the image file. This only reads the metadata/headers, which is fast and memory efficient.
        with Image.open(file_path) as img:
            # The verify() method reads the image files to check if it's truncated or corrupt.
            img.verify()
        logger.info(f"Image integrity check passed for: {file_path}")
    except Exception as e:
        logger.error(f"Pillow verification failed for image {file_path}: {e}", exc_info=True)
        raise ImageServiceError(f"The image is corrupted or not a valid image file. Details: {e}")

    # 9. Return the validated Path object.
    return file_path

def get_mime_type(image_path: Path) -> str:
    """
    Determines the standardized MIME type of the image based on its suffix.

    Parameters:
        image_path (Path): A pathlib.Path object representing the image.

    Returns:
        str: The MIME type string (e.g. 'image/jpeg').

    Raises:
        ImageServiceError: If the extension is not mapped to any MIME type.
    """
    # 1. Log the mapping process.
    logger.info(f"Extracting MIME type for path: {image_path}")

    # 2. Extract the suffix (extension) in lowercase.
    extension = image_path.suffix.lower()

    # 3. Look up the extension in the MIME_TYPE_MAPPING dictionary.
    mime_type = MIME_TYPE_MAPPING.get(extension)

    # 4. If the mime type is not found in the lookup dictionary, raise an exception.
    if not mime_type:
        logger.error(f"MIME type mapping missing for extension '{extension}' at path: {image_path}")
        raise ImageServiceError(f"Unsupported extension '{extension}' for MIME type mapping.")

    # 5. Return the mapped MIME type string.
    return mime_type

def read_image(image_path: str) -> dict:
    """
    Validates the image file, reads its binary contents, and returns a dictionary
    containing the raw bytes and the corresponding MIME type.

    Parameters:
        image_path (str): The file path of the image.

    Returns:
        dict: A dictionary containing:
            - 'bytes' (bytes): The raw binary content of the file.
            - 'mime_type' (str): The standardized MIME type string.

    Raises:
        ImageServiceError: If validation, MIME extraction, or file reading fails.
    """
    logger.info(f"Reading image from path: {image_path}")

    # 1. Validate the path and get the Path object.
    # If this fails, it raises an ImageServiceError and stops execution.
    file_path = validate_image(image_path)

    # 2. Retrieve the MIME type for this file.
    # If the extension is unsupported, it raises an ImageServiceError.
    mime_type = get_mime_type(file_path)

    # 3. Read the image file binary contents safely.
    try:
        # Open the file in read-binary ('rb') mode.
        with open(file_path, "rb") as file_handle:
            # Read the entire file content into memory as bytes.
            image_bytes = file_handle.read()
        logger.info(f"Successfully read {len(image_bytes)} bytes with MIME type '{mime_type}'.")
    except Exception as e:
        logger.error(f"Failed to read image bytes from path '{file_path}': {e}", exc_info=True)
        raise ImageServiceError(f"Failed to read binary data from image file. Details: {e}")

    # 4. Construct and return the dictionary matching the required specification format.
    return {
        "bytes": image_bytes,
        "mime_type": mime_type
    }


def is_image_file(image_path: Optional[str]) -> bool:
    """
    Safely determines if the provided file path is a valid image file.
    Does not raise exceptions if validation fails; returns False.

    Parameters:
        image_path (str or None): Path to the file.

    Returns:
        bool: True if the file exists, has a valid image extension, and
              matches image magic bytes; False otherwise.
    """
    if not image_path or not isinstance(image_path, str):
        return False

    try:
        file_path = resolve_image_path(image_path)
        if not file_path.is_file():
            return False

        ext = file_path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False

        # Verify magic bytes
        with open(file_path, "rb") as f:
            header = f.read(12)

        if len(header) < 3:
            return False

        # JPEG: FF D8 FF
        if header.startswith(b"\xff\xd8\xff"):
            return True

        # PNG: 89 50 4E 47 0D 0A 1A 0A
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return True

        # WEBP: RIFFxxxxWEBP
        if header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
            return True

    except Exception as e:
        logger.warning(f"Error checking image file signature for '{image_path}': {e}")
        
    return False


