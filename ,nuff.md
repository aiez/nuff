<!-- Copyright (c) 2026 Tim Menzies, MIT License https://opensource.org/licenses/MIT -->
<a href="https://timm.fyi"><img align="right" alt="Author" src="https://img.shields.io/badge/Author-timm-dc143c?logo=readme&logoColor=white"></a><img align="right" alt="Language" src="https://img.shields.io/badge/Language-Python%203.12+-000080?logo=python&logoColor=white"><img align="right" alt="Deps" src="https://img.shields.io/badge/Deps-0-32cd32?logo=checkmarx&logoColor=white"><a href="https://choosealicense.com/licenses/mit/"><img align="right" alt="License" src="https://img.shields.io/badge/License-MIT-32cd32?logo=open-source-initiative&logoColor=white"></a><img align="right" alt="Purpose" src="https://img.shields.io/badge/Purpose-Python·Tricks-7b68ee?logo=githubcopilot&logoColor=white">

### [http://tiny.cc/nuff](http://tiny.cc/nuff)
nuff: one tiny file of reusable Python tricks — attribute-dicts,
typed CSV, pretty-print, seeded randomness, non-parametric stats,
minimal column summaries, and row distances. Pure stdlib, zero
dependencies. The cut-down kernel under my bigger apps, **with no
global config**: every parameter (`p`, `cliff`, `conf`, `rng`) is
passed as a keyword, so any function lifts out into another project.

```python
from nuff import o, csv, say, Data, disty, same, shuffle
import random

d = Data(csv("../optimiz/auto93.csv"))         # build a table
say(disty(d, d.rows[0], p=1))                  # row->goal distance, p a kwarg
shuffle(rows, rng=random.Random(1))            # repeatable, own RNG
same(a, b, cliff=0.195, conf=1.36)             # are two samples the same?
```

**Sections:** [NAME](#name) | [DESIGN](#design) | [API](#api) | [STYLE](#style) | [LICENSE](#license) | [AUTHOR](#author)

**Files:** [nuff.py](#file-nuff-py) | [test_nuff.py](#file-test_nuff-py) | [Makefile](#file-makefile) | [pyproject.toml](#file-pyproject-toml)

## NAME

    nuff - one file of tiny stdlib python tricks (no global config)

## DESIGN

    One file, themed sections, no module-level `the`. Tuning rides
    along as keyword args, so any function drops into another app:
      disty(data, row, p=2)
      same(xs, ys, cliff=0.195, conf=1.36)
      shuffle(lst, rng=random.Random(seed))

## API

    records / io / format
      o(dict)        attribute access: d.x is d['x']
      thing(s)       coerce str -> int|float|bool|str
      settings(s)    every var=val in s -> an o (vals coerced)
      csv(file)      yield typed rows ('#' = comment)
      say(x, dec=2)  pretty str; whole floats as ints
      main(funs)     run funs[name] for each --name in argv

    rand   (pass your own random.Random(seed) for repeatability)
      shuffle(lst, rng)     shuffled copy
      some(lst, k, rng)     sample without replacement
      one(lst, rng)         one random item

    stats  (non-parametric "are these two the same?")
      cliffs(xs, ys)        Cliff's delta effect size 0..1
      ks(xs, ys)            Kolmogorov-Smirnov CDF gap
      same(xs, ys, cliff=.195, conf=1.36)
      top_tier(groups, ...) names tied for best (min median)

    columns / table  (Num, Sym, Cols, Data all just o-records)
      Num(txt,at) Sym(txt,at)  column summaries (Sym counts in .has)
      add(it,v,inc=1)          add v to a Num/Sym, or a row to a Data;
                               inc=-1 subtracts (Num resets if n<2)
      adds(src,it)             add every item of src to it
      mid(col) spread(col)     mean/mode, stdev/entropy
      norm(col,v)              0..1 via a logistic on v's z-score
      Cols(names)              -> o(names, all, x, y, klass) by role
      Data(rows)               -> o(cols, rows); first row = names
      clone(data, src=None)    new Data, same columns, fresh rows
                               Upper=Num lower=Sym; +/-/! goal; ! klass; X skip
      Data(rows)           header sets roles: Upper=Num, lower=Sym,
                           +/-/! = goal, X = skip

    distance  (exponent `p` is a keyword)
      minkowski(vals, p=2)
      disty(data, row, p=2)      distance to best goals (0=ideal)
      distx(data, r1, r2, p=2)   distance between two rows on x
      gap(col, u, v)             per-column value distance 0..1

    bayes  (naive bayes; m, k carried as kwargs, no global the)
      like(col, v, prior=0, k=1)            how a column likes a value
      likes(data, row, nrows, nklasses)     log-likelihood of a row
      confuse(pairs)                        (want,got) -> per-class
                                            o(pd, pf, prec, acc)

## STYLE

    Minimal python: one file, one-line comments, ~65-char lines,
    very short functions, `i` (not self), records over classes.
    Threshold for a new file vs a new gist: parts you *import* stay
    in here; *wholes* you *run* (apps, other languages, data) get
    their own gist.

## LICENSE

    MIT. https://choosealicense.com/licenses/mit/

## AUTHOR

    Tim Menzies <timm@ieee.org>
