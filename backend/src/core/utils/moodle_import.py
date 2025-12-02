import csv
import io
from core.models import Competency, CriticalLearning

def import_moodle_csv(file_content_bytes):
    """
    Parses a Moodle Competency Framework CSV and imports it into the database.

    Expected CSV columns (Moodle standard or simplified):
    - Parent ID number (optional, indicates hierarchy)
    - ID number (required, unique identifier)
    - Short name (required)
    - Description (optional)

    Mapping Strategy:
    - Items with no 'Parent ID number' (or empty) are treated as Competencies.
    - Items with a 'Parent ID number' referring to a Competency are treated as Critical Learnings (AC).
    - Moodle 'ID number' maps to SIBUT 'short_code' (Competency) or 'code' (AC).
    """

    decoded_file = file_content_bytes.decode('utf-8-sig').splitlines()
    reader = csv.DictReader(decoded_file)

    # Normalize headers to lowercase and remove spaces for easier matching
    # Map common variations
    field_map = {}
    for field in reader.fieldnames:
        clean = field.lower().strip().replace(' ', '')
        if 'parentid' in clean:
            field_map['parent_id'] = field
        elif 'idnumber' in clean:
            field_map['id_number'] = field
        elif 'shortname' in clean:
            field_map['short_name'] = field
        elif 'description' in clean:
            field_map['description'] = field

    if 'id_number' not in field_map or 'short_name' not in field_map:
        raise ValueError("CSV must contain 'ID number' and 'Short name' columns.")

    # Pass 1: Collect all rows and identify hierarchies
    rows = list(reader)

    competencies_map = {} # ID Number -> Competency Object
    acs_pending = []

    # First pass: Create/Update Competencies (Roots)
    for row in rows:
        parent_id = row.get(field_map.get('parent_id', ''), '').strip()
        id_number = row.get(field_map['id_number'], '').strip()
        short_name = row.get(field_map['short_name'], '').strip()
        description = row.get(field_map.get('description', ''), '').strip()

        if not id_number:
            continue

        if not parent_id:
            # It's a Competency
            # Attempt to extract color? Default to blue.
            comp, created = Competency.objects.update_or_create(
                short_code=id_number,
                defaults={
                    'name': short_name,
                    'description': description,
                    'color_hex': '#3b82f6' # Default
                }
            )
            competencies_map[id_number] = comp
        else:
            # It's likely an AC, strictly if parent is in map (handled in pass 2) or we assume it will be.
            acs_pending.append(row)

    # Second pass: Create/Update ACs
    for row in acs_pending:
        parent_id = row.get(field_map.get('parent_id', ''), '').strip()
        id_number = row.get(field_map['id_number'], '').strip()
        short_name = row.get(field_map['short_name'], '').strip() # In Moodle AC name might be in shortname
        description = row.get(field_map.get('description', ''), '').strip()

        # In SIBUT, AC has 'code' and 'description'. 'Short name' usually contains the text.
        # Description in Moodle might be long text.
        # Let's use 'short_name' as description if 'description' is empty, or vice versa.
        # SIBUT Model: code (AC1.1), description (Text), level (int)

        # Logic to infer Level from code (AC1.1 -> 1)
        level = 1
        # Try to parse level from ID Number (e.g., AC11.01)
        # Assuming format AC<Level><Comp>...
        if id_number.upper().startswith('AC'):
             try:
                 # Remove AC prefix
                 digits = id_number[2:]
                 if digits and digits[0].isdigit():
                     level = int(digits[0])
             except:
                 pass

        # Parent mapping
        if parent_id in competencies_map:
            parent_comp = competencies_map[parent_id]

            # Use short_name as description if it looks like text, or description if available.
            ac_desc = description if description else short_name

            CriticalLearning.objects.update_or_create(
                code=id_number,
                competency=parent_comp,
                defaults={
                    'description': ac_desc,
                    'level': level
                }
            )

    return {
        "competencies_count": len(competencies_map),
        "acs_count": len(acs_pending)
    }
