"""
METS XML Generator
Generates METS (Metadata Encoding and Transmission Standard) XML from database records
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
from app.models.document import Document, DocumentFile


class METSGenerator:
    """Generator for METS XML documents from database records"""
    
    def __init__(self):
        # METS namespace declarations
        self.namespaces = {
            'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'mix': 'http://www.loc.gov/mix/v20',
            'dct': 'http://purl.org/dc/terms/',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Register namespaces
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)
    
    def generate_mets_xml(self, document: Document) -> str:
        """Generate complete METS XML for a document"""
        
        # Create root METS element
        mets_attrs = {
            'xmlns:mets': self.namespaces['mets'],
            'xmlns:mods': self.namespaces['mods'],
            'xmlns:mix': self.namespaces['mix'],
            'xmlns:dct': self.namespaces['dct'],
            'xmlns:xlink': self.namespaces['xlink'],
            'xmlns:xsi': self.namespaces['xsi'],
            'xsi:schemaLocation': 'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd',
            'OBJID': document.logical_id,
            'TYPE': document.document_type or 'Document',
            'PROFILE': 'http://www.loc.gov/mets/profiles/00000040.xml'
        }
        
        root = ET.Element(f"{{{self.namespaces['mets']}}}mets", mets_attrs)
        
        # Add header
        self._add_mets_header(root, document)
        
        # Add descriptive metadata
        self._add_descriptive_metadata(root, document)
        
        # Add administrative metadata
        self._add_administrative_metadata(root, document)
        
        # Add file section
        self._add_file_section(root, document)
        
        # Add structural map
        self._add_structural_map(root, document)
        
        # Convert to string with pretty formatting
        self._indent(root)
        xml_str = ET.tostring(root, encoding='unicode', xml_declaration=True)
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
    
    def _add_mets_header(self, root: ET.Element, document: Document):
        """Add METS header section"""
        header = ET.SubElement(root, f"{{{self.namespaces['mets']}}}metsHdr")
        header.set('CREATEDATE', document.created_at.strftime('%Y-%m-%dT%H:%M:%S'))
        header.set('LASTMODDATE', document.updated_at.strftime('%Y-%m-%dT%H:%M:%S'))
        
        # Agent - Archive
        if document.archive_name:
            agent = ET.SubElement(header, f"{{{self.namespaces['mets']}}}agent")
            agent.set('ROLE', 'CUSTODIAN')
            agent.set('TYPE', 'ORGANIZATION')
            
            name = ET.SubElement(agent, f"{{{self.namespaces['mets']}}}name")
            name.text = document.archive_name
            
            if document.archive_contact:
                note = ET.SubElement(agent, f"{{{self.namespaces['mets']}}}note")
                note.text = f"Contact: {document.archive_contact}"
        
        # Agent - Creator/Scanner
        if document.image_producer or document.scanner_manufacturer:
            agent = ET.SubElement(header, f"{{{self.namespaces['mets']}}}agent")
            agent.set('ROLE', 'CREATOR')
            agent.set('TYPE', 'OTHER')
            agent.set('OTHERTYPE', 'DIGITIZATION')
            
            name = ET.SubElement(agent, f"{{{self.namespaces['mets']}}}name")
            name.text = document.image_producer or document.scanner_manufacturer or "Unknown"
            
            if document.scanner_model:
                note = ET.SubElement(agent, f"{{{self.namespaces['mets']}}}note")
                note.text = f"Scanner: {document.scanner_model}"
    
    def _add_descriptive_metadata(self, root: ET.Element, document: Document):
        """Add descriptive metadata (MODS) section"""
        dmd_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}dmdSec")
        dmd_sec.set('ID', f'dmd_{document.id}')
        
        md_wrap = ET.SubElement(dmd_sec, f"{{{self.namespaces['mets']}}}mdWrap")
        md_wrap.set('MDTYPE', 'MODS')
        
        xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")
        
        # MODS root
        mods = ET.SubElement(xml_data, f"{{{self.namespaces['mods']}}}mods")
        
        # Title
        if document.title:
            title_info = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}titleInfo")
            title = ET.SubElement(title_info, f"{{{self.namespaces['mods']}}}title")
            title.text = document.title
        
        # Identifiers
        identifier = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
        identifier.set('type', 'logicalId')
        identifier.text = document.logical_id
        
        if document.conservative_id:
            identifier = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}identifier")
            identifier.set('type', 'conservativeId')
            if document.conservative_id_authority:
                identifier.set('authority', document.conservative_id_authority)
            identifier.text = document.conservative_id
        
        # Description
        if document.description:
            abstract = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}abstract")
            abstract.text = document.description
        
        # Physical description
        if document.total_pages or document.document_type:
            phys_desc = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}physicalDescription")
            
            if document.document_type:
                form = ET.SubElement(phys_desc, f"{{{self.namespaces['mods']}}}form")
                form.text = document.document_type
            
            if document.total_pages:
                extent = ET.SubElement(phys_desc, f"{{{self.namespaces['mods']}}}extent")
                extent.text = f"{document.total_pages} pages"
        
        # Rights
        if document.license_url or document.rights_statement:
            access_condition = ET.SubElement(mods, f"{{{self.namespaces['mods']}}}accessCondition")
            access_condition.set('type', 'use and reproduction')
            
            if document.license_url:
                access_condition.set(f"{{{self.namespaces['xlink']}}}href", document.license_url)
            
            if document.rights_statement:
                access_condition.text = document.rights_statement
    
    def _add_administrative_metadata(self, root: ET.Element, document: Document):
        """Add administrative metadata (technical) section"""
        amd_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}amdSec")
        amd_sec.set('ID', f'amd_{document.id}')
        
        tech_md = ET.SubElement(amd_sec, f"{{{self.namespaces['mets']}}}techMD")
        tech_md.set('ID', f'tech_{document.id}')
        
        md_wrap = ET.SubElement(tech_md, f"{{{self.namespaces['mets']}}}mdWrap")
        md_wrap.set('MDTYPE', 'OTHER')
        md_wrap.set('OTHERMDTYPE', 'MIX')
        
        xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")
        
        # MIX metadata for images
        mix = ET.SubElement(xml_data, f"{{{self.namespaces['mix']}}}mix")
        
        # Basic digital object information
        basic_info = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}BasicDigitalObjectInformation")
        
        if document.image_producer:
            obj_id = ET.SubElement(basic_info, f"{{{self.namespaces['mix']}}}ObjectIdentifier")
            obj_id_type = ET.SubElement(obj_id, f"{{{self.namespaces['mix']}}}objectIdentifierType")
            obj_id_type.text = "Producer"
            obj_id_value = ET.SubElement(obj_id, f"{{{self.namespaces['mix']}}}objectIdentifierValue")
            obj_id_value.text = document.image_producer
        
        # Scanner information
        if document.scanner_manufacturer or document.scanner_model:
            img_creation = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}ImageCreation")
            scanner_capture = ET.SubElement(img_creation, f"{{{self.namespaces['mix']}}}ScannerCapture")
            
            if document.scanner_manufacturer:
                scanner_manufacturer = ET.SubElement(scanner_capture, f"{{{self.namespaces['mix']}}}scannerManufacturer")
                scanner_manufacturer.text = document.scanner_manufacturer
            
            if document.scanner_model:
                scanner_model = ET.SubElement(scanner_capture, f"{{{self.namespaces['mix']}}}ScannerModel")
                scanner_model_name = ET.SubElement(scanner_model, f"{{{self.namespaces['mix']}}}scannerModelName")
                scanner_model_name.text = document.scanner_model
    
    def _add_file_section(self, root: ET.Element, document: Document):
        """Add file section with all document files"""
        file_sec = ET.SubElement(root, f"{{{self.namespaces['mets']}}}fileSec")
        
        # Group files by use
        file_groups = {}
        for doc_file in document.document_files:
            use = doc_file.file_use or 'ARCHIVE'
            if use not in file_groups:
                file_groups[use] = []
            file_groups[use].append(doc_file)
        
        # Create file groups
        for use, files in file_groups.items():
            file_grp = ET.SubElement(file_sec, f"{{{self.namespaces['mets']}}}fileGrp")
            file_grp.set('USE', use)
            
            for doc_file in files:
                file_elem = ET.SubElement(file_grp, f"{{{self.namespaces['mets']}}}file")
                
                # Handle both database objects and schema objects
                if hasattr(doc_file, 'file'):
                    # Database object with relationships
                    file_id = doc_file.file.id
                    content_type = doc_file.file.content_type
                    file_size = doc_file.file.file_size
                    filename = doc_file.file.filename
                else:
                    # Schema object (DocumentFileSchema)
                    file_id = doc_file.file_id
                    content_type = doc_file.content_type
                    file_size = doc_file.file_size
                    filename = doc_file.filename
                
                file_elem.set('ID', f'file_{file_id}')
                file_elem.set('MIMETYPE', content_type or 'application/octet-stream')
                file_elem.set('SIZE', str(file_size))
                
                if doc_file.checksum_md5:
                    file_elem.set('CHECKSUM', doc_file.checksum_md5)
                    file_elem.set('CHECKSUMTYPE', 'MD5')
                
                # File location
                flocat = ET.SubElement(file_elem, f"{{{self.namespaces['mets']}}}FLocat")
                flocat.set('LOCTYPE', 'URL')
                flocat.set(f"{{{self.namespaces['xlink']}}}href", f"files/{filename}")
                
                # Technical metadata for this file
                if any([doc_file.image_width, doc_file.image_height, doc_file.bits_per_sample]):
                    tech_md_ref = ET.SubElement(file_elem, f"{{{self.namespaces['mets']}}}techMD")
                    tech_md_ref.set('ID', f'tech_file_{file_id}')
                    
                    md_wrap = ET.SubElement(tech_md_ref, f"{{{self.namespaces['mets']}}}mdWrap")
                    md_wrap.set('MDTYPE', 'OTHER')
                    md_wrap.set('OTHERMDTYPE', 'MIX')
                    
                    xml_data = ET.SubElement(md_wrap, f"{{{self.namespaces['mets']}}}xmlData")
                    mix = ET.SubElement(xml_data, f"{{{self.namespaces['mix']}}}mix")
                    
                    if doc_file.image_width or doc_file.image_height:
                        img_char = ET.SubElement(mix, f"{{{self.namespaces['mix']}}}ImageCharacteristics")
                        img_dim = ET.SubElement(img_char, f"{{{self.namespaces['mix']}}}ImageDimensions")
                        
                        if doc_file.image_width:
                            width = ET.SubElement(img_dim, f"{{{self.namespaces['mix']}}}imageWidth")
                            width.text = str(doc_file.image_width)
                        
                        if doc_file.image_height:
                            height = ET.SubElement(img_dim, f"{{{self.namespaces['mix']}}}imageHeight")
                            height.text = str(doc_file.image_height)
    
    def _add_structural_map(self, root: ET.Element, document: Document):
        """Add structural map organizing the document structure"""
        struct_map = ET.SubElement(root, f"{{{self.namespaces['mets']}}}structMap")
        struct_map.set('TYPE', 'LOGICAL')
        
        # Main document div
        div = ET.SubElement(struct_map, f"{{{self.namespaces['mets']}}}div")
        div.set('TYPE', document.document_type or 'Document')
        div.set('DMDID', f'dmd_{document.id}')
        div.set('ADMID', f'amd_{document.id}')
        
        if document.title:
            div.set('LABEL', document.title)
        
        # Add files in sequence
        sorted_files = sorted(document.document_files, 
                            key=lambda x: x.sequence_number or 0)
        
        for doc_file in sorted_files:
            file_div = ET.SubElement(div, f"{{{self.namespaces['mets']}}}div")
            file_div.set('TYPE', 'page' if doc_file.file_use == 'ARCHIVE' else 'file')
            
            if doc_file.file_label:
                file_div.set('LABEL', doc_file.file_label)
            
            if doc_file.sequence_number:
                file_div.set('ORDER', str(doc_file.sequence_number))
            
            # File pointer
            fptr = ET.SubElement(file_div, f"{{{self.namespaces['mets']}}}fptr")
            
            # Handle both database objects and schema objects
            if hasattr(doc_file, 'file'):
                # Database object with relationships
                file_id = doc_file.file.id
            else:
                # Schema object (DocumentFileSchema)
                file_id = doc_file.file_id
                
            fptr.set('FILEID', f'file_{file_id}')
    
    def _indent(self, elem, level=0):
        """Add indentation for pretty printing"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
