# Gufo Err Example: Global Hook

Lets install the error handling as the global python
exception hook.

```  py title="global.py" linenums="1"
--8<-- "examples/global.py"
```

The code is straightforward:

```  py title="global.py" linenums="1" hl_lines="1"
--8<-- "examples/global.py"
```

All error configuration is performed via `err` singleton,
so we need to import it first.

```  py title="global.py" linenums="1" hl_lines="3"
--8<-- "examples/global.py"
```

`err.setup()` function must be called to initialize and confugure
the error protection. `catch_all` argument set to true to replace
the Python global error handling.
See [Err.setup()](../reference/gufo/err/err.md#gufo.err.err.Err.setup) for
details.

```  py title="global.py" linenums="1" hl_lines="6 7"
--8<-- "examples/global.py"
```

Lets define the function which will intentionally fail.

```  py title="global.py" linenums="1" hl_lines="10"
--8<-- "examples/global.py"
```

And call it.

## Running

Run example as:

```
$ python3 examples/global.py
```

And got the output:

```
Error: 39dc9706-9550-5959-9c67-e702d036d4f9
Traceback (most resent call last):
  File "/workspaces/gufo_err/examples/global.py", line 10, in <module>
    fail()
  File "/workspaces/gufo_err/examples/global.py", line 7, in fail
    raise RuntimeError("failing")
RuntimeError: failing
```

Just like a default python traceback? Sure. Gufo Err installs `terse` traceback
format by default to mimic Python's default behavior. But note the first string.
`39dc9706-9550-5959-9c67-e702d036d4f9` is the error fingerprint - the unique
error discriminator.

Lets run our example again and check the output:
```
Error: 39dc9706-9550-5959-9c67-e702d036d4f9
Traceback (most resent call last):
  File "/workspaces/gufo_err/examples/global.py", line 10, in <module>
    fail()
  File "/workspaces/gufo_err/examples/global.py", line 7, in fail
    raise RuntimeError("failing")
RuntimeError: failing
```

Error fingerprint is the same. Fingerprint stability is the key to the
error analysis. Who want to analyze same error again and again?