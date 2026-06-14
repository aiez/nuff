<!-- Copyright (c) 2026 Tim Menzies, MIT License https://opensource.org/licenses/MIT -->
<a href="https://timm.fyi"><img align="right" alt="Author" src="https://img.shields.io/badge/Author-timm-dc143c?logo=readme&logoColor=white"></a><img align="right" alt="Language" src="https://img.shields.io/badge/Language-Python%203.12+-000080?logo=python&logoColor=white"><img align="right" alt="Deps" src="https://img.shields.io/badge/Deps-0-32cd32?logo=checkmarx&logoColor=white"><a href="https://choosealicense.com/licenses/mit/"><img align="right" alt="License" src="https://img.shields.io/badge/License-MIT-32cd32?logo=open-source-initiative&logoColor=white"></a><img align="right" alt="Purpose" src="https://img.shields.io/badge/Purpose-Python·Tricks-7b68ee?logo=githubcopilot&logoColor=white">

### [http://tiny.cc/gape](http://tiny.cc/gape)
gape: a tiny pocketful of reusable Python tricks — attribute-dicts,
typed CSV, pretty-print, non-parametric stats, minimal column
summaries, and row distances. Pure stdlib, zero dependencies. The
cut-down kernel under my bigger apps, **with no global config**:
every parameter (`p`, `cliff`, `conf`) is passed as a keyword, so
the functions drop cleanly into any other project.

```python
from gape import o, csv, thing, say, cliffs, ks, same, top_tier
from data import Data, Num, Sym, add, adds, mid, spread, norm
from dist import disty, distx, minkowski

d = Data(csv("../optimiz/auto93.csv"))     # build a table
say(disty(d, d.rows[0], p=1))              # row->goal distance, p as a kwarg
same(a, b, cliff=0.195, conf=1.36)         # are two samples the same?
```

**Sections:** [NAME](#name) | [DESIGN](#design) | [GAPE](#gape) | [DATA](#data) | [DIST](#dist) | [STYLE](#style) | [LICENSE](#license) | [AUTHOR](#author)

**Files:** [gape.py](#file-gape-py) | [data.py](#file-data-py) | [dist.py](#file-dist-py) | [pyproject.toml](#file-pyproject-toml)

## NAME

    gape - tiny stdlib python tricks (no global config)

## DESIGN

    No module-level `the`. State and tuning ride along as
    keyword args, so any function lifts out into another app:
      disty(data, row, p=2)
      same(xs, ys, cliff=0.195, conf=1.36)
    Layering (each uses the one above, never the reverse):
      gape.py  -> data.py -> dist.py

## GAPE

    gape.py -- io, records, format, stats:
      o(dict)        attribute access: d.x is d['x']
      thing(s)       coerce str -> int|float|bool|str
      csv(file)      yield typed rows ('#' = comment)
      say(x, dec=2)  pretty str; whole floats as ints
      main(funs)     run funs[name] for each --name in argv
      cliffs(xs,ys)  Cliff's delta effect size (0..1)
      ks(xs,ys)      Kolmogorov-Smirnov CDF gap
      same(xs,ys, cliff=.195, conf=1.36)  same distribution?
      top_tier(groups, ...)  names tied for best (min median)

## DATA

    data.py (uses gape) -- minimal columns + table:
      Num            slots-backed numeric summary (n,mu,m2,lo,hi)
      Sym            dict-of-counts symbolic summary
      add(col,v)     update a column (skips '?')
      adds(src,col)  summarize an iterable
      mid(col)       mean (Num) or mode (Sym)
      spread(col)    stdev (Num) or entropy (Sym)
      norm(col,v)    map v to 0..1 over lo..hi
      Data(rows)     table; header names set roles:
                       Upper=Num, lower=Sym, +/-/! = goal, X=skip

## DIST

    dist.py (uses data) -- row distances, exponent `p` a keyword:
      minkowski(vals, p=2)     p-norm aggregate
      disty(data, row, p=2)    distance to best goals (0=ideal)
      distx(data, r1, r2, p=2) distance between two rows on x
      gap(col, u, v)           per-column value distance (0..1)

## STYLE

    Minimal python: one-line comments, ~65-char lines, very
    short functions, `i` (not self), records over heavy classes.

## LICENSE

    MIT. https://choosealicense.com/licenses/mit/

## AUTHOR

    Tim Menzies <timm@ieee.org>
