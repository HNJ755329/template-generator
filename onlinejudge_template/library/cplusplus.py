from typing import *

import onlinejudge_template.library.common as common
from onlinejudge_template.types import *


def _join_with_indent(lines: Sequence[str], *, nest: int, data: Dict[str, Any]) -> str:
    indent = data['config'].get('indent', ' ' * 4)
    buf = []
    nest = 1
    for line in lines:
        if line.startswith('}'):
            nest -= 1
        buf.append(indent * nest + line)
        if line.endswith('{'):
            nest += 1
    return '\n'.join(buf)


def _declare_loop(var: str, size: str, *, data: Dict[str, Any]) -> str:
    rep = data['config'].get('rep_macro')
    if rep is None:
        return f"""for (int {var} = 0; {var} < {size}; ++{var})"""
    elif isinstance(rep, str):
        return f"""{rep} ({var}, {size})"""
    elif callable(rep):
        return rep(var, size)
    else:
        assert False


def _read_int(var: str, *, data: Dict[str, Any]) -> str:
    scanner = data['config'].get('scanner')
    if scanner is None or scanner == 'scanf':
        return f"""scanf("%d", &{var});"""
    elif scanner in ('cin', 'std::cin'):
        return f"""{_get_std(data=data)}cin >> {var};"""
    elif callable(scanner):
        return scanner(var)
    else:
        assert False


def _write_int(var: str, *, data: Dict[str, Any]) -> str:
    printer = data['config'].get('printer')
    if printer is None or printer == 'scanf':
        return f"""printf("%d\\n", &{var});"""
    elif printer in ('cout', 'std::cout'):
        return f"""{_get_std(data=data)}cout << {var} << {_get_std(data=data)}endl;"""
    elif callable(printer):
        return printer(var)
    else:
        assert False


def _get_std(data: Dict['str', Any]) -> str:
    if data['config'].get('using_namespace_std', True):
        return ''
    else:
        return 'std::'


def _declare_variable(name: str, dims: List[str], *, data: Dict[str, Any]) -> str:
    type = "int"
    ctor = ""
    for dim in reversed(dims):
        ctor = f"""({dim}, {type}({ctor}))"""
        type = f"""{_get_std(data=data)}vector<{type}>"""
    return f"""{type} {name}{ctor};"""


def _read_input_dfs(node: FormatNode, *, declared: Set[str], dims: Dict[str, List[str]], data: Dict[str, Any]) -> Iterator[str]:
    if node.__class__.__name__ == 'ItemNode':
        if node.name not in declared:
            declared.add(node.name)
            yield _declare_variable(node.name, dims[node.name], data=data)
        var = node.name
        for index in node.indices:
            var = f"""{var}[{index}]"""
        yield f"""scanf("%d", &{var});"""
    elif node.__class__.__name__ == 'NewlineNode':
        pass
    elif node.__class__.__name__ == 'SequenceNode':
        for item in node.items:
            yield from _read_input_dfs(item, declared=declared, dims=dims, data=data)
    elif node.__class__.__name__ == 'LoopNode':
        yield _declare_loop(var=node.name, size=node.size, data=data) + ' {'
        yield from _read_input_dfs(node.body, declared=declared, dims=dims, data=data)
        yield '}'


def read_input(data: Dict[str, Any], *, nest: int = 1) -> str:
    dims = common.list_used_items(data['input'])
    lines = _read_input_dfs(data['input'], dims=dims, declared=set(), data=data)
    return _join_with_indent(lines, nest=nest, data=data)


def write_output(data: Dict[str, Any], *, nest: int = 1) -> str:
    lines = []
    lines.append(_write_int('ans', data=data))
    return _join_with_indent(lines, nest=nest, data=data)


def arguments_types(data: Dict[str, Any]) -> str:
    decls = []
    for name, dims in common.list_used_items(data['input']).items():
        type = "int"
        for dim in reversed(dims):
            type = f"""{_get_std(data=data)}vector<{type}>"""
        if dims:
            type = f"""const {type} &"""
        decls.append(f"""{type} {name}""")
    return ', '.join(decls)


def arguments(data: Dict[str, Any]) -> str:
    dims = common.list_used_items(data['input'])
    return ', '.join(dims.keys())


def return_type(data: Dict[str, Any]) -> str:
    return "auto"
