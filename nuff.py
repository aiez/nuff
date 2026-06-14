#!/usr/bin/env python3 -B
# nuff.py: tiny python tricks in one file -- records, io, format,
# rand, stats, columns, distance.  (c) 2026 Tim Menzies, MIT.
# No global config: pass params (p, cliff, conf, rng) as keywords.
import re, sys, random, traceback
from math import log2, log, exp, sqrt, pi
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

def settings(s):
  "Parse every var=val in a string into an o (vals coerced)."
  return o(**{k: thing(v) for k, v in re.findall(r"(\w+)=(\S+)", s)})

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

def main(g, help=None, argv=None, seed=1):
  """Run g's test_* fns: --name picks some, none = all; reseed each.
  -h prints `help` (default g's __doc__) + the commands. --seed=N
  sets the seed. Pass globals() as g."""
  fns = {k[5:]: v for k, v in g.items() if k.startswith("test_")}
  argv = sys.argv[1:] if argv is None else argv
  if "-h" in argv or "--help" in argv:
    print((help if help is not None else g.get("__doc__") or "").strip())
    print("\ncommands:", *(" --" + n for n in fns))
    return 0
  for a in argv:
    if a.startswith("--seed="): seed = int(a.split("=", 1)[1])
  named = [a[2:] for a in argv if a[:2] == "--" and "=" not in a]
  fails = 0
  for name in ([n for n in named if n in fns] or list(fns)):
    random.seed(seed)
    try: fns[name]()
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

# ---- columns: Num, Sym, Cols are all just o-records ------------
def Num(txt="", at=0):
  "Numeric column summary (an o-record)."
  return o(it=Num, txt=txt, at=at, n=0, mu=0, m2=0,
           heaven=0 if txt[-1:] == "-" else 1)

def Sym(txt="", at=0):
  "Symbolic column summary: counts live in `has`."
  return o(it=Sym, txt=txt, at=at, n=0, has={})

def add(i, v, inc=1):
  "Add v to a Num/Sym/Cols/Data, in place. Skips '?'; inc=-1 subtracts."
  if i.it is Cols: [add(col, v[col.at], inc) for col in i.all]
  elif i.it is Data:                                 
    (i.rows.append if inc == 1 else i.rows.remove)(v)
    add(i.cols, v, inc)
  elif v != "?": 
    i.n += inc
    if i.it is Sym: i.has[v] = i.has.get(v, 0) + inc
    elif i.n < 2 and inc < 0: i.n = i.mu = i.m2 = 0
    else: 
      d = v - i.mu
      i.mu += inc * d / i.n
      i.m2 += inc * d * (v - i.mu)
  return v

def adds(src, col=None):
  "Summarize an iterable into a Num (default) or given col."
  col = Num() if col is None else col
  for v in src: add(col, v)
  return col

def mid(col):
  "Central tendency: mean (Num) or mode (Sym)."
  return (max(col.has, key=col.has.get) if col.it is Sym
          else col.mu)

def spread(col):
  "Diversity: stdev (Num) or entropy (Sym)."
  if col.it is Sym:
    n = col.n
    return -sum(v/n * log2(v/n) for v in col.has.values())
  return (col.m2 / (col.n - 1)) ** 0.5 if col.n > 1 else 0

def norm(col, v):
  "Map v to 0..1 via a logistic on its z-score (Num only)."
  if v == "?": return v
  z = (v - col.mu) / (spread(col) + 1e-32)
  return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))

def Cols(names):
  """Summaries from header names, split into roles.
  Upper=Num, lower=Sym; +/-/! = goal y; ! = klass; X = skip."""
  cols = o(it=Cols, names=names, all=[], x=[], y=[], klass=None)
  for at, s in enumerate(names):
    col = Num(s, at) if s[0].isupper() else Sym(s, at)
    cols.all.append(col)
    if s[-1] == "X": continue
    (cols.y if s[-1] in "+-!" else cols.x).append(col)
    if s[-1] == "!": cols.klass = col
  return cols

def Data(src=None):
  "Table: data.cols (from the first row) + data.rows."
  src = iter(src or [])
  return adds(src, o(it=Data, cols=Cols(next(src, [])), rows=[]))

def clone(data, src=None):
  "New Data with data's columns; optionally seed with src rows."
  return adds(src or [], Data([data.cols.names]))

# ---- distance: exponent `p` is a keyword, never a global -------
def minkowski(vals, p=2):
  "Aggregate per-item distances via the p-norm."
  total, n = 0, 0
  for v in vals: total += v ** p; n += 1
  return (total / (n or 1)) ** (1 / p)

def disty(data, row, **kw):
  "Distance of a row to the best goals (0 = ideal)."
  return minkowski((abs(norm(c, row[c.at]) - c.heaven)
                    for c in data.cols.y), **kw)

def distx(data, r1, r2, **kw):
  "Distance between two rows over the x-columns."
  return minkowski((gap(c, r1[c.at], r2[c.at])
                    for c in data.cols.x), **kw)

def gap(col, u, v):
  "Distance between two values of one column (0..1)."
  if u == v == "?": return 1
  if col.it is Sym: return u != v           # Sym
  u = norm(col, u) if u != "?" else (1 if v == "?" else 0)
  v = norm(col, v) if v != "?" else (1 if u == "?" else 0)
  return abs(u - v)

# ---- bayes: naive-bayes likelihood (m, k carried as kwargs) ----
def like(col, v, prior=0, k=1):
  "How much a column likes value v (Sym: m-estimate, Num: gauss)."
  if col.it is Sym:
    return (col.has.get(v, 0) + k * prior) / (col.n + k)
  sd = spread(col) + 1e-32; z = 2 * sd * sd
  return exp(-(v - col.mu) ** 2 / z) / sqrt(pi * z)

def likes(data, row, nrows, nklasses, m=2, k=1):
  "Log-likelihood of a row under this data (naive bayes)."
  prior = (len(data.rows) + m) / (nrows + m * nklasses)
  ls = [like(c, v, prior, k) for c in data.cols.x
        if (v := row[c.at]) != "?"]
  return log(prior) + sum(log(x) for x in ls if x > 0)

def confuse(pairs):
  "From (want, got) pairs, an o(pd, pf, prec, acc) per unique want."
  out, n = {}, len(pairs)
  for k in sorted({want for want, _ in pairs}):
    tp = sum(want == k and got == k for want, got in pairs)
    fn = sum(want == k and got != k for want, got in pairs)
    fp = sum(want != k and got == k for want, got in pairs)
    tn = n - tp - fn - fp
    out[k] = o(label=k, pd=tp / (tp + fn + 1e-32),
               pf=fp / (fp + tn + 1e-32),
               prec=tp / (tp + fp + 1e-32), acc=(tp + tn) / (n + 1e-32))
  return out
