from luasb import LuaSandbox
from luasb.modules import load_modules

load_modules('.lmods')

sb = LuaSandbox({
    'name': 'Joe'
})

code = """
Result.value = name

json = require("json")
"""

print("executing code")
sb.execute(code)

print(sb.Result['value'])
