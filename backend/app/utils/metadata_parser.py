"""
Metadata parser for extracting document metadata from XML and CSV files
"""
import csv
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataParser:
    """Parser for document metadata from XML and CSV files"""

    @staticmethod
    def parse_xml_metadata(xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse metadata from XML file (METS or custom format)

        Args:
            xml_content: XML content as string

        Returns:
            Dictionary with extracted metadata or None if parsing fails
        """
        try:
            root = ET.fromstring(xml_content)
            metadata = {}

            # Define namespace mappings for METS
            namespaces = {
                'mets': 'http://www.loc.gov/METS/',
                'mods': 'http://www.loc.gov/mods/v3',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dct': 'http://purl.org/dc/terms/',
                'xlink': 'http://www.w3.org/1999/xlink'
            }

            # Try to parse as METS ECO-MiC format first
            if root.tag.endswith('mets') or 'METS' in root.tag:
                metadata = MetadataParser._parse_mets_xml(root, namespaces)
            else:
                # Try to parse as simple XML with common fields
                metadata = MetadataParser._parse_simple_xml(root)

            logger.info(f"Successfully parsed XML metadata: {len(metadata)} fields")
            return metadata if metadata else None

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            return None

    @staticmethod
    def _parse_mets_xml(root: ET.Element, namespaces: Dict[str, str]) -> Dict[str, Any]:
        """Parse METS XML format"""
        metadata = {}

        # Extract from dmdSec (descriptive metadata)
        dmd_sec = root.find('.//mets:dmdSec', namespaces)
        if dmd_sec is not None:
            # Try MODS
            mods = dmd_sec.find('.//mods:mods', namespaces)
            if mods is not None:
                # Title
                title_elem = mods.find('.//mods:title', namespaces)
                if title_elem is not None and title_elem.text:
                    metadata['title'] = title_elem.text.strip()

                # Description/Abstract
                abstract = mods.find('.//mods:abstract', namespaces)
                if abstract is not None and abstract.text:
                    metadata['description'] = abstract.text.strip()

                # Type of resource
                type_of_resource = mods.find('.//mods:typeOfResource', namespaces)
                if type_of_resource is not None and type_of_resource.text:
                    metadata['type_of_resource'] = type_of_resource.text.strip()

                # Language
                language = mods.find('.//mods:languageTerm', namespaces)
                if language is not None and language.text:
                    metadata['language'] = language.text.strip()

                # Subjects
                subjects = mods.findall('.//mods:subject/mods:topic', namespaces)
                if subjects:
                    metadata['subjects'] = ','.join([s.text.strip() for s in subjects if s.text])

                # Location
                location = mods.find('.//mods:physicalLocation', namespaces)
                if location is not None and location.text:
                    metadata['location'] = location.text.strip()

                # Archive information from relatedItem
                related_item = mods.find('.//mods:relatedItem[@type="host"]', namespaces)
                if related_item is not None:
                    archive_title = related_item.find('.//mods:title', namespaces)
                    if archive_title is not None and archive_title.text:
                        metadata['archive_name'] = archive_title.text.strip()

                    fund_name = related_item.find('.//mods:relatedItem[@displayLabel="Fondo"]/mods:titleInfo/mods:title', namespaces)
                    if fund_name is not None and fund_name.text:
                        metadata['fund_name'] = fund_name.text.strip()

                    series_name = related_item.find('.//mods:relatedItem[@displayLabel="Serie"]/mods:titleInfo/mods:title', namespaces)
                    if series_name is not None and series_name.text:
                        metadata['series_name'] = series_name.text.strip()

                # Dates
                origin_info = mods.find('.//mods:originInfo', namespaces)
                if origin_info is not None:
                    date_created_start = origin_info.find('.//mods:dateCreated[@point="start"]', namespaces)
                    if date_created_start is not None and date_created_start.text:
                        metadata['date_from'] = date_created_start.text.strip()

                    date_created_end = origin_info.find('.//mods:dateCreated[@point="end"]', namespaces)
                    if date_created_end is not None and date_created_end.text:
                        metadata['date_to'] = date_created_end.text.strip()

                    # Period
                    date_other = origin_info.find('.//mods:dateOther[@type="period"]', namespaces)
                    if date_other is not None and date_other.text:
                        metadata['period'] = date_other.text.strip()

                # Names (agents)
                names = mods.findall('.//mods:name', namespaces)
                for name in names:
                    name_part = name.find('.//mods:namePart', namespaces)
                    role = name.find('.//mods:roleTerm', namespaces)

                    if name_part is not None and role is not None:
                        name_type = name.get('type', 'personal')
                        role_text = role.text.strip() if role.text else ''

                        if 'producer' in role_text.lower() or 'editore' in role_text.lower():
                            metadata['producer_name'] = name_part.text.strip()
                            metadata['producer_type'] = name_type
                            metadata['producer_role'] = role_text
                        elif 'creator' in role_text.lower() or 'autore' in role_text.lower():
                            metadata['creator_name'] = name_part.text.strip()
                            metadata['creator_type'] = name_type
                            metadata['creator_role'] = role_text

                # Physical description
                physical_desc = mods.find('.//mods:physicalDescription', namespaces)
                if physical_desc is not None:
                    form = physical_desc.find('.//mods:form', namespaces)
                    if form is not None and form.text:
                        metadata['physical_form'] = form.text.strip()

                    extent = physical_desc.find('.//mods:extent', namespaces)
                    if extent is not None and extent.text:
                        metadata['extent_description'] = extent.text.strip()

            # Try Dublin Core as fallback
            dc_elements = dmd_sec.findall('.//*[@{http://purl.org/dc/elements/1.1/}*]', namespaces)
            for elem in dc_elements:
                tag_name = elem.tag.split('}')[-1]  # Get local name
                if elem.text and tag_name:
                    metadata[tag_name.lower()] = elem.text.strip()

        # Extract identifier from metsHdr or objID
        obj_id = root.get('OBJID')
        if obj_id:
            metadata['conservative_id'] = obj_id

        # Extract from metsHdr
        mets_hdr = root.find('.//mets:metsHdr', namespaces)
        if mets_hdr is not None:
            record_status = mets_hdr.get('RECORDSTATUS')
            if record_status:
                metadata['record_status'] = record_status

        return metadata

    @staticmethod
    def _parse_simple_xml(root: ET.Element) -> Dict[str, Any]:
        """Parse simple XML with direct field mapping"""
        metadata = {}

        # Common field mappings
        field_mapping = {
            'title': ['title', 'Title', 'titolo', 'Titolo'],
            'description': ['description', 'Description', 'descrizione', 'Descrizione', 'abstract', 'Abstract'],
            'logical_id': ['logical_id', 'logicalId', 'id', 'ID'],
            'conservative_id': ['conservative_id', 'conservativeId', 'conservativeID'],
            'conservative_id_authority': ['conservative_id_authority', 'authority', 'Authority'],
            'archive_name': ['archive_name', 'archiveName', 'archive', 'Archive', 'archivio'],
            'archive_contact': ['archive_contact', 'archiveContact', 'contact'],
            'fund_name': ['fund_name', 'fundName', 'fondo', 'Fondo'],
            'series_name': ['series_name', 'seriesName', 'serie', 'Serie'],
            'folder_number': ['folder_number', 'folderNumber', 'busta', 'Busta'],
            'date_from': ['date_from', 'dateFrom', 'startDate', 'start_date'],
            'date_to': ['date_to', 'dateTo', 'endDate', 'end_date'],
            'period': ['period', 'Period', 'periodo', 'Periodo'],
            'location': ['location', 'Location', 'luogo', 'Luogo'],
            'language': ['language', 'Language', 'lingua', 'Lingua'],
            'subjects': ['subjects', 'Subjects', 'soggetti', 'Soggetti', 'keywords'],
            'type_of_resource': ['type_of_resource', 'typeOfResource', 'type', 'Type', 'tipo'],
            'document_type': ['document_type', 'documentType'],
            'physical_form': ['physical_form', 'physicalForm', 'form'],
            'extent_description': ['extent_description', 'extentDescription', 'extent'],
            'producer_name': ['producer_name', 'producerName', 'producer'],
            'creator_name': ['creator_name', 'creatorName', 'creator', 'author'],
            'license_url': ['license_url', 'licenseUrl', 'license'],
            'rights_statement': ['rights_statement', 'rightsStatement', 'rights'],
            'rights_category': ['rights_category', 'rightsCategory'],
            'rights_holder': ['rights_holder', 'rightsHolder'],
            'rights_constraint': ['rights_constraint', 'rightsConstraint']
        }

        # Try to find fields by walking the XML tree
        for our_field, xml_variants in field_mapping.items():
            for xml_field in xml_variants:
                # Try as direct child
                elem = root.find(f'.//{xml_field}')
                if elem is not None and elem.text:
                    metadata[our_field] = elem.text.strip()
                    break

        return metadata

    @staticmethod
    def parse_csv_metadata(csv_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse metadata from CSV file

        Supports two CSV formats:
        1. Two-column format: field_name, value
        2. Single-row format: header row with field names, single data row

        Args:
            csv_content: CSV content as string

        Returns:
            Dictionary with extracted metadata or None if parsing fails
        """
        try:
            # Parse CSV
            lines = csv_content.strip().split('\n')
            if not lines:
                return None

            metadata = {}
            reader = csv.reader(lines)
            rows = list(reader)

            if len(rows) == 0:
                return None

            # Detect format
            if len(rows) == 1:
                # Single row without headers - skip
                logger.warning("CSV has only one row, cannot determine format")
                return None
            elif len(rows[0]) == 2:
                # Two-column format: field, value
                for row in rows:
                    if len(row) >= 2 and row[0] and row[1]:
                        field_name = row[0].strip().lower().replace(' ', '_')
                        metadata[field_name] = row[1].strip()
            else:
                # Multi-column format with headers
                headers = [h.strip().lower().replace(' ', '_') for h in rows[0]]
                if len(rows) > 1:
                    # Use first data row
                    values = rows[1]
                    for i, header in enumerate(headers):
                        if i < len(values) and values[i]:
                            metadata[header] = values[i].strip()

            logger.info(f"Successfully parsed CSV metadata: {len(metadata)} fields")
            return metadata if metadata else None

        except Exception as e:
            logger.error(f"Error parsing CSV metadata: {e}")
            return None

    @staticmethod
    def extract_metadata_from_folder(file_list: list) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from metadata folder in file list

        Args:
            file_list: List of file info dicts with 'folder_path', 'full_path', 'filename'

        Returns:
            Dictionary with extracted metadata or None if no metadata found
        """
        metadata = None

        # Look for metadata folder
        for file_info in file_list:
            folder_path = file_info.get('folder_path', '')
            filename = file_info.get('filename', '')
            full_path = file_info.get('full_path', '')

            # Check if file is in metadata folder
            if 'metadata' in folder_path.lower() or folder_path.lower() == 'metadata':
                logger.info(f"Found metadata file: {filename} in {folder_path}")

                # Read file content
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Parse based on extension
                    if filename.lower().endswith('.xml'):
                        logger.info(f"Parsing XML metadata from {filename}")
                        metadata = MetadataParser.parse_xml_metadata(content)
                        if metadata:
                            logger.info(f"Extracted {len(metadata)} fields from XML")
                            break  # Use first valid metadata file found

                    elif filename.lower().endswith('.csv'):
                        logger.info(f"Parsing CSV metadata from {filename}")
                        metadata = MetadataParser.parse_csv_metadata(content)
                        if metadata:
                            logger.info(f"Extracted {len(metadata)} fields from CSV")
                            break  # Use first valid metadata file found

                except Exception as e:
                    logger.error(f"Error reading metadata file {filename}: {e}")
                    continue

        return metadata
