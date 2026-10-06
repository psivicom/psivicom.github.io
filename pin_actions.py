import glob
import re

shas = {
    'actions/checkout': '11d5960a326750d5838078e36cf38b85af677262',
    'actions/cache': '0057852bfaa89a56745cba8c7296529d2fc39830',
    'actions/setup-python': 'a26af69be951a213d495a4c3e4e4022e16d87065',
    'actions/setup-go': '40f1582b2485089dde7abd97c1529aa768e1baff',
    'actions/upload-artifact': '4cec3d8aa04e39d1a68397de0c4cd6fb9dce8ec1',
    'actions/download-artifact': 'fa0a91b85d4f404e444e00e005971372dc801d16',
    'actions/github-script': '60a0d83039c74a4aee543508d2ffcb1c3799cdea'
}

for f in glob.glob('.github/workflows/*.yml'):
    if 'bulk-pin-actions.yml' in f:
        continue
    with open(f, 'r') as file:
        content = file.read()
    for action, sha in shas.items():
        content = re.sub(f'{action}@v[0-9]+', f'{action}@{sha}', content)
    with open(f, 'w') as file:
        file.write(content)
print('All actions pinned successfully!')
