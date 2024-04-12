constable
--------------

constable allows you to monitor the state of specified variables at each assignment operation, providing a step-by-step view of variable changes!

View the `Github repository <https://github.com/saurabh0719/constable>`__ and the `official docs <https://github.com/saurabh0719/constable#README>`__.


How does it work?
~~~~~~~~~~~~~~~~~~

The `constable.trace` decorator uses Python's Abstract Syntax Tree (AST) in much the same way we add `print`(s) to debug states. During runtime, it prepares and inserts `print` statements into the function's AST after every assignment operation (`ast.Assign`, `ast.AugAssign` and `ast.AnnAssign`), and then executes the modified code in a separate namespace with `exec`.


.. code:: sh

    $ pip install constable

Tested for python 3.8 and above.


Usage :
~~~~~~~~~~~~~


Monitoring functions

.. code:: python

    import constable

    @constable.trace(['a', 'b'])
    def example(a, b):
        a = a + b
        c = a
        a = "Experimenting with the AST"
        b = c + b
        a = c + b
        return a

    example(5, 6)


Output :

::

    constable.trace: example:19 -
        a = a + b
        a = 11
        type(a) = <class 'int'>

    constable.trace: example:21 -
        a = "Experimenting with the AST"
        a = Experimenting with the AST
        type(a) = <class 'str'>

    constable.trace: example:22 -
        b = c + b
        b = 17
        type(b) = <class 'int'>

    constable.trace: example:23 -
        a = c + b
        a = 28
        type(a) = <class 'int'>

    constable.trace: example -
        args: (5, 6)
        kwargs: {}
        returned: 28
        execution time: 0.00029278 seconds
