# axiomoria

Axiomoria is a command-line universe reasoning simulator that explores how changes in fundamental physical constants could reshape atoms, stars, chemistry, and the possibility of life. It produces interpretable, physics-informed explanations rather than simple rule-based outputs.

## Usage

```bash
python3 axiomoria.py --strong-force 1.2 --speed-of-light 0.8 --electron-mass 1.1 --verbose
```

All inputs are positive dimensionless multipliers relative to the constants in our universe. Supported knobs include:

- `--strong-force`
- `--speed-of-light`
- `--electron-mass`
- `--gravity`
- `--fine-structure`
- `--proton-electron-mass-ratio`

Use `--compact` for a short report or `--verbose` for the full reasoning trace, competing hypotheses, assumptions, limitations, and confidence estimates.
