# Gufo Err Example: Fail-fast

Errors may be unrecoverable. Application should be stopped
as soon as possible to minimise the possible damage.
Lets implement the simple fail-fast behavior. Consider
the `RuntimeError` is fatal.

```  py title="failfast.py" linenums="1"
--8<-- "examples/failfast.py"
```

Lets see.

```  py title="failfast.py" linenums="1" hl_lines="1 2"
--8<-- "examples/failfast.py"
```

Type hints is the great help, so lets import the necessary
types.


```  py title="failfast.py" linenums="1" hl_lines="3"
--8<-- "examples/failfast.py"
```

All error configuration is performed via `err` singleton,
so we need to import it first. We also need the `BaseFailFast`
class to implement our handler.

```  py title="failfast.py" linenums="1" hl_lines="6"
--8<-- "examples/failfast.py"
```

Lets define our fail-fast handler. It must be derived
from `BaseFailFast`.

```  py title="failfast.py" linenums="1" hl_lines="7"
--8<-- "examples/failfast.py"
```
Our handler accepts exception type to check as its own
configuration parameter.

```  py title="failfast.py" linenums="1" hl_lines="8"
--8<-- "examples/failfast.py"
```

Do not forget *always* call base class constructor
unless you know what you do. Otherwise, you code
may be broken with future update.

```  py title="failfast.py" linenums="1" hl_lines="9"
--8<-- "examples/failfast.py"
```

Lets store our configuration as `exc_type` argument.

```  py title="failfast.py" linenums="1" hl_lines="11 12 13"
--8<-- "examples/failfast.py"
```

`must_die` function is the key function for fail-fast
handler. It accepts the result of `sys.exc_info()`
function. First parameter is the exception type.
Second is the exception value. Last is the frame
information. Fail-fast handlers return boolean value.
`True` should be returned if the error is unrecoverable,
`False` - otherwise.

```  py title="failfast.py" linenums="1" hl_lines="14"
--8<-- "examples/failfast.py"
```

The logic is simple. If the exception type is matched
with configured one - we must fail.

```  py title="failfast.py" linenums="1" hl_lines="17"
--8<-- "examples/failfast.py"
```

`err.setup()` function must be called to initialize and confugure
the error protection. None, we pass to the `fail_fast` argument
a list of configured fail-fast handler instances, not a classes.
`fail_fast_code` parameter is optional and sets the exit code
on fail-fast termination. Default code is `1`, but we set it
to `5` for our example.
See [Err.setup()](../reference.md#gufo.err.err.Err.setup) for
details.

```  py title="failfast.py" linenums="1" hl_lines="20 21"
--8<-- "examples/failfast.py"
```

Lets define the function which will intentionally fail.

```  py title="failfast.py" linenums="1" hl_lines="24 26"
--8<-- "examples/failfast.py"
```

Lets wrap our error domain.

```  py title="failfast.py" linenums="1" hl_lines="25"
--8<-- "examples/failfast.py"
```

And call our faulty function.

```  py title="failfast.py" linenums="1" hl_lines="27"
--8<-- "examples/failfast.py"
```

Run all the error processing machinery.

```  py title="failfast.py" linenums="1" hl_lines="27"
--8<-- "examples/failfast.py"
```
Here we print the debug message. If our fail-fast code
works correctly, we will not see this message.

## Running

Run example as:

```
$ python3 examples/failfast.py
```

And got the empty output. Let check our error code:

```
$ echo $?
5
```

Note, we didn't saw "Stopping" message and our process returns error code `5`.
All just we configured.
