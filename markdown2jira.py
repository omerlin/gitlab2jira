def markdown_to_jira(markdown_text):
    lines = markdown_text.split('\n')
    jira_lines = []
    stack = []  # To track list hierarchy

    for line in lines:
        stripped = line.lstrip()
        indent_level = len(line) - len(stripped)  # Calculate indentation
        is_ordered = stripped.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))
        is_unordered = stripped.startswith(('-', '*', '+'))

        # Determine the current list type and level
        if is_ordered or is_unordered:
            # Calculate the current depth
            depth = indent_level // 2  # Assuming 2 spaces per indent level
            while len(stack) > depth:
                stack.pop()  # Pop deeper levels

            if is_ordered:
                list_char = '#'
            else:
                list_char = '-'

            # Add the current list type to the stack
            stack.append(list_char)

            # Generate the Jira line
            jira_line = (list_char * len(stack)) + ' ' + stripped.split(' ', 1)[1]
            jira_lines.append(jira_line)
        else:
            # Non-list line, add as-is
            jira_lines.append(line)

    return '\n'.join(jira_lines)


# Example Usage
markdown_text = """
1. First item
   - Nested unordered item 1
   - Nested unordered item 2
     1. Nested ordered item 1
     2. Nested ordered item 2
2. Second item
   - Nested unordered item 3
"""

jira_text = markdown_to_jira(markdown_text)
print(jira_text)
