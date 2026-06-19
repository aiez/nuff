# nuff TODO

## tree: `_impurity` mixes m2 (Num) and entropy (Sym)

Looks like it compares two different units/scales. It does NOT.

`_separate` builds the yes/no groups from `y(r)` into a `Y()`
accumulator. `Y` is fixed for the whole tree:
- regression  (`y=disty`, `Y=Num`) -> `_impurity` = m2 (total deviance)
- classification (`y=class`, `Y=Sym`) -> `_impurity` = entropy * count

So inside one `treeCut`'s `min()`, every candidate hits the SAME
branch. m2 vs m2, or entropy vs entropy. The branch is chosen once by
the tree's `Y`, never per-candidate. Units are consistent within every
comparison.

Caveat (real, but the code never trips it): scores from a regression
tree and a classification tree are not comparable to each other.

Possible cleanups to consider:
- [ ] Rename `_impurity` -> make the "score in the tree's own y-units"
      contract obvious; or split into `_devianceNum` / `_entropySym`
      dispatched by `Y` so the single-type invariant is explicit.
- [ ] Assert / document that `Y` matches the type of `y(r)` values.
- [ ] Decide if impurity should be per-row (mean) vs summed. Summed
      deviance is the standard CART criterion and is fine here (the
      yes/no partition covers a fixed row set), so probably leave it.
