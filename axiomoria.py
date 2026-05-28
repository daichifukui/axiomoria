#!/usr/bin/env python3
"""Axiomoria: a lightweight scientific-style universe reasoning simulator.

The model is intentionally heuristic. It uses dimensionless multipliers
relative to the constants in our universe and propagates them through
interpretable scaling relations. The goal is not precision cosmology, but explicit causal
reasoning with uncertainty and stated assumptions.
"""

from __future__ import annotations

import argparse
import math
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple


EPSILON = 1.0e-12


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_pow(base: float, exponent: float) -> float:
    return math.exp(exponent * math.log(max(base, EPSILON)))


def band_score(value: float, low: float, high: float, softness: float = 0.18) -> float:
    """Smoothly score values inside a preferred band.

    Values inside [low, high] receive score 1. Values outside decay in log-space
    rather than flipping abruptly, so uncertainty bands remain visible.
    """
    if low <= value <= high:
        return 1.0
    if value < low:
        distance = abs(math.log(max(value, EPSILON) / low))
    else:
        distance = abs(math.log(value / max(high, EPSILON)))
    return math.exp(-distance / max(softness, EPSILON))


@dataclass(frozen=True)
class Constants:
    strong_force: float = 1.0
    speed_of_light: float = 1.0
    electron_mass: float = 1.0
    gravity: float = 1.0
    fine_structure: float = 1.0
    proton_electron_mass_ratio: float = 1.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "strong_force": self.strong_force,
            "speed_of_light": self.speed_of_light,
            "electron_mass": self.electron_mass,
            "gravity": self.gravity,
            "fine_structure": self.fine_structure,
            "proton_electron_mass_ratio": self.proton_electron_mass_ratio,
        }


@dataclass
class Conclusion:
    title: str
    statement: str
    chain: List[str]
    confidence: float
    assumptions: List[str]
    limitations: List[str] = field(default_factory=list)


@dataclass
class Hypothesis:
    name: str
    plausibility: float
    evidence_for: List[str]
    evidence_against: List[str]


@dataclass
class UniverseAssessment:
    constants: Constants
    derived: Dict[str, float]
    reasoning_steps: List[str]
    conclusions: List[Conclusion]
    hypotheses: List[Hypothesis]
    universe_class: str
    confidence: float
    key_uncertainties: List[str]


class UniverseReasoner:
    """Propagates altered constants through heuristic physics domains."""

    def __init__(self, constants: Constants) -> None:
        self.c = constants
        self.steps: List[str] = []

    def analyze(self) -> UniverseAssessment:
        derived = self.derive_quantities()
        conclusions = self.build_conclusions(derived)
        hypotheses = self.compare_hypotheses(derived)
        universe_class, class_confidence = self.classify(derived, hypotheses)
        confidence = self.overall_confidence(derived, class_confidence)
        uncertainties = self.key_uncertainties(derived)
        return UniverseAssessment(
            constants=self.c,
            derived=derived,
            reasoning_steps=self.steps,
            conclusions=conclusions,
            hypotheses=hypotheses,
            universe_class=universe_class,
            confidence=confidence,
            key_uncertainties=uncertainties,
        )

    def derive_quantities(self) -> Dict[str, float]:
        sf = self.c.strong_force
        c0 = self.c.speed_of_light
        me = self.c.electron_mass
        g = self.c.gravity
        alpha = self.c.fine_structure
        mu = self.c.proton_electron_mass_ratio

        # Nuclear binding rises with the strong interaction, but is eroded by
        # electromagnetic repulsion. The c multiplier is included because rest
        # energy and relativistic nuclear scales alter the effective mass defect.
        coulomb_pressure = safe_pow(alpha, 1.55) / safe_pow(sf, 0.75)
        nuclear_binding_margin = safe_pow(sf, 1.85) * safe_pow(c0, 0.25) - 0.34 * coulomb_pressure
        isotope_stability_index = clamp((nuclear_binding_margin - 0.42) / 1.65)
        maximum_stable_atomic_number = 82.0 * safe_pow(max(nuclear_binding_margin, 0.05), 0.72) / safe_pow(alpha, 0.58)

        # Hydrogen burning requires deuterium-like bottlenecks to be neither too
        # weak nor too easy; both extremes shorten the window for ordinary stars.
        deuterium_bottleneck = safe_pow(sf, 2.15) / (safe_pow(alpha, 0.35) * safe_pow(c0, 0.20))
        fusion_threshold_scale = safe_pow(alpha, 2.0) * safe_pow(me, 0.18) / safe_pow(sf, 1.25)

        # Bohr-like radius scaling: a0 ∝ 1/(alpha * reduced mass). The
        # proton-electron mass-ratio multiplier changes reduced-mass corrections
        # for light atoms without pretending to solve full molecular spectra.
        reduced_mass_scale = me * (mu * 1836.0 + 1.0) / (mu * 1836.0 + me)
        atomic_radius_scale = 1.0 / max(alpha * reduced_mass_scale, EPSILON)
        atomic_energy_scale = safe_pow(alpha, 2.0) * reduced_mass_scale * safe_pow(c0, 2.0)
        relativistic_stiffness = alpha / max(c0, EPSILON)
        bound_state_stability = band_score(relativistic_stiffness, 0.15, 1.45, 0.45) * band_score(
            atomic_energy_scale, 0.08, 18.0, 0.55
        )

        # Chemical diversity favors moderate atom sizes, enough stable nuclei,
        # and non-extreme relativistic electron behavior.
        chemistry_viability_score = clamp(
            0.42 * isotope_stability_index
            + 0.25 * band_score(atomic_radius_scale, 0.18, 7.5, 0.60)
            + 0.23 * bound_state_stability
            + 0.10 * band_score(maximum_stable_atomic_number / 82.0, 0.35, 2.2, 0.45)
        )

        # Stellar rates are intentionally semi-continuous. Stronger gravity and
        # easier fusion raise luminosity; lower c changes rest-energy yield.
        stellar_burn_rate_scale = safe_pow(g, 1.75) * safe_pow(fusion_threshold_scale, -1.25) / safe_pow(c0, 1.15)
        stellar_lifetime_scale = safe_pow(c0, 2.0) / max(stellar_burn_rate_scale, EPSILON)
        hydrogen_consumption_intensity = safe_pow(stellar_burn_rate_scale, 0.65) * safe_pow(deuterium_bottleneck, 0.25)
        supernova_tendency = clamp(
            0.30 * math.log1p(maximum_stable_atomic_number / 82.0)
            + 0.34 * safe_pow(g, 0.72)
            + 0.22 * safe_pow(sf, 0.58)
            + 0.14 / safe_pow(c0, 0.85)
            - 0.45
        )

        # Cosmological structure is favored by gravity that can collect matter,
        # a causal horizon that is not too restrictive, and long-lived stars.
        causality_limit_scale = c0 / math.sqrt(max(g, EPSILON))
        flatness_stability_score = band_score(g / safe_pow(c0, 4.0), 0.08, 12.0, 0.75)
        structure_formation_plausibility = clamp(
            0.40 * band_score(g, 0.05, 18.0, 0.75)
            + 0.25 * band_score(causality_limit_scale, 0.12, 8.0, 0.70)
            + 0.20 * flatness_stability_score
            + 0.15 * band_score(stellar_lifetime_scale, 0.02, 100.0, 0.90)
        )
        long_lived_star_score = band_score(stellar_lifetime_scale, 0.25, 80.0, 0.70) * band_score(
            hydrogen_consumption_intensity, 0.12, 12.0, 0.55
        )
        life_permitting_score = clamp(
            0.34 * chemistry_viability_score
            + 0.26 * long_lived_star_score
            + 0.20 * structure_formation_plausibility
            + 0.12 * flatness_stability_score
            + 0.08 * bound_state_stability
        )

        reliable_regime_score = self.reliable_regime_score()

        derived = {
            "coulomb_pressure": coulomb_pressure,
            "nuclear_binding_margin": nuclear_binding_margin,
            "isotope_stability_index": isotope_stability_index,
            "maximum_stable_atomic_number": maximum_stable_atomic_number,
            "deuterium_bottleneck": deuterium_bottleneck,
            "fusion_threshold_scale": fusion_threshold_scale,
            "reduced_mass_scale": reduced_mass_scale,
            "atomic_radius_scale": atomic_radius_scale,
            "atomic_energy_scale": atomic_energy_scale,
            "relativistic_stiffness": relativistic_stiffness,
            "bound_state_stability": bound_state_stability,
            "stellar_burn_rate_scale": stellar_burn_rate_scale,
            "stellar_lifetime_scale": stellar_lifetime_scale,
            "hydrogen_consumption_intensity": hydrogen_consumption_intensity,
            "supernova_tendency": supernova_tendency,
            "causality_limit_scale": causality_limit_scale,
            "flatness_stability_score": flatness_stability_score,
            "structure_formation_plausibility": structure_formation_plausibility,
            "chemistry_viability_score": chemistry_viability_score,
            "long_lived_star_score": long_lived_star_score,
            "life_permitting_score": life_permitting_score,
            "reliable_regime_score": reliable_regime_score,
        }

        self.steps.extend(
            [
                "Strong-force and electromagnetic multipliers were combined into a nuclear binding margin: stronger attraction increases mass-defect binding, while fine-structure pressure penalizes large nuclei.",
                "Atomic length and energy scales were inferred from Bohr-like scalings: radius varies as 1/(alpha * reduced mass), while electronic binding energy varies as alpha^2 * reduced mass * c^2.",
                "Relativistic stiffness was estimated from alpha/c; high values imply electrons and nuclear processes feel stronger relativistic corrections and may destabilize ordinary bound states.",
                "Fusion thresholds and stellar burn rates were propagated from nuclear binding, gravity, and c-dependent energy release rather than assigned as fixed outcomes.",
                "Cosmological viability was estimated by combining causal horizon scale, gravity-driven structure formation, flatness sensitivity, and the availability of long-lived stars.",
            ]
        )
        return derived

    def reliable_regime_score(self) -> float:
        values = list(self.c.as_dict().values())
        # Highest confidence near 1; decay when any knob leaves roughly two
        # orders of magnitude around our universe.
        worst_log = max(abs(math.log10(max(v, EPSILON))) for v in values)
        return clamp(1.0 - max(0.0, worst_log - 0.45) / 1.55)

    def build_conclusions(self, d: Dict[str, float]) -> List[Conclusion]:
        return [
            Conclusion(
                title="Nuclear structure",
                statement=(
                    f"The model estimates a nuclear binding margin of {d['nuclear_binding_margin']:.3g} "
                    f"and a maximum stable atomic number near {d['maximum_stable_atomic_number']:.0f}."
                ),
                chain=[
                    "Increasing strong-force strength raises the attractive part of the nuclear potential.",
                    "Increasing fine-structure strength raises Coulomb repulsion among protons.",
                    "The balance sets isotope stability and the approximate reach of the periodic table.",
                ],
                confidence=0.72 * d["reliable_regime_score"],
                assumptions=["Liquid-drop-like scaling is used for heavy nuclei.", "Weak-interaction details are compressed into the deuterium bottleneck proxy."],
                limitations=["Does not solve nuclear shell structure or beta-decay networks."],
            ),
            Conclusion(
                title="Atomic and chemical behavior",
                statement=(
                    f"Atomic radius is scaled by {d['atomic_radius_scale']:.3g}; chemistry viability is "
                    f"{d['chemistry_viability_score']:.2f} on a 0-1 heuristic scale."
                ),
                chain=[
                    "Larger electron reduced mass or fine-structure coupling shrinks Bohr-like orbitals.",
                    "The relativistic stiffness proxy alpha/c tests whether electrons remain in ordinary non-collapse bound states.",
                    "Chemical complexity requires stable nuclei plus a moderate range of molecular bond lengths and energies.",
                ],
                confidence=0.70 * d["reliable_regime_score"],
                assumptions=["Chemistry is approximated by hydrogenic scaling plus nuclear diversity."],
                limitations=["Molecular orbital calculations are not performed."],
            ),
            Conclusion(
                title="Stellar evolution",
                statement=(
                    f"Stellar burn rate scales as {d['stellar_burn_rate_scale']:.3g}, giving a lifetime scale of "
                    f"{d['stellar_lifetime_scale']:.3g}; supernova tendency is {d['supernova_tendency']:.2f}."
                ),
                chain=[
                    "Fusion ignition responds to Coulomb barriers, nuclear attraction, and stellar compression from gravity.",
                    "Burn rate is increased by stronger gravity or easier fusion thresholds.",
                    "Lifetime is penalized when fuel consumption rises faster than available rest-energy yield.",
                ],
                confidence=0.58 * d["reliable_regime_score"],
                assumptions=["Main-sequence-like stars are treated through scaling laws, not stellar structure equations."],
                limitations=["Metallicity, opacity, and detailed reaction chains are not simulated."],
            ),
            Conclusion(
                title="Cosmology and life-permitting conditions",
                statement=(
                    f"Structure formation plausibility is {d['structure_formation_plausibility']:.2f}; "
                    f"life-permitting score is {d['life_permitting_score']:.2f}."
                ),
                chain=[
                    "Gravity must be strong enough to seed structures but not so dominant that rapid collapse erases stable eras.",
                    "Speed of light sets causal communication and the energetic scale E = mc^2.",
                    "Life-friendliness combines stable chemistry, long-lived stars, and cosmological structure formation.",
                ],
                confidence=0.52 * d["reliable_regime_score"],
                assumptions=["Initial perturbation amplitude and dark-sector physics are held fixed."],
                limitations=["No numerical Friedmann evolution or galaxy formation simulation is included."],
            ),
        ]

    def compare_hypotheses(self, d: Dict[str, float]) -> List[Hypothesis]:
        nuclear_matter = clamp(0.55 * clamp((self.c.strong_force - 1.25) / 1.4) + 0.30 * d["isotope_stability_index"] + 0.15 * clamp((d["nuclear_binding_margin"] - 1.7) / 2.5))
        exotic_atoms = clamp(0.55 * (1.0 - d["bound_state_stability"]) + 0.25 * clamp(abs(math.log(max(d["atomic_radius_scale"], EPSILON))) / 2.4) + 0.20 * clamp(d["relativistic_stiffness"] / 2.0))
        short_lived = clamp(0.45 * (1.0 - d["long_lived_star_score"]) + 0.35 * clamp(math.log1p(d["stellar_burn_rate_scale"]) / 4.0) + 0.20 * d["supernova_tendency"])
        stable_life = d["life_permitting_score"] * d["reliable_regime_score"]
        causality = clamp(0.65 * (1.0 - band_score(d["causality_limit_scale"], 0.2, 6.0, 0.65)) + 0.35 * clamp(d["relativistic_stiffness"] / 2.0))
        nonviable = clamp(1.0 - d["life_permitting_score"] + 0.25 * (1.0 - d["structure_formation_plausibility"]))

        return [
            Hypothesis(
                "stable-life-friendly universe",
                stable_life,
                ["Chemistry, long-lived stars, and structure formation retain jointly high scores."],
                ["Heuristic model cannot guarantee biochemistry or planet formation."],
            ),
            Hypothesis(
                "exotic-atom universe",
                exotic_atoms,
                ["Atomic radius, binding energy, or relativistic stiffness deviate from the ordinary chemistry band."],
                ["Some alternative chemistry may still exist if nuclear diversity is high."],
            ),
            Hypothesis(
                "short-lived-high-density universe",
                short_lived,
                ["Fast stellar burning, stronger gravity, or high supernova tendency compress the habitable time window."],
                ["Low-mass or nonstandard stars could extend lifetimes outside this scaling model."],
            ),
            Hypothesis(
                "nuclear-matter-dominated universe",
                nuclear_matter,
                ["High strong-force binding can over-stabilize heavy nuclei and favor dense nuclear aggregates."],
                ["Coulomb pressure and shell effects may still prevent bulk nuclear domination."],
            ),
            Hypothesis(
                "causality-distorted universe",
                causality,
                ["The causal horizon proxy or relativistic stiffness lies outside the ordinary range."],
                ["Changing units versus changing physical dimensionless ratios can be subtle for c-like inputs."],
            ),
            Hypothesis(
                "non-viable universe",
                nonviable,
                ["One or more required pillars—stable atoms, stars, or structure—has a low combined score."],
                ["The model may miss exotic viable regimes unrelated to Earth-like life."],
            ),
        ]

    def classify(self, d: Dict[str, float], hypotheses: Sequence[Hypothesis]) -> Tuple[str, float]:
        sorted_h = sorted(hypotheses, key=lambda h: h.plausibility, reverse=True)
        top = sorted_h[0]
        runner_up = sorted_h[1]
        separation = top.plausibility - runner_up.plausibility
        confidence = clamp(0.42 + 0.48 * separation + 0.10 * d["reliable_regime_score"])
        return top.name, confidence

    def overall_confidence(self, d: Dict[str, float], class_confidence: float) -> float:
        return clamp(0.55 * class_confidence + 0.45 * d["reliable_regime_score"])

    def key_uncertainties(self, d: Dict[str, float]) -> List[str]:
        uncertainties = [
            "Heuristic exponents are calibrated for qualitative reasoning near our universe, not precision prediction.",
            "Weak force, quark masses, baryon asymmetry, dark matter, and primordial fluctuation amplitude are held fixed.",
        ]
        if d["reliable_regime_score"] < 0.65:
            uncertainties.append("At least one input lies outside the reliable near-reference regime; confidence is degraded.")
        close_hypotheses = sorted(self.compare_hypotheses(d), key=lambda h: h.plausibility, reverse=True)[:2]
        if len(close_hypotheses) == 2 and abs(close_hypotheses[0].plausibility - close_hypotheses[1].plausibility) < 0.12:
            uncertainties.append(
                f"Top hypotheses are close: {close_hypotheses[0].name} versus {close_hypotheses[1].name}."
            )
        return uncertainties


