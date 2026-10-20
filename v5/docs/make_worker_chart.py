#!/usr/bin/env python3
"""
Renders the worker-scaling chart in PERFORMANCE.md from worker_scaling.json
(inline SVG between the CHART markers, so it shows on GitHub and on the
site, with native hover tooltips on every point). Re-run after a new
measurement:  python3 v5/docs/make_worker_chart.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "worker_scaling.json")))
runs = data["runs"]
native = data["native_s"]

W, H = 720, 380
L, R, T, B = 64, 150, 24, 56          # plot margins (right side holds the direct labels)
xmax, ymax = 16, 90
px = lambda n: L + (n - 1) / (xmax - 1) * (W - L - R)
py = lambda s: T + (1 - s / ymax) * (H - T - B)

base = runs[0][1]
ideal = [(n, base / n) for n in range(1, 17)]
ideal_d = "M" + " L".join(f"{px(n):.1f} {py(s):.1f}" for n, s in ideal)
meas_d = "M" + " L".join(f"{px(n):.1f} {py(s):.1f}" for n, s in runs)

parts = [f'<figure class="viz-root" style="margin:1.5em 0;max-width:{W}px">',
         '<style>.viz-root{color-scheme:light;--surface-1:#fcfcfb;--text-primary:#0b0b0b;--text-secondary:#52514e;'
         '--grid:#e6e5e1;--series-1:#2a78d6;--series-2:#eb6834}'
         '@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;'
         '--surface-1:#1a1a19;--text-primary:#f0efec;--text-secondary:#c3c2b7;--grid:#33332f;--series-1:#3987e5;--series-2:#d95926}}'
         '.viz-root svg{width:100%;height:auto;background:var(--surface-1);border-radius:10px}'
         '.viz-root text{font:12px system-ui,sans-serif;fill:var(--text-secondary)}'
         '.viz-root .pt:hover circle.mark{r:7}.viz-root figcaption{font-size:13px;color:var(--text-secondary);margin-top:.5em}</style>',
         f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="ws-title ws-desc">',
         '<title id="ws-title">Render time vs number of Web Workers</title>',
         f'<desc id="ws-desc">Wall time for 88 Minkowski sums falls from {base} s with 1 worker to '
         f'{runs[-1][1]} s with 16; native Python takes {native} s.</desc>']
for s in range(0, ymax + 1, 15):
    parts.append(f'<line x1="{L}" x2="{W - R}" y1="{py(s):.1f}" y2="{py(s):.1f}" stroke="var(--grid)" stroke-width="1"/>'
                 f'<text x="{L - 8}" y="{py(s) + 4:.1f}" text-anchor="end">{s}</text>')
for n in (1, 2, 4, 8, 12, 16):
    parts.append(f'<text x="{px(n):.1f}" y="{H - B + 18}" text-anchor="middle">{n}</text>')
parts.append(f'<text x="{(L + W - R) / 2:.1f}" y="{H - 14}" text-anchor="middle" style="fill:var(--text-primary)">Web Workers</text>'
             f'<text transform="translate(16 {(T + H - B) / 2:.1f}) rotate(-90)" text-anchor="middle" style="fill:var(--text-primary)">Wall time (s)</text>')
# native reference
parts.append(f'<line x1="{L}" x2="{W - R}" y1="{py(native):.1f}" y2="{py(native):.1f}" stroke="var(--text-secondary)" stroke-width="1.5" stroke-dasharray="2 4"/>'
             f'<text x="{W - R + 8}" y="{py(native) + 4:.1f}">native Python {native} s</text>')
# ideal + measured
parts.append(f'<path d="{ideal_d}" fill="none" stroke="var(--series-2)" stroke-width="2" stroke-dasharray="6 5"/>'
             f'<text x="{W - R + 8}" y="{py(ideal[-1][1]) + 16:.1f}" style="fill:var(--text-primary)">perfect scaling</text>')
parts.append(f'<path d="{meas_d}" fill="none" stroke="var(--series-1)" stroke-width="2" stroke-linejoin="round"/>'
             f'<text x="{W - R + 8}" y="{py(runs[-1][1]) + 4:.1f}" style="fill:var(--text-primary);font-weight:600">measured {runs[-1][1]} s</text>')
for n, s in runs:
    tip = f"{n} worker{'s' if n > 1 else ''}: {s} s  ({base / s:.1f}x vs 1 worker, {native / s:.2f}x vs native)"
    parts.append(f'<g class="pt"><title>{tip}</title><circle cx="{px(n):.1f}" cy="{py(s):.1f}" r="14" fill="transparent"/>'
                 f'<circle class="mark" cx="{px(n):.1f}" cy="{py(s):.1f}" r="5" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2"/></g>')
# selective direct labels: the 2-worker headline and the best point
for n, s, label in ((2, 45.8, "2 workers: 1.9x faster"),):
    parts.append(f'<text x="{px(n) + 10:.1f}" y="{py(s) - 10:.1f}" style="fill:var(--text-primary)">{label}</text>')
parts.append('</svg>')
m = data["machine"]
parts.append(f'<figcaption>{data["job"]}. Measured {data["measured"]} on {m["computer"]}, {m["cpu"]}, {m["ram"]} RAM, '
             f'{m["os"]}, {m["browser"]}; {m["engine"]}. Native: {data["native_note"]}. Hover a point for exact numbers.</figcaption>')
parts.append('</figure>')
chart = "\n".join(parts)

# HTML table, not Markdown: Jekyll's kramdown won't parse a pipe table that
# sits inside this HTML-commented block (it rendered as one run-on line).
rows = "".join(f"<tr><td>{n}</td><td>{s} s</td><td>{base / s:.1f}x</td><td>"
               + (f"{native / s:.2f}x faster" if s < native else f"{s / native:.2f}x slower") + "</td></tr>"
               for n, s in runs)
table = [f'<table><thead><tr><th>Workers</th><th>Wall time</th><th>vs 1 worker</th><th>vs native ({native} s)</th></tr></thead>'
         f"<tbody>{rows}</tbody></table>"]
block = f"<!-- CHART:START (generated by make_worker_chart.py - edit worker_scaling.json, not this block) -->\n{chart}\n\n" + "\n".join(table) + "\n<!-- CHART:END -->"

doc = os.path.join(HERE, "PERFORMANCE.md")
text = open(doc).read()
text = re.sub(r"<!-- CHART:START.*?<!-- CHART:END -->", lambda _m: block, text, flags=re.S)
open(doc, "w").write(text)
print("chart written into", doc)
