# axiomoria

Axiomoria is a command-line universe reasoning simulator that explores how changes in fundamental physical constants could reshape atoms, stars, chemistry, and the possibility of life. It produces interpretable, physics-informed explanations rather than simple rule-based outputs.

## Usage

```bash
python3 axiomoria.py --strong-force 1.2 --speed-of-light 0.8 --electron-mass 1.1 --verbose
```

All inputs are positive multipliers relative to the constants in our universe. Supported knobs include:

- `--strong-force`
- `--speed-of-light`
- `--electron-mass`
- `--gravity`
- `--fine-structure`
- `--proton-electron-mass-ratio`
- `--c-convention {charges-fixed,couplings-fixed}`: how a change in `c` is interpreted (see below)

Use `--compact` for a few-line summary, the default for core quantities plus the top hypotheses, or `--verbose` for the full reasoning trace, competing hypotheses, assumptions, limitations, and confidence estimates.

Run the tests with:

```bash
python3 -m unittest discover -s tests
```

## How the knobs are interpreted

Only dimensionless combinations of constants are physically observable, so the simulator first maps the six knobs onto four dimensionless couplings. The report prints these under "Effective dimensionless couplings".

| Coupling | Meaning | Mapping from knobs |
| --- | --- | --- |
| α | electromagnetic strength | `fine_structure / c` (charges-fixed) or `fine_structure` (couplings-fixed) |
| strong | residual nuclear attraction | `strong_force / c` (charges-fixed) or `strong_force` (couplings-fixed) |
| μ = m_p/m_e | proton-to-electron mass ratio | `1836 × proton_electron_mass_ratio / electron_mass` |
| α_G = G m_p²/ħc | gravitational strength | `gravity / c` |

- **Nucleon mass is fixed by QCD.** `--electron-mass 2` and `--proton-electron-mass-ratio 0.5` therefore describe the same universe.
- **charges-fixed (default):** changing `c` with ħ and the gauge charges held fixed rescales every coupling g²/(ħc) as 1/c. A slower `c` strengthens electromagnetism, the strong force, and gravity together.
- **couplings-fixed:** the fine-structure and strong knobs are taken as the final dimensionless values, so `c` only enters through α_G. This is the strict "only dimensionless constants matter" reading.

## Model overview

Each domain is a calibrated scaling law. Our universe (all multipliers = 1) reproduces lead (Z ≈ 82) as the heaviest stable element, a deuteron binding of 2.22 MeV, m_n − m_p = 1.29 MeV, primordial helium Y ≈ 0.25, and about 10¹⁰ stars per galaxy.

| Domain | Physics used |
| --- | --- |
| Nuclei | Liquid-drop mass formula: attraction ∝ strong, Fermi kinetic energy fixed, Coulomb ∝ α. Heaviest stable element from the fission limit Z²/A ∝ (surface/Coulomb), calibrated to lead. |
| Two-nucleon thresholds | Deuteron unbinds about 8% below today's strong force (near-threshold B ∝ (s − s_c)²); diproton binds about 10% above. |
| Weak stability | m_n − m_p = 2.05 MeV (quark masses) − 0.76 MeV·α. Hydrogen needs m_e < m_n − m_p, otherwise it decays by electron capture. Deuterium needs m_n − m_p < B_d + m_e, otherwise it β-decays and the pp/pep chain cannot start. |
| Big-bang nucleosynthesis | n/p freeze-out at about 0.8 MeV, then neutron decay, then helium locking via deuterium (or a bound diproton). |
| Atoms | Bohr radius relative to nuclear size ∝ 1/(α m_e); Dirac limit Z·α ≲ 1 (Z ≈ 170 today); Born–Oppenheimer localization (m_e/m_p)^¼. |
| Stars | Mass ∝ α_G^(−3/2); main-sequence lifetime ∝ ε α² α_G⁻¹ μ² (Carr & Rees), expressed in atomic (chemical) time units; ignition needs a Gamow energy ∝ α² μ that is not too large; Carter's convective/radiative coincidence α_G ~ α¹² μ⁻⁴; Carr–Rees weak/gravity coincidence for supernovae. |
| Structure | Rees–Ostriker cooling: stars per galaxy ∝ α⁵ α_G^(−½) μ^½. |
| Life score | Weighted **geometric** mean of chemistry, long-lived stars, hydrogen availability, structure, and stellar diversity, so any failed prerequisite dominates. |

Outcome classes: stable-life-friendly, exotic-atom, short-lived-star, nuclear-matter-dominated, hydrogen-unstable, no-bound-nuclei (nothing beyond a free proton is bound), nucleosynthesis-starved (nuclei could exist but stars cannot make them), and non-viable.

## Reading the confidence

- **Out-of-range runs.** Confidence is multiplied by a reliability score for how far the couplings sit from the calibrated range. Runs far outside that range report confidence near 0 and flag the class as an extrapolation.
- **Changing c.** Whenever `--speed-of-light` differs from 1, the run is repeated under the other c convention. If the two conventions give different classes, both are reported and confidence is halved.
- **Strong coupling far from 1.** Outside roughly 0.67–1.5× today's strong coupling, a warning explains that holding the proton mass fixed is no longer justified, because the proton's mass itself comes from the strong interaction.
- **Not-applicable quantities.** Quantities with no physical meaning in a given universe are shown as `n/a` with the reason. For example, stellar lifetimes are `n/a` when stars cannot burn hydrogen.

## Limitations

The simulator is qualitative. Thresholds such as the deuteron/diproton strong-force limits and the electromagnetic share of m_n − m_p vary between literature sources. The reliability score and the threshold-proximity flag reduce reported confidence near those edges.

These are not modelled: nuclear shell structure, the Hoyle (carbon) resonance, stellar structure equations, reaction networks, the weak coupling, quark masses, baryon asymmetry, dark matter, dark energy, and primordial fluctuations. Everything in that list is held fixed.

Background reading: Carr & Rees (1979), Barrow & Tipler (1986), Hogan (2000), Adams (2008), Barnes (2012).
