"""Recovery and invariant tests for the generator, damage, estimators and metrics.

Run: python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paper4 import methods as M  # noqa: E402
from paper4.effects import companion_radius, cumulative, irf, mean_lag  # noqa: E402
from paper4.estimator import fit_equations, parent_terms  # noqa: E402
from paper4.generator import GeneratorConfig, add_latent, add_measurement_noise, build_dynamic_sem  # noqa: E402
from paper4.metrics import evaluate, interval_score, truth_effects  # noqa: E402
from paper4.skeleton import Skeleton, _creates_cycle, damage, true_skeleton  # noqa: E402
from paper4.topology import Topology, load_bank  # noqa: E402


def toy_topology() -> Topology:
    nodes = tuple("ABCDEF")
    edges = (("A", "B"), ("B", "C"), ("A", "D"), ("D", "C"), ("C", "E"), ("E", "F"), ("B", "F"))
    return Topology("toy", "toy", "development", "hand", nodes, edges, "")


def toy_sem(seed: int, **kw):
    return build_dynamic_sem(toy_topology(), GeneratorConfig(**kw), np.random.default_rng(seed))


class EffectsTest(unittest.TestCase):
    def test_irf_matches_hand_computation(self):
        # x1_t = 0.5 x1_{t-1} + e1 ;  x2_t = 0.8 x1_t + e2
        B = np.zeros((2, 2, 2))
        B[1, 0, 0] = 0.5
        B[0, 1, 0] = 0.8
        theta = irf(B, 3)
        np.testing.assert_allclose(theta[:, 0, 0], [1, 0.5, 0.25, 0.125])
        np.testing.assert_allclose(theta[:, 1, 0], [0.8, 0.4, 0.2, 0.1])
        self.assertAlmostEqual(cumulative(theta, 3)[1, 0], 1.5)
        self.assertAlmostEqual(mean_lag(theta, 3)[1, 0], (0.4 + 0.4 + 0.3) / 1.5)

    def test_mean_lag_tolerates_small_opposite_mass_only(self):
        theta = np.zeros((3, 2, 2))
        theta[:, 1, 0] = [-0.02, 0.5, 0.5]       # 2% opposite mass: noise, lag stays defined
        self.assertTrue(np.isfinite(mean_lag(theta, 2)[1, 0]))
        theta[:, 1, 0] = [-0.4, 0.5, 0.5]        # 29% opposite mass: undefined
        self.assertTrue(np.isnan(mean_lag(theta, 2)[1, 0]))


class GeneratorTest(unittest.TestCase):
    def test_stationary_and_one_lag_per_edge(self):
        for seed in range(20):
            sem = toy_sem(seed)
            self.assertLess(companion_radius(sem.B), 0.9)
            self.assertEqual(len(sem.edge_lag), len(toy_topology().edges))
            cross = sem.B.copy()
            cross[:, np.arange(sem.n), np.arange(sem.n)] = 0
            self.assertEqual(int((cross != 0).sum()), len(toy_topology().edges))

    def test_contemporaneous_part_is_acyclic(self):
        sem = toy_sem(0, q0=1.0)
        self.assertTrue(np.all(np.linalg.eigvals(sem.B[0]) == 0))  # nilpotent iff acyclic


class DamageTest(unittest.TestCase):
    def setUp(self):
        self.sem = toy_sem(3, q0=0.5)
        self.skel = true_skeleton(self.sem)

    def test_counts_and_acyclicity(self):
        n_true = len(self.skel.pairs())
        k = int(np.floor(0.3 * n_true + 0.5))
        miss = damage(self.skel, "missing", 0.3, np.random.default_rng(0))
        self.assertEqual(len(miss.pairs()), n_true - k)
        extra = damage(self.skel, "extra", 0.3, np.random.default_rng(0))
        self.assertEqual(len(extra.pairs()), n_true + k)
        self.assertTrue(self.skel.pairs() <= extra.pairs())
        for s in (miss, extra):
            self.assertFalse(_creates_cycle(s.oriented, s.n))
            self.assertEqual(s.damage["k"], k)

    def test_reversed_touches_contemporaneous_edges_only(self):
        rev = damage(self.skel, "reversed", 1.0, np.random.default_rng(0), self.sem.edge_lag)
        for entry in rev.log:
            self.assertEqual(entry["true_lag"], 0)
        self.assertEqual(rev.pairs(), self.skel.pairs())
        self.assertFalse(_creates_cycle(rev.oriented, rev.n))

    def test_rates_are_nested(self):
        lo = damage(self.skel, "missing", 0.2, np.random.default_rng(5))
        hi = damage(self.skel, "missing", 0.5, np.random.default_rng(5))
        self.assertTrue(hi.pairs() <= lo.pairs())

    def test_public_record_hides_damaged_pairs(self):
        miss = damage(self.skel, "missing", 0.3, np.random.default_rng(0))
        self.assertEqual(set(miss.damage), {"kind", "rate", "k"})
        rec = miss.to_interface(self.sem.nodes, T=40, lag_max=2, generator_id="toy", seed=[1, 2])
        self.assertNotIn("log", rec)
        a = np.array(rec["adjacency"])
        self.assertTrue((a == a.T).all())


class StructuredDamageTest(unittest.TestCase):
    def setUp(self):
        self.sem = toy_sem(3, q0=0.5)
        self.truth = true_skeleton(self.sem)
        self.coef = {e: float(self.sem.B[l, e[1], e[0]]) for e, l in self.sem.edge_lag.items()}

    def test_weak_missing_drops_weakest(self):
        s = damage(self.truth, "weak_missing", 0.3, np.random.default_rng(0), self.sem.edge_lag, self.coef)
        k = s.damage["missing"]
        dropped = {frozenset(e["pair"]) for e in s.log}
        strength = {frozenset(e): abs(c) for e, c in self.coef.items()}
        weakest = sorted(self.truth.pairs(), key=lambda p: (strength[p], sorted(p)))
        self.assertEqual(dropped, set(weakest[:k]))

    def test_shortcut_keeps_pair_count_and_acyclicity(self):
        s = damage(self.truth, "shortcut", 0.3, np.random.default_rng(1), self.sem.edge_lag, self.coef)
        self.assertEqual(len(s.pairs()), len(self.truth.pairs()))
        self.assertEqual(s.damage["missing"], s.damage["extra"])
        self.assertFalse(_creates_cycle(s.oriented, s.n))

    def test_stated_counts_read_both_formats(self):
        self.assertEqual(M.stated_counts({"kind": "missing", "rate": 0.2, "k": 3}),
                         {"missing": 3, "extra": 0, "reversed": 0})
        self.assertEqual(M.width_key({"kind": "shortcut", "missing": 2, "extra": 2, "reversed": 0}), "missing")


class EstimatorTest(unittest.TestCase):
    def test_lags_admitted_both_ways_contemporaneous_by_orientation(self):
        skel = Skeleton(3, oriented={(0, 1)}, undetermined={frozenset((1, 2))})
        t1, t0 = parent_terms(skel, 1, 2), parent_terms(skel, 0, 2)
        self.assertIn((0, 0), t1)
        self.assertNotIn((1, 0), t0)
        self.assertIn((1, 1), t0)            # reverse lagged term is admitted
        self.assertNotIn((2, 0), t1)         # undetermined pair: no contemporaneous term
        self.assertIn((2, 2), t1)

    def test_oracle_recovers_truth(self):
        sem = toy_sem(5)
        data = sem.simulate(20000, np.random.default_rng(6))
        skel = true_skeleton(sem, with_lags=True)
        fit = fit_equations(data, [parent_terms(skel, j, sem.lag_max) for j in range(sem.n)], sem.lag_max)
        np.testing.assert_allclose(fit.B, sem.B, atol=0.03)

    def test_underdetermined_flag(self):
        sem = toy_sem(1)
        full = Skeleton(sem.n, oriented={(u, v) for u in range(sem.n) for v in range(u + 1, sem.n)})
        f = fit_equations(sem.simulate(12, np.random.default_rng(2)),
                          [parent_terms(full, j, sem.lag_max) for j in range(sem.n)], sem.lag_max)
        self.assertEqual(f.status, "underdetermined")

    def test_ridge_with_zero_penalty_equals_ols(self):
        sem = toy_sem(2)
        data = sem.simulate(300, np.random.default_rng(3))
        terms = [parent_terms(true_skeleton(sem), j, 2) for j in range(sem.n)]
        ols = fit_equations(data, terms, 2)
        ridge = fit_equations(data, terms, 2, [np.zeros(len(t)) for t in terms])
        np.testing.assert_allclose(ols.B, ridge.B, atol=1e-10)


class MethodsTest(unittest.TestCase):
    def setUp(self):
        self.sem = toy_sem(8)
        self.data = self.sem.simulate(300, np.random.default_rng(9))
        self.truth = true_skeleton(self.sem)

    def test_plugin_covers_on_true_skeleton(self):
        res = M.plugin(self.data, self.truth, 2, 4, 199, np.random.default_rng(10))
        row = evaluate(self.sem, res, 4)
        self.assertGreater(row["coverage_nonnull"], 0.75)

    def test_inflate_widens_about_midpoint(self):
        base = M.plugin(self.data, self.truth, 2, 4, 49, np.random.default_rng(1))
        wide = M.inflate(base, 2.0)
        np.testing.assert_allclose(wide.hi - wide.lo, 2 * (base.hi - base.lo))
        np.testing.assert_allclose(wide.hi + wide.lo, base.hi + base.lo)

    def test_lp_allpast_is_consistent(self):
        data = self.sem.simulate(20000, np.random.default_rng(11))
        res = M.lp_allpast(data, self.truth, 2, 4)
        _, C_true, _, _ = __import__("paper4.metrics", fromlist=["truth_effects"]).truth_effects(self.sem, 4)
        off = ~np.eye(self.sem.n, dtype=bool)
        self.assertLess(np.max(np.abs(res.C - C_true)[off]), 0.15)

    def test_soft_recovers_missing_lagged_edge(self):
        sem = toy_sem(4, q0=0.0)                     # all edges lagged
        data = sem.simulate(2000, np.random.default_rng(5))
        for seed in range(50):  # pick a deletion that actually cuts a path
            miss = damage(true_skeleton(sem), "missing", 0.3, np.random.default_rng(seed), sem.edge_lag)
            hard = M.plugin(data, miss, 2, 4, 0, None)
            r_hard = evaluate(sem, hard, 4)
            if r_hard["n_lost"] > 0:
                break
        self.assertGreater(r_hard["n_lost"], 0)
        soft = M.soft(data, miss, 2, 4, 19, np.random.default_rng(7))
        r_soft = evaluate(sem, soft, 4)
        self.assertEqual(r_soft["n_lost"], 0)
        self.assertLess(r_soft["C_abs_err_nonnull"], r_hard["C_abs_err_nonnull"])

    def test_tolerant_equals_plugin_without_stated_damage(self):
        a = M.plugin(self.data, self.truth, 2, 4, 29, np.random.default_rng(3))
        b = M.tolerant(self.data, self.truth, 2, 4, 29, np.random.default_rng(3))
        np.testing.assert_allclose(a.C, b.C)
        np.testing.assert_allclose(a.lo, b.lo)
        np.testing.assert_allclose(a.hi, b.hi)

    def test_repair_finds_removed_contemporaneous_edge(self):
        sem = toy_sem(4, q0=1.0)                     # all edges contemporaneous
        data = sem.simulate(3000, np.random.default_rng(5))
        truth = true_skeleton(sem)
        (u, v) = sorted(truth.oriented)[0]
        skel = truth.copy()
        skel.oriented.discard((u, v))
        skel.damage = {"kind": "missing", "rate": 0.15, "k": 1}
        res = M.tolerant(data, skel, 2, 4, 19, np.random.default_rng(6))
        self.assertEqual(res.info["n_repair"], 1)
        terms = [M.soft_terms(skel, j, 2) for j in range(sem.n)]
        resid = M.fit_equations(data, terms, 2).residuals
        self.assertEqual(M.repair_candidates(resid, skel, 1), [(min(u, v), max(u, v))])

    def test_interval_score(self):
        self.assertAlmostEqual(float(interval_score(0.0, 1.0, 0.5)), 1.0)
        self.assertAlmostEqual(float(interval_score(0.0, 1.0, 1.5)), 1.0 + 40 * 0.5)


class TopologyBankTest(unittest.TestCase):
    def test_banks_verify(self):
        for name in ("D-07", "D-07H"):
            bank = load_bank(name, split=None)
            self.assertEqual(len(bank), 40)
            self.assertEqual(sum(t.split == "development" for t in bank), 20)
            for topo in bank:
                self.assertEqual(topo.n_nodes, 14)
                self.assertEqual(len(topo.edges), 21)
                topo.topological_order()


class ExtensionTest(unittest.TestCase):
    """A-group extensions: latent confounders, measurement noise, published baselines, learned skeletons."""

    def setUp(self):
        topo = load_bank("D-07", "development")[0]
        self.sem = build_dynamic_sem(topo, GeneratorConfig(), np.random.default_rng(1))

    def test_latent_keeps_observed_truth(self):
        aug = add_latent(self.sem, 2, np.random.default_rng(2))
        self.assertEqual(aug.n, self.sem.n)
        self.assertEqual(aug.n_all, self.sem.n + 2)
        np.testing.assert_allclose(truth_effects(aug, 4)[1], truth_effects(self.sem, 4)[1])
        self.assertEqual(aug.simulate(30, np.random.default_rng(3)).shape, (30, self.sem.n))
        # nested: the first latent node is the same whether one or two are added
        one = add_latent(self.sem, 1, np.random.default_rng(2))
        np.testing.assert_allclose(one.B[:, :, -1], aug.B[:, : self.sem.n + 1, self.sem.n])

    def test_measurement_noise_ratio(self):
        x = np.random.default_rng(4).normal(size=(20000, 3)) * [1.0, 2.0, 3.0]
        y = add_measurement_noise(x, 0.5, np.random.default_rng(5))
        np.testing.assert_allclose(y.var(axis=0) / x.var(axis=0), 1.5, rtol=0.05)

    def test_equivalence_class(self):
        truth = true_skeleton(self.sem)
        members = M.equivalence_class(truth.oriented, self.sem.n, 1000, np.random.default_rng(6))
        self.assertEqual(members[0], truth.oriented)
        target = M._vstructures(truth.oriented, self.sem.n)
        for dag in members:
            self.assertEqual({frozenset(e) for e in dag}, truth.pairs())
            self.assertEqual(M._vstructures(dag, self.sem.n), target)
        self.assertEqual(len({frozenset(d) for d in members}), len(members))

    def test_published_baselines_run(self):
        data = self.sem.simulate(80, np.random.default_rng(7))
        skel = true_skeleton(self.sem)
        for f in (M.ida_union, M.bvar_minnesota):
            res = f(data, skel, 2, 4, 39, np.random.default_rng(8))
            self.assertEqual(res.status, "ok")
            self.assertTrue(np.all(res.lo <= res.hi))

    def test_damage_counts(self):
        from paper4.learned import damage_counts
        truth = true_skeleton(self.sem)
        bad = damage(truth, "missing", 0.2, np.random.default_rng(9))
        self.assertEqual(damage_counts(bad, truth), {"missing": bad.damage["k"], "extra": 0, "reversed": 0})
        rev = damage(truth, "reversed", 0.5, np.random.default_rng(9), self.sem.edge_lag)
        self.assertEqual(damage_counts(rev, truth)["reversed"], rev.damage["k"])


class RunnerGuardTest(unittest.TestCase):
    def test_methods_get_public_skeleton(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
        import run_experiment as R
        topo = load_bank("D-07", "development")[0]
        sem = build_dynamic_sem(topo, GeneratorConfig(), np.random.default_rng(1))
        full = damage(true_skeleton(sem, with_lags=True), "missing", 0.2, np.random.default_rng(2), sem.edge_lag)
        self.assertTrue(full.log)
        pub = R.public(full)
        self.assertEqual(pub.log, [])
        self.assertIsNone(pub.lag_hint)
        self.assertEqual(pub.pairs(), full.pairs())
        self.assertEqual(pub.damage, full.damage)
        self.assertEqual(R.ext_seed("tolerant_v5"), R.ext_seed("tolerant_v5"))
        self.assertNotEqual(R.ext_seed("tolerant_v5"), R.ext_seed("targeted_lp"))


if __name__ == "__main__":
    unittest.main()
