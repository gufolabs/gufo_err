# ---------------------------------------------------------------------
# Gufo Err: failfast module
# ---------------------------------------------------------------------
# Copyright (C) 2022-23, Gufo Labs
# ---------------------------------------------------------------------
"""
Fail-fast handlers.

Fail-fast handlers are launched on every unnhandled
exception and have to deside if the error is fatal
and the process must be terminated quickly.
See [gufo.err.abs.failfast.BaseFailFast] for details.

The following fail-fast handlers are available out-of-the-box:

* [AlwaysFailFast][gufo.err.failfast.always.AlwaysFailFast]:
  Triggers fail-fast unconditionaly.
* [NeverFailFast][gufo.err.failfast.never.NeverFailFast]:
  Never triggers fail-fast.
* [TypeMatchFailFast][gufo.err.failfast.typematch.TypeMatchFailFast]:
  Fail-fast on the given exception types and optional substrings.
* [TypesFailFast][gufo.err.failfast.types.TypesFailFast]:
  Fail-fast on the given list of exception types.
"""
