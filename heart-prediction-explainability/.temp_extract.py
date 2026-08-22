import json
import base64
import os

os.chdir(r'C:\Users\gyanr\gyan-python-workspace\ml-capstones\heart-prediction-explainability')

with open('dsc-680-heart_disease_prediction.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

image_num = 0
image_metadata = []

for cell_idx, cell in enumerate(nb['cells']):
    if cell.get('outputs'):
        for output_idx, output in enumerate(cell['outputs']):
            if output.get('data', {}).get('image/png'):
                image_num += 1
                
                # Get markdown/code context
                context = ""
                if cell['cell_type'] == 'code':
                    source = ''.join(cell['source'])
                    # Extract first meaningful line
                    for line in source.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            context = line[:100]
                            break
                elif cell['cell_type'] == 'markdown':
                    source = ''.join(cell['source'])
                    context = source[:100].replace('\n', ' ')
                
                # Save image
                img_data = base64.b64decode(output['data']['image/png'])
                img_path = f'.temp_images/image_{image_num}.png'
                with open(img_path, 'wb') as img_file:
                    img_file.write(img_data)
                
                image_metadata.append({
                    'num': image_num,
                    'cell': cell_idx,
                    'context': context,
                    'path': img_path
                })
                
                print(f"Image {image_num}: Cell {cell_idx}")
                print(f"  Context: {context}")
                print()

print(f"\nTotal images extracted: {image_num}")
