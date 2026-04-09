import ast

from bandit.core import utils
from bandit.core.context import Context

from spoils.plugins.os_path_join import no_os_path_join


def _build_aliases(tree):
    aliases = {}

    for node in tree.body:
        if isinstance(node, ast.Import):
            for imported_name in node.names:
                if imported_name.asname:
                    aliases[imported_name.asname] = imported_name.name
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            for imported_name in node.names:
                alias = imported_name.asname or imported_name.name
                aliases[alias] = f"{node.module}.{imported_name.name}"

    return aliases


def _make_context(source, node_type, predicate=None):
    tree = ast.parse(source)
    aliases = _build_aliases(tree)

    for node in ast.walk(tree):
        if isinstance(node, node_type) and (predicate is None or predicate(node)):
            raw_context = {
                "node": node,
                "import_aliases": aliases,
                "filename": "test.py",
                "file_data": source,
            }

            if isinstance(node, ast.Call):
                qualname = utils.get_call_name(node, aliases)
                raw_context["call"] = node
                raw_context["qualname"] = qualname
                raw_context["name"] = qualname.split(".")[-1]

            return Context(raw_context)

    raise AssertionError(f"Unable to find {node_type.__name__} in test source")


def test_flags_os_path_join():
    context = _make_context(
        "import os\nos.path.join('a', 'b')\n",
        ast.Call,
    )

    assert no_os_path_join(context) is not None


def test_flags_multi_argument_path_constructor():
    context = _make_context(
        "from pathlib import Path\nPath('a', 'b')\n",
        ast.Call,
    )

    assert no_os_path_join(context) is not None


def test_flags_joinpath_calls_on_path_objects():
    context = _make_context(
        "from pathlib import Path\nPath('a').joinpath('b')\n",
        ast.Call,
        lambda node: isinstance(node.func, ast.Attribute) and node.func.attr == "joinpath",
    )

    assert no_os_path_join(context) is not None


def test_flags_division_operator_on_path_objects():
    context = _make_context(
        "from pathlib import Path as P\nP('a') / 'b'\n",
        ast.BinOp,
        lambda node: isinstance(node.op, ast.Div),
    )

    assert no_os_path_join(context) is not None


def test_does_not_flag_single_argument_path_constructor():
    context = _make_context(
        "from pathlib import Path\nPath('a')\n",
        ast.Call,
    )

    assert no_os_path_join(context) is None


def test_does_not_flag_joinpath_on_non_path_objects():
    context = _make_context(
        "builder.joinpath('a')\n",
        ast.Call,
        lambda node: isinstance(node.func, ast.Attribute) and node.func.attr == "joinpath",
    )

    assert no_os_path_join(context) is None


def test_does_not_flag_regular_division():
    context = _make_context(
        "left / right\n",
        ast.BinOp,
        lambda node: isinstance(node.op, ast.Div),
    )

    assert no_os_path_join(context) is None
