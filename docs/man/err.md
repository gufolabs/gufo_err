# err Man Page

## Name

`err` - Gufo Err reporting tool.

## Synopsys
```
usage: err [-h] [-p PREFIX] {version,list,view,clear} ...

positional arguments:
  {version,list,view,clear}
    version             Show Gufo Err version
    list                Show the list of the registered errors
    view                View error report
    clear               Remove error info

options:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        JSON directory path
```

## Description

`err` manipulates with the error information, collected by
[ErrorInfoMiddleware][gufo.err.middleware.errorinfo.ErrorInfoMiddleware].

The following commands are supported:

* `version`: Display Gufo Err version and exit.
* `list`: Show terse list of collected error reports.
* `view`: View one or more error details. Dumped format
  may be set with `-f` option:

  * `terse` (default): Terse format similar to standart python's tracebacks.
  * `extend`: Extended format with code surroundings and stack variables dump.

* `clear`: Remove on or more error reports.

## Environment

* `GUFO_ERR_PREFIX`: Default value to `--prefix` options. Points to the directory
  where error reports are stored.

## Exit Status

## Error Fingerprint Expressions

Fingerprint expressions can be resolved to zero or more fingerprints
in `list`, `view`, and `clear` subcommands.
Following types of expressions are supported:

* `<UUID>`, like '0dc69dd9-85f9-5491-bc06-7a493e708738': resolves to single fingerprint.
* `all`: Resolves to all registered errors.
* `*`: Same as `all`.

## Examples

### Generating Reports

Enable [ErrorInfoMiddleware][gufo.err.middleware.errorinfo.ErrorInfoMiddleware]
in your code and point to the designated directory to store serialized
ErrorInfo files. Add to you code:

``` py
from gufo.err import err

err.setup(error_info_path="/var/err/", error_info_compress="gz")
```

Ensure your process has permission to write to the designated directory
(`/var/err/` in our example).

### Gufo Err Setup

Set up `GUFO_ERR_PREFIX` environment variable in your shell
to avoid a need to use `--prefix` option all the time.

```
$ export GUFO_ERR_PREFIX=/var/err/
```

### Show Version

```
err version
```

Output:
```
Gufo Err 0.4.0
```

### Show List of Errors

```
err list
```

Output:
```
Fingreprint                          Exception            Service                       Time                           Place                                             
------------------------------------ -------------------- ----------------------------- ------------------------------ --------------------------------------------------
0dc69dd9-85f9-5491-bc06-7a493e708738 NameError: foobar    fmt-gz                        2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57         
30dae827-0264-549a-b96f-a9b0298341b2 NotImplementedError  fmt-xz                        2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57         
4d2895ed-519d-508e-9ab9-ecc30c65b7cf ValueError           fmt-None                      2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57         
d6ee6183-170c-5c5f-8645-f0e1506f433e TypeError            fmt-bz2                       2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57 
```

### Show List of Particular Errors

```
err list <fingerprint1> ... <fingerprintN>
```

Where `<fingerprintX>` is an [Fingerprint Expression](#error-fingerprint-expressions).
Output:
```
Fingreprint                          Exception            Service                       Time                           Place                                             
------------------------------------ -------------------- ----------------------------- ------------------------------ --------------------------------------------------
0dc69dd9-85f9-5491-bc06-7a493e708738 NameError: foobar    fmt-gz                        2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57         
4d2895ed-519d-508e-9ab9-ecc30c65b7cf ValueError           fmt-None                      2023-09-01T07:54:59.690078     /workspaces/gufo_err/tests/test_cli.py:57         
```

### Show Error Detail

```
err view <fingerprint>
```

Where `<fingerprint>` is an [Fingerprint Expression](#error-fingerprint-expressions).
Output:
```
Error: be8ccd86-3661-434c-8569-40dd65d9860a
Traceback (most resent call last):
  File "/app/tests/test_frames.py", line 174, in test_iter_frames
    entry()
    ^^^^^^^
  File "/app/tests/sample/trace.py", line 15, in entry
    to_oops()
    ^^^^^^^^^
  File "/app/tests/sample/trace.py", line 9, in to_oops
    oops()
    ^^^^^^
  File "/app/tests/sample/trace.py", line 3, in oops
    raise RuntimeError(msg)
    ^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: oops
```

### Show Multiple Error Details

```
$ err view <fingerprint1> ... <fingerprintN>
```
Where `<fingerprintX>` is an [Fingerprint Expression](#error-fingerprint-expressions).

### Show Terse Version of Error Detail

```
$ err view -f terse <fingerprint>
```
Where `<fingerprint>` is an [Fingerprint Expression](#error-fingerprint-expressions).
Output:
```
Error: be8ccd86-3661-434c-8569-40dd65d9860a
Traceback (most resent call last):
  File "/app/tests/test_frames.py", line 174, in test_iter_frames
    entry()
    ^^^^^^^
  File "/app/tests/sample/trace.py", line 15, in entry
    to_oops()
    ^^^^^^^^^
  File "/app/tests/sample/trace.py", line 9, in to_oops
    oops()
    ^^^^^^
  File "/app/tests/sample/trace.py", line 3, in oops
    raise RuntimeError(msg)
    ^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: oops
```

### Show Extended Version of Error Detail

```
$ err view -f extend <fingerprint>
```

Where `<fingerprint>` is an [Fingerprint Expression](#error-fingerprint-expressions).

```
Error: be8ccd86-3661-434c-8569-40dd65d9860a
RuntimeError: oops
Traceback (most resent call last):
-------------------------------------------------------------------------------
File: /app/tests/test_frames.py (line 174)
  167         ),
  168     ]
  169     
  170     
  171     def test_iter_frames():
  172         """Call the function which raises an exception."""
  173         try:
  174 ==>         entry()
                  ^^^^^^^
  175             msg = "No trace"
  176             raise AssertionError(msg)
  177         except RuntimeError:
  178             frames = list(iter_frames(exc_traceback()))
  179             assert frames == SAMPLE_FRAMES
-------------------------------------------------------------------------------
File: /app/tests/sample/trace.py (line 15)
    8         x += 1
    9         oops()
   10     
   11     
   12     def entry():
   13         s = 2
   14         s += 1
   15 ==>     to_oops()
              ^^^^^^^^^
Locals:
                   s = 3
-------------------------------------------------------------------------------
File: /app/tests/sample/trace.py (line 9)
    2         msg = "oops"
    3         raise RuntimeError(msg)
    4     
    5     
    6     def to_oops():
    7         x = 1
    8         x += 1
    9 ==>     oops()
              ^^^^^^
   10     
   11     
   12     def entry():
   13         s = 2
   14         s += 1
   15         to_oops()
Locals:
                   x = 2
-------------------------------------------------------------------------------
File: /app/tests/sample/trace.py (line 3)
    1     def oops():
    2         msg = "oops"
    3 ==>     raise RuntimeError(msg)
              ^^^^^^^^^^^^^^^^^^^^^^^
    4     
    5     
    6     def to_oops():
    7         x = 1
    8         x += 1
    9         oops()
   10     
Locals:
                 msg = 'oops'
-------------------------------------------------------------------------------
```

### Clearing Single Error

```
$ err clear <fingerprint>
```
Where `<fingerprint>` is an [Fingerprint Expression](#error-fingerprint-expressions).

### Clearing Multiple Errors

```
$ err clear <fingerprint1> ... <fingerprintN>
```
Where `<fingerprintX>` is an [Fingerprint Expression](#error-fingerprint-expressions).

### Clearing All Errors

```
$ err clear all
```
