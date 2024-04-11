constable
--------------

One decorator for lazy debugging. Inserts print statements directly into your AST.

View the `Github repository <https://github.com/saurabh0719/constable>`__ and the `official docs <https://github.com/saurabh0719/constable#README>`__.

.. code:: sh

    $ pip install constable

Tested for python 3.8 and above.

Key Features
------------

- Capture function args and result
- Monitor variable state at each assignment op
- Measure execution time
- Any of the above can be turned on/off.


Usage :
~~~~~~~~~~~~~


Monitoring functions

.. code:: python

    import constable

    @constable.trace()
    def add(a=1, b=2):
        return a + b

    add(1, 2)


Output :

::

    executing: add(a = 1, b = 2)
    execution time: add(a = 1, b = 2) -> 0.00014877 seconds


Tracing variable assignments


.. code:: python

    import constable

    @constable.trace(['a', 'b'])
    def do_something(a=5, b=6):
        a = a + b
        c = a
        a = "Experimenting with the AST"
        b = c + b
        a = c + b
        return a

    do_something(1, 2)


Output :

::

    executing: do_something(a = 1, b = 2)
    debug: do_something: a = 3
    debug: do_something: a = Experimenting with the AST
    debug: do_something: b = 5
    debug: do_something: a = 8
    execution time: do_something(a = 1, b = 2) -> 0.00009584 seconds
