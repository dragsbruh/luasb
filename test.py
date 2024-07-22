from luasb import LuaSandbox
from luasb.modules import load_modules

load_modules('.lmods')

sb = LuaSandbox({
    'name': 'Joe'
})

code = """
print("Hello world!")
"""

print("executing code")
sb.execute(code)

print(sb.output)
