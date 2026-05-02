def check_tags(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    stack = []
    for i, line in enumerate(lines):
        line_num = i + 1
        # Simple regex-like search
        import re
        tags = re.findall(r'{%\s*(if|for|block|endif|endfor|endblock)\s*.*?%}', line)
        for tag in tags:
            if tag in ['if', 'for', 'block']:
                stack.append((tag, line_num))
            elif tag.startswith('end'):
                if not stack:
                    print(f"Error: {tag} at line {line_num} has no matching start tag")
                    continue
                last_tag, last_line = stack.pop()
                if tag != 'end' + last_tag:
                    print(f"Error: {tag} at line {line_num} does not match {last_tag} from line {last_line}")

    while stack:
        tag, line = stack.pop()
        print(f"Error: {tag} at line {line} was never closed")

check_tags('/home/npe-tech/Projets/Comsas/templates/main/member_portfolio.html')
