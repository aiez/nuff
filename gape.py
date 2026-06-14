#!/usr/bin/env python3 -B
# gape.py: tiny python tricks -- io, records, format, stats.
# (c) 2026 Tim Menzies, timm@ieee.org, MIT license.
# No global config: pass params (cliff, conf, ...) as keywords.
import sys, traceback
from bisect import bisect_left, bisect_right

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
  "Yield typed rows from a CSV file (# starts a comment)."
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

# ---- stats: non-parametric "are these two samples the same?" ----

def cliffs(xs, ys):
  "Cliff's delta effect size in 0..1 (0=identical)."
  ys = sorted(ys); m = len(ys)
  gt = sum(bisect_left(ys, x)  for x in xs)   # ys below x
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
