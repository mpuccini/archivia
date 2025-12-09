"""
File Categorization Service

Implements ECO-MiC 5.3 and 5.4 guidelines for automatic file categorization
based on folder structure and file extensions.
"""

import os
import re
from typing import Optional, Dict, Tuple
from pathlib import Path


class FileCategorizer:
    """
    Categorizes files according to ECO-MiC archival digitization guidelines.

    Categories:
    - master: Preservation master files (DNG, RAW, uncompressed TIFF)
    - normalized: Normalized TIFF files (Adobe RGB profile, 2400px)
    - export_high: High-quality JPEG (300 DPI, ~2400px)
    - export_low: Low-quality JPEG (150 DPI, ~1200-1500px)
    - metadata: XML, metadata files
    - icc: ICC color profiles
    - logs: Log files
    - other: Uncategorized files
    """

    # File extensions by category
    MASTER_EXTENSIONS = {'.dng', '.raw', '.cr2', '.nef', '.arw', '.orf', '.rw2'}
    TIFF_EXTENSIONS = {'.tif', '.tiff'}
    JPEG_EXTENSIONS = {'.jpg', '.jpeg'}
    METADATA_EXTENSIONS = {'.xml', '.mets', '.mods'}
    ICC_EXTENSIONS = {'.icc', '.icm'}
    LOG_EXTENSIONS = {'.log', '.txt'}

    # Folder patterns (ECO-MiC 5.4)
    FOLDER_PATTERNS = {
        'master': ['TIF.Master', 'TIFF.Master', 'Master', 'RAW'],
        'normalized': ['TIF.Derived', 'TIFF.Derived', 'Derived', 'Normalized'],
        'export_high': ['JPG300', 'JPEG300', 'Export300', 'High'],
        'export_low': ['JPG150', 'JPEG150', 'Export150', 'Low'],
        'metadata': ['Metadata', 'XML', 'METS'],
        'icc': ['ICC', 'ColorProfiles', 'Profiles'],
        'logs': ['Logs', 'Log']
    }

    @classmethod
    def categorize_file(cls, filename: str, folder_path: Optional[str] = None) -> Tuple[str, float]:
        """
        Categorize a file based on its name and optional folder path.

        Args:
            filename: The filename (with extension)
            folder_path: Optional folder path containing the file

        Returns:
            Tuple of (category, confidence)
            - category: One of the category strings
            - confidence: 0.0-1.0 indicating detection confidence
        """
        file_ext = Path(filename).suffix.lower()
        folder_name = Path(folder_path).name if folder_path else None

        # High confidence: Folder-based detection
        if folder_name:
            category_from_folder = cls._categorize_by_folder(folder_name, file_ext)
            if category_from_folder:
                return category_from_folder, 0.95

        # Medium confidence: Extension-based detection
        category_from_ext = cls._categorize_by_extension(file_ext, filename)
        if category_from_ext:
            return category_from_ext, 0.75

        # Low confidence: Fallback
        return 'other', 0.3

    @classmethod
    def _categorize_by_folder(cls, folder_name: str, file_ext: str) -> Optional[str]:
        """
        Categorize based on folder structure (ECO-MiC 5.4).
        """
        # Check each category's folder patterns
        for category, patterns in cls.FOLDER_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in folder_name.lower():
                    # Validate extension matches category expectations
                    if category == 'master':
                        if file_ext in cls.MASTER_EXTENSIONS or file_ext in cls.TIFF_EXTENSIONS:
                            return category
                    elif category == 'normalized':
                        if file_ext in cls.TIFF_EXTENSIONS:
                            return category
                    elif category in ['export_high', 'export_low']:
                        if file_ext in cls.JPEG_EXTENSIONS:
                            return category
                    elif category == 'metadata':
                        if file_ext in cls.METADATA_EXTENSIONS:
                            return category
                    elif category == 'icc':
                        if file_ext in cls.ICC_EXTENSIONS:
                            return category
                    elif category == 'logs':
                        if file_ext in cls.LOG_EXTENSIONS:
                            return category

        return None

    @classmethod
    def _categorize_by_extension(cls, file_ext: str, filename: str) -> Optional[str]:
        """
        Categorize based on file extension and naming conventions.
        """
        # Master files
        if file_ext in cls.MASTER_EXTENSIONS:
            return 'master'

        # TIFF files - try to distinguish master from normalized
        if file_ext in cls.TIFF_EXTENSIONS:
            # Check filename for hints
            filename_lower = filename.lower()
            if any(keyword in filename_lower for keyword in ['master', 'raw', 'original']):
                return 'master'
            elif any(keyword in filename_lower for keyword in ['derived', 'normalized', 'processed']):
                return 'normalized'
            else:
                # Default TIFF to normalized (more common for derived files)
                return 'normalized'

        # JPEG files - try to distinguish quality levels
        if file_ext in cls.JPEG_EXTENSIONS:
            filename_lower = filename.lower()
            # Check for resolution hints in filename
            if '300' in filename or '2400' in filename or 'high' in filename_lower:
                return 'export_high'
            elif '150' in filename or '1200' in filename or 'low' in filename_lower:
                return 'export_low'
            else:
                # Default to export_high
                return 'export_high'

        # Metadata files
        if file_ext in cls.METADATA_EXTENSIONS:
            return 'metadata'

        # ICC profiles
        if file_ext in cls.ICC_EXTENSIONS:
            return 'icc'

        # Log files
        if file_ext in cls.LOG_EXTENSIONS:
            return 'logs'

        return None

    @classmethod
    def get_file_use_from_category(cls, category: str) -> str:
        """
        Map category to METS fileGrp USE attribute.

        Returns the standard METS USE value for the category.
        """
        category_to_use = {
            'master': 'MASTER',
            'normalized': 'REFERENCE',
            'export_high': 'HIGH',
            'export_low': 'THUMBNAIL',
            'metadata': 'METADATA',
            'icc': 'METADATA',
            'logs': 'METADATA',
            'other': 'OTHER'
        }
        return category_to_use.get(category, 'OTHER')

    @classmethod
    def get_category_description(cls, category: str) -> str:
        """
        Get human-readable description of a file category.
        """
        descriptions = {
            'master': 'Preservation Master (RAW/DNG/Uncompressed TIFF)',
            'normalized': 'Normalized TIFF (Adobe RGB, 2400px)',
            'export_high': 'High-Quality JPEG (300 DPI, ~2400px)',
            'export_low': 'Low-Quality JPEG (150 DPI, ~1200px)',
            'metadata': 'Metadata Files (XML, METS, etc.)',
            'icc': 'ICC Color Profiles',
            'logs': 'Log Files',
            'other': 'Other/Uncategorized'
        }
        return descriptions.get(category, 'Unknown')

    @classmethod
    def validate_folder_structure(cls, file_list: list) -> Dict[str, list]:
        """
        Analyze a list of files and group them by detected category.

        Args:
            file_list: List of dicts with 'filename' and optional 'folder_path'

        Returns:
            Dict mapping category to list of files in that category
        """
        categorized = {
            'master': [],
            'normalized': [],
            'export_high': [],
            'export_low': [],
            'metadata': [],
            'icc': [],
            'logs': [],
            'other': []
        }

        for file_info in file_list:
            filename = file_info.get('filename', '')
            folder_path = file_info.get('folder_path', '')

            category, confidence = cls.categorize_file(filename, folder_path)
            categorized[category].append({
                **file_info,
                'category': category,
                'confidence': confidence
            })

        return categorized
