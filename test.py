from luasb import LuaSandbox
from luasb.modules import load_modules

load_modules('.lmods')


def cprint(msg: str):
    print(msg)


sb = LuaSandbox({
    'name': 'Joe'
}, print_fn=cprint)

code = """
print("Hello world!")
"""

print("executing code")
sb.execute(code)
