import re

# Read the content
with open('adder2.cif', 'r', encoding='windows-1251') as file:
    file_content = file.read()

# Extracting the layer types
layer_types = re.findall(r'L (\w+);', file_content)

# Remove duplicates
seen = set()
unique_layer_types = []
for layer in layer_types:
    if layer not in seen:
        unique_layer_types.append(layer)
        seen.add(layer)

output = ' '.join(unique_layer_types)
print(output)
