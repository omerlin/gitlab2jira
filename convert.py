import re

def convert_gitlab_to_jira(markdown_text):
    # Convert headers
    markdown_text = re.sub(r'^#\s+(.*)$', r'h1. \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^##\s+(.*)$', r'h2. \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^###\s+(.*)$', r'h3. \1', markdown_text, flags=re.MULTILINE)

    # Convert bold and italics
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', markdown_text)
    markdown_text = re.sub(r'__(.*?)__', r'*\1*', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'_\1_', markdown_text)
    markdown_text = re.sub(r'_(.*?)_', r'_\1_', markdown_text)

    # Convert unordered lists
    markdown_text = re.sub(r'^\s*-\s+(.*)$', r'- \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^\s{2,}-\s+(.*)$', r'-- \1', markdown_text, flags=re.MULTILINE)

    # Convert ordered lists
    markdown_text = re.sub(r'^\s*\d+\.\s+(.*)$', r'# \1', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^\s{2,}\d+\.\s+(.*)$', r'## \1', markdown_text, flags=re.MULTILINE)

    # Convert links
    markdown_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'[\1|\2]', markdown_text)

    # Convert images
    markdown_text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'!\2|alt=\1!', markdown_text)

    # Convert inline code
    markdown_text = re.sub(r'`(.*?)`', r'{{\1}}', markdown_text)

    # Convert code blocks
    markdown_text = re.sub(r'```(.*?)\n(.*?)```', r'{code:\1}\n\2\n{code}', markdown_text, flags=re.DOTALL)

    # Convert blockquotes
    markdown_text = re.sub(r'^>\s+(.*)$', r'{quote}\n\1\n{quote}', markdown_text, flags=re.MULTILINE)

    # Convert tables
    markdown_text = re.sub(r'^\|(.*)\|$', r'||\1||', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^\|\s*:?-+:?\s*\|', r'|', markdown_text, flags=re.MULTILINE)

    # Convert horizontal rules
    markdown_text = re.sub(r'^-{3,}', r'----', markdown_text)

    # Convert strikethrough
    markdown_text = re.sub(r'~~(.*?)~~', r'-\1-', markdown_text)

    # Convert mentions
    markdown_text = re.sub(r'@(\w+)', r'[~\1]', markdown_text)

    return markdown_text

# Example GitLab Markdown input
gitlab_markdown = """
# Heading 1
## Heading 2
### Heading 3

**Bold text** and *italic text*.

- Item 1
- Item 2
  - Sub-item 2.1

1. Item 1
2. Item 2
   1. Sub-item 2.1

[Link Text](https://example.com)

![Alt Text](https://example.com/image.png)

`inline code`

```python
def hello():
    print("Hello, World!")
