"""
METS ECO-MiC Validation Service
Service for validating METS XML files against ECO-MiC 1.1 standard using external API
"""

import httpx
import html
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException

# Set up logging
logger = logging.getLogger(__name__)

# Note: We use standard ElementTree for creating XML (safe)
# If we need to parse user-provided XML, we would use defusedxml


class METSValidationService:
    """Service for validating METS XML against ECO-MiC 1.1 standard"""

    def __init__(self):
        self.validation_api_url = "https://validavmetsecomic.prod.os01.ocp.cineca.it/api/v1/checkmetsecomic/files"
        self.timeout = 30.0  # seconds

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """Sanitize text for safe inclusion in XML"""
        if not text:
            return ""
        # HTML escape to prevent XML injection
        return html.escape(str(text), quote=True)
    
    async def validate_mets_xml(self, xml_content: str, filename: str = "mets.xml") -> Dict[str, Any]:
        """
        Validate METS XML content against ECO-MiC 1.1 standard
        
        Args:
            xml_content: The METS XML content as string
            filename: Optional filename for the validation (default: mets.xml)
            
        Returns:
            Dict containing validation results with structure:
            {
                "valid": bool,
                "response": dict,  # Original API response
                "errors": list,    # Simplified error list for UI
                "summary": str     # Human-readable summary
            }
        """
        try:
            # Prepare file data for multipart form
            files = {
                "files": (filename, xml_content.encode('utf-8'), "application/xml")
            }

            logger.info(f"Validating METS XML against Cineca API: {filename}")
            logger.debug(f"XML content length: {len(xml_content)} bytes")

            # Make request to validation API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.validation_api_url,
                    files=files
                )

            logger.info(f"Cineca API response: HTTP {response.status_code}")
            
            # Process response based on status code
            if response.status_code == 200:
                # Validation successful
                api_response = response.json()
                return self._process_success_response(api_response)

            elif response.status_code == 412:
                # Validation failed
                api_response = response.json()
                return self._process_error_response(api_response)

            else:
                # Unexpected status code - log response details
                logger.error(f"Cineca API returned unexpected status code: {response.status_code}")

                error_detail = f"Validation service error: HTTP {response.status_code}"
                try:
                    error_body = response.text
                    logger.error(f"Cineca API response body: {error_body}")
                    if error_body:
                        error_detail += f" - Response: {error_body[:500]}"  # Limit to 500 chars
                except Exception as e:
                    logger.error(f"Failed to read response body: {e}")

                raise HTTPException(
                    status_code=500,
                    detail=error_detail
                )
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=408,
                detail="Validation service timeout. Please try again later."
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to connect to validation service: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPException without wrapping
            raise
        except Exception as e:
            # Log the full exception for debugging
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Validation service error: {str(e)}"
            )
    
    def _process_success_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process successful validation response (HTTP 200)"""
        return {
            "valid": True,
            "response": api_response,
            "errors": [],
            "summary": "METS XML è conforme al standard ECO-MiC 1.1"
        }
    
    def _process_error_response(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process failed validation response (HTTP 412)"""
        errors = []
        
        # Extract errors from response
        if "listaMessaggi" in api_response:
            # Direct error list in response
            for error in api_response["listaMessaggi"]:
                errors.append(self._format_error(error))
        elif "filesResponse" in api_response:
            # Errors nested in filesResponse
            for file_response in api_response["filesResponse"]:
                if "listaMessaggi" in file_response:
                    for error in file_response["listaMessaggi"]:
                        errors.append(self._format_error(error))
        
        summary = f"METS XML non conforme: {len(errors)} errore/i trovato/i"
        
        return {
            "valid": False,
            "response": api_response,
            "errors": errors,
            "summary": summary
        }
    
    def _format_error(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Format error for UI display"""
        return {
            "id": error.get("idErrore", "N/A"),
            "type": error.get("tipologiaErrore", "Unknown"),
            "description": error.get("descrizioneErrore", "No description"),
            "tag": error.get("tagCoinvolto", "N/A"),
            "location": error.get("fileLocationDetail", "N/A")
        }
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Get a human-readable summary of validation results"""
        if validation_result["valid"]:
            return "✅ METS XML validato con successo secondo lo standard ECO-MiC 1.1"
        else:
            error_count = len(validation_result["errors"])
            if error_count == 1:
                return "❌ Validazione fallita: 1 errore trovato"
            else:
                return f"❌ Validazione fallita: {error_count} errori trovati"
    
    def generate_mets_xml_from_form_data(self, form_data: Dict[str, Any]) -> str:
        """Generate METS XML from form data for validation purposes"""
        # Create a minimal METS structure for validation
        # This is a simplified version for validation only
        
        namespaces = {
            'mets': 'http://www.loc.gov/METS/',
            'mods': 'http://www.loc.gov/mods/v3',
            'mix': 'http://www.loc.gov/mix/v20',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'dct': 'http://purl.org/dc/terms/'
        }
        
        # Register namespaces
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)
        
        # Create root METS element
        mets_attrs = {
            'xmlns:mets': namespaces['mets'],
            'xmlns:mods': namespaces['mods'],
            'xmlns:mix': namespaces['mix'],
            'xmlns:dct': namespaces['dct'],
            'xmlns:xlink': namespaces['xlink'],
            'xmlns:xsi': namespaces['xsi'],
            'xsi:schemaLocation': 'http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd',
            'OBJID': form_data.get('logical_id', 'unknown'),
            'TYPE': form_data.get('document_type', 'Document'),
            'PROFILE': 'http://www.loc.gov/mets/profiles/00000040.xml'
        }
        
        root = ET.Element(f"{{{namespaces['mets']}}}mets", mets_attrs)
        
        # Add header
        self._add_mets_header_from_form(root, form_data, namespaces)
        
        # Add descriptive metadata
        self._add_descriptive_metadata_from_form(root, form_data, namespaces)
        
        # Add basic file section (empty for validation)
        self._add_minimal_file_section(root, namespaces)
        
        # Add basic structural map
        self._add_minimal_structural_map(root, form_data, namespaces)
        
        # Convert to string with pretty formatting
        self._indent_xml(root)
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
    
    def _add_mets_header_from_form(self, root: ET.Element, form_data: Dict[str, Any], namespaces: Dict[str, str]):
        """Add METS header from form data"""
        header = ET.SubElement(root, f"{{{namespaces['mets']}}}metsHdr")
        header.set('CREATEDATE', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        header.set('LASTMODDATE', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        
        # Agent - Archive
        if form_data.get('archive_name'):
            agent = ET.SubElement(header, f"{{{namespaces['mets']}}}agent")
            agent.set('ROLE', 'CUSTODIAN')
            agent.set('TYPE', 'ORGANIZATION')
            
            name = ET.SubElement(agent, f"{{{namespaces['mets']}}}name")
            name.text = self._sanitize_text(form_data['archive_name'])

            if form_data.get('archive_contact'):
                note = ET.SubElement(agent, f"{{{namespaces['mets']}}}note")
                note.text = self._sanitize_text(form_data['archive_contact'])
    
    def _add_descriptive_metadata_from_form(self, root: ET.Element, form_data: Dict[str, Any], namespaces: Dict[str, str]):
        """Add descriptive metadata (MODS) from form data"""
        dmd_sec = ET.SubElement(root, f"{{{namespaces['mets']}}}dmdSec")
        dmd_sec.set('ID', 'dmd_1')
        
        md_wrap = ET.SubElement(dmd_sec, f"{{{namespaces['mets']}}}mdWrap")
        md_wrap.set('MDTYPE', 'MODS')
        
        xml_data = ET.SubElement(md_wrap, f"{{{namespaces['mets']}}}xmlData")
        mods = ET.SubElement(xml_data, f"{{{namespaces['mods']}}}mods")
        
        # Title
        if form_data.get('title'):
            title_info = ET.SubElement(mods, f"{{{namespaces['mods']}}}titleInfo")
            title = ET.SubElement(title_info, f"{{{namespaces['mods']}}}title")
            title.text = self._sanitize_text(form_data['title'])

        # Identifier
        if form_data.get('logical_id'):
            identifier = ET.SubElement(mods, f"{{{namespaces['mods']}}}identifier")
            identifier.set('type', 'logical')
            identifier.text = self._sanitize_text(form_data['logical_id'])

        if form_data.get('conservative_id'):
            identifier = ET.SubElement(mods, f"{{{namespaces['mods']}}}identifier")
            identifier.set('type', 'conservative')
            identifier.text = self._sanitize_text(form_data['conservative_id'])

        # Abstract/Description
        if form_data.get('description'):
            abstract = ET.SubElement(mods, f"{{{namespaces['mods']}}}abstract")
            abstract.text = self._sanitize_text(form_data['description'])

        # Language
        if form_data.get('language'):
            language_elem = ET.SubElement(mods, f"{{{namespaces['mods']}}}language")
            language_term = ET.SubElement(language_elem, f"{{{namespaces['mods']}}}languageTerm")
            language_term.set('type', 'text')
            language_term.text = self._sanitize_text(form_data['language'])

        # Location/Geographic subject
        if form_data.get('location'):
            subject = ET.SubElement(mods, f"{{{namespaces['mods']}}}subject")
            geographic = ET.SubElement(subject, f"{{{namespaces['mods']}}}geographic")
            geographic.text = self._sanitize_text(form_data['location'])
        
        # Physical description
        if form_data.get('document_type') or form_data.get('total_pages'):
            phys_desc = ET.SubElement(mods, f"{{{namespaces['mods']}}}physicalDescription")
            
            if form_data.get('document_type'):
                form_elem = ET.SubElement(phys_desc, f"{{{namespaces['mods']}}}form")
                form_elem.text = self._sanitize_text(form_data['document_type'])

            if form_data.get('total_pages'):
                extent = ET.SubElement(phys_desc, f"{{{namespaces['mods']}}}extent")
                extent.text = self._sanitize_text(f"{form_data['total_pages']} pages")
    
    def _add_minimal_file_section(self, root: ET.Element, namespaces: Dict[str, str]):
        """Add minimal file section for validation"""
        file_sec = ET.SubElement(root, f"{{{namespaces['mets']}}}fileSec")
        file_grp = ET.SubElement(file_sec, f"{{{namespaces['mets']}}}fileGrp")
        file_grp.set('USE', 'ARCHIVE')
    
    def _add_minimal_structural_map(self, root: ET.Element, form_data: Dict[str, Any], namespaces: Dict[str, str]):
        """Add minimal structural map for validation"""
        struct_map = ET.SubElement(root, f"{{{namespaces['mets']}}}structMap")
        struct_map.set('TYPE', 'logical')
        
        div = ET.SubElement(struct_map, f"{{{namespaces['mets']}}}div")
        div.set('TYPE', form_data.get('document_type', 'Document'))
        div.set('LABEL', form_data.get('title', 'Untitled Document'))
        div.set('DMDID', 'dmd_1')
    
    def _indent_xml(self, elem, level=0):
        """Add indentation for pretty printing XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i