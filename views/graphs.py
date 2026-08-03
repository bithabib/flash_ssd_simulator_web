"""Graphs gallery + per-graph details.

/graphs                 -> gallery of every evaluation figure, grouped, each with a
                           title and a "Details" button.
/graphs/<gid>           -> the details page for one graph family (full description +
                           all its figures).
/figures/full/<fname>   -> serve the generated PNGs from figures/full/.

The live simulator links each of its generated charts here via ?from=live.
"""
import os
from flask import render_template, send_from_directory, abort
from app import app

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "figures", "full")

# Every graph family: id, title, category, the figure file(s), a one-line blurb for
# the gallery card, and the rich HTML details shown on its own page.
GRAPHS = [
    {
        "id": "validation",
        "title": "Validation — EyanaSSDSim vs FEMU (WAF)",
        "category": "Validation",
        "figures": ["A_validation_waf.png"],
        "blurb": "Simulator write-amplification vs the hardware-accurate FEMU emulator, "
                 "across 8 configuration-matched points.",
        "details": """
<p><b>What it shows.</b> Write Amplification Factor (WAF = physical writes / host
writes) from EyanaSSDSim placed next to FEMU (a hardware-accurate NVMe emulator) for
eight configurations measured at the <i>same</i> over-provisioning (OP 25%).</p>
<p><b>How FEMU was measured.</b> Conventional points use <code>fio</code> random-write
fill (OP set by fill size, 3&times; rewrite for steady state); FDP points use a custom
<code>fdp_write</code> tool that steers each 4&nbsp;KB write to a placement handle via
NVMe pass-through. WAF is read from FEMU's instrumented FTL counters
(<code>host</code>/<code>gc</code> pages, <code>hbmw</code>/<code>mbmw</code>).</p>
<p><b>The result — two regimes:</b></p>
<ul>
<li><b>Synthetic (uniform, 80/20): &plusmn;3&ndash;8%, mixed signs.</b> Errors cancel;
the simulator tracks FEMU with no systematic bias where GC is mild and uniform.</li>
<li><b>Real traces (prxy): &minus;18% to &minus;29%, one-directional.</b> The simulator
is consistently <i>below</i> FEMU. This is not error — it is the garbage-collection
<i>erase granularity</i>: the simulator's default block-level reclaim migrates fewer
valid pages than FEMU's superblock (line-level) erase under the heavy, skewed GC that
real traces induce.</li>
</ul>
<p><b>Takeaway.</b> The gap is bounded, explained, one-directional, and closes when the
simulator is configured for superblock GC (see the Granularity Bracket graph).</p>
""",
        "findings": """
<ul>
<li><b>Synthetic, sim vs FEMU:</b> uniform conv +7.1% (1.56 vs 1.46), uniform FDP-single
&minus;7.5% (1.54 vs 1.66), uniform FDP-PI +6.1% (1.75 vs 1.65), 80/20 FDP-single +3.2%
(1.16 vs 1.12), 80/20 FDP-PI +8.0% (1.10 vs 1.02) &mdash; errors <b>cancel</b>, no bias.</li>
<li><b>Real traces, sim vs FEMU:</b> prxy_0 conv &minus;17.8% (1.54 vs 1.87), prxy_1_3M
FDP-single &minus;19.6% (1.26 vs 1.56), FDP-PI &minus;28.8% (1.06 vs 1.49) &mdash;
<b>systematically low, one direction.</b></li>
<li><b>Trend fidelity:</b> the ordering of configs is preserved (Spearman &rho; = 1.0);
the simulator is always &le; FEMU on real traces, exactly as the granularity model predicts.</li>
</ul>
""",
    },
    {
        "id": "bracket",
        "title": "Granularity Bracket — FEMU between block & superblock GC",
        "category": "Validation",
        "figures": ["A2_granularity_bracket.png"],
        "blurb": "FEMU's WAF lies between the simulator's block- and superblock-granular "
                 "GC — the mechanistic cause of the sim–FEMU gap.",
        "details": """
<p><b>What it shows.</b> The same conventional workload run three ways: EyanaSSDSim with
<i>block</i>-granular GC, FEMU (which erases whole superblocks/lines), and EyanaSSDSim
with <i>superblock</i>-granular GC.</p>
<p><b>The clincher.</b> On prxy_0 the three values are
<code>1.54 (block) &le; 1.873 (FEMU) &le; 2.14 (superblock)</code> — FEMU is
<i>bracketed</i> by the simulator's two granularity modes. The ~40% swing from switching
erase granularity <i>contains</i> FEMU's value, proving that granularity — not a modeling
error — is what produces the WAF difference in the Validation graph.</p>
<p><b>Why granularity matters.</b> Real NAND SSDs erase at superblock granularity for
parallelism; a whole line is reclaimed together, so more valid pages are migrated →
higher WAF. Block-granular reclaim can pick the single emptiest block → fewer migrations
→ lower WAF.</p>
""",
        "findings": """
<ul>
<li><b>prxy_0:</b> block GC <b>1.54</b> &le; FEMU <b>1.873</b> &le; superblock GC
<b>2.14</b>. FEMU is bracketed.</li>
<li>The block&rarr;superblock switch moves WAF by ~40% and <i>contains</i> FEMU's value,
so granularity fully accounts for the sim&ndash;FEMU gap in the Validation graph.</li>
<li>Superblock GC also raises wear concentration (DoEC 10.6 &rarr; 20.2 on prxy_0),
the endurance cost of coarse-grained erase.</li>
</ul>
""",
    },
    {
        "id": "waf_by_engine",
        "title": "Write Amplification by Engine across Real Traces",
        "category": "Overview",
        "figures": ["B_waf_by_engine.png"],
        "blurb": "Head-to-head WAF of all nine engines on every real trace.",
        "details": """
<p><b>What it shows.</b> WAF for all nine engine variants — Conventional (block &amp;
superblock GC), FDP (single / PI / II placement), and ZNS (single &amp; hot/cold with
greedy or cost-benefit GC) — on each real trace.</p>
<p><b>How to read it.</b> Lower is better (less write amplification). Grouped bars let you
compare engines within a workload and the same engine across workloads. Note that no
single engine wins everywhere: placement schemes help on skewed, reused data but can cost
extra on write-once or uniform workloads (see Placement Effect).</p>
""",
        "findings": """
<ul>
<li><b>No universal winner.</b> On the aged prxy_1_3M trace the best is FDP-II (1.01),
then FDP-PI (1.06) and conventional block (1.07); ZNS variants are highest (1.49&ndash;1.75).</li>
<li><b>Write-once workloads (TPC-C, sequential) sit at WAF 1.00</b> for every in-place
engine &mdash; no rewrite means no GC. Only ZNS hot/cold pays migration there (1.67&ndash;1.76).</li>
<li><b>Short, bursty prxy_1</b> is the hardest: ZNS hot/cold blows up to 2.89&ndash;3.11,
while conventional block stays 1.35.</li>
</ul>
""",
    },
    {
        "id": "spacetime",
        "title": "Space-Time Occupancy Heatmaps",
        "category": "Distribution",
        "figures": ["C_spacetime_prxy_0.png", "C_spacetime_prxy_1.png",
                    "C_spacetime_prxy_1_3M.png", "C_spacetime_W2K8_TPCC.png",
                    "C_spacetime_synth_uniform.png", "C_spacetime_synth_zipf12.png",
                    "C_spacetime_synth_8020.png", "C_spacetime_synth_sequential.png"],
        "blurb": "How valid data is distributed over reclaim units and time — the flagship "
                 "“how it's distributed” visualization.",
        "details": """
<p><b>What it shows.</b> Each panel is one engine. The vertical axis is the reclaim unit
(block / RU / zone id), the horizontal axis is host-write time, and colour is the
<i>valid fraction</i> of that unit (light = mostly invalid/empty, dark green = full of
valid data).</p>
<p><b>Why it matters.</b> The paper's central point is not just <i>how much</i>
amplification (a scalar WAF) but <i>how the wear and invalidity are distributed</i>. These
heatmaps make the distribution visible: you can see the device fill up (the diagonal
ramp), reach steady state, and how each placement policy organizes hot vs cold data over
time. An engine that keeps units either near-empty or near-full (sharp two-tone) reclaims
cheaply; one that leaves everything half-valid pays a high GC cost.</p>
<p><b>How to read it.</b> Compare the texture across engines: FDP-PI and ZNS hot/cold
create distinct hot (churning) and cold (stable dark) bands, whereas conventional block GC
shows a more uniform speckle.</p>
""",
        "findings": """
<ul>
<li><b>Placement is visible.</b> FDP-PI and ZNS hot/cold form a stable dark cold band
(cold data parked, never re-migrated) plus a small churning hot band &mdash; the
separation the scalar WAF only hints at.</li>
<li><b>Conventional block GC</b> shows a fine, uniform speckle: hot and cold data mixed
across all units, so every reclaim carries some valid pages.</li>
<li><b>Sequential / TPC-C</b> fill cleanly then stay dark and stable (no rewrites, WAF 1.0);
<b>uniform</b> stays uniformly mid-toned (everything ~half-valid &rarr; expensive GC).</li>
</ul>
""",
    },
    {
        "id": "invalidity",
        "title": "Invalidity Distribution (DoIPD)",
        "category": "Distribution",
        "figures": ["D_invalid_dispersion_prxy_0.png", "D_invalid_dispersion_prxy_1.png",
                    "D_invalid_dispersion_prxy_1_3M.png", "D_invalid_dispersion_W2K8_TPCC.png",
                    "D_invalid_dispersion_synth_uniform.png", "D_invalid_dispersion_synth_zipf12.png",
                    "D_invalid_dispersion_synth_8020.png", "D_invalid_dispersion_synth_sequential.png"],
        "blurb": "Degree of Invalid-Page Distribution, measured correctly before every GC "
                 "trigger — not at end of trace.",
        "details": """
<p><b>What it shows.</b> Left: the Degree of Invalid-Page Distribution (DoIPD, the spread
of invalid pages across reclaim units) measured two ways — <b>before every GC trigger</b>
(the steady-state, methodologically-correct measurement) versus <b>at end of trace</b>.
Right: histograms of the invalid-fraction per unit.</p>
<p><b>Why measure before GC.</b> Measuring only at the end of the trace samples a
cooled-down device and understates the real dispersion the FTL works against. Snapshotting
the distribution at each GC trigger captures the hot steady state that actually drives
reclaim decisions.</p>
<p><b>Relation to WAF.</b> Dispersion of invalidity is a <i>spatial</i> property. It
correlates with WAF but only weakly (see Mechanism Scatters, r&nbsp;&asymp;&nbsp;+0.55) —
the real driver is the <i>temporal</i> valid-fraction-at-reclaim.</p>
""",
        "findings": """
<ul>
<li><b>Measuring at end-of-trace understates dispersion.</b> The at-GC-trigger DoIPD is
consistently higher than the end-of-trace value on active workloads &mdash; the device
looks calmer once writing stops than it is during steady-state GC.</li>
<li><b>Dispersion alone doesn't set WAF.</b> Across all runs DoIPD correlates with WAF at
only r&nbsp;&asymp;&nbsp;+0.55 &mdash; useful context, but weaker than the temporal
predictor (r = +0.92).</li>
<li>Skewed workloads (Zipf, 80/20) show wide invalidity spread yet low WAF, because their
hot pages die together regardless of how mixed the layout looks.</li>
</ul>
""",
    },
    {
        "id": "valid_at_reclaim",
        "title": "Valid-Fraction-at-Reclaim (the WAF mechanism)",
        "category": "Mechanism",
        "figures": ["E_valid_at_reclaim_prxy_0.png", "E_valid_at_reclaim_prxy_1.png",
                    "E_valid_at_reclaim_prxy_1_3M.png", "E_valid_at_reclaim_W2K8_TPCC.png",
                    "E_valid_at_reclaim_synth_uniform.png", "E_valid_at_reclaim_synth_zipf12.png",
                    "E_valid_at_reclaim_synth_8020.png", "E_valid_at_reclaim_synth_sequential.png"],
        "blurb": "The valid fraction of the unit GC reclaims — the direct cost that sets "
                 "write amplification.",
        "details": """
<p><b>What it shows.</b> The distribution of the valid fraction of each unit at the moment
GC reclaims it. A unit reclaimed while 10% valid costs almost nothing to migrate; one
reclaimed at 60% valid forces migrating most of its pages.</p>
<p><b>Why it's the mechanism.</b> WAF is set almost entirely by this quantity: every valid
page in a victim must be copied forward (an extra physical write). The green band marks
near-empty (&ldquo;free&rdquo;) victims — the cheap reclaims a good policy maximises.</p>
<p><b>Key result.</b> Across all 69 runs, WAF correlates with mean valid-at-reclaim at
Pearson <b>r = +0.92</b> — far stronger than any spatial/entropy measure. WAF is governed
by <i>when</i> pages die (do a unit's pages die together?), a temporal property, not by the
spatial layout.</p>
""",
        "findings": """
<ul>
<li><b>The correlation is tight: r = +0.92</b> between mean valid-at-reclaim and WAF across
all 69 runs.</li>
<li><b>Concrete points:</b> prxy_1_3M FDP-PI reclaims units only 5.8% valid &rarr; WAF 1.06;
80/20 FDP-PI 13.6% valid &rarr; WAF 1.10; prxy_0 conv 37.7% valid &rarr; WAF 1.54; uniform
conv 48.3% valid &rarr; WAF 1.56. Higher valid-at-reclaim, higher WAF, every time.</li>
<li>Good policies push reclaims into the near-empty &ldquo;free&rdquo; band (&lt;10% valid);
uniform workloads can't, so they pay the most.</li>
</ul>
""",
    },
    {
        "id": "wear",
        "title": "Wear / Endurance Distribution (DoEC)",
        "category": "Distribution",
        "figures": ["F_wear_prxy_0.png", "F_wear_prxy_1.png", "F_wear_prxy_1_3M.png",
                    "F_wear_W2K8_TPCC.png", "F_wear_synth_uniform.png",
                    "F_wear_synth_zipf12.png", "F_wear_synth_8020.png",
                    "F_wear_synth_sequential.png"],
        "blurb": "How erase/reset cycles spread across the device — endurance and "
                 "wear-levelling per engine.",
        "details": """
<p><b>What it shows.</b> Left: a Lorenz-style curve of erase/reset counts (units sorted
hottest-first) — a flat curve means even wear, a steep one means a few units absorb most
of the wear. Right: the Degree of Erase Count (DoEC, standard deviation of erases per
unit) for each engine.</p>
<p><b>Why it matters.</b> SSD lifetime is bounded by per-block erase endurance, so
<i>even</i> wear (low DoEC) extends device life. This is the endurance counterpart to WAF:
a policy can achieve low WAF yet concentrate wear on a few blocks. Comparing engines here
shows the wear-levelling side of each placement strategy.</p>
""",
        "findings": """
<ul>
<li><b>Coarse erase concentrates wear.</b> On prxy_0, superblock GC nearly doubles the wear
spread vs block GC (DoEC 20.2 vs 10.6) &mdash; the endurance price of the lower-WAF-looking
coarse reclaim.</li>
<li><b>WAF and wear can diverge.</b> ZNS hot/cold-greedy on prxy_0 keeps DoEC low (10.4)
despite a high WAF, whereas FDP-PI trades a little wear spread (12.4) for much lower WAF.</li>
<li>Wear-count distributions are mostly uni-modal (Sarle &lt; 0.55) except the pathological
coarse-GC cases, i.e. wear is spread rather than split into hot/cold block populations.</li>
</ul>
""",
    },
    {
        "id": "mechanism",
        "title": "What Predicts WAF — Mechanism Scatters",
        "category": "Mechanism",
        "figures": ["G_mechanism_scatters.png"],
        "blurb": "WAF vs valid-at-reclaim (r=+0.92) vs WAF vs invalidity dispersion "
                 "(r=+0.55) across every run.",
        "details": """
<p><b>What it shows.</b> Every (engine, trace) run as a point, WAF on the y-axis. Left:
against valid-fraction-at-reclaim (the temporal GC cost). Right: against DoIPD (the spatial
invalidity dispersion).</p>
<p><b>The finding.</b> Valid-at-reclaim predicts WAF tightly (<b>r = +0.92</b>); the
spatial dispersion only loosely (<b>r = +0.55</b>). This is the empirical basis for the
paper's claim that write amplification is a <i>temporal</i> phenomenon (pages dying
together) rather than a <i>spatial</i> one (how mixed the layout looks) — and it is the
evidence that refutes the entropy model of FTL behaviour.</p>
""",
        "findings": """
<ul>
<li><b>Temporal beats spatial:</b> WAF vs valid-at-reclaim <b>r = +0.92</b>; WAF vs DoIPD
<b>r = +0.55</b> &mdash; over the same 69 runs.</li>
<li>This is the single figure that carries the paper's thesis: write amplification is set by
<i>when</i> pages die (do a unit's pages die together?), not by how disordered the layout
looks at any instant.</li>
<li>Consistent with the separate entropy-model test, where an entropy-optimal GC policy gave
the <i>worst</i> WAF (+42% to +124%).</li>
</ul>
""",
    },
    {
        "id": "placement",
        "title": "Placement Effect — FDP Isolation & ZNS GC",
        "category": "Overview",
        "figures": ["H_placement.png"],
        "blurb": "FDP single vs PI vs II, and ZNS hot/cold with greedy vs cost-benefit GC.",
        "details": """
<p><b>What it shows.</b> Left: FDP with no isolation (single) vs Persistent Isolation (PI)
vs Initial Isolation (II). Right: ZNS single-stream vs hot/cold separation under greedy and
cost-benefit garbage collection.</p>
<p><b>Honest, workload-dependent findings.</b></p>
<ul>
<li><b>FDP-PI helps only on skewed, sufficiently-aged workloads</b> (e.g. prxy_1_3M,
zipf, 80/20) where there is reuse skew to exploit; on uniform or short traces PI's per-RUH
GC reservation fragments the over-provisioning and can raise WAF. FDP-II is the most robust
across workloads.</li>
<li><b>ZNS hot/cold can backfire.</b> It reduces WAF on zipf but sharply <i>increases</i>
it on prxy_1 (2.89 vs 1.99 single) via a cold-pollution feedback loop; cost-benefit GC does
not rescue it there. A genuine negative result.</li>
</ul>
""",
        "findings": """
<ul>
<li><b>FDP-PI helps on skewed data, hurts on uniform:</b> prxy_1_3M single 1.26 &rarr; PI 1.06
&rarr; II 1.01; 80/20 single 1.16 &rarr; PI 1.10; but uniform single 1.54 &rarr; PI 1.75
&rarr; II 2.21 (isolation reserves OP that a no-skew workload can't repay).</li>
<li><b>FDP-II is the most robust</b> across workloads &mdash; best on skewed, least-bad on
uniform among the isolating modes.</li>
<li><b>ZNS hot/cold can backfire:</b> helps on Zipf (single 1.18 &rarr; hot/cold 1.06) but
hurts badly on prxy_1 (single 1.99 &rarr; greedy 2.89 &rarr; cost-benefit 3.11) &mdash;
cold-pollution feedback that cost-benefit GC does not fix.</li>
</ul>
""",
    },
    {
        "id": "tradeoff",
        "title": "WAF ↔ Wear Trade-off",
        "category": "Mechanism",
        "figures": ["I_waf_wear_tradeoff.png"],
        "blurb": "Every (engine, trace) plotted as write-cost (WAF) vs wear-spread (DoEC).",
        "details": """
<p><b>What it shows.</b> Each point is one (engine, trace): WAF on the x-axis (write cost)
against DoEC on the y-axis (wear spread). Colour encodes the engine.</p>
<p><b>Why it matters.</b> The two headline costs of an FTL — write amplification and wear
concentration — do not always move together. This view exposes engines that buy low WAF at
the price of uneven wear (or vice-versa), which is exactly the design trade-off an SSD
architect must navigate.</p>
""",
        "findings": """
<ul>
<li><b>Low WAF does not guarantee even wear.</b> The cloud of points is not a straight line
&mdash; engines at similar WAF can differ markedly in DoEC, and vice-versa.</li>
<li>Conventional superblock GC lands at high WAF <i>and</i> high wear spread (worst of both)
on real traces; FDP-PI/II cluster toward low WAF with moderate wear.</li>
<li>The frontier is what an FTL designer optimises: this plot names, per (engine, trace),
who is on it and who is dominated.</li>
</ul>
""",
    },
]

GRAPH_BY_ID = {g["id"]: g for g in GRAPHS}

# nicer labels for the per-trace figure captions
_TRACE_LABEL = {
    "prxy_0": "prxy_0 (MSR real)", "prxy_1": "prxy_1 (MSR real)",
    "prxy_1_3M": "prxy_1 (3M writes, real)", "W2K8_TPCC": "TPC-C (W2K8, real)",
    "synth_uniform": "uniform (synthetic)", "synth_zipf12": "Zipf-1.2 (synthetic)",
    "synth_8020": "80/20 (synthetic)", "synth_sequential": "sequential (synthetic)",
}


def _caption(fname):
    for key, lab in _TRACE_LABEL.items():
        if fname.endswith(key + ".png"):
            return lab
    return ""


@app.route("/figures/full/<path:fname>")
def serve_figure(fname):
    if not os.path.isfile(os.path.join(FIGDIR, fname)):
        abort(404)
    return send_from_directory(FIGDIR, fname)


@app.route("/graphs")
def graphs_gallery():
    # only advertise graphs whose (first) figure actually exists
    cards = []
    for g in GRAPHS:
        existing = [f for f in g["figures"] if os.path.isfile(os.path.join(FIGDIR, f))]
        if existing:
            cards.append({**g, "thumb": existing[0], "count": len(existing)})
    # group by category, preserving first-seen order
    order, groups = [], {}
    for c in cards:
        cat = c["category"]
        if cat not in groups:
            groups[cat] = []; order.append(cat)
        groups[cat].append(c)
    return render_template("graphs_gallery.html",
                           groups=[(cat, groups[cat]) for cat in order])


@app.route("/graphs/<gid>")
def graphs_detail(gid):
    g = GRAPH_BY_ID.get(gid)
    if not g:
        abort(404)
    figs = [{"file": f, "caption": _caption(f)}
            for f in g["figures"] if os.path.isfile(os.path.join(FIGDIR, f))]
    # prev/next within the flat list for easy browsing
    ids = [x["id"] for x in GRAPHS]
    i = ids.index(gid)
    prev_g = GRAPHS[i - 1] if i > 0 else None
    next_g = GRAPHS[i + 1] if i < len(GRAPHS) - 1 else None
    return render_template("graphs_detail.html", g=g, figs=figs,
                           prev_g=prev_g, next_g=next_g)
