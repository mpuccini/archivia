"""
Thumbnail generation utilities for image files, including DNG support
"""
import io
import logging
from typing import Optional, BinaryIO
from PIL import Image
import rawpy

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """Generate thumbnails for various image formats including DNG"""

    def __init__(self, max_size: tuple = (800, 800), quality: int = 85):
        """
        Initialize thumbnail generator

        Args:
            max_size: Maximum dimensions (width, height) for thumbnail
            quality: JPEG quality for output (1-100)
        """
        self.max_size = max_size
        self.quality = quality

    def generate_thumbnail(
        self,
        file_data: BinaryIO,
        content_type: str,
        original_filename: str = ""
    ) -> Optional[tuple[bytes, str]]:
        """
        Generate thumbnail from image file

        Args:
            file_data: File-like object containing image data
            content_type: MIME type of the image
            original_filename: Original filename for extension detection

        Returns:
            Tuple of (thumbnail_bytes, mime_type) or None if generation failed
        """
        try:
            # Handle DNG files specially
            if self._is_dng_file(content_type, original_filename):
                return self._generate_dng_thumbnail(file_data)

            # Handle standard image formats
            elif content_type.startswith('image/'):
                return self._generate_standard_thumbnail(file_data)

            else:
                logger.warning(f"Unsupported content type for thumbnail: {content_type}")
                return None

        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}", exc_info=True)
            return None

    def _is_dng_file(self, content_type: str, filename: str) -> bool:
        """Check if file is a DNG file"""
        dng_mime_types = ['image/x-adobe-dng', 'image/dng', 'image/x-dng']
        if content_type in dng_mime_types:
            return True
        if filename and filename.lower().endswith('.dng'):
            return True
        return False

    def _generate_dng_thumbnail(self, file_data: BinaryIO) -> Optional[tuple[bytes, str]]:
        """
        Generate thumbnail from DNG file

        DNG files contain embedded JPEG preview which we can extract
        """
        try:
            # Read file data into memory (MinIO streams may not support seek)
            file_bytes = file_data.read()
            # Don't try to seek on original stream - it may not support it

            # Try to extract embedded thumbnail first (fast method)
            try:
                with rawpy.imread(io.BytesIO(file_bytes)) as raw:
                    # Try to extract the embedded JPEG preview
                    try:
                        # Get the largest embedded thumbnail
                        thumb = raw.extract_thumb()
                        if thumb.format == rawpy.ThumbFormat.JPEG:
                            # Resize if needed
                            thumb_image = Image.open(io.BytesIO(thumb.data))
                            thumb_image.thumbnail(self.max_size, Image.Resampling.LANCZOS)

                            # Convert to RGB if necessary
                            if thumb_image.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', thumb_image.size, (255, 255, 255))
                                if thumb_image.mode == 'P':
                                    thumb_image = thumb_image.convert('RGBA')
                                background.paste(thumb_image, mask=thumb_image.split()[-1] if 'A' in thumb_image.mode else None)
                                thumb_image = background
                            elif thumb_image.mode != 'RGB':
                                thumb_image = thumb_image.convert('RGB')

                            # Save to bytes
                            output = io.BytesIO()
                            thumb_image.save(output, format='JPEG', quality=self.quality, optimize=True)
                            output.seek(0)

                            logger.info("Generated thumbnail from DNG embedded preview")
                            return output.read(), 'image/jpeg'
                    except (rawpy.LibRawNoThumbnailError, rawpy.LibRawUnsupportedThumbnailError):
                        logger.info("No embedded thumbnail, processing RAW data")

                    # If no embedded thumbnail, process the RAW data (slower)
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        half_size=True,  # Use half-size for faster processing
                        no_auto_bright=True,
                        output_bps=8
                    )

                    # Convert to PIL Image
                    image = Image.fromarray(rgb)
                    image.thumbnail(self.max_size, Image.Resampling.LANCZOS)

                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # Save to bytes
                    output = io.BytesIO()
                    image.save(output, format='JPEG', quality=self.quality, optimize=True)
                    output.seek(0)

                    logger.info("Generated thumbnail from DNG RAW data")
                    return output.read(), 'image/jpeg'

            except Exception as e:
                logger.error(f"Error processing DNG with rawpy: {e}", exc_info=True)

                # Fallback: try with PIL (may work for some DNG files)
                try:
                    image = Image.open(io.BytesIO(file_bytes))
                    return self._process_pil_image(image)
                except Exception as pil_error:
                    logger.error(f"PIL fallback also failed: {pil_error}")
                    return None

        except Exception as e:
            logger.error(f"Error generating DNG thumbnail: {e}", exc_info=True)
            return None

    def _generate_standard_thumbnail(self, file_data: BinaryIO) -> Optional[tuple[bytes, str]]:
        """Generate thumbnail from standard image formats (JPEG, PNG, TIFF)"""
        try:
            # Open image with PIL
            image = Image.open(file_data)
            return self._process_pil_image(image)

        except Exception as e:
            logger.error(f"Error generating standard thumbnail: {e}", exc_info=True)
            return None

    def _process_pil_image(self, image: Image.Image) -> Optional[tuple[bytes, str]]:
        """Process PIL image to create thumbnail"""
        try:
            # Create thumbnail
            image.thumbnail(self.max_size, Image.Resampling.LANCZOS)

            # Convert to RGB if necessary (handle RGBA, LA, P modes)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.quality, optimize=True)
            output.seek(0)

            return output.read(), 'image/jpeg'

        except Exception as e:
            logger.error(f"Error processing PIL image: {e}", exc_info=True)
            return None


# Singleton instance
_thumbnail_generator = None


def get_thumbnail_generator() -> ThumbnailGenerator:
    """Get thumbnail generator singleton instance"""
    global _thumbnail_generator
    if _thumbnail_generator is None:
        _thumbnail_generator = ThumbnailGenerator(
            max_size=(1200, 1200),  # Good quality for preview
            quality=85
        )
    return _thumbnail_generator
