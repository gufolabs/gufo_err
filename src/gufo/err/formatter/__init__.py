# ---------------------------------------------------------------------
# Gufo Err: format module
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""
ErrInfo formatters.

Formatters process [ErrorInfo][gufo.err.ErrorInfo]
structure and produces human-readable output.

Available out-of-box:

* [TerseFormatter][gufo.err.formatter.terse.TerseFormatter]:
  condensed minimal output.
* [ExtendFormatter][gufo.err.formatter.extend.ExtendFormatter]:
  extended detailed output.

Configured formatter instances can be obtained via
[get_formatter()][gufo.err.formatter.loader.get_formatter]
function.
"""
