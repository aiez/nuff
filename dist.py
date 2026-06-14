#!/usr/bin/env python3 -B
# dist.py: row distances. Uses data.py. The exponent `p` is a
# keyword (1=Manhattan, 2=Euclidean), never a global.
from data import Sym, norm

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
