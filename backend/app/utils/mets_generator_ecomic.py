"""
METS ECO-MiC 1.1 Generator
Generates METS XML compliant with ECO-MiC 1.1 standard for archival description
Compatible with Cineca validation API
"""

import xml.etree.ElementTree as ET
from app.models.document import Document
from datetime import datetime


class METSEcoMicGenerator:
    """Generator for METS ECO-MiC 1.1 compliant XML documents"""

    def __init__(self):
        # METS ECO-MiC namespaces
        self.namespaces = {
            'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'mix': 'http://www.loc.gov/mix/v20',
            'dct': 'http://purl.org/dc/terms/',
            'metsrights': 'http://cosimo.stanford.edu/sdr/metsrights/',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Register namespaces
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)

    def generate_mets_xml(self, document: Document) -> str:
        """Generate complete ECO-MiC 1.1 compliant METS XML"""

        # Create root METS element
        # ElementTree automatically adds xmlns declarations when using namespaced elements
        mets_attrs = {
            f"{{{self.namespaces['xsi']}}}schemaLocation": 'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd http://www.loc.gov/mix/ http://www.loc.gov/standards/mix/mix02/mix02.xsd http://www.loc.gov/mods/v3 http://www.loc.gov/mods/v3/mods-3-7.xsd http://cosimo.stanford.edu/sdr/metsrights/ https://www.loc.gov/standards/rights/METSRights.xsd'
        }

        root = ET.Element(f"{{{self.namespaces['mets']}}}mets", mets_attrs)

        # Add sections in ECO-MiC order
        self._add_mets_header(root, document)
        self._add_descriptive_metadata(root, document)
        self._add_administrative_metadata(root, document)
        self._add_file_section(root, document)
        self._add_structural_map(root, document)

        # Convert to string with pretty formatting
        self._indent(root)
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _add_mets_header(self, root: ET.Element, document: Document):
        """Add METS header with ECO-MiC RECORDSTATUS"""
        header = ET.SubElement(root, f"{{{self.namespaces['mets']}}}metsHdr")
        header.set('CREATEDATE', document.created_at.strftime('%Y-%m-%dT%H:%M:%S'))
        header.set('LASTMODDATE', document.updated_at.strftime('%Y-%m-%dT%H:%M:%S'))
        header.set('RECORDSTATUS', document.record_status or 'COMPLETE')

        # Agent - CREATOR (Ministero della Cultura or organization)
        agent_creator = ET.SubElement(header, f"{{{self.namespaces['mets']}}}agent")
        agent_creator.set('ROLE', 'CREATOR')
        agent_creator.set('TYPE', 'ORGANIZATION')

        name_creator = ET.SubElement(agent_creator, f"{{{self.namespaces['mets']}}}name")
        name_creator.text = "Archivia Digital Archive System"

        # Agent - CUSTODIAN (Archive)
        if document.archive_name:
            agent_custodian = ET.SubElement(header, f"{{{self.namespaces['mets']}}}agent")
            agent_custodian.set('ROLE', 'CUSTODIAN')
            agent_custodian.set('TYPE', 'ORGANIZATION')

            name_custodian = ET.SubElement(agent_custodian, f"{{{self.namespaces['mets']}}}name")
            name_custodian.text = document.archive_name

            if document.archive_contact:
                note = ET.SubElement(agent_custodian, f"{{{self.namespaces['mets']}}}note")
                note.text = f"Contact: {document.archive_contact}"

    def _add_descriptive_metadata(self, root: ET.Element, document: Document):
        """Add MODS descriptive metadata in ECO-MiC structure"""
        dmd_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}dmdSec")
        dmd_sec.set('ID', 'dmd01')  # Use standard ID format for ECO-MiC 1.1
        dmd_sec.set('STATUS', 'referenced')  # ECO-MiC 1.1 requirement

        md_wrap = ET.SubElement(dmd_sec, f"{{{self.namespaces['mets']}}}mdWrap")
        md_wrap.set('MDTYPE', 'MODS')

        xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")

        # MODS root
        mods = ET.SubElement(xml_data, f"{{{self.namespaces['mods']}}}mods")

        # 1. Identifiers (ECO-MiC 1.1: logical, conservative, and relation IDs)
        identifier_logical = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
        identifier_logical.set('type', 'logicalId')
        identifier_logical.text = document.logical_id

        if document.conservative_id:
            identifier_conservative = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
            identifier_conservative.set('type', 'conservativeId')
            identifier_conservative.text = document.conservative_id

        if document.conservative_id_authority:
            identifier_authority = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
            identifier_authority.set('type', 'conservativeIdAuthority')
            identifier_authority.text = document.conservative_id_authority

        # Add relationId as per ECO-MiC 1.1 example
        identifier_relation = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
        identifier_relation.set('type', 'relationId')
        identifier_relation.text = 'representation'

        # 2. Title
        if document.title:
            title_info = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}titleInfo")
            title = ET.SubElement(title_info, f"{{{self.namespaces['mods']}}}title")
            title.text = document.title

        # 3. Type of Resource (ECO-MiC required)
        if document.type_of_resource:
            type_of_resource = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}typeOfResource")
            type_of_resource.text = document.type_of_resource

        # 4. Abstract/Description
        if document.description:
            abstract = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}abstract")
            abstract.text = document.description

        # 5. Corporate/Personal Names (ECO-MiC structure)
        if document.producer_name:
            name_producer = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}name")
            name_producer.set('type', document.producer_type or 'corporate')

            name_part = ET.SubElement(name_producer, f"{{{self.namespaces['mods']}}}namePart")
            name_part.text = document.producer_name

            if document.producer_role:
                role = ET.SubElement(name_producer, f"{{{self.namespaces['mods']}}}role")
                role_term = ET.SubElement(role, f"{{{self.namespaces['mods']}}}roleTerm")
                role_term.set('type', 'text')
                role_term.text = document.producer_role

        if document.creator_name:
            name_creator = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}name")
            name_creator.set('type', document.creator_type or 'personal')

            name_part = ET.SubElement(name_creator, f"{{{self.namespaces['mods']}}}namePart")
            name_part.text = document.creator_name

            if document.creator_role:
                role = ET.SubElement(name_creator, f"{{{self.namespaces['mods']}}}role")
                role_term = ET.SubElement(role, f"{{{self.namespaces['mods']}}}roleTerm")
                role_term.set('type', 'text')
                role_term.text = document.creator_role

        # 6. Origin Info (dates)
        if document.date_from or document.date_to or document.period:
            origin_info = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}originInfo")

            if document.date_from and document.date_to:
                date_created_start = ET.SubElement(origin_info, f"{{{self.namespaces['mods']}}}dateCreated")
                date_created_start.set('point', 'start')
                date_created_start.text = document.date_from

                date_created_end = ET.SubElement(origin_info, f"{{{self.namespaces['mods']}}}dateCreated")
                date_created_end.set('point', 'end')
                date_created_end.text = document.date_to
            elif document.date_from:
                date_created = ET.SubElement(origin_info, f"{{{self.namespaces['mods']}}}dateCreated")
                date_created.text = document.date_from
            elif document.date_to:
                date_created = ET.SubElement(origin_info, f"{{{self.namespaces['mods']}}}dateCreated")
                date_created.text = document.date_to

            if document.period:
                date_other = ET.SubElement(origin_info, f"{{{self.namespaces['mods']}}}dateOther")
                date_other.set('type', 'period')
                date_other.text = document.period

        # 7. Language
        if document.language:
            language_elem = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}language")
            language_term = ET.SubElement(language_elem, f"{{{self.namespaces['mods']}}}languageTerm")
            language_term.set('type', 'code')
            language_term.set('authority', 'iso639-2b')
            language_term.text = document.language

        # 8. Physical Description (ECO-MiC structure)
        if document.physical_form or document.extent_description or document.total_pages:
            phys_desc = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}physicalDescription")

            if document.physical_form:
                form = ET.SubElement(phys_desc, f"{{{self.namespaces['mods']}}}form")
                form.set('authority', 'gmd')
                form.text = document.physical_form

            if document.extent_description:
                extent = ET.SubElement(phys_desc, f"{{{self.namespaces['mods']}}}extent")
                extent.text = document.extent_description
            elif document.total_pages:
                extent = ET.SubElement(phys_desc, f"{{{self.namespaces['mods']}}}extent")
                extent.text = f"{document.total_pages} pages"

        # 9. Subjects
        if document.subjects:
            subjects_list = [s.strip() for s in document.subjects.replace(';', ',').split(',') if s.strip()]
            for subject_text in subjects_list:
                subject = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}subject")
                topic = ET.SubElement(subject, f"{{{self.namespaces['mods']}}}topic")
                topic.text = subject_text

        # 10. Geographic subject
        if document.location:
            subject_geo = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}subject")
            geographic = ET.SubElement(subject_geo, f"{{{self.namespaces['mods']}}}geographic")
            geographic.text = document.location

        # 11. Archival hierarchy (ECO-MiC relatedItem structure)
        if document.fund_name or document.series_name or document.folder_number:
            related_item = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}relatedItem")
            related_item.set('type', 'host')

            if document.fund_name:
                title_info = ET.SubElement(related_item, f"{{{self.namespaces['mods']}}}titleInfo")
                title = ET.SubElement(title_info, f"{{{self.namespaces['mods']}}}title")
                title.text = document.fund_name

                if document.conservative_id:
                    identifier = ET.SubElement(related_item, f"{{{self.namespaces['mods']}}}identifier")
                    identifier.set('type', 'collection')
                    identifier.text = document.conservative_id

            if document.series_name or document.folder_number:
                part = ET.SubElement(related_item, f"{{{self.namespaces['mods']}}}part")

                if document.series_name:
                    detail_series = ET.SubElement(part, f"{{{self.namespaces['mods']}}}detail")
                    detail_series.set('type', 'series')
                    caption = ET.SubElement(detail_series, f"{{{self.namespaces['mods']}}}caption")
                    caption.text = "Series"
                    title = ET.SubElement(detail_series, f"{{{self.namespaces['mods']}}}title")
                    title.text = document.series_name

                if document.folder_number:
                    detail_folder = ET.SubElement(part, f"{{{self.namespaces['mods']}}}detail")
                    detail_folder.set('type', 'folder')
                    caption = ET.SubElement(detail_folder, f"{{{self.namespaces['mods']}}}caption")
                    caption.text = "Folder"
                    number = ET.SubElement(detail_folder, f"{{{self.namespaces['mods']}}}number")
                    number.text = document.folder_number

        # 12. Access Condition (Rights)
        if document.license_url or document.rights_statement:
            access_condition = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}accessCondition")
            access_condition.set('type', 'use and reproduction')

            if document.license_url:
                access_condition.set(f"{{{self.namespaces['xlink']}}}href", document.license_url)

            if document.rights_statement:
                access_condition.text = document.rights_statement

    def _add_administrative_metadata(self, root: ET.Element, document: Document):
        """Add administrative metadata with techMD per file and rightsMD"""
        amd_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}amdSec")
        amd_sec.set('ID', f'amd_{document.id}')

        # Rights Metadata (ECO-MiC requirement)
        if any([document.rights_category, document.rights_holder, document.rights_constraint]):
            rights_md = ET.SubElement(amd_sec, f"{{{self.namespaces['mets']}}}rightsMD")
            rights_md.set('ID', f'rights_{document.id}')

            md_wrap = ET.SubElement(rights_md, f"{{{self.namespaces['mets']}}}mdWrap")
            md_wrap.set('MDTYPE', 'OTHER')
            md_wrap.set('OTHERMDTYPE', 'METSRIGHTS')

            xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")

            # METSRights declaration
            rights_decl = ET.SubElement(xml_data, f"{{{self.namespaces['metsrights']}}}RightsDeclaration")
            rights_decl.set('RIGHTSCATEGORY', document.rights_category or 'COPYRIGHTED')

            if document.rights_holder:
                rights_holder = ET.SubElement(rights_decl, f"{{{self.namespaces['metsrights']}}}RightsHolder")
                rights_holder_name = ET.SubElement(rights_holder, f"{{{self.namespaces['metsrights']}}}RightsHolderName")
                rights_holder_name.text = document.rights_holder

            if document.rights_constraint:
                context = ET.SubElement(rights_decl, f"{{{self.namespaces['metsrights']}}}Context")
                context.set('CONTEXTCLASS', 'GENERAL PUBLIC')

                constraints = ET.SubElement(context, f"{{{self.namespaces['metsrights']}}}Constraints")
                constraint_desc = ET.SubElement(constraints, f"{{{self.namespaces['metsrights']}}}ConstraintDescription")
                constraint_desc.text = document.rights_constraint

        # Technical Metadata per file (ECO-MiC structure)
        for doc_file in document.document_files:
            file_id = doc_file.file.id if hasattr(doc_file, 'file') else doc_file.file_id

            tech_md = ET.SubElement(amd_sec, f"{{{self.namespaces['mets']}}}techMD")
            tech_md.set('ID', f'tech_{file_id}')

            md_wrap = ET.SubElement(tech_md, f"{{{self.namespaces['mets']}}}mdWrap")
            md_wrap.set('MDTYPE', 'OTHER')
            md_wrap.set('OTHERMDTYPE', 'MIX')

            xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")

            # MIX metadata
            mix = ET.SubElement(xml_data, f"{{{self.namespaces['mix']}}}mix")

            # Image characteristics
            if any([doc_file.image_width, doc_file.image_height, doc_file.bits_per_sample,
                    doc_file.compression_scheme, doc_file.color_space]):
                img_char = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}ImageCharacteristics")

                # Dimensions
                if doc_file.image_width or doc_file.image_height:
                    img_dim = ET.SubElement(img_char, f"{{{self.namespaces['mix']}}}ImageDimensions")

                    if doc_file.image_width:
                        width = ET.SubElement(img_dim, f"{{{self.namespaces['mix']}}}imageWidth")
                        width.text = str(doc_file.image_width)

                    if doc_file.image_height:
                        height = ET.SubElement(img_dim, f"{{{self.namespaces['mix']}}}imageHeight")
                        height.text = str(doc_file.image_height)

                # Bits per sample
                if doc_file.bits_per_sample:
                    img_color = ET.SubElement(img_char, f"{{{self.namespaces['mix']}}}PhotometricInterpretation")
                    color_space = ET.SubElement(img_color, f"{{{self.namespaces['mix']}}}colorSpace")
                    color_space.text = doc_file.color_space or 'RGB'

                # Sampling frequency (DPI)
                if doc_file.x_sampling_frequency or doc_file.y_sampling_frequency:
                    sampling = ET.SubElement(img_char, f"{{{self.namespaces['mix']}}}SamplingFrequency")

                    if doc_file.x_sampling_frequency:
                        x_freq = ET.SubElement(sampling, f"{{{self.namespaces['mix']}}}xSamplingFrequency")
                        x_freq.text = str(doc_file.x_sampling_frequency)

                    if doc_file.y_sampling_frequency:
                        y_freq = ET.SubElement(sampling, f"{{{self.namespaces['mix']}}}ySamplingFrequency")
                        y_freq.text = str(doc_file.y_sampling_frequency)

                    if doc_file.sampling_frequency_unit:
                        unit = ET.SubElement(sampling, f"{{{self.namespaces['mix']}}}samplingFrequencyUnit")
                        unit.text = doc_file.sampling_frequency_unit

            # Scanner/Camera information (from file-level metadata extracted from EXIF)
            if doc_file.scanner_manufacturer or doc_file.scanner_model_name:
                img_creation = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}ImageCreation")
                scanner_capture = ET.SubElement(img_creation, f"{{{self.namespaces['mix']}}}ScannerCapture")

                if doc_file.scanner_manufacturer:
                    manufacturer = ET.SubElement(scanner_capture, f"{{{self.namespaces['mix']}}}scannerManufacturer")
                    manufacturer.text = doc_file.scanner_manufacturer

                if doc_file.scanner_model_name:
                    scanner_model = ET.SubElement(scanner_capture, f"{{{self.namespaces['mix']}}}ScannerModel")
                    model_name = ET.SubElement(scanner_model, f"{{{self.namespaces['mix']}}}scannerModelName")
                    model_name.text = doc_file.scanner_model_name

            # Scanning software information (from file-level metadata)
            if doc_file.scanning_software_name or doc_file.scanning_software_version:
                if not any([doc_file.scanner_manufacturer, doc_file.scanner_model_name]):
                    img_creation = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}ImageCreation")
                    scanner_capture = ET.SubElement(img_creation, f"{{{self.namespaces['mix']}}}ScannerCapture")

                if doc_file.scanning_software_name:
                    software = ET.SubElement(scanner_capture, f"{{{self.namespaces['mix']}}}scanningSoftware")
                    software_name = ET.SubElement(software, f"{{{self.namespaces['mix']}}}scanningSoftwareName")
                    software_name.text = doc_file.scanning_software_name

                    if doc_file.scanning_software_version:
                        software_version = ET.SubElement(software, f"{{{self.namespaces['mix']}}}scanningSoftwareVersionNo")
                        software_version.text = doc_file.scanning_software_version

    def _add_file_section(self, root: ET.Element, document: Document):
        """Add file section with proper ECO-MiC structure grouped by file_category"""
        file_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}fileSec")

        # Map file_category to METS USE attribute (ECO-MiC compliant)
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

        # Group files by file_category
        file_groups = {}
        for doc_file in document.document_files:
            # Use file_category if available, fallback to file_use, then 'other'
            category = doc_file.file_category or 'other'
            use_attr = category_to_use.get(category, 'OTHER')

            if use_attr not in file_groups:
                file_groups[use_attr] = []
            file_groups[use_attr].append(doc_file)

        # Define order for fileGrp elements (ECO-MiC best practice: MASTER first)
        use_order = ['MASTER', 'REFERENCE', 'HIGH', 'THUMBNAIL', 'METADATA', 'OTHER']

        # Create fileGrp for each USE type in proper order
        for use in use_order:
            if use not in file_groups:
                continue

            file_grp = ET.SubElement(file_sec, f"{{{self.namespaces['mets']}}}fileGrp")
            file_grp.set('USE', use)

            for doc_file in sorted(file_groups[use], key=lambda x: x.sequence_number or 0):
                file_elem = ET.SubElement(file_grp, f"{{{self.namespaces['mets']}}}file")

                # Get file information
                if hasattr(doc_file, 'file'):
                    file_id = doc_file.file.id
                    content_type = doc_file.file.content_type
                    file_size = doc_file.file.file_size
                    filename = doc_file.file.filename
                else:
                    file_id = doc_file.file_id
                    content_type = doc_file.content_type
                    file_size = doc_file.file_size
                    filename = doc_file.filename

                file_elem.set('ID', f'file_{file_id}')
                file_elem.set('MIMETYPE', content_type or 'application/octet-stream')
                file_elem.set('SIZE', str(file_size))
                file_elem.set('ADMID', f'tech_{file_id}')  # Link to techMD

                if doc_file.checksum_md5:
                    file_elem.set('CHECKSUM', doc_file.checksum_md5)
                    file_elem.set('CHECKSUMTYPE', 'MD5')

                # File location - use category-based folder structure
                category = doc_file.file_category or 'other'
                folder_name = self._get_folder_name_for_category(category)
                flocat = ET.SubElement(file_elem, f"{{{self.namespaces['mets']}}}FLocat")
                flocat.set('LOCTYPE', 'URL')
                flocat.set(f"{{{self.namespaces['xlink']}}}href", f"file://./{folder_name}/{filename}")

    def _get_folder_name_for_category(self, category: str) -> str:
        """Map file_category to ECO-MiC folder naming convention"""
        folder_mapping = {
            'master': 'Master',
            'normalized': 'Normalized',
            'export_high': 'Export300',
            'export_low': 'Export150',
            'metadata': 'Metadata',
            'icc': 'ICC',
            'logs': 'Logs',
            'other': 'Other'
        }
        return folder_mapping.get(category, 'Other')

    def _add_structural_map(self, root: ET.Element, document: Document):
        """Add PHYSICAL structural map (ECO-MiC requirement)"""
        struct_map = ET.SubElement(root, f"{{{self.namespaces['mets']}}}structMap")
        struct_map.set('TYPE', 'PHYSICAL')  # ECO-MiC uses PHYSICAL not LOGICAL

        # Main folder div
        folder_div = ET.SubElement(struct_map, f"{{{self.namespaces['mets']}}}div")
        folder_div.set('TYPE', 'folder')
        folder_div.set('DMDID', f'dmd_{document.id}')
        folder_div.set('ADMID', f'amd_{document.id}')

        if document.title:
            folder_div.set('LABEL', document.title)

        # Group files by sequence number for pages
        files_by_sequence = {}
        for doc_file in document.document_files:
            seq = doc_file.sequence_number or 0
            if seq not in files_by_sequence:
                files_by_sequence[seq] = []
            files_by_sequence[seq].append(doc_file)

        # Add page divs with multiple file pointers (for different versions)
        for seq in sorted(files_by_sequence.keys()):
            files = files_by_sequence[seq]

            page_div = ET.SubElement(folder_div, f"{{{self.namespaces['mets']}}}div")
            page_div.set('TYPE', 'page')
            page_div.set('ORDER', str(seq))

            # Use file_label from first file if available
            if files and files[0].file_label:
                page_div.set('LABEL', files[0].file_label)

            # Add file pointers for all versions (ARCHIVE, HIGH, etc.)
            for doc_file in files:
                fptr = ET.SubElement(page_div, f"{{{self.namespaces['mets']}}}fptr")

                file_id = doc_file.file.id if hasattr(doc_file, 'file') else doc_file.file_id
                fptr.set('FILEID', f'file_{file_id}')

    def _indent(self, elem, level=0):
        """Add indentation for pretty printing"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
