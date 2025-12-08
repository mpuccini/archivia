# XML Security - defusedxml Usage Note

## Why Standard ElementTree for Creating XML?

In this application, we use **standard `xml.etree.ElementTree`** for creating XML (METS generation), not `defusedxml`.

### Reasoning:

1. **Creating XML is Safe**: There's no security risk in creating XML from our controlled data
2. **defusedxml is for Parsing**: The security risk (XXE attacks) only exists when **parsing** untrusted XML input
3. **API Compatibility**: Standard ElementTree has full API support for creating XML

### Where We Use What:

**Standard ElementTree (`xml.etree.ElementTree`):**
- ✅ `mets_generator.py` - Creating METS XML from database records
- ✅ `mets_validation.py` - Creating METS XML from form data

**Why it's safe:**
- We control all the data being put into the XML
- We use `html.escape()` to sanitize user input before XML insertion
- No external entities or DTDs are being processed

**When to Use defusedxml:**
- ❌ We don't currently parse any user-uploaded XML files
- ✅ If we ever add functionality to parse XML files uploaded by users, use defusedxml

### Security Measures in Place:

1. **Text Sanitization**: All user input is escaped with `html.escape()` before insertion
   ```python
   title.text = self._sanitize_text(form_data['title'])
   ```

2. **No XML Parsing**: We only CREATE XML, we don't parse user-provided XML
   ```python
   # We do this (safe):
   xml_str = ET.tostring(root, encoding='unicode')

   # We don't do this:
   # tree = ET.parse(user_file)  # Would need defusedxml
   ```

3. **Controlled Schema**: All XML structure is defined by us, not user input

### If We Ever Need to Parse XML:

```python
# DON'T do this:
import xml.etree.ElementTree as ET
tree = ET.parse(uploaded_file)  # UNSAFE!

# DO this instead:
import defusedxml.ElementTree as DefusedET
tree = DefusedET.parse(uploaded_file)  # SAFE!
```

### Summary:

**Current State**: ✅ Secure
- Creating XML: Standard ElementTree (correct choice)
- User input: Sanitized with html.escape()
- No XML parsing from users: No XXE risk

**Future Consideration**:
If you add XML file upload/parsing functionality, use `defusedxml` for parsing.
