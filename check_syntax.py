import ast, sys
with open('app.py', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print('app.py syntax OK')
except SyntaxError as e:
    print(f'SyntaxError: {e}')
    sys.exit(1)
