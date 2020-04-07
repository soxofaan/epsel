
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


## EPSEL: decorater based logging setup for PySpark executors

Around the web you can find various solutions to set up loggingi n your executors. 
It typically involves passing and loading a separate file with logging setup code.
Managing this file might be cumbersome depending on your use case.


In contrast, `epsel` takes a decorator based approach.
You just have to decorate the data processing functions you are passing 
to `map()`, `filter()`, `sortBy()`, ..., for example:


    import logging
    import epsel
    
    
    @epsel.ensure_basic_logging
    def process(x):
        logging.info("Got {x}".format(x=x))
        return x * x
