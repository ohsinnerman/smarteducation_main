import os
import re
import glob
from html.parser import HTMLParser

class TagStackParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'):
            return
        self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f'Unexpected closing tag </{tag}> at line {self.getpos()[0]}')
            return
        last, pos = self.stack[-1]
        if last == tag:
            self.stack.pop()
            return
        found = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                found = True
                break
        if found:
            self.errors.append(
                f'Mismatched closing </{tag}> at line {self.getpos()[0]}, opened <{last}> at line {pos[0]}')
            self.stack = self.stack[:i]
        else:
            self.errors.append(f'Unexpected closing tag </{tag}> at line {self.getpos()[0]}')

    def error(self, message):
        pass


def normalize_text(text):
    text = re.sub(r"\{\%.*?\%\}", ' ', text, flags=re.S)
    text = re.sub(r"\{\{.*?\}\}", ' ', text, flags=re.S)
    return text

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
html_files = glob.glob(os.path.join(base, '**', '*.html'), recursive=True)
issues = {}
for path in html_files:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()
    cleaned = normalize_text(raw)
    parser = TagStackParser()
    parser.feed(cleaned)
    if parser.stack:
        parser.errors.append('Unclosed tags: ' + ', '.join(f'<{tag}>' for tag, pos in parser.stack))
    if parser.errors:
        issues[path] = parser.errors

print('HTML files checked:', len(html_files))
if not issues:
    print('No structural issues found in HTML templates.')
else:
    for path, errs in issues.items():
        print(path)
        for e in errs:
            print('  ', e)
