import ast
import functools
import inspect
import textwrap
import time as t


__all__ = ['trace']

yellow = lambda x: f"\033[93m{x}\033[0m"
green = lambda x: f"\033[92m{x}\033[0m"
cyan = lambda x: f"\033[96m{x}\033[0m"
blue = lambda x: f"\033[94m{x}\033[0m"
red = lambda x: f"\033[91m{x}\033[0m"


def trunc(s: str, max_len: int, dot=False):
    """
    Keep this outside scope of the decorator because it's used in the AST.
    """
    if max_len is None:
        return s
    s = str(s)
    if len(s) > max_len:
        if dot:
            s = (s[:max_len] + f"...'")
        else:
            s = (s[:max_len] + f"...[+{len(s)-max_len} chars]").replace('"', '\\"')
    return s


def trace(
    variables=None,
    args=True,
    result=False,
    max_len=None,
    verbose=False,
    time=True,
    use_spaces=False
):
    """
    An experimental decorator for tracing function execution using AST.

    Args:
        variables (list, optional): Variables to trace. Traces all if None. Default is None.
        args (bool, optional): Whether to print function arguments. Default is True.
        result (bool, optional): Whether to print function return value. Default is False.
        max_len (int, optional): Max length of printed values. Truncates if exceeded. Default is None.
        verbose (bool, optional): Whether to print detailed trace info. Default is False.
        time (bool, optional): Whether to print execution time. Default is True.
        use_spaces (bool, optional): Whether to add empty lines for readability. Default is False.

    Returns:
        function: Decorator for function tracing.
    """

    if max_len and not isinstance(max_len, int):
        raise ValueError("max_len must be an integer")
    
    if variables is None:
        variables = []

    def get_ast_module(func):
        source_code = textwrap.dedent(
                '\n'.join(inspect.getsource(func).splitlines()[1:])
            )
        return ast.parse(source_code)
    
    def get_arg_values(func, *a, **k):
        keyword_arguments = inspect.getcallargs(func, *a, **k)
        return ", ".join([
            f"{green(k)} = {trunc(v, max_len)}" for k, v in keyword_arguments.items()
        ])
    
    def get_function_signature(func, arg_values):
        return f"{cyan(func.__name__)}({arg_values})"

    def debug_prefix(func):
        return f"{yellow('debug:')} {cyan(func.__name__)}"

    def get_verbose_statements_to_insert(func, target, node):
        source_code_lines = inspect.getsource(func).splitlines()
        return [
            f'print("{debug_prefix(func)}:")',
            f'print({trunc(repr(source_code_lines[node.lineno].strip()), 30, True)})',
            f'print("{green(target.id)}", green("="), green(trunc(str({target.id}), {max_len})))',
        ]
    
    def get_statements_to_insert(func, target):
        return [
            f'print("{debug_prefix(func)}: {green(target.id)}", "=", trunc(str({target.id}), {max_len}))',
        ]

    def get_nodes_to_insert(func, target, node):
        empty_print_node = ast.parse(f'print("")').body[0]
        nodes_to_insert = []
        statements = (
            get_verbose_statements_to_insert(func, target, node) if verbose
            else get_statements_to_insert(func, target)
        )
        for stmnt in statements:
            node_to_insert = ast.parse(stmnt).body[0]
            nodes_to_insert.append(node_to_insert)

        if use_spaces and nodes_to_insert:
            nodes_to_insert = [empty_print_node] + nodes_to_insert + [empty_print_node]
        return nodes_to_insert

    def insert_nodes(module, nodes_to_insert, node):
        i = 1
        for node_to_insert in nodes_to_insert:
            node_to_insert.lineno = node.lineno + i
            node_to_insert.end_lineno = node.lineno + i
            node_to_insert.col_offset = 0
            module.body[0].body.insert(
                module.body[0].body.index(node) + i,
                node_to_insert
            )
            i += 1
        
        # Update line numbers of subsequent nodes
        for next_node in module.body[0].body[module.body[0].body.index(node) + i:]:
            next_node.lineno += i
            next_node.end_lineno += i

    def insert_logs_into_module(module, func, variables):
        # Add a print statement after each assignment statement
        for node in module.body[0].body:
            # skip any statement apart from assignment
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in variables:
                    nodes_to_insert = get_nodes_to_insert(
                        func, target, node)
                    insert_nodes(module, nodes_to_insert, node)
    
    def execute_function(module, func, *a, **k):
        code = compile(module, filename='<ast>', mode='exec')
        global_vars = {**globals(), **locals(), **func.__globals__}
        namespace = {func.__name__: func, **global_vars}
        exec(code, namespace)
        return namespace[func.__name__](*a, **k)
    
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*a, **k):
            if args or result:
                arg_values = get_arg_values(func, *a, **k)

            if args:
                print(f"{red('executing:')} {get_function_signature(func, arg_values)}")

            module = get_ast_module(func)
            insert_logs_into_module(module, func, variables)

            start = t.time()
            ret = execute_function(module, func, *a, **k)
            runtime = t.time() - start

            if time:
                prefix = f"{blue('execution time:')}"
                prefix += f" {get_function_signature(func, arg_values)}"
                print(f"{prefix} -> {runtime:.8f} seconds")

            if result:
                prefix = f"{red('return:')} {yellow(trunc(ret, max_len))}"
                print(f"{prefix} [{get_function_signature(func, arg_values)}]")
            return ret

        return wrapper
    
    return decorator
