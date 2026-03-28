import asyncio
import httpx
from typing import List, Dict
from pathlib import Path
from keyscan.utils.models import ValidationResult, TemplateModel
from keyscan.engine.template import load_all_templates
from keyscan.engine.validator import validate_key_with_template
from keyscan.classifiers.analyzer import analyze_key
from rich.progress import Progress, SpinnerColumn, TextColumn
from keyscan.utils.logger import get_logger

log = get_logger("keyscan.scanner")

class Scanner:
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, TemplateModel] = {}
        self.load_templates()
        
    def load_templates(self):
        loaded = load_all_templates(self.templates_dir)
        for val in loaded:
            self.templates[val.info.name] = val
        log.info(f"Loaded {len(self.templates)} templates.")
        
    async def scan_key(self, key: str, client: httpx.AsyncClient) -> List[ValidationResult]:
        """Classify key and run against matching templates"""
        classifications = analyze_key(key)
        results = []
        
        # We take the top probable services with confidence > 0.0
        # If generic, we might want to run against ALL templates?
        # But MVP just runs against the matched ones
        
        to_check = []
        for c in classifications:
            # Match directly by service name mapping
            if c.service in self.templates:
                to_check.append(self.templates[c.service])
        
        # Fallback to general checking if only generic or unknown
        if not to_check:
            # In MVP, if we don't know it, we could try all templates
            # But that might trigger rate limits. 
            # For now, we just skip or report unknown.
            results.append(
                ValidationResult(
                    key=key, 
                    service="Unknown", 
                    status="skipped", 
                    confidence=0.0, 
                    message="No matching template service found based on classification."
                )
            )
            return results
            
        # Run validations concurrently
        tasks = [validate_key_with_template(client, key, t) for t in to_check]
        validation_promises = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in validation_promises:
            if isinstance(res, Exception):
                log.error(f"Error validating key {key}: {res}")
            else:
                results.append(res)
                
        return results
        
    async def scan_keys(self, keys: List[str]) -> List[ValidationResult]:
        all_results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("[green]Scanning keys...", total=len(keys))
            
            async with httpx.AsyncClient() as client:
                for key in keys:
                    key = key.strip()
                    if not key:
                        continue
                    res = await self.scan_key(key, client)
                    all_results.extend(res)
                    progress.advance(task)
                    
        return all_results
