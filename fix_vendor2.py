import os
path = os.path.join('api', 'vendor.py')
with open(path, encoding='utf-8') as f:
    content = f.read()

# Fix 1: valid statuses
content = content.replace(
    "valid      = ['pending', 'preparing', 'ready', 'done']",
    "valid      = ['pending', 'preparing', 'ready', 'collected']"
)

# Fix 2: order status update logic - replace 'done' with 'collected'
content = content.replace(
    "if statuses <= {'done'}:\n        order.status = 'collected'\n    elif statuses <= {'ready', 'done'}:\n        order.status = 'ready'\n    elif 'preparing' in statuses or 'pending' in statuses:\n        order.status = 'preparing'",
    "if statuses <= {'collected'}:\n        order.status = 'collected'\n    elif statuses <= {'ready', 'collected'}:\n        order.status = 'ready'\n    elif 'preparing' in statuses:\n        order.status = 'preparing'\n    else:\n        order.status = 'placed'"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
print('Lines 82-105:')
for i, line in enumerate(lines[81:105], 82):
    print(i, line.rstrip())
