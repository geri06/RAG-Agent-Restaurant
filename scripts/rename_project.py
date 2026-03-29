import os
import re

directories = ['agent', 'docs', 'dashboard/src', 'scripts']
files_to_check = ['README.md', 'pyproject.toml']

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return # Skip binary or non-utf8 files

    # Special case for "Company Digital Assistant" -> "Company Digital Assistant"
    # and "la asistente" / "Asistente" since Company Digital Assistant is female, "Company Digital Assistant" is generic.
    original = content
    content = content.replace("Company Digital Assistant", "Company Digital Assistant")
    content = content.replace('Eres "Company Digital Assistant", el asistente de IA interno de', 'Eres "Company Digital Assistant", el asistente de IA interno de')
    
    # Generic replacements
    # Need to be careful with casing
    
    # CompanyState -> CompanyState
    content = content.replace("CompanyState", "CompanyState")
    
    # Company-Flow -> Company-Flow
    content = content.replace("Company-Flow", "Company-Flow")
    content = content.replace("company-flow", "company-flow")
    
    # Generic Company -> Company
    content = content.replace("Company", "Company")
    content = content.replace("company", "company")
    content = content.replace("COMPANY", "COMPANY")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for d in directories:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith(('.py', '.md', '.tsx', '.css', '.toml')):
                replace_in_file(os.path.join(root, file))

for file in files_to_check:
    if os.path.exists(file):
        replace_in_file(file)
