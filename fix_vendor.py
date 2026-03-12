import os
path = os.path.join('api', 'vendor.py')
with open(path, encoding='utf-8') as f:
    content = f.read()
old = "new_status = data.get('status')\n    valid      = ['pending', 'preparing', 'ready', 'done']\n\n    if new_status not in valid:\n        return jsonify({'error': f'Status must be one of {valid}'}), 400"
new = "new_status = (data.get('status') or '').strip()\n    if new_status not in ['pending','preparing','ready','collected']:\n        return jsonify({'error': 'Invalid status'}), 400"
if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS - vendor.py fixed! Now restart Flask.')
else:
    print('ERROR - pattern not found')
    lines = content.split('\n')
    for i in range(81, 89):
        print(i+1, repr(lines[i]))
