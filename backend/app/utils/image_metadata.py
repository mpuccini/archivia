"""
Comprehensive Image Metadata Extraction Utility
Extracts ALL technical metadata from images (EXIF, DNG, TIFF tags, etc.) for METS ECO-MiC compliance
"""

from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageMetadataExtractor:
    """Extract comprehensive technical metadata from image files"""

    def __init__(self):
        self.exif_tags = TAGS

    def extract_metadata(self, file_path: str) -> Dict:
        """
        Extract comprehensive metadata from an image file

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary containing:
            - Standard fields for METS MIX compliance
            - raw_metadata: Complete dictionary of ALL extracted tags
        """
        metadata = {
            # Standard MIX fields
            'image_width': None,
            'image_height': None,
            'bits_per_sample': None,
            'samples_per_pixel': None,
            'compression_scheme': None,
            'color_space': None,
            'x_sampling_frequency': None,
            'y_sampling_frequency': None,
            'sampling_frequency_unit': None,
            'date_time_created': None,
            'format_name': None,
            'byte_order': None,
            'orientation': None,
            'icc_profile_name': None,
            'scanner_model_name': None,
            'scanning_software_name': None,
            'scanning_software_version': None,
            # Comprehensive raw metadata (ALL tags)
            'raw_metadata': {}
        }

        try:
            # Check if file is DNG (RAW)
            is_dng = file_path.lower().endswith('.dng')

            # Extract ALL metadata using exifread
            metadata_exifread = self._extract_with_exifread(file_path)
            metadata['raw_metadata'] = metadata_exifread

            # Extract using PIL for standard fields
            pil_metadata = self._extract_with_pil(file_path)

            # Merge standard fields
            for key in ['image_width', 'image_height', 'bits_per_sample', 'samples_per_pixel',
                       'compression_scheme', 'color_space', 'x_sampling_frequency',
                       'y_sampling_frequency', 'sampling_frequency_unit', 'date_time_created',
                       'format_name', 'byte_order', 'orientation', 'icc_profile_name']:
                if pil_metadata.get(key):
                    metadata[key] = pil_metadata[key]

            # Extract additional metadata from raw_metadata for standard fields
            metadata.update(self._map_raw_to_standard_fields(metadata['raw_metadata']))

            # For DNG files, try rawpy for additional data
            if is_dng:
                try:
                    import rawpy
                    with rawpy.imread(file_path) as raw:
                        # Override dimensions from RAW data
                        metadata['image_width'] = raw.sizes.width
                        metadata['image_height'] = raw.sizes.height
                        if not metadata['samples_per_pixel']:
                            metadata['samples_per_pixel'] = raw.num_colors
                except Exception as e:
                    logger.debug(f"Could not extract rawpy metadata: {e}")

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}", exc_info=True)

        return metadata

    def _extract_with_exifread(self, file_path: str) -> Dict[str, Any]:
        """Extract ALL EXIF/DNG tags using exifread library"""
        raw_metadata = {}

        try:
            import exifread

            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=True)

                for tag_name, tag_value in tags.items():
                    # Convert tag value to serializable format
                    try:
                        # Get the printable value
                        value_str = str(tag_value)

                        # Try to parse numeric values
                        if hasattr(tag_value, 'values'):
                            values = tag_value.values
                            # Handle ratio values
                            if len(values) == 1 and hasattr(values[0], 'num') and hasattr(values[0], 'den'):
                                if values[0].den != 0:
                                    raw_metadata[tag_name] = float(values[0].num) / float(values[0].den)
                                else:
                                    raw_metadata[tag_name] = values[0].num
                            # Handle multiple ratio values
                            elif all(hasattr(v, 'num') and hasattr(v, 'den') for v in values):
                                raw_metadata[tag_name] = [
                                    float(v.num) / float(v.den) if v.den != 0 else v.num
                                    for v in values
                                ]
                            # Handle integer arrays
                            elif all(isinstance(v, int) for v in values):
                                raw_metadata[tag_name] = values if len(values) > 1 else values[0]
                            else:
                                raw_metadata[tag_name] = value_str
                        else:
                            raw_metadata[tag_name] = value_str

                    except Exception as e:
                        logger.debug(f"Could not parse tag {tag_name}: {e}")
                        raw_metadata[tag_name] = value_str

        except ImportError:
            logger.warning("exifread not available, using PIL only")
        except Exception as e:
            logger.error(f"Error with exifread extraction: {e}", exc_info=True)

        return raw_metadata

    def _extract_with_pil(self, file_path: str) -> Dict:
        """Extract metadata using PIL/Pillow"""
        metadata = {}

        try:
            with Image.open(file_path) as img:
                # Basic image information
                metadata['image_width'] = img.width
                metadata['image_height'] = img.height

                # Format information
                if img.format:
                    format_map = {
                        'JPEG': 'image/jpeg',
                        'PNG': 'image/png',
                        'TIFF': 'image/tiff',
                        'DNG': 'image/dng',
                        'BMP': 'image/bmp'
                    }
                    metadata['format_name'] = format_map.get(img.format, f'image/{img.format.lower()}')

                # Image mode to samples per pixel and color space
                mode_to_info = {
                    '1': (1, 'Bi-level'),
                    'L': (1, 'Grayscale'),
                    'P': (1, 'Palette'),
                    'RGB': (3, 'RGB'),
                    'RGBA': (4, 'RGBA'),
                    'CMYK': (4, 'CMYK'),
                    'YCbCr': (3, 'YCbCr'),
                    'LAB': (3, 'LAB'),
                    'HSV': (3, 'HSV')
                }
                if img.mode in mode_to_info:
                    metadata['samples_per_pixel'], metadata['color_space'] = mode_to_info[img.mode]

                # Compression scheme
                if img.format:
                    compression_map = {
                        'JPEG': 'JPEG',
                        'PNG': 'Deflate',
                        'TIFF': 'uncompressed',
                        'BMP': 'uncompressed',
                        'GIF': 'LZW'
                    }
                    metadata['compression_scheme'] = compression_map.get(img.format)

                # Extract EXIF data
                exif_data = img.getexif()
                if exif_data:
                    metadata.update(self._parse_pil_exif(exif_data))

                # ICC Profile
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    try:
                        from PIL import ImageCms
                        icc_profile = ImageCms.ImageCmsProfile(io.BytesIO(img.info['icc_profile']))
                        metadata['icc_profile_name'] = icc_profile.profile.profile_description
                    except:
                        pass

        except Exception as e:
            logger.error(f"Error with PIL extraction: {e}", exc_info=True)

        return metadata

    def _parse_pil_exif(self, exif_data) -> Dict:
        """Parse PIL EXIF data"""
        metadata = {}

        try:
            # Common EXIF tags
            EXIF_TAGS = {
                0x0100: 'image_width',
                0x0101: 'image_height',
                0x0102: 'bits_per_sample',
                0x0103: 'compression',
                0x010F: 'scanner_manufacturer',
                0x0110: 'scanner_model',
                0x0112: 'orientation',
                0x011A: 'x_resolution',
                0x011B: 'y_resolution',
                0x0128: 'resolution_unit',
                0x0131: 'software',
                0x0132: 'date_time',
                0x9003: 'date_time_original',
            }

            for tag_id, field_name in EXIF_TAGS.items():
                if tag_id in exif_data:
                    value = exif_data[tag_id]

                    if field_name == 'x_resolution':
                        if isinstance(value, tuple) and len(value) == 2:
                            metadata['x_sampling_frequency'] = int(value[0] / value[1]) if value[1] != 0 else None
                        else:
                            metadata['x_sampling_frequency'] = int(value) if value else None

                    elif field_name == 'y_resolution':
                        if isinstance(value, tuple) and len(value) == 2:
                            metadata['y_sampling_frequency'] = int(value[0] / value[1]) if value[1] != 0 else None
                        else:
                            metadata['y_sampling_frequency'] = int(value) if value else None

                    elif field_name == 'resolution_unit':
                        unit_map = {1: 'none', 2: 'in.', 3: 'cm'}
                        metadata['sampling_frequency_unit'] = unit_map.get(value, 'in.')

                    elif field_name == 'bits_per_sample':
                        if isinstance(value, (tuple, list)):
                            metadata['bits_per_sample'] = ','.join(str(b) for b in value)
                        else:
                            metadata['bits_per_sample'] = str(value)

                    elif field_name == 'orientation':
                        orientation_map = {
                            1: 'normal*',
                            2: 'flip horizontal',
                            3: 'rotate 180',
                            4: 'flip vertical',
                            5: 'transpose',
                            6: 'rotate 90',
                            7: 'transverse',
                            8: 'rotate 270'
                        }
                        metadata['orientation'] = orientation_map.get(value, f'unknown ({value})')

                    elif field_name == 'scanner_model':
                        metadata['scanner_model_name'] = str(value)

                    elif field_name == 'software':
                        metadata['scanning_software_name'] = str(value)

                    elif 'date_time' in field_name:
                        try:
                            if isinstance(value, str):
                                dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                metadata['date_time_created'] = dt
                        except:
                            pass

        except Exception as e:
            logger.error(f"Error parsing PIL EXIF: {e}", exc_info=True)

        return metadata

    def _map_raw_to_standard_fields(self, raw_metadata: Dict) -> Dict:
        """Map raw EXIF/DNG tags to standard MIX fields"""
        metadata = {}

        # Mapping of common EXIF/DNG tags to our standard fields
        tag_mappings = {
            'Image Make': 'scanner_manufacturer',
            'Image Model': 'scanner_model_name',
            'Image Software': 'scanning_software_name',
            'EXIF DateTimeOriginal': 'date_time_created',
            'EXIF DateTimeDigitized': 'date_time_created',
        }

        for raw_tag, std_field in tag_mappings.items():
            if raw_tag in raw_metadata and not metadata.get(std_field):
                value = raw_metadata[raw_tag]

                if 'DateTime' in raw_tag:
                    try:
                        if isinstance(value, str):
                            # Parse EXIF datetime format
                            dt = datetime.strptime(value.split()[0], '%Y:%m:%d')
                            metadata[std_field] = dt
                    except:
                        pass
                else:
                    metadata[std_field] = str(value)

        return metadata


def extract_image_metadata(file_path: str) -> Dict:
    """
    Extract comprehensive metadata from an image file

    Args:
        file_path: Path to the image file

    Returns:
        Dictionary containing both standard MIX fields and raw_metadata with ALL tags
    """
    extractor = ImageMetadataExtractor()
    return extractor.extract_metadata(file_path)
