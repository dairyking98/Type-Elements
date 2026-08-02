---
layout: page
title: Roadmap
---

## Machine ports: done

Every planned machine has been ported: Blickensderfer, Postal, Mignon,
Bennett, Helios Klimax, Hammond, Hammond Split, the IBM/Selectric family
(Selectric12, Selectric3, Selectric Composer), and the standalone Type
Slug family (Type Slug, Vogue Slug, Gauge Slug, Oliver Slug, Lumi Slug).
See [Machines](machines) for what each one shares with the others.
Nothing else is on the roadmap for new machine ports.

## Planned, not started

### Portable single-executable packaging

Ship v4 as a single portable executable per platform (Linux binary,
Windows `.exe`, macOS binary/app) that needs no `.venv`/repo checkout to
run - true portable/USB-stick semantics, not an installed app scattering
files into OS user-data directories. Not a near-term priority as of
2026-07-22; see the [full plan](roadmap-packaging) for the phased
approach and why it isn't a small change (path resolution, the `f3d`
subprocess dependency, and `tune.py`'s live log-streaming architecture
all need to survive being frozen into a single binary).

## Recently shipped

This documentation site itself - a Jekyll site over the existing
`README.md`/`SESSION_LOG.md`/`docs/*.md` content, deployed to GitHub
Pages via a `gh-pages` branch and Action.
