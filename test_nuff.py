#!/usr/bin/env python3 -B
"""test_nuff.py: nuff smoke tests.

Usage: python3 -B test_nuff.py [--name ...] [--seed=N]
  no --name runs every test; -h shows this help.
"""
import random
import os
from nuff import (o, Sym, csv, thing, settings, say, sho, main, shuffle, some,
                  same, top_tier, Data, clone, likes, confuse,
                  disty, distx, tree, treePredict, treeShow)

def _confuseShow(name, m):
  "Print a confuse() result as an aligned per-class table (% scores, class RHS)."
  pct = lambda x: say(round(100 * x))             # 0.82 -> 82
  rows = [["n", "pd", "pf", "prec", "acc", ""]]
  for lab, c in sorted(m.items()):
    rows.append([say(c.n), pct(c.pd), pct(c.pf), pct(c.prec), pct(c.acc), str(lab)])
  print(f"\n{name}:")
  print(sho(rows, ">"*5 + "<"))                   # nums right, class label RHS

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
  "Build + print a min-variance regression tree on auto93."
  d = Data(csv("../optimiz/auto93.csv"))
  t = tree(d, leaf=30)                      # bigger leaf -> compact tree
  assert t.at is not None                  # the root split
  assert 0 <= treePredict(t, d.rows[0]) <= 1
  treeShow(d, t)                            # the print check

def test_tree_classify():
  "Classification trees (Y=Sym); print confuse stats for each dataset."
  for name, leaf, floor in [("diabetes", 30, 0.75), ("soybean", 20, 0.55)]:
    f = f"../klassif/{name}.csv"
    if not os.path.exists(f): continue
    d = Data(csv(f)); k = d.klass
    t = tree(d, y=lambda r: r[k], Y=Sym, leaf=leaf)   # discrete y -> class tree
    pairs = [(r[k], treePredict(t, r)) for r in d.rows]
    assert treePredict(t, d.rows[0]) in {r[k] for r in d.rows}  # leaf = label
    treeShow(d, t)                                  # show the tree
    m = confuse(pairs)                              # nuff's scorer
    _confuseShow(name, m)
    acc = sum(w == g for w, g in pairs) / len(pairs)
    assert acc > floor                              # self-classify beats chance
    assert all(0 <= c.pd <= 1 and 0 <= c.pf <= 1 for c in m.values())

if __name__ == "__main__":
  raise SystemExit(main(globals(), __doc__))   # __doc__ = help above
