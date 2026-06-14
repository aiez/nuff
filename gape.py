#!/usr/bin/env python3 -B
# gape.py: tiny python tricks in one file -- records, io, format,
# rand, stats, columns, distance.  (c) 2026 Tim Menzies, MIT.
# No global config: pass params (p, cliff, conf, rng) as keywords.
import sys, random, traceback
from math import log2
from bisect import bisect_left, bisect_right

# ---- records, io, format ----------------------------------------

class o(dict):
  "Dict with attribute access: d.x is d['x']."
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__
  def __repr__(i): return say(i)

def thing(s):
  "Coerce a string to int, float, bool, else str."
  s = s.strip()
  for fn in (int, float):
    try: return fn(s)
    except ValueError: pass
  return {"True": True, "False": False}.get(s, s)

def csv(file, clean=lambda s: s.partition("#")[0].split(",")):
  "Yield typed rows from a CSV file ('#' starts a comment)."
  with open(file, encoding="utf-8") as f:
    for line in f:
      row = clean(line)
      if any(x.strip() for x in row):
        yield [thing(x) for x in row]

def say(x, dec=2):
  "Pretty string: whole floats as ints, else `dec` places."
  if isinstance(x, float):
    return str(int(x)) if x == int(x) else f"{x:.{dec}f}"
  if isinstance(x, dict):
    return "{" + ", ".join(f"{k}: {say(v,dec)}"
                 for k, v in sorted(x.items())) + "}"
  if isinstance(x, (list, tuple)):
    return "[" + ", ".join(say(v, dec) for v in x) + "]"
  return str(x)

def main(funs, argv=None):
  "Run funs[name]() for each `--name` in argv; count fails."
  fails = 0
  for a in (sys.argv[1:] if argv is None else argv):
    name = a[2:] if a.startswith("--") else a
    if name in funs:
      try: funs[name]()
      except Exception: fails += 1; traceback.print_exc()
  return fails

# ---- rand: pass your own random.Random(seed) for repeatability -

def shuffle(lst, rng=random):
  "Shuffled copy via the given RNG (no global config)."
  lst = lst[:]; rng.shuffle(lst); return lst

def some(lst, k=512, rng=random):
  "Up to k items sampled without replacement, via rng."
  return rng.sample(lst, min(k, len(lst)))

def one(lst, rng=random):
  "One random item via rng."
  return rng.choice(lst)

# ---- stats: are two samples the same? ---------------------------

def cliffs(xs, ys):
  "Cliff's delta effect size in 0..1 (0=identical)."
  ys = sorted(ys); m = len(ys)
  gt = sum(bisect_left(ys, x)      for x in xs)   # ys below x
  lt = sum(m - bisect_right(ys, x) for x in xs)   # ys above x
  return abs(gt - lt) / (len(xs) * m + 1e-32)

def ks(xs, ys):
  "Kolmogorov-Smirnov: max gap between the two CDFs."
  xs, ys = sorted(xs), sorted(ys)
  n, m = len(xs), len(ys)
  gap = lambda v: abs(bisect_right(xs, v)/n
                     - bisect_right(ys, v)/m)
  return max(map(gap, xs + ys))

def same(xs, ys, cliff=0.195, conf=1.36):
  "True if xs,ys are statistically indistinguishable."
  if cliffs(xs, ys) > cliff: return False
  n, m = len(xs), len(ys)
  return ks(xs, ys) <= conf * ((n + m) / (n * m)) ** 0.5

def top_tier(groups, cliff=0.195, conf=1.36):
  "Groups {name:nums} tied for best (lowest median wins)."
  rank = lambda lst: sorted(lst)[len(lst) // 2]
  items = sorted(groups.items(), key=lambda kv: rank(kv[1]))
  best, (k0, lst0) = {}, items[0]
  for k, lst in items:
    if k == k0 or same(lst0, lst, cliff, conf): best[k] = lst
    else: break
  return best

# ---- columns: Num (slots/tuple-backed), Sym (dict) --------------

class Num:
  "Numeric column: running n, mean, m2, lo, hi, goal."
  __slots__ = "txt at n mu m2 lo hi heaven".split()
  def __init__(i, txt="", at=0):
    i.txt, i.at, i.n, i.mu, i.m2 = txt, at, 0, 0, 0
    i.lo, i.hi = 1e32, -1e32
    i.heaven = 0 if txt[-1:] == "-" else 1

class Sym:
  "Symbolic column: counts of each seen value."
  __slots__ = "txt at n has".split()
  def __init__(i, txt="", at=0):
    i.txt, i.at, i.n, i.has = txt, at, 0, {}

def add(col, v, inc=1):
  "Update a Num or Sym with value v (inc times). Skips '?'."
  if v == "?": return v
  col.n += inc
  if type(col) is Sym:
    col.has[v] = col.has.get(v, 0) + inc
  else:
    col.lo, col.hi = min(col.lo, v), max(col.hi, v)
    d = v - col.mu; col.mu += d / col.n
    col.m2 += d * (v - col.mu)
  return v

def adds(src, col=None):
  "Summarize an iterable into a Num (default) or given col."
  col = Num() if col is None else col
  for v in src: add(col, v)
  return col

def mid(col):
  "Central tendency: mean (Num) or mode (Sym)."
  return (max(col.has, key=col.has.get)
          if type(col) is Sym else col.mu)

def spread(col):
  "Diversity: stdev (Num) or entropy (Sym)."
  if type(col) is Sym:
    n = col.n
    return -sum(v/n * log2(v/n) for v in col.has.values())
  return (col.m2 / (col.n - 1)) ** 0.5 if col.n > 1 else 0

def norm(col, v):
  "Map v to 0..1 over the seen lo..hi (Num only)."
  if v == "?": return v
  return (v - col.lo) / (col.hi - col.lo + 1e-32)

def Data(src=None):
  "Table: column summaries (x, y, all) + the raw rows."
  data = o(x=[], y=[], all=[], rows=[])
  for row in (src or []): row1(data, row)
  return data

def row1(data, row):
  "Add a row; the first row (names) builds the columns."
  if data.all:
    for col in data.all: add(col, row[col.at])
    data.rows.append(row)
  else:
    for at, s in enumerate(row):
      col = (Num if s[0].isupper() else Sym)(s, at)
      data.all.append(col)
      if s[-1] != "X":
        (data.y if s[-1] in "+-!" else data.x).append(col)
  return data

# ---- distance: exponent `p` is a keyword, never a global -------

def minkowski(vals, p=2):
  "Aggregate per-item distances via the p-norm."
  total, n = 0, 0
  for v in vals: total += v ** p; n += 1
  return (total / (n or 1)) ** (1 / p)

def disty(data, row, p=2):
  "Distance of a row to the best goals (0 = ideal)."
  return minkowski((abs(norm(c, row[c.at]) - c.heaven)
                    for c in data.y), p=p)

def distx(data, row1, row2, p=2):
  "Distance between two rows over the x-columns."
  return minkowski((gap(c, row1[c.at], row2[c.at])
                    for c in data.x), p=p)

def gap(col, u, v):
  "Distance between two values of one column (0..1)."
  if u == v == "?": return 1
  if type(col) is Sym: return u != v
  u = norm(col, u) if u != "?" else (1 if v == "?" else 0)
  v = norm(col, v) if v != "?" else (1 if u == "?" else 0)
  return abs(u - v)
