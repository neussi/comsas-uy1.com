import re

def check_template(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Find all relevant tags
    tags = re.findall(r'{%\s*(block|endblock|if|endif|for|endfor)\s*(.*?)\s*%}', content)
    
    stack = []
    for tag, attr in tags:
        if tag in ['block', 'if', 'for']:
            stack.append((tag, attr))
        else:
            if not stack:
                print(f"Error: Found {{% {tag} %}} but no start tag found.")
                continue
            
            start_tag, start_attr = stack.pop()
            expected = 'end' + start_tag
            if tag != expected:
                print(f"Error: Mismatched tag. Found {{% {tag} %}} but expected {{% {expected} %}} for {{% {start_tag} {start_attr} %}}")
                # Try to recover by popping until we find a match or stack is empty
                while stack:
                    start_tag, start_attr = stack.pop()
                    expected = 'end' + start_tag
                    if tag == expected:
                        print(f"Recovered by closing {{% {start_tag} %}}")
                        break
                continue

    if stack:
        print(f"Error: Unclosed tags: {stack}")
    else:
        print("Template structure is valid.")

check_template('/home/npe-tech/Projets/Comsas/templates/base.html')
