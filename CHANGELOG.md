# Changelog

Notable, interface-affecting changes. Newest first.

## 0.2.0 — unreleased

Lightweight column model (modeled on fft.py). **Breaking.**

- **Columns are bare values, not records.** `Sym` is now a
  `{value: count}` dict (`Sym = dict`); `Num` is a `(n, mu, m2)`
  tuple. Gone: the old `o`-records with `.txt/.at/.n/.has/.mu`.
  Read a Num's mean with `mu_(num)`; dispatch with `isa(col, Sym)`.
- **`Cols` removed.** Roles fold into `Data`, which is now
  `o(names, cols{at: col}, x, y, goal, klass, rows)`. Columns are
  keyed by their at-index, not held in a list of records.
  `data.cols.y` → `data.y`; `data.cols.klass.at` → `data.klass`.
- **`add(it, v, inc=1)` RETURNS the new `it`** (Num is an immutable
  tuple, so it cannot mutate in place). Use `it = add(it, v)`;
  `adds` does this for you. `inc=-1` subtracts; Num resets if n<2.
- **`merge` renamed to `mix(i, j, inc=1)`** (inc=-1 mixes j back out).
- **`o` is now `types.SimpleNamespace`** (was a `dict` subclass).
  Attribute access only — `d.x`, not `d["x"]`.
- **Removed** the `symp`/`nump` predicates (use `isa(col, Sym)`),
  the unused `n_`/`m2_` accessors (kept `mu_`), and the standalone
  `Cols`.
- **Fixed `gap`** for missing values: normalize the known values
  first, then push a missing value to the far end (max distance),
  per the ezr/Aha rule. Old code collapsed the gap toward 0.
- `data.goal[at]` is now a bool (`s[-1] == "+"`).
- Export `BIG = 1e32` (the "no cut yet" sentinel).
- **`like(col, v, n=0, prior=0, k=1)`** gains an `n` (row count)
  arg; the Sym denominator uses it instead of `sum(col.values())`
  (Sym no longer stores its own count). `likes` passes it for you.

## 0.1.0

- Initial release as **nuff** (renamed from `gape`). One-file,
  stdlib-only: records, io, rand, non-parametric stats, columns,
  distance, naive bayes. No global config — tuning via kwargs.
