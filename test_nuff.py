#!/usr/bin/env python3 -B
"""test_nuff.py: nuff smoke tests.

Usage: python3 -B test_nuff.py [--name ...] [--seed=N]
  no --name runs every test; -h shows this help.
"""
import random
import os
from nuff import (o, csv, thing, settings, say, main, shuffle, some,
                  same, top_tier, Data, clone, likes, confuse,
                  disty, distx, tree, treePredict, treeShow)

def test_o():
  p = o(a=1, b=3.0); assert p.a == 1 and say(p.b) == "3"

def test_thing():
  assert thing("3") == 3 and thing("2.5") == 2.5 and thing("x") == "x"

def test_settings():
  s = settings("seed=1 p=2 who=tim")
  assert s.seed == 1 and s.p == 2 and s.who == "tim"

def test_rand():
  "Own RNG -> repeatable; no global state."
  r1, r2 = random.Random(1), random.Random(1)
  xs = list(range(20))
  assert shuffle(xs, rng=r1) == shuffle(xs, rng=r2)
  assert len(some(xs, 5, rng=random.Random(1))) == 5

def test_cols():
  d = Data([["name", "Age", "Weight-", "sick!"]])
  assert len(d.x) == 2 and len(d.y) == 2 and d.klass == 3
  assert d.names[d.klass] == "sick!"

def test_data():
  d = Data(csv("../optimiz/auto93.csv"))
  assert len(d.rows) == 398 and len(d.y) == 3
  assert distx(d, d.rows[0], d.rows[0]) == 0
  assert 0 <= disty(d, d.rows[0]) <= 1
  assert disty(d, d.rows[0], p=1) != disty(d, d.rows[0], p=3)

def test_like():
  "naive bayes self-classify beats chance (needs ../klassif)."
  f = "../klassif/diabetes.csv"
  if not os.path.exists(f): return
  d = Data(csv(f)); k = d.klass
  g = {}
  for r in d.rows: g.setdefault(r[k], []).append(r)
  ds = {cl: clone(d, rows) for cl, rows in g.items()}
  ok = sum(max(ds, key=lambda cl: likes(ds[cl], r, len(d.rows), len(ds)))
           == r[k] for r in d.rows)
  assert ok / len(d.rows) > 0.7

def test_confuse():
  "per-class pd/pf from (want, got) pairs."
  m = confuse([("a","a"), ("a","a"), ("b","b"), ("b","a")])
  assert m["a"].pd == 1 and m["b"].pd == 0.5 and m["a"].pf == 0.5

def test_stats():
  assert same([1,2,3,4], [1,2,3,4])
  assert not same([1,2,3,4], [7,8,9,10])
  assert list(top_tier({"a":[1,2,3], "b":[9,9,9]})) == ["a"]

def test_tree():
  "Build + print a min-variance tree on auto93."
  d = Data(csv("../optimiz/auto93.csv"))
  t = tree(d)
  assert t.at is not None                  # the root split
  assert 0 <= treePredict(t, d.rows[0]) <= 1
  treeShow(d, t)                            # the print check

if __name__ == "__main__":
  raise SystemExit(main(globals(), __doc__))   # __doc__ = help above
