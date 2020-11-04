
![PyPI](https://img.shields.io/pypi/v/epsel)

[![Build Status](https://travis-ci.org/soxofaan/epsel.svg?branch=master)](https://travis-ci.org/soxofaan/epsel)

# EPSEL: Ensure PySpark Executor Logging

`epsel` is a simple Python module that provides
a decorator based approach to enable/ensure standard Python logging 
from PySpark Executors.


## The problem: logging from my PySpark executors doesn't work

In PySpark, the actual data processing is done in so called "executors",
which are forked processes that are separate from the "driver" program.
As a user you have full control over the driver process, 
but not so much over the executor processes.

For example, in your PySpark driver program you can set up 
standard Python logging as desired, 
but this setup is not replicated in the executor processes.
There are no (default) logging handlers, so all logging messages are lost.
Since Python 3.2 however, when there are not handlers, 
there is still a "last resort" handler that will show 
`warning()` and `error()` messages in their bare format on standard error,
but you probably want something more flexible than that.


Illustration in interactive PySpark shell:

    >>> import os, logging
    >>> logging.basicConfig(level=logging.INFO)
    
    >>> def describe():
    ...     return "pid: {p}, root handlers: {h}".format(p=os.getpid(), h=logging.root.handlers)
    ... 
    >>> describe()
    'pid: 3376, root handlers: [<StreamHandler <stderr> (NOTSET)>]'

    >>> sc.parallelize([1, 2, 3]).map(lambda x: describe()).collect()
    ['pid: 4153, root handlers: []', 'pid: 4136, root handlers: []', 'pid: 4120, root handlers: []']

The first `describe()` happens in the driver and has root handlers because
of the `basicConfig()` earlier.
However, the `describe()` calls in the `map()` happen in separate process
(note the different PIDs) and have no root handlers.



## EPSEL: decorator based logging setup for PySpark executors

Around the web you can find various solutions to set up logging in your executors. 
It typically involves passing and loading a separate file with logging setup code.
Managing this file might be cumbersome depending on your use case.


In contrast, `epsel` takes a decorator based approach.
You just have to decorate the data processing functions you are passing 
to `map()`, `filter()`, `sortBy()`, etc. 

A very minimal example:

    @epsel.ensure_basic_logging
    def process(x):
        logger.info("Got {x}".format(x=x))
        return x * x
    
    result = rdd.map(process).collect()

What will happen here is that the first time `process()` is called 
in the executor, basic logging is set up as desired, 
so that logging messages are not lost.


### Options and finetuning

The `ensure_basic_logging` decorator will do a basic logging setup using 
[`logging.basicConfig()`](https://docs.python.org/3/library/logging.html#logging.basicConfig), 
and desired options can be directly provided to the decorator
as illustrated in the following example using the interactive PySpark shell:

    >>> import logging
    >>> from epsel import ensure_basic_logging
    >>> logger = logging.getLogger("example")
    
    >>> @ensure_basic_logging(level=logging.INFO)
    ... def process(x):
    ...     logger.info("Got {x}".format(x=x))
    ...     return x * x
    ... 
    >>> sc.parallelize(range(5)).map(process).collect()
    INFO:example:Got 0
    INFO:example:Got 1
    INFO:example:Got 3
    INFO:example:Got 2
    INFO:example:Got 4
    [0, 1, 4, 9, 16]

To improve readability or code reuse, you can of course predefine decorators:

    with_logging = ensure_basic_logging(
        level=logging.INFO,
        format="[%(process)s/%(name)s] %(levelname)s %(message)s"
    )
    
    @with_logging
    def process(x):
        ...


`epsel` also defines some simple predefined decorators:

    # Predefined decorator for stderr/INFO logging
    ensure_info_logging = ensure_basic_logging(level=logging.INFO)
    
    # Predefined decorator for stderr/DEBUG logging
    ensure_debug_logging = ensure_basic_logging(level=logging.DEBUG)


### Fine-grained logging set up

If a logging setup in `logging.basicConfig()` style is not flexible enough,
you can also inject your custom setup code with the `on_first_time` decorator.
This decorator is not limited to logging setup, it just expects
a callable (that can be called without arguments). A very simple example:


    @epsel.on_first_time(lambda: print("hello world"))
    def process(x):
        ....

This will print "hello world" the first time the `process` function is 
called in each executor.
