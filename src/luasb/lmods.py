import os
import httpx


modules = [
    'https://raw.githubusercontent.com/rxi/json.lua/master/json.lua',
    'https://raw.githubusercontent.com/philanc/plc/master/plc/base85.lua'
]


def load_modules():
    os.makedirs("lua_modules", exist_ok=True)
    for module in modules:
        response = httpx.get(module)
        response.raise_for_status()

        path = os.path.basename(module)
        path = f'lua_modules/{path}'

        with open(path, 'w') as f:
            f.write(response.text)
