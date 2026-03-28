import httpx
import re
import base64
from typing import Dict, Any, List
from keyscan.utils.models import TemplateModel, ValidationResult, MatcherModel

def map_variables(content: str, key: str) -> str:
    """Replace {{key}} and {{key_base64}} with the actual key in text"""
    if not content:
        return content
    content = content.replace("{{key}}", key)
    
    parts = key.split(":") if ":" in key else [key]
    
    # Dynamically find requested key parts
    part_matches = re.finditer(r"\{\{key_part(\d+)\}\}", content)
    for match in part_matches:
        i = int(match.group(1))
        if i >= len(parts):
            raise ValueError(f"Template requires key part {i} but input string is too short.")
        content = content.replace(match.group(0), parts[i])
            
    if "{{key_base64}}" in content:
        b64_key = base64.b64encode(key.encode('utf-8')).decode('utf-8')
        content = content.replace("{{key_base64}}", b64_key)
    return content

def dict_map_variables(d: Dict[str, str], key: str) -> Dict[str, str]:
    """Replace {{key}} in dictionary values"""
    return {k: map_variables(v, key) for k, v in d.items()} if d else d

def check_matchers(response: httpx.Response, matchers: List[MatcherModel]) -> bool:
    """
    Check if the response satisfies the given matchers.
    Returns True if valid based on condition (and/or)
    """
    if not matchers:
        return False
        
    results = []
    
    for m in matchers:
        match_success = False
        
        if m.type == "status" and m.status:
            match_success = response.status_code in m.status
            
        elif m.type == "word" and m.words:
            content = response.text
            match_success = any(word in content for word in m.words)
            
        elif m.type == "regex" and m.regex:
            content = response.text
            match_success = any(re.search(expr, content) for expr in m.regex)
            
        results.append(match_success)
        
    # Condition: and, or
    condition = matchers[0].condition if matchers else 'and'
    if condition == 'or':
        return any(results)
    return all(results)


async def validate_key_with_template(client: httpx.AsyncClient, key: str, template: TemplateModel) -> ValidationResult:
    """
    Validates a single key against a single template requests.
    Stops at the first successful matcher set or returns Failure.
    """
    # Create copy of req 
    for req in template.requests:
        try:
            if req.type == "command" and req.command:
                import asyncio
                import os
                
                command = map_variables(req.command, key)
                env = {**os.environ, **dict_map_variables(req.env, key)}
                
                try:
                    proc = await asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        env=env
                    )
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15.0)
                    
                    mock_resp = httpx.Response(
                        status_code=proc.returncode,
                        content=stdout + b"\n" + stderr,
                        request=httpx.Request("GET", "http://localhost")
                    )
                    
                    is_valid = check_matchers(mock_resp, template.matchers)
                    
                    if is_valid:
                        return ValidationResult(
                            key=key,
                            service=template.info.name,
                            status="valid",
                            confidence=1.0,
                            message="Command matchers succeeded."
                        )
                    else:
                        return ValidationResult(
                            key=key,
                            service=template.info.name,
                            status="invalid",
                            confidence=0.5,
                            message=f"Command exit {proc.returncode}"
                        )
                        
                except Exception as e:
                    return ValidationResult(
                        key=key,
                        service=template.info.name,
                        status="unknown",
                        confidence=0.0,
                        message=f"Command failed: {str(e)}"
                    )
                    
            url = map_variables(req.url, key)
            method = map_variables(req.method, key)
            headers = dict_map_variables(req.headers, key)
            body = map_variables(req.body, key)
            
        except ValueError as e:
            # Catch mapping errors such as missing key parts
            return ValidationResult(
                key=key,
                service=template.info.name,
                status="invalid",
                confidence=0.0,
                message=str(e)
            )
            
        try:
            response = await client.request(
                method, 
                url, 
                headers=headers, 
                content=body, 
                timeout=10.0,
                follow_redirects=True
            )
            
            # Check matchers
            is_valid = check_matchers(response, template.matchers)
            
            if is_valid:
                return ValidationResult(
                    key=key,
                    service=template.info.name,
                    status="valid",
                    confidence=1.0,
                    message="Matchers matched successfully."
                )
                
            # Rate limited checking
            if response.status_code == 429:
                return ValidationResult(
                    key=key,
                    service=template.info.name,
                    status="unknown",
                    confidence=0.0,
                    message="Rate limited (429)"
                )
                
            # If forbidden or unauthorized
            if response.status_code in [401, 403]:
                return ValidationResult(
                    key=key,
                    service=template.info.name,
                    status="invalid",
                    confidence=1.0, # Complete confident it's invalid
                    message=f"Access denied ({response.status_code})"
                )
                
        except httpx.RequestError as e:
            return ValidationResult(
                key=key,
                service=template.info.name,
                status="unknown",
                confidence=0.0,
                message=f"Request failed: {str(e)}"
            )

    # Could not determine from matchers and no auth error
    return ValidationResult(
        key=key,
        service=template.info.name,
        status="invalid",
        confidence=0.5,
        message="Did not match valid criteria"
    )
