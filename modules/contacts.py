import re
import pandas as pd

def parse_cif_file(file_path, encoding='windows-1251'):
    with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
        cif_content = file.read()
    pattern = re.compile(r'4N (\S+)')
    matches = pattern.findall(cif_content)
    return matches

file_path = 'adder2.cif'

matches = parse_cif_file(file_path, encoding='latin-1')

unique_matches = set(re.sub(r'\d+', '', match) for match in matches)

formatted_matches = ', '.join(f"'{match}'" for match in sorted(unique_matches))

print(formatted_matches)
