import json

def parse_schema():
    with open('raw_schema.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    schema_list = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Replace multiple spaces with a single tab for easier splitting if tabs aren't present
        import re
        # The copy-paste often converts tabs to spaces or weird unicode spaces
        # The prompt has " " which is an Em Space (U+2003)
        parts = re.split(r'\u2003+|\\t|\t', line)
        if len(parts) >= 8:
            schema_list.append({
                "id": parts[0].strip(),
                "category": parts[1].strip(),
                "description": parts[2].strip(),
                "parameter": parts[3].strip(),
                "content_type": parts[4].strip(),
                "min": parts[5].strip(),
                "max": parts[6].strip(),
                "ac": parts[7].strip()
            })
            
    with open('schema.json', 'w', encoding='utf-8') as f:
        json.dump(schema_list, f, indent=4)

if __name__ == '__main__':
    parse_schema()
