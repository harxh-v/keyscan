import os
import re
import yaml
from pathlib import Path

def parse_keyhacks(md_file: str, out_dir: str):
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by "## "
    sections = content.split("## ")
    
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    count = 0
    
    for section in sections[1:]:
        lines = section.strip().split("\n")
        header = lines[0].strip()
        
        # Parse name: [Name](url) or Name
        name_match = re.search(r"\[([^\]]+)\]", header)
        if name_match:
            name = name_match.group(1)
        else:
            name = header
            
        # Clean up name for ID
        template_id = name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")
        
        # Find curl blocks
        curl_match = re.search(r"```(?:bash)?\s+(curl[^\`]+)\s+```", section, re.IGNORECASE | re.MULTILINE)
        if not curl_match:
            continue
            
        curl_cmd = curl_match.group(1).strip()
        
        # Simple parser for curl
        method = "GET"
        if "-X POST" in curl_cmd or "-XPOST" in curl_cmd or "--request POST" in curl_cmd:
            method = "POST"
        elif "-X PUT" in curl_cmd:
            method = "PUT"
            
        # Extract headers
        headers = {}
        header_matches = re.finditer(r"(?:-H|--header)\s+[\"']([^:]+):\s*([^\"']+)[\"']", curl_cmd)
        for hm in header_matches:
            # Replace placeholder Tokens with {{key}}
            val = hm.group(2)
            val = re.sub(r'(TOKEN_HERE|<TOKEN>|YOUR_API_KEY|KEY_HERE|<KEY_HERE>|\[ACCESS_TOKEN\]|\[API-KEY-HERE\])', '{{key}}', val, flags=re.IGNORECASE)
            headers[hm.group(1)] = val
            
        # Check basic auth
        auth_match = re.search(r"(?:-u|--user)\s+[\"']?([^:\"']+:[^\"'\s]*)[\"']?", curl_cmd)
        if auth_match:
            val = auth_match.group(1)
            # If it's token:, we want to put {{key}}: giving basic auth
            val = re.sub(r'(TOKEN_HERE|API_KEY_HERE|YOUR_API_KEY)', '{{key}}', val, flags=re.IGNORECASE)
            headers["Authorization"] = f"Basic {{{{key_base64}}}}" # Approximating Basic, or just using the string for now. Actually, if curl uses -u, it automatically base64 encodes it.
            # For simplicity in keyscan, if we see -u, we add {{key_base64}} or similar if it's token:, wait, let's just make authorization custom if we want
            # To be simple:
            headers["Authorization"] = "Basic {{key_base64}}"
            
        # Extract Body
        body_match = re.search(r"(?:-d|--data|--data-binary)\s+('[^']+'|\"[^\"]+\")", curl_cmd)
        body = None
        if body_match:
            body = body_match.group(1).strip("'\"")
            
        # Extract URL
        url_match = re.search(r"(?:curl.*?)(https?://[^\s\"']+)", curl_cmd)
        url = url_match.group(1) if url_match else None
        
        if not url:
            continue
            
        # Replace placeholders in URL
        url = re.sub(r'(TOKEN_HERE|<TOKEN>|YOUR_API_KEY|KEY_HERE|<KEY_HERE>|{keyhere})', '{{key}}', url, flags=re.IGNORECASE)

        template = {
            "id": template_id,
            "info": {
                "name": name,
                "author": "keyhacks_generator"
            },
            "requests": [
                {
                    "method": method,
                    "url": url,
                    "headers": headers
                }
            ],
            "matchers": [
                {
                    "type": "status",
                    "status": [200]
                }
            ]
        }
        
        if body:
            template["requests"][0]["body"] = body

        # Write to yaml
        out_path = Path(out_dir) / f"{template_id}.yaml"
        # Only write if it doesn't already exist to avoid overwriting hand-crafted ones
        if not out_path.exists():
            with open(out_path, "w") as f:
                yaml.dump(template, f, sort_keys=False)
            count += 1
            
    print(f"Generated {count} templates.")

if __name__ == "__main__":
    md_file = r"C:\Users\harsh\.gemini\antigravity\brain\9d17c305-bf2a-4295-89d1-5d6e32ccc44c\.system_generated\steps\120\content.md"
    out_dir = r"c:\Drive\keyscan\templates"
    parse_keyhacks(md_file, out_dir)
