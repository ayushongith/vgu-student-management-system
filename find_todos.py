import os

exclude = ['venv', 'staticfiles', 'media', '.git', 'static', '__pycache__']
for root, dirs, files in os.walk(r'd:\Projects\Student management system'):
    dirs[:] = [d for d in dirs if d not in exclude]
    for file in files:
        if file.endswith('.py') or file.endswith('.html'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if 'TODO' in line or line.strip() == 'pass':
                            print(f"{filepath}:{i+1}: {line.strip()}")
            except Exception as e:
                pass
