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
    if not s or max_len is None:
        return s
    
    s = str(s)
    if len(s) > max_len:
        if dot:
            s = (s[:max_len] + f"...'")
        else:
            s = (s[:max_len] + f"...[+{len(s)-max_len} chars]").replace('"', '\\"')
    return s


class FunctionWrapper:
    """
    Wraps a function along with its arguments and provides utility methods.
    """
    def __init__(self, func, args=None, kwargs=None):
        self.func = func
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}
        self.start_line_num = func.__code__.co_firstlineno
        self.source_code_lines = inspect.getsource(func).splitlines()
        self.func_def_offset = 0
        for i in range(len(self.source_code_lines)):
            line = self.source_code_lines[i].strip()
            if line.startswith('def '):
                # Python uses 1-based indexing for line nums, so add 1 to the index
                self.func_def_offset = i + 1
                break
        self.end_line_num = self.start_line_num + len(self.source_code_lines) - 1

    def debug_prefix(self, line_num=None, to_line_num=None):
        signature = f"{self.func.__name__}"
        if line_num:
            signature += f": line {line_num}"
        if to_line_num:
            signature += f" to {to_line_num}"
        return f"{blue('constable:')} {signature}"


class AstProcessor:
    """
    Processes the AST of a function and inserts print statements for debugging.
    """
    def __init__(
        self,
        fn_wrapper: FunctionWrapper,
        verbose=True,
        use_spaces=True,
        max_len=None
    ):
        self.fn_wrapper = fn_wrapper
        self.max_len = max_len
        self.use_spaces = use_spaces
        self.verbose = verbose
        self.module = None

    def get_ast_module(self):
        if self.module is not None:
            return self.module
        source_code = textwrap.dedent(
            '\n'.join(inspect.getsource(self.fn_wrapper.func).splitlines()[1:])
        )
        self.module = ast.parse(source_code)
        return self.module

    def get_source_code_and_line_number(self, node_line_num) -> tuple:
        # source_code_lines will contain decorators, func def etc.
        # func_def_offset is the line num of the function definition in the source code
        # node_line_num is the line num of the statement in the function
        # we need to find the line num of the statement inside source code
        line_index = self.fn_wrapper.func_def_offset + node_line_num - 2
        line = self.fn_wrapper.source_code_lines[line_index].strip()
        start_line_num = self.fn_wrapper.start_line_num + node_line_num
        return line, start_line_num

    def get_statements_to_insert(self, target, node):
        line, line_num = self.get_source_code_and_line_number(node.lineno)
        debug_prefix = self.fn_wrapper.debug_prefix(line_num=line_num)
        if self.verbose:
            return [
                f'print("{debug_prefix}")',
                f'print("   ", {trunc(repr(line), 80, True)})',
                f'print("    {target.id} =", green(trunc(str({target.id}), {self.max_len})))',
                f'print("    type({target.id}) =", green(str(type({target.id}))))',
            ]
        else:
            return [
                f'print("{debug_prefix} - {green(target.id)}", green("="), green(trunc(str({target.id}), {self.max_len})))',
            ]

    def get_nodes_to_insert(self, target, node):
        empty_print_node = ast.parse(f'print("")').body[0]
        nodes_to_insert = [empty_print_node] if self.use_spaces else []
        statements = self.get_statements_to_insert(target, node)
        for stmnt in statements:
            node_to_insert = ast.parse(stmnt).body[0]
            nodes_to_insert.append(node_to_insert)
        return nodes_to_insert

    def insert_nodes(self, nodes_to_insert, node):
        i = 1
        module = self.get_ast_module()
        for node_to_insert in nodes_to_insert:
            node_to_insert.lineno = node.lineno + i
            node_to_insert.end_lineno = node.lineno + i
            node_to_insert.col_offset = 0
            module.body[0].body.insert(
                module.body[0].body.index(node) + i,
                node_to_insert
            )
            i += 1

    def insert_print_statements(self, variables):
        module = self.get_ast_module()
        for node in module.body[0].body:
            # skip any statement apart from assignment
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                continue
            targets = []
            # a = 5
            if isinstance(node, ast.Assign):
                targets = node.targets
            # a: int = 5 or a += 5
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
                targets = [node.target]

            for target in targets:
                if isinstance(target, ast.Name) and target.id in variables:
                    nodes_to_insert = self.get_nodes_to_insert(target, node)
                    self.insert_nodes(nodes_to_insert, node)


class Executor:
    """
    Executes and times function after inserting print statements
    """
    def __init__(self, processor: AstProcessor, variables: list, exec_info=True):
        self.processor = processor
        self.exec_info = exec_info
        self.variables = variables
        self.fn_wrapper = processor.fn_wrapper
        self.max_len = processor.max_len

    def print_execution_info(self, result, runtime):
        debug_prefix = self.fn_wrapper.debug_prefix(
            self.fn_wrapper.start_line_num,
            self.fn_wrapper.end_line_num
        )
        print(f"\n{debug_prefix}")
        print(f"    args: {green(self.fn_wrapper.args)}")
        print(f"    kwargs: {green(self.fn_wrapper.kwargs)}")
        print(f"    returned: {green(trunc(result, self.max_len))}")
        print(f"    execution time: {green(f'{runtime:.8f} seconds')}\n")

    def execute(self):
        self.processor.insert_print_statements(self.variables)
        module = self.processor.get_ast_module()
        start = t.perf_counter()
        # compile and execute
        code = compile(module, filename='<ast>', mode='exec')
        global_vars = {**globals(), **locals(), **self.fn_wrapper.func.__globals__}
        namespace = {
            self.fn_wrapper.func.__name__: self.fn_wrapper.func,
            **global_vars
        }
        exec(code, namespace)
        fn = namespace[self.fn_wrapper.func.__name__]
        result = fn(*self.fn_wrapper.args, **self.fn_wrapper.kwargs)
        runtime = t.perf_counter() - start
        if self.exec_info:
            self.print_execution_info(result, runtime)
        return result


def trace(
    *variables,
    exec_info=True,
    verbose=True,
    use_spaces=True,
    max_len=None,
):
    """
    An experimental decorator for tracing function execution using AST.

    Args:
        variables (list): List of variable names to trace.
        exec_info (bool, optional): Whether to print execution info.
        verbose (bool, optional): Whether to print detailed trace info.
        use_spaces (bool, optional): Whether to add empty lines for readability.
        max_len (int, optional): Max length of printed values. Truncates if exceeded.

    Returns:
        function: Decorator for function tracing.
    """

    if max_len and not isinstance(max_len, int):
        raise ValueError("max_len must be an integer")

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            fn_wrapper = FunctionWrapper(func, args, kwargs)
            processor = AstProcessor(fn_wrapper, verbose, use_spaces, max_len)
            executor = Executor(processor, variables, exec_info)
            ret = executor.execute()
            return ret

        return wrapper
    return decorator
