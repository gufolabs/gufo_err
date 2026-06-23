# FAQ

## Multiple `err.setup()` calls

`err.setup()` is designed for exactly one call per process. Calling it twice raises `RuntimeError`. This prevents accidental double installation of exception hooks or middleware chain corruption.

If you need conditional setup, guard it yourself:

```python
from gufo.err import err

if not err.is_initialized:
    err.setup(name="service", version="1.0")
```

## How does the error fingerprint work?

The fingerprint is a stable **UUID v5** derived from these inputs:

- Service name (`name` in `setup()`)
- Service version (`version` in `setup()`)
- Exception class name
- Topmost stack frame module, callable, and source line
- Application top frame (if `root_module` is set)

All inputs are hashed with SHA-1 (default) to produce a 128-bit UUID. Two crashes produce the same fingerprint when their service context and error location match — even across process restarts. This makes deduplication reliable for tracking unique bugs.

Change any input (service name, version, exception type called from a different line, etc.) produces a new fingerprint.

## Using without `catch_all`

Yes. Set `catch_all=False` (the default) to leave `sys.excepthook` untouched and use error handling explicitly in code blocks:

```python
from gufo.err import err

err.setup(name="service", version="1.0")

def main():
    try:
        do_something()
    except Exception:
        err.process()  # collects current exception
```

Use this when you want structured error analysis for specific blocks without intercepting all unhandled exceptions.

## "File already exists" when writing error info files

`ErrorInfoMiddleware` uses exclusive-create file mode (`open(path, "xb")`). This is deliberate — it prevents duplicate error entries if the same exception fires twice before recovery. If you encounter a `FileExistsError`, the error was **already recorded for this crash**.

## Calling `err.process()` without an active exception

It is safe — nothing happens. `err.process()` checks the current exception context first; if there is no active exception, it returns immediately.

This means you do not need to wrap every call in a conditional check:

```python
from gufo.err import err

err.setup(name="service", version="1.0")

def safe_cleanup():
    try:
        cleanup()
    except SomeKnownError:
        pass  # no problem — err.process() does nothing without an active exception
    err.process()  # only records if something else raised above
```

## Compressing error info files

When `error_info_path` is set, you can optionally compress the output files with `error_info_compress`:

```python
err.setup(
    name="service", version="1.0",
    error_info_path="/var/crash",
    error_info_compress="gz",  # one of: "gz", "bz2", "xz"
)
```

Valid values are `"gz"` (GZip), `"bz2"` (BZip2), or `"xz"` (LZMA).
Useful for embedded environments with limited storage — a 40 KB error info file typically compresses to under 5 KB.

## Python version support

Gufo Err supports **Python 3.9 through 3.14**. For older versions, no compatibility guarantee exists. The library uses only stdlib modules — no external runtime dependencies.

## System exceptions (`SystemExit`, `KeyboardInterrupt`)

These are always re-raised through the original exception hook, not processed by Gufo Err. This is intentional — terminating a process should always be able to propagate.

## Can I use Gufo Err without Sentry?

Yes, and no external dependencies at all. The core package (`gufo.err`) has zero runtime dependencies. Sentry integration requires `pip install "gufo_err[sentry]"`. Without it, the Sentry middleware is simply unavailable — it does not affect anything else.

## How does `root_module` affect fingerprinting?

By default, fingerprints use the topmost stack frame. With `root_module="myapp"` set, a second frame pair from the application namespace (topmost frame within your code vs library/framework frames) is also included. This helps separate bugs in your code from upstream exceptions coming from third-party libraries.

## Can I disable traceback output?

Yes. Pass `format=None` to suppress all stderr output:

```python
err.setup(name="service", version="1.0", format=None)
```

This is useful when you only need file persistence without any console noise.

## Support and License

### What is the license of Gufo Err?

Gufo Err is released under the [3-clause BSD License](LICENSE.md).

### Where can I get support?

Please use GitHub Issues for bugs or Discussions for feature requests.

### Can I help the Gufo Err project financially?

Yes, you can support our work via [GitHub Sponsors](https://github.com/sponsors/gufolabs) or [Buy Me a Coffee](https://www.buymeacoffee.com/dvolodin). Your contributions help us continue developing and maintaining NOC as a high-quality open-source project.

## What is "Gufo"?

*Gufo* means *the Owl* in Italian.

## Why the owls?

We love owls and the viable parts of our technologies were proven at the project, named "the Owl".

## What is "Gufo Labs"?

[Gufo Labs](https://gufolabs.com/) is the italian company specialized on network and IT consulting, and on software research.

## What is "Gufo Stack"?

We've extracted core components behind the [NOC](https://getnoc.com/) and released them as independent packages, available under the terms of the 3-clause BSD license. Our software shares common code quality standards and is battle-proven under the high load. We hope our key components will help the engineers and the developers to build reliable networks and robust network management software. See [more for details](https://gufolabs.com/products/gufo-stack/).
