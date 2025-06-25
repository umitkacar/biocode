#!/usr/bin/env python3
"""
Generate API documentation from OpenAPI spec
"""
import os
import json
import yaml
from pathlib import Path

# Try to use spectacle-docs if available
try:
    import subprocess
    
    def generate_html_docs():
        """Generate HTML documentation using spectacle-docs"""
        spec_path = Path("docs/api/openapi.yaml")
        output_path = Path("docs/api/index.html")
        
        if not spec_path.exists():
            print(f"Error: {spec_path} not found")
            return False
            
        try:
            # Install spectacle-docs if not available
            subprocess.run(["npm", "install", "-g", "spectacle-docs"], check=False)
            
            # Generate documentation
            subprocess.run([
                "spectacle", 
                "-d", str(spec_path),
                "-t", str(output_path.parent)
            ], check=True)
            
            print(f"✅ API documentation generated at {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error generating docs with spectacle: {e}")
            return False
            
except ImportError:
    pass

def generate_markdown_docs():
    """Generate Markdown documentation from OpenAPI spec"""
    spec_path = Path("docs/api/openapi.yaml")
    output_path = Path("docs/api/API_REFERENCE.md")
    
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    md_content = f"""# BioCode API Reference

{spec['info']['description']}

**Version:** {spec['info']['version']}

## Base URL

```
{spec['servers'][0]['url']}
```

## Endpoints

"""
    
    # Group endpoints by tag
    endpoints_by_tag = {}
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete']:
                tags = details.get('tags', ['Other'])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'details': details
                    })
    
    # Generate documentation for each tag
    for tag, endpoints in endpoints_by_tag.items():
        md_content += f"\n### {tag}\n\n"
        
        for endpoint in endpoints:
            details = endpoint['details']
            md_content += f"#### {details['summary']}\n\n"
            md_content += f"```\n{endpoint['method']} {endpoint['path']}\n```\n\n"
            
            if 'description' in details:
                md_content += f"{details['description']}\n\n"
            
            # Parameters
            if 'parameters' in details:
                md_content += "**Parameters:**\n\n"
                md_content += "| Name | Type | Required | Description |\n"
                md_content += "|------|------|----------|-------------|\n"
                
                for param in details['parameters']:
                    required = "Yes" if param.get('required', False) else "No"
                    param_type = param.get('schema', {}).get('type', 'string')
                    md_content += f"| {param['name']} | {param_type} | {required} | {param.get('description', '')} |\n"
                
                md_content += "\n"
            
            # Request body
            if 'requestBody' in details:
                md_content += "**Request Body:**\n\n"
                content = details['requestBody'].get('content', {})
                if 'application/json' in content:
                    schema_ref = content['application/json'].get('schema', {}).get('$ref', '')
                    if schema_ref:
                        schema_name = schema_ref.split('/')[-1]
                        md_content += f"See schema: `{schema_name}`\n\n"
                    
                    example = content['application/json'].get('example')
                    if example:
                        md_content += "Example:\n```json\n"
                        md_content += json.dumps(example, indent=2)
                        md_content += "\n```\n\n"
            
            # Responses
            if 'responses' in details:
                md_content += "**Responses:**\n\n"
                for code, response in details['responses'].items():
                    md_content += f"- `{code}`: {response.get('description', '')}\n"
                md_content += "\n"
            
            md_content += "---\n\n"
    
    # Add schemas section
    md_content += "\n## Schemas\n\n"
    
    for schema_name, schema in spec.get('components', {}).get('schemas', {}).items():
        md_content += f"### {schema_name}\n\n"
        
        if 'properties' in schema:
            md_content += "| Property | Type | Description |\n"
            md_content += "|----------|------|-------------|\n"
            
            for prop_name, prop_details in schema['properties'].items():
                prop_type = prop_details.get('type', 'object')
                if 'format' in prop_details:
                    prop_type += f" ({prop_details['format']})"
                description = prop_details.get('description', '')
                md_content += f"| {prop_name} | {prop_type} | {description} |\n"
            
            md_content += "\n"
    
    # Write markdown file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    print(f"✅ Markdown API documentation generated at {output_path}")

def generate_postman_collection():
    """Generate Postman collection from OpenAPI spec"""
    spec_path = Path("docs/api/openapi.yaml")
    output_path = Path("docs/api/biocode.postman_collection.json")
    
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Create Postman collection
    collection = {
        "info": {
            "name": spec['info']['title'],
            "description": spec['info']['description'],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Add endpoints
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete']:
                item = {
                    "name": details['summary'],
                    "request": {
                        "method": method.upper(),
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}{path}",
                            "host": ["{{base_url}}"],
                            "path": path.strip('/').split('/')
                        }
                    }
                }
                
                # Add request body if present
                if 'requestBody' in details:
                    content = details['requestBody'].get('content', {})
                    if 'application/json' in content:
                        example = content['application/json'].get('example', {})
                        item['request']['body'] = {
                            "mode": "raw",
                            "raw": json.dumps(example, indent=2),
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                
                collection['item'].append(item)
    
    # Add variables
    collection['variable'] = [
        {
            "key": "base_url",
            "value": spec['servers'][0]['url'],
            "type": "string"
        }
    ]
    
    # Write collection
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Postman collection generated at {output_path}")

if __name__ == "__main__":
    print("🔧 Generating API documentation...")
    
    # Generate all formats
    generate_markdown_docs()
    generate_postman_collection()
    
    # Try to generate HTML docs
    try:
        generate_html_docs()
    except:
        print("ℹ️  Install spectacle-docs for HTML documentation: npm install -g spectacle-docs")
    
    print("\n✨ API documentation generation complete!")