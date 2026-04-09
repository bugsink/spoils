import ast

import bandit
from bandit.core import utils
from bandit.core.test_properties import checks, test_id


PATHLIB_CONSTRUCTORS = {
    "pathlib.Path",
    "pathlib.PosixPath",
    "pathlib.PurePath",
    "pathlib.PurePosixPath",
    "pathlib.PureWindowsPath",
    "pathlib.WindowsPath",
}


def _new_issue():
    return bandit.Issue(
        severity=bandit.HIGH,
        confidence=bandit.MEDIUM,
        text="Avoid unvalidated path joining via os.path.join() or pathlib"
    )


def _is_path_constructor_call(node, import_aliases):
    return (
        isinstance(node, ast.Call)
        and utils.get_call_name(node, import_aliases) in PATHLIB_CONSTRUCTORS
    )


def _is_joinpath_call(node, import_aliases):
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "joinpath"
        and _is_path_expression(node.func.value, import_aliases)
    )


def _is_path_division(node, import_aliases):
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and (
            _is_path_expression(node.left, import_aliases)
            or _is_path_expression(node.right, import_aliases)
        )
    )


def _is_path_expression(node, import_aliases):
    return (
        _is_path_constructor_call(node, import_aliases)
        or _is_joinpath_call(node, import_aliases)
        or _is_path_division(node, import_aliases)
    )


# when I picked B380, B325 was the highest taken number in the B3xx series (blacklisted function calls)
@test_id('B380')
@checks('Call', 'BinOp')
def no_os_path_join(context):
    if context.call_function_name_qual == 'os.path.join':
        return _new_issue()

    if _is_path_constructor_call(context.node, context.import_aliases):
        if context.call_args_count and context.call_args_count > 1:
            return _new_issue()

    if _is_joinpath_call(context.node, context.import_aliases):
        return _new_issue()

    if _is_path_division(context.node, context.import_aliases):
        return _new_issue()
