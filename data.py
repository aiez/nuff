#!/usr/bin/env python3 -B
# data.py: minimal columns + table. Uses gape.py.
# Num is slots-backed (tuple-like); Sym is a dict of counts.
from math import log2
from gape import o

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
