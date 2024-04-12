<p align="left">
    <img src="https://github.com/saurabh0719/constable/assets/127945292/80cf03c8-af53-4161-9a47-b9acbc9bb413" width=500>
</p>

<hr>


If you find yourself aimlessly adding :sparkles: `print` :sparkles: statements while debugging your code, this is for you. :handshake:

Constable inserts print statements directly into the AST at runtime to print variable assignments and other details.

It turns this 🔽 ....
```python
@constable.trace('a', 'b')
def do_something(a, b):
    a = a + b
```
.... into this 🔽 during runtime
```python
# During runtime, print statements will be added for every assignment on 'a' & 'b'.
# Resulting in something like -
def do_something(a, b):
    a = a + b
    print(f"wowww i wonder who put this print here! a = {a}")
```

Monitor the state of specified variables at each assignment operation, providing a step-by-step view of variable changes!

```sh
$ pip install constable
```

### How does it work?

The `constable.trace` decorator uses Python's Abstract Syntax Tree (AST) in much the same way we add `print`(s) to debug states. During runtime, it prepares and inserts `print` statements into the function's AST after every assignment operation (`ast.Assign`, `ast.AugAssign` and `ast.AnnAssign`), and then executes the modified code in a separate namespace with `exec`.

:memo: Use at your own risk in mission-critical environments, or with unknown agents, as compiling and executing code during runtime can cause unwanted side effects. For all use cases that matter, use `pdb` instead.

#### Print variable assignments and execution info.

```python
import constable

@constable.trace('a', 'b')
def example(a, b):
    a = a + b
    c = a
    a = "Experimenting with the AST"
    b = c + b
    a = c + b
    return a

example(5, 6)
```

Output -

```
constable: example: line 5
    a = a + b
    a = 11
    type(a) = <class 'int'>

constable: example: line 7
    a = "Experimenting with the AST"
    a = Experimenting with the AST
    type(a) = <class 'str'>

constable: example: line 8
    b = c + b
    b = 17
    type(b) = <class 'int'>

constable: example: line 9
    a = c + b
    a = 28
    type(a) = <class 'int'>

constable: example: line 3 to 10
    args: (5, 6)
    kwargs: {}
    returned: 28
    execution time: 0.00018480 seconds
```

You can also use it on its own to track function execution info. 

```python
import constable

@constable.trace()
def add(a, b):
    return a + b

add(5, 6)
```

Output - 

```
constable: add: line 3 to 5
    args: (5, 6)
    kwargs: {}
    returned: 11
    execution time: 0.00004312 seconds
```


#### @trace
The `trace` function is the decorator to add `print` statements into the AST.

```python

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

```
<hr>
