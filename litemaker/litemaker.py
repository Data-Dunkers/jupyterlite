import os
import json

current_directory = os.getcwd()
if 'litemaker' not in current_directory:
    os.chdir('litemaker')

# create a folder called 'modified' if it doesn't exist
if not os.path.exists('modified'):
    os.makedirs('modified')

notebooks = []
for dirpath, _, filenames in os.walk('.'):
    for filename in filenames:
        if filename.endswith('.ipynb'):
            notebooks.append(os.path.join(dirpath, filename))

for notebook_name_and_path in notebooks:
    notebook_name = notebook_name_and_path.split('/')[-1]
    print(notebook_name)
    original_file = open(notebook_name_and_path, 'r', encoding='utf-8')
    original_content = original_file.read()
    original_file.close()
    notebook_data = json.loads(original_content)
    for cell in notebook_data['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            for i, line in enumerate(source):
                if 'read_csv' in line:
                    new_line = line.replace("pd.read_csv(", "pd.read_csv(pyodide_http.open_url(").replace(")", "))")
                    cell['source'] = source[:i] + [new_line] + source[i+1:]
    new_imports = ["import piplite, pyodide_http, pyodide\n", "await piplite.install(['pandas', 'plotly', 'nbformat', 'statsmodels'])\n", "pyodide_http.patch_all()\n"]
    for cell in notebook_data['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            for i, line in enumerate(source):
                if 'import pandas as pd' in line:
                    cell['source'] = source[:i] + new_imports + source[i:]
    modified_content = json.dumps(notebook_data, indent=1)
    modified_file = open(f'modified/{notebook_name}', 'w', encoding='utf-8')
    modified_file.write(modified_content)
    modified_file.close()

print("All notebooks have been modified for JupyterLite and saved in the 'modified' folder.")