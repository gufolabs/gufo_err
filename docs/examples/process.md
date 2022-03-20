# Gufo Err Example: Process the Exception.

Python default error hook is the last resort in the error
handling, called just before thread or process termination.
What if we want to catch and process errors early? 

Lets modify our [globalextend.py](globalextend.md) example to
get more information beyound default error traceback.

```  py title="process.py" linenums="1"
--8<-- "examples/process.py"
```

The code is straightforward:

```  py title="process.py" linenums="1" hl_lines="1"
--8<-- "examples/process.py"
```

All error configuration is performed via `err` singleton,
so we need to import it first.

```  py title="process.py" linenums="1" hl_lines="3"
--8<-- "examples/process.py"
```

`err.setup()` function must be called to initialize and confugure
the error protection. `format` argument sets
traceback format to extended version. Note, we do not set `catch_all`
exception and do not install the global hook.
See [Err.setup()](../reference.md#gufo.err.err.Err.setup) for
details.

```  py title="process.py" linenums="1" hl_lines="6 7 8 9"
--8<-- "examples/process.py"
```

Lets define the function which will intentionally fail. We define
the `x` variable to catch it in the trace later.

```  py title="process.py" linenums="1" hl_lines="12 14"
--8<-- "examples/process.py"
```

Unlike the [previous example](globalextend.md), we wrap our function directly
in `try ... except` block. We do not know which exception
we may catch, so `Exception` is the good start.

```  py title="process.py" linenums="1" hl_lines="13"
--8<-- "examples/process.py"
```

Lets call our function.

```  py title="process.py" linenums="1" hl_lines="15"
--8<-- "examples/process.py"
```
`err.process()` runs all error handling machinery, so just
call this.

## Running

Run example as:

```
$ python3 examples/process.py
```

And got the output:

```
Error: eda58358-92cc-5e8b-a466-e50c699268a1
RuntimeError: failing
Traceback (most resent call last):
-------------------------------------------------------------------------------
File: /workspaces/gufo_err/examples/process.py (line 13)
    6     def fail():
    7         x = 1
    8         x += 1
    9         raise RuntimeError("failing")
   10     
   11     
   12     try:
   13 ==>     fail()
   14     except Exception:
   15         err.process()
Locals:
            __name__ = '__main__'
             __doc__ = None
         __package__ = None
          __loader__ = <_frozen_importlib_external.SourceFileLoader object at 0x7f24b83a4c10>
            __spec__ = None
     __annotations__ = {}
        __builtins__ = <module 'builtins' (built-in)>
            __file__ = '/workspaces/gufo_err/examples/process.py'
          __cached__ = None
                 err = <gufo.err.err.Err object at 0x7f24b80052d0>
                fail = <function fail at 0x7f24b84e3d90>
-------------------------------------------------------------------------------
File: /workspaces/gufo_err/examples/process.py (line 9)
    2     
    3     err.setup(format="extend")
    4     
    5     
    6     def fail():
    7         x = 1
    8         x += 1
    9 ==>     raise RuntimeError("failing")
   10     
   11     
   12     try:
   13         fail()
   14     except Exception:
   15         err.process()
Locals:
                   x = 2
-------------------------------------------------------------------------------
```

Just same behaviour as in [previous example](globalextend.md), but we have
isolated the error domain and imply error processing as soon as possible.