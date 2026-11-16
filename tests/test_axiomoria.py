import contextlib
import io
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

import axiomoria as ax  # noqa: E402


def assess(convention: str = "charges-fixed", **knobs: float) -> ax.UniverseAssessment:
    return ax.UniverseReasoner(ax.Constants(**knobs), convention).analyze()


class ReferenceCalibrationTest(unittest.TestCase):
    """Our universe (all multipliers = 1) must reproduce known values."""

    def setUp(self) -> None:
        self.a = assess()
        self.d = self.a.derived

    def test_heaviest_stable_element_is_lead(self) -> None:
        self.assertAlmostEqual(self.d["maximum_stable_atomic_number"], 82.0, delta=1.0)

    def test_two_nucleon_and_weak_values(self) -> None:
        self.assertAlmostEqual(self.d["deuteron_binding_mev"], ax.DEUTERON_BINDING_MEV, places=6)
        self.assertAlmostEqual(self.d["neutron_proton_gap_mev"], 1.29, places=2)
        self.assertLess(self.d["diproton_bound_score"], 0.01)
        self.assertGreater(self.d["hydrogen_stability_margin_mev"], 0.7)

    def test_primordial_helium_fraction(self) -> None:
        self.assertAlmostEqual(self.d["primordial_helium_fraction"], 0.25, delta=0.02)

    def test_relative_scales_are_unity(self) -> None:
        for key in ("nuclear_binding_margin", "atomic_radius_scale", "atomic_energy_scale",
                    "stellar_lifetime_scale", "reduced_mass_scale", "galaxy_star_count_scale"):
            self.assertAlmostEqual(self.d[key], 1.0, places=6, msg=key)

    def test_reference_is_life_friendly(self) -> None:
        self.assertGreater(self.d["life_permitting_score"], 0.95)
        self.assertGreater(self.d["chemistry_viability_score"], 0.95)
        self.assertEqual(self.a.universe_class, "stable-life-friendly universe")
        self.assertGreater(self.a.confidence, 0.9)


class MassParameterTest(unittest.TestCase):
    def test_mass_ratio_knob_changes_physics(self) -> None:
        # Regression: the old reduced-mass formula ignored the ratio knob entirely.
        base = assess().derived
        lighter_proton = assess(proton_electron_mass_ratio=0.5).derived
        self.assertNotAlmostEqual(base["reduced_mass_scale"], lighter_proton["reduced_mass_scale"])
        self.assertNotAlmostEqual(base["stellar_lifetime_scale"], lighter_proton["stellar_lifetime_scale"])

    def test_electron_mass_and_ratio_are_equivalent(self) -> None:
        # With the nucleon mass pinned by QCD, only m_e / m_p is observable.
        a = assess(electron_mass=2.0).derived
        b = assess(proton_electron_mass_ratio=0.5).derived
        for key in a:
            self.assertAlmostEqual(a[key], b[key], places=9, msg=key)

    def test_reduced_mass_formula(self) -> None:
        d = assess(electron_mass=2.0).derived
        expected = 2.0 * (ax.MU0 + 1.0) / (ax.MU0 + 2.0)
        self.assertAlmostEqual(d["reduced_mass_scale"], expected, places=12)

    def test_heavy_electron_destabilizes_hydrogen(self) -> None:
        a = assess(electron_mass=3.0)
        self.assertLess(a.derived["hydrogen_stability_margin_mev"], 0.0)
        self.assertEqual(a.universe_class, "hydrogen-unstable universe")
        self.assertLess(a.derived["life_permitting_score"], 0.5)


class NuclearTest(unittest.TestCase):
    def test_weaker_strong_force_stops_hydrogen_burning(self) -> None:
        a = assess(strong_force=0.9)
        self.assertEqual(a.derived["deuteron_binding_mev"], 0.0)
        self.assertEqual(a.universe_class, "nucleosynthesis-starved universe")

    def test_stronger_strong_force_binds_diproton(self) -> None:
        self.assertGreater(assess(strong_force=1.2).derived["diproton_bound_score"], 0.99)

    def test_heavy_element_limit_trends(self) -> None:
        ref = assess().derived["maximum_stable_atomic_number"]
        self.assertLess(assess(fine_structure=2.0).derived["maximum_stable_atomic_number"], ref)
        self.assertGreater(assess(strong_force=1.2).derived["maximum_stable_atomic_number"], ref)

    def test_deuteron_binding_is_continuous(self) -> None:
        below = ax.deuteron_binding_mev(1.0 - 1e-9)
        above = ax.deuteron_binding_mev(1.0 + 1e-9)
        self.assertAlmostEqual(below, above, places=5)


class AggregationTest(unittest.TestCase):
    def test_failed_pillar_dominates_life_score(self) -> None:
        # Regression: an additive score let a universe without chemistry look life-friendly.
        a = assess(strong_force=0.5)
        self.assertLess(a.derived["life_permitting_score"], 0.1)
        self.assertNotEqual(a.universe_class, "stable-life-friendly universe")

    def test_weak_gravity_is_not_penalized(self) -> None:
        # Regression: long stellar lifetimes were previously treated as a defect.
        d = assess(gravity=1.0e-3).derived
        self.assertGreater(d["long_lived_star_score"], 0.95)
        self.assertGreater(d["life_permitting_score"], 0.8)

    def test_strong_gravity_shortens_stars(self) -> None:
        a = assess(gravity=100.0)
        self.assertAlmostEqual(a.derived["stellar_lifetime_scale"], 0.01, places=6)
        self.assertEqual(a.universe_class, "short-lived-star universe")


class SpeedOfLightConventionTest(unittest.TestCase):
    def assert_same(self, a: ax.UniverseAssessment, b: ax.UniverseAssessment) -> None:
        for key in a.derived:
            if key == "reliable_regime_score":
                continue
            self.assertAlmostEqual(a.derived[key], b.derived[key], places=9, msg=key)

    def test_couplings_fixed_c_only_changes_gravity(self) -> None:
        self.assert_same(assess("couplings-fixed", speed_of_light=0.5), assess("couplings-fixed", gravity=2.0))

    def test_charges_fixed_c_rescales_all_couplings(self) -> None:
        self.assert_same(
            assess("charges-fixed", speed_of_light=0.5),
            assess("charges-fixed", fine_structure=2.0, strong_force=2.0, gravity=2.0),
        )

    def test_unknown_convention_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ax.effective_parameters(ax.Constants(), "nonsense")


class CliTest(unittest.TestCase):
    def run_cli(self, *argv: str) -> str:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(ax.main(list(argv)), 0)
        return buffer.getvalue()

    def test_modes_have_different_lengths(self) -> None:
        compact = self.run_cli("--compact")
        default = self.run_cli()
        verbose = self.run_cli("--verbose")
        self.assertLess(len(compact), len(default))
        self.assertLess(len(default), len(verbose))
        self.assertIn("universe_class", default)

    def test_invalid_inputs_rejected(self) -> None:
        for bad in ("-1", "0", "nan", "inf", "abc"):
            with self.assertRaises(Exception):
                ax.positive_float(bad)

    def test_extreme_inputs_do_not_crash(self) -> None:
        for value in ("1e-200", "1e200"):
            out = self.run_cli("--gravity", value, "--fine-structure", value, "--compact")
            self.assertIn("class =", out)
            self.assertNotIn("nan", out.lower())


if __name__ == "__main__":
    unittest.main()
