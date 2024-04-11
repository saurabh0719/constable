<p align="left">
    <img src="https://github.com/saurabh0719/constable/assets/127945292/80cf03c8-af53-4161-9a47-b9acbc9bb413" width=500>
</p>

<hr>


If you find yourself aimlessly adding :sparkles: `print` :sparkles: statements while debugging your code, this is for you. :handshake:

Constable inserts print statements directly into the AST at runtime to print variable assignments and other details.

It turns this 🔽 ....
```python
@constable.trace(['a', 'b'])
def do_something(a=5, b=6):
    a = a + b
```
.... into this 🔽 during runtime
```python
# During runtime, print statements will be added for every assignment on 'a' & 'b'.
# Resulting in something like -
def do_something(a=5, b=6):
    a = a + b
    print(f"debug: do_something: a = {a}")
```

### Key features

- Capture function args and result

- Monitor variable state at each assignment op

- Measure execution time

- Any of the above can be turned on/off.


```sh
$ pip install constable
```

### How does it work?

The `trace` decorator uses Python's Abstract Syntax Tree (AST) in much the same way we add `print`(s) to debug states. During runtime, it prepares and inserts `print` statements into the function's AST after every assignment operation, and then executes the modified code in a separate namespace with `exec`.

:memo: Use at your own risk in mission-critical environments, or with unknown agents, as compiling and executing code during runtime can cause unwanted side effects. For all use cases that matter, use `pdb` instead.

#### Tracing variable assignments 

```python

import constable

@constable.trace(['a', 'b'])
def do_something(a=5, b=6):
    a = a + b
    c = a
    a = "Experimenting with the AST"
    b = c + b
    a = c + b
    return a

do_something()

```

Output -

```
executing: do_something(a = 5, b = 6)
debug: do_something: a = 11
debug: do_something: a = Experimenting with the AST
debug: do_something: b = 17
debug: do_something: a = 28
execution time: do_something(a = 5, b = 6) -> 0.00008297 seconds
```


#### Monitoring functions

```python

import constable

@constable.trace()
def add(a=1, b=2):
    return a + b

add(1, 2)

```

Output - 

```
executing: add(a = 1, b = 2)
execution time: add(a = 1, b = 2) -> 0.00014877 seconds
```

### API

The `trace` function is the decorator to add prints to the AST.

```python

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

```
<hr>
