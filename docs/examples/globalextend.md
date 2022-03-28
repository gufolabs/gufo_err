# Gufo Err Example: Global Hook, Expanded Dump.

Lets modify our [global.py](global.md) example to
get more information beyound default error traceback.

```  py title="globalextend.py" linenums="1"
--8<-- "examples/globalextend.py"
```

The code is straightforward:

```  py title="globalextend.py" linenums="1" hl_lines="1"
--8<-- "examples/globalextend.py"
```

All error configuration is performed via `err` singleton,
so we need to import it first.

```  py title="globalextend.py" linenums="1" hl_lines="3"
--8<-- "examples/globalextend.py"
```

`err.setup()` function must be called to initialize and confugure
the error protection. `catch_all` argument set to true to replace
the Python global error handling. `format` argument sets
traceback format to extended version.
See [Err.setup()](../reference/gufo/err/err.md#gufo.err.err.Err.setup) for
details.

```  py title="globalextend.py" linenums="1" hl_lines="6 7 8 9"
--8<-- "examples/globalextend.py"
```

Lets define the function which will intentionally fail. We define
the `x` variable to catch it in the trace later.

```  py title="globalextend.py" linenums="1" hl_lines="12"
--8<-- "examples/globalextend.py"
```

And call it.

## Running

Run example as:

```
$ python3 examples/globalextend.py
```

And got the output:

```
Error: 70173ec8-930f-5579-bb26-623847905f64
RuntimeError: failing
Traceback (most resent call last):
-------------------------------------------------------------------------------
File: /workspaces/gufo_err/examples/globalextend.py (line 12)
    5     
    6     def fail():
    7         x = 1
    8         x += 1
    9         raise RuntimeError("failing")
   10     
   11     
   12 ==> fail()
Locals:
            __name__ = '__main__'
             __doc__ = None
         __package__ = None
          __loader__ = <_frozen_importlib_external.SourceFileLoader object at 0x7f47a335cc10>
            __spec__ = None
     __annotations__ = {}
        __builtins__ = <module 'builtins' (built-in)>
            __file__ = '/workspaces/gufo_err/examples/globalextend.py'
          __cached__ = None
                 err = <gufo.err.err.Err object at 0x7f47a2fbd240>
                fail = <function fail at 0x7f47a3497d90>
-------------------------------------------------------------------------------
File: /workspaces/gufo_err/examples/globalextend.py (line 9)
    2     
    3     err.setup(catch_all=True, format="extend")
    4     
    5     
    6     def fail():
    7         x = 1
    8         x += 1
    9 ==>     raise RuntimeError("failing")
   10     
   11     
   12     fail()
Locals:
                   x = 2
-------------------------------------------------------------------------------
```

Wow, much more details. Note, the fingerprint is differs. We also got a
source code context and local variables for each frame. Such great improvement
to analysis.
