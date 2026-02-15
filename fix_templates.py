import sys
import re
import os

def flatten_tags(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        content = f.read()
    
    # Regex pour trouver {{ ... }} avec des sauts de ligne
    pattern = re.compile(r'\{\{(.*?)\}\}', re.DOTALL)
    
    def replacer(match):
        # Remplacer les sauts de ligne et espaces multiples par un seul espace
        inner = match.group(1)
        if '\n' in inner:
            return '{{ ' + ' '.join(inner.split()) + ' }}'
        return match.group(0)
        
    new_content = pattern.sub(replacer, content)
    
    # Idem pour {% ... %}
    pattern_block = re.compile(r'\{\%(.*?)\%\}', re.DOTALL)
    def replacer_block(match):
        inner = match.group(1)
        if '\n' in inner:
             return '{% ' + ' '.join(inner.split()) + ' %}'
        return match.group(0)
    
    new_content = pattern_block.sub(replacer_block, new_content)

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Flattened tags in {filepath}")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        flatten_tags(f)
