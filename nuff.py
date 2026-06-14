#!/usr/bin/env python3 -B
# nuff.py: tiny python tricks in one file -- records, io, format,
# rand, stats, columns, distance.  (c) 2026 Tim Menzies, MIT.
# No global config: pass params (p, cliff, conf, rng) as keywords.
import re, sys, random, traceback
from math import log2, log, exp, sqrt, pi
from bisect import bisect_left, bisect_right
from types import SimpleNamespace as o    # attr-record: o(a=1).a == 1

# ---- records, io, format ----------------------------------------
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
  if isinstance(x, o): x = vars(x)                 # unwrap a namespace
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

# ---- columns: Sym = {value:count}, Num = (n, mu, m2) -----------
def Sym(): return {}
def Num(n=0, mu=0, m2=0): return (n, mu, m2)

def n_(x):  return x[0]
def mu_(x): return x[1]
def m2_(x): return x[2]

def symp(x): return isinstance(x, dict)    # dict = Sym (o is not a dict)
def nump(x): return isinstance(x, tuple)   # tuple = Num

def sd(num):
  "Standard deviation of a Num from its m2."
  n, mu, m2 = num
  return 0 if n < 2 else (max(0, m2) / (n - 1)) ** 0.5

def welford(num, v, inc=1):
  "Num + v (inc=-1 removes); returns a new (n, mu, m2)."
  n, mu, m2 = num
  if (n := n + inc) <= 0: return Num()
  d = v - mu; mu += inc * d / n
  return n, mu, m2 + inc * d * (v - mu)

def norm(num, v):
  "Map v to 0..1 via a logistic on its z-score (Num only)."
  if v == "?": return v
  z = (v - mu_(num)) / (sd(num) + 1e-32)
  return 1 / (1 + exp(-1.7 * max(-3, min(3, z))))

def mix(i, j, inc=1):
  "Combine two same-type cols; inc=-1 removes j from i."
  if symp(i):
    return {k: i.get(k, 0) + inc * j.get(k, 0) for k in i | j}
  i_n, i_mu, i_m2 = i; j_n, j_mu, j_m2 = j
  n = i_n + inc * j_n
  if n <= 0: return Num()
  mu = (i_n * i_mu + inc * j_n * j_mu) / n
  d  = j_mu - i_mu
  m2 = i_m2 + inc * j_m2 + inc * d * d * i_n * j_n / n
  return Num(n, mu, m2)

# ---- table: roles in Data, columns held by at-index -----------
def Data(src=None):
  """Table o(names, cols{at:col}, x, y, goal, klass, rows).
  Upper=Num lower=Sym; +/-/! = goal y; + maximizes; ! klass; X skip."""
  src = iter(src or [])
  data = o(names=[], cols={}, x=[], y=[], goal={}, klass=None, rows=[])
  roles(data, next(src, []))
  return adds(src, data)

def roles(data, names):
  "Read header names into column roles (mutates data)."
  data.names = names
  for at, s in enumerate(names):
    data.cols[at] = Num() if s[0].isupper() else Sym()
    if s[-1] == "X": continue
    if s[-1] in "+-!":
      data.y.append(at); data.goal[at] = 1 if s[-1] == "+" else 0
      if s[-1] == "!": data.klass = at
    else: data.x.append(at)

def add(it, v, inc=1):
  "Add to a Sym/Num/Data; RETURNS the (new) it. Skips '?'."
  if symp(it):
    if v != "?": it[v] = it.get(v, 0) + inc
    return it
  if nump(it):
    return welford(it, v, inc) if v != "?" else it
  (it.rows.append if inc == 1 else it.rows.remove)(v)      # Data: v a row
  for at in it.cols: it.cols[at] = add(it.cols[at], v[at], inc)
  return it

def adds(src, it=None):
  "Fold src into it (a fresh Num by default); returns it."
  if it is None: it = Num()
  for v in src: it = add(it, v)
  return it

def clone(data, src=None):
  "New Data with data's columns; optionally seed with src rows."
  return adds(src or [], Data([data.names]))

def mid(col):
  "Central tendency: mode (Sym) or mean (Num)."
  return max(col, key=col.get) if symp(col) else mu_(col)

def spread(col):
  "Diversity: entropy (Sym) or stdev (Num)."
  if nump(col): return sd(col)
  n = sum(col.values())
  return -sum(c/n * log2(c/n) for c in col.values())

# ---- distance: exponent `p` is a keyword, never a global -------
def minkowski(vals, p=2):
  "Aggregate per-item distances via the p-norm."
  total, n = 0, 0
  for v in vals: total += v ** p; n += 1
  return (total / (n or 1)) ** (1 / p)

def disty(data, row, **kw):
  "Distance of a row to the best goals (0 = ideal)."
  return minkowski((abs(norm(data.cols[at], row[at]) - data.goal[at])
                    for at in data.y if row[at] != "?"), **kw)

def distx(data, r1, r2, **kw):
  "Distance between two rows over the x-columns."
  return minkowski((gap(data.cols[at], r1[at], r2[at])
                    for at in data.x), **kw)

def gap(col, u, v):
  "Distance between two values of one column (0..1)."
  if u == v == "?": return 1
  if symp(col): return u != v               # Sym
  u = norm(col, u) if u != "?" else (1 if v == "?" else 0)
  v = norm(col, v) if v != "?" else (1 if u == "?" else 0)
  return abs(u - v)

# ---- bayes: naive-bayes likelihood (m, k carried as kwargs) ----
def like(col, v, prior=0, k=1):
  "How much a column likes value v (Sym: m-estimate, Num: gauss)."
  if symp(col):
    return (col.get(v, 0) + k * prior) / (sum(col.values()) + k)
  s = sd(col) + 1e-32; z = 2 * s * s
  return exp(-(v - mu_(col)) ** 2 / z) / sqrt(pi * z)

def likes(data, row, nrows, nklasses, m=2, k=1):
  "Log-likelihood of a row under this data (naive bayes)."
  prior = (len(data.rows) + m) / (nrows + m * nklasses)
  ls = [like(data.cols[at], v, prior, k) for at in data.x
        if (v := row[at]) != "?"]
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
