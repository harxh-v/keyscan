import yaml
from pathlib import Path
from typing import List, Optional
from pydantic import ValidationError
from keyscan.utils.models import TemplateModel

def load_template(filepath: Path) -> Optional[TemplateModel]:
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            return TemplateModel(**data)
    except yaml.YAMLError as e:
        # Avoid print here, use logger when caller catches this
        # raise ValueError(f"YAML parsing error in {filepath}: {e}")
        pass
    except ValidationError as e:
        # raise ValueError(f"Template validation error in {filepath}: {e}")
        pass
    return None

def load_all_templates(templates_dir: Path) -> List[TemplateModel]:
    templates = []
    if not templates_dir.exists() or not templates_dir.is_dir():
        return templates
        
    for file in templates_dir.glob("*.yaml"):
        template = load_template(file)
        if template:
            templates.append(template)
            
    # Also support .yml
    for file in templates_dir.glob("*.yml"):
        template = load_template(file)
        if template:
            templates.append(template)
            
    return templates
