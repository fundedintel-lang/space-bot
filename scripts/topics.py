#!/usr/bin/env python3
"""Seed the Planner's knowledge-coverage table from a curated topic map.

    python3 scripts/topics.py --domains mechanics,thermodynamics
    python3 scripts/topics.py --list
    python3 scripts/topics.py --domains mechanics --format md > coverage.md

This is a checklist generator, NOT a claim of completeness. The Plan's coverage
table stays the source of truth, and the Checker must still verify every row.
"""
from __future__ import annotations

import argparse
import sys

DOMAINS: dict[str, list[str]] = {
    "mechanics": [
        "kinematics (1D/2D/3D)", "Newton's laws", "friction", "circular motion",
        "work-energy theorem", "conservation of momentum", "collisions",
        "rotational dynamics", "moment of inertia", "angular momentum",
        "gravitation & orbits", "simple harmonic motion", "damped/forced oscillation",
        "Lagrangian & Hamiltonian mechanics", "normal modes",
    ],
    "thermodynamics": [
        "zeroth/first/second law", "ideal gas law", "heat capacity",
        "isothermal/adiabatic processes", "entropy", "Carnot efficiency",
        "heat engines & refrigerators", "phase transitions", "kinetic theory",
        "free energy", "statistical ensembles",
    ],
    "electromagnetism": [
        "Coulomb's law", "electric field & potential", "Gauss's law",
        "capacitance & dielectrics", "DC circuits & Kirchhoff", "magnetic force",
        "Ampere's law", "Biot-Savart", "Faraday induction", "inductance & LC/RLC",
        "Maxwell's equations", "electromagnetic waves",
    ],
    "waves-optics": [
        "wave equation", "superposition & interference", "diffraction",
        "standing waves & resonance", "Doppler effect", "geometric optics",
        "polarisation", "dispersion", "Fourier decomposition",
    ],
    "quantum": [
        "wave-particle duality", "Schrodinger equation", "barrier tunnelling",
        "quantum harmonic oscillator", "hydrogen atom", "spin & angular momentum",
        "uncertainty principle", "identical particles/Pauli", "perturbation theory",
        "selection rules", "decoherence",
    ],
    "relativity": [
        "Lorentz transformations", "time dilation & length contraction",
        "relativistic momentum/energy", "four-vectors", "equivalence principle",
        "Schwarzschild metric", "gravitational time dilation", "energy-momentum tensor",
    ],
    "fluids": [
        "continuity equation", "Bernoulli", "Navier-Stokes", "Reynolds number",
        "viscosity & drag", "laminar vs turbulent", "boundary layers",
        "surface tension", "buoyancy", "shock waves",
    ],
    "maths-core": [
        "algebra & identities", "trigonometry", "vectors", "matrices & eigenvalues",
        "complex numbers", "single-variable calculus", "multivariable calculus",
        "differential equations (ODE/PDE)", "linear algebra & null spaces",
        "sequences & series", "probability & statistics", "numerical methods",
        "optimisation & gradients", "graphs & networks", "number theory",
    ],
    "numerics-software": [
        "floating point & conditioning", "stability of integrators",
        "convergence & error order", "Monte Carlo", "interpolation", "regression",
        "unit/dimension checking", "validation vs analytic solution",
        "reproducibility (seeds, versions)",
    ],
}

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def coverage_rows(domains: list[str]) -> list[tuple[str, str, str]]:
    rows = []
    for domain in domains:
        for i, topic in enumerate(DOMAINS[domain]):
            rows.append((domain, f"{LETTERS[i % 26]}", topic))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domains", default=','.join(DOMAINS),
                        help="comma-separated domains (default: all)")
    parser.add_argument("--list", action="store_true", help="list domain names")
    parser.add_argument("--format", choices=("md", "plain"), default="md")
    args = parser.parse_args(argv)

    if args.list:
        for name, topics in DOMAINS.items():
            print(f"{name} ({len(topics)} topics)")
        return 0

    wanted = [d.strip() for d in args.domains.split(",") if d.strip()]
    unknown = [d for d in wanted if d not in DOMAINS]
    if unknown:
        print(f"error: unknown domain(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"known: {', '.join(DOMAINS)}", file=sys.stderr)
        return 2

    if args.format == "md":
        print("| domain | key | topic | used where? | covered by |")
        print("|---|---|---|---|---|")
        for domain, key, topic in coverage_rows(wanted):
            print(f"| {domain} | {key} | {topic} |  |  |")
    else:
        for domain, _key, topic in coverage_rows(wanted):
            print(f"{domain}: {topic}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
