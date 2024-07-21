from base64 import b85decode
import lupa  # type: ignore
import json

from lupa import LuaRuntime  # type: ignore
from typing import Any, Optional

_default_max_memory = 50 * 1024 * 1024  # 50mb

default_allowed_modules = []
default_blocked_globals = []


class LuaRuntimeError(RuntimeError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class LuaSandbox:
    def __init__(self, values: Optional[dict[str, dict[str, Any] | str]] = None, max_memory: int = _default_max_memory, allowed_modules: list[str] = default_allowed_modules, blocked_globals: list[str] = default_blocked_globals) -> None:
        self.allowed_modules = allowed_modules
        self.blocked_globals = blocked_globals
        self.result = None

        self.runtime = LuaRuntime(
            unpack_returned_tuples=True,
            max_memory=max_memory,
            attribute_filter=self._filter_attr_access
        )

        self._old_require = self.runtime.globals().require

        allowed_path = 'lua_modules/?.lua'
        self.runtime.execute(
            f"package.path = '{allowed_path};' .. package.path")
        self.lua_globals = self.runtime.globals()

        if values:
            self.runtime.execute('json = require("json")')
            self.runtime.execute('base85 = require("base85")')
            for item in values:
                if isinstance(values[item], str):  # base85 encoded data
                    self.lua_globals[item] = b85decode(
                        values[item])  # type: ignore
                else:
                    self.runtime.execute(
                        f'{item} = json.decode([[{json.dumps(values[item])}]]);')
            # self.lua_globals.json = None
            # self.lua_globals.base85 = None
            # FIXME: Fix imports

        for item in blocked_globals:
            code = f'{item} = nil'
            self.runtime.execute(code)

        self.lua_globals.require = self._require

        self.output: list[str] = []

        # print_func: Callable[[Any], None] = lambda _: None

        # self.lua_globals.print = print_func

        self.lua_globals.Result = {}

    def execute(self, code: str):
        try:
            self.runtime.execute(code)
        except Exception as e:
            raise LuaRuntimeError(f'Error executing script: {e}')

        try:
            self.Result = self._lua_table_to_dict(self.lua_globals.Result)
        except Exception as e:
            raise LuaRuntimeError(f'Error parsing result')

    def _require(self, modname: str):
        if modname in self.allowed_modules:
            return self._old_require(modname)
        raise LuaRuntimeError(f'Cannot import {modname}')

    def _filter_attr_access(self, _: object, attr: str, __: bool):
        if attr.startswith('_'):
            raise LuaRuntimeError(f'Cannot access or modify attribute {attr}')

    def _lua_table_to_dict(self, table: Any) -> dict[str, Any]:
        if not table:
            return {}

        python_dict: dict[str, Any] = {}
        for key, value in table.items():
            if lupa.lua_type(value) == 'table':
                python_dict[key] = self._lua_table_to_dict(value)
            else:
                python_dict[key] = value

        return python_dict