def positive_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("constant multipliers must be positive")
    return value


def format_float(value: float) -> str:
    if abs(value) >= 1000 or abs(value) < 0.01:
        return f"{value:.3e}"
    return f"{value:.3f}"


def wrap_lines(lines: Iterable[str], indent: str = "  ", width: int = 88) -> str:
    return "\n".join(textwrap.fill(line, width=width, initial_indent=indent, subsequent_indent=indent) for line in lines)


def render_report(assessment: UniverseAssessment, verbose: bool = False) -> str:
    c = assessment.constants.as_dict()
    d = assessment.derived
    lines: List[str] = ["=== Universe Reasoning Report ===", "", "Observed inputs:"]
    for key, value in c.items():
        lines.append(f"  {key} = {format_float(value)}")

    core_keys = [
        "nuclear_binding_margin",
        "atomic_radius_scale",
        "relativistic_stiffness",
        "stellar_burn_rate_scale",
        "chemistry_viability_score",
        "life_permitting_score",
    ]
    verbose_keys = [key for key in d if key not in core_keys]
    lines.extend(["", "Derived intermediate quantities:"])
    for key in core_keys + (verbose_keys if verbose else []):
        lines.append(f"  {key} = {format_float(d[key])}")

    if verbose:
        lines.extend(["", "Causal reasoning steps:"])
        for index, step in enumerate(assessment.reasoning_steps, 1):
            lines.append(textwrap.fill(f"{index}. {step}", width=92, initial_indent="  ", subsequent_indent="     "))

        lines.extend(["", "Major conclusions:"])
        for conclusion in assessment.conclusions:
            lines.append(f"  - {conclusion.title}: {conclusion.statement}")
            lines.append("    Reasoning chain:")
            for part in conclusion.chain:
                lines.append(textwrap.fill(f"-> {part}", width=92, initial_indent="      ", subsequent_indent="         "))
            lines.append(f"    Confidence: {conclusion.confidence:.2f}")
            lines.append("    Assumptions: " + "; ".join(conclusion.assumptions))
            if conclusion.limitations:
                lines.append("    Limitations: " + "; ".join(conclusion.limitations))

        lines.extend(["", "Competing hypotheses:"])
        for hypothesis in sorted(assessment.hypotheses, key=lambda h: h.plausibility, reverse=True):
            lines.append(f"  - {hypothesis.name}: plausibility = {hypothesis.plausibility:.2f}")
            lines.append("    Evidence for: " + "; ".join(hypothesis.evidence_for))
            lines.append("    Evidence against: " + "; ".join(hypothesis.evidence_against))
    else:
        top = sorted(assessment.hypotheses, key=lambda h: h.plausibility, reverse=True)[:3]
        lines.extend(["", "Top competing hypotheses:"])
        for hypothesis in top:
            lines.append(f"  - {hypothesis.name}: {hypothesis.plausibility:.2f}")

    lines.extend(
        [
            "",
            "Final assessment:",
            f"  universe_class = {assessment.universe_class}",
            f"  confidence = {assessment.confidence:.2f}",
            "  key uncertainties:",
        ]
    )
    lines.append(wrap_lines((f"- {item}" for item in assessment.key_uncertainties), indent="    "))
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate how dimensionless changes in physical constants alter a hypothetical universe.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--strong-force", type=positive_float, default=1.0, help="strong nuclear force multiplier")
    parser.add_argument("--speed-of-light", type=positive_float, default=1.0, help="speed of light multiplier")
    parser.add_argument("--electron-mass", type=positive_float, default=1.0, help="electron mass multiplier")
    parser.add_argument("--gravity", type=positive_float, default=1.0, help="gravitational strength multiplier")
    parser.add_argument("--fine-structure", type=positive_float, default=1.0, help="fine-structure constant multiplier")
    parser.add_argument(
        "--proton-electron-mass-ratio",
        type=positive_float,
        default=1.0,
        help="proton-to-electron mass-ratio multiplier",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--compact", action="store_true", help="print compact summary only")
    mode.add_argument("--verbose", action="store_true", help="print full reasoning trace")
    return parser


def constants_from_args(args: argparse.Namespace) -> Constants:
    return Constants(
        strong_force=args.strong_force,
        speed_of_light=args.speed_of_light,
        electron_mass=args.electron_mass,
        gravity=args.gravity,
        fine_structure=args.fine_structure,
        proton_electron_mass_ratio=args.proton_electron_mass_ratio,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    assessment = UniverseReasoner(constants_from_args(args)).analyze()
    print(render_report(assessment, verbose=args.verbose and not args.compact))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
