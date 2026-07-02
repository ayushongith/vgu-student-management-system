import os
import re

exclude = ['venv', 'staticfiles', 'media', '.git', 'static', '__pycache__']
broken_links = 0
for root, dirs, files in os.walk(r'd:\Projects\Student management system'):
    dirs[:] = [d for d in dirs if d not in exclude]
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'href="#"' in content:
                    broken_links += 1
                    print(f"Broken link in {filepath}")

print(f"Total files with broken links: {broken_links}")
