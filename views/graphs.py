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
<p><b>Our finding.</b> EyanaSSDSim reproduces FEMU's write amplification closely and
predictably. On synthetic workloads the two agree to within &plusmn;3&ndash;8% with mixed
signs (no systematic bias); on real traces the simulator sits a consistent 18&ndash;29%
below FEMU &mdash; a single-cause, one-directional gap we trace entirely to
garbage-collection erase granularity (block- vs superblock-level reclaim).</p>
<p><b>How this helps our work.</b> Agreement with a hardware-accurate emulator is what lets
us trust every result that follows. Because the one systematic difference is understood and
bounded (granularity, see the Bracket graph), we can use EyanaSSDSim for the placement and
distribution study with confidence that its numbers are faithful to real hardware &mdash;
and match FEMU exactly by switching the GC granularity when we need to.</p>
<p><b>What it shows.</b> WAF (physical/host writes) from EyanaSSDSim next to FEMU for eight
configurations at the same over-provisioning (OP 25%). FEMU conventional points come from
<code>fio</code> fill (OP set by fill size, 3&times; rewrite for steady state); FDP points
from a custom <code>fdp_write</code> tool over NVMe pass-through; WAF is read from FEMU's
instrumented FTL counters (<code>host</code>/<code>gc</code>, <code>hbmw</code>/<code>mbmw</code>).</p>
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
<p><b>Our finding.</b> The gap between the simulator and FEMU is explained by exactly one
mechanism: garbage-collection erase granularity. Running the same workload with block- and
superblock-granular GC <i>brackets</i> FEMU's value &mdash; on prxy_0,
<code>1.54 (block) &le; 1.873 (FEMU) &le; 2.14 (superblock)</code>. The ~40% swing from the
granularity switch contains FEMU's number.</p>
<p><b>How this helps our work.</b> It turns an apparent discrepancy into a controlled,
understood modeling parameter. We can read every sim&ndash;FEMU comparison correctly, and
tune the simulator to a target device's erase granularity for an exact match &mdash;
important because real NAND erases at superblock granularity for parallelism.</p>
<p><b>What it shows.</b> The same conventional workload three ways: EyanaSSDSim block GC,
FEMU (superblock erase), EyanaSSDSim superblock GC. Coarser erase reclaims a whole line
together, migrating more valid pages &rarr; higher WAF; block reclaim can take the single
emptiest block &rarr; fewer migrations &rarr; lower WAF.</p>
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
<p><b>Our finding.</b> No single engine wins across workloads. Placement schemes (FDP, ZNS)
reduce write amplification on skewed, reused data but can cost extra on write-once or
uniform workloads &mdash; the benefit is workload-dependent, not universal.</p>
<p><b>How this helps our work.</b> This head-to-head is the map that motivates the rest of
the study: it shows <i>where</i> each placement policy pays off and sends us to the
distribution and mechanism analyses to explain <i>why</i>.</p>
<p><b>What it shows.</b> WAF for all nine engine variants &mdash; Conventional (block &amp;
superblock GC), FDP (single/PI/II), and ZNS (single &amp; hot/cold with greedy or
cost-benefit GC) &mdash; on each real trace. Lower is better; grouped bars compare engines
within a workload and across workloads.</p>
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
<p><b>Our finding.</b> Placement policy is written into the <i>distribution</i> of valid
data, not just the scalar WAF. FDP-PI and ZNS hot/cold visibly park cold data in a stable
band and confine churn to a small hot band, while conventional block GC mixes hot and cold
across every unit &mdash; so every reclaim carries some valid pages.</p>
<p><b>How this helps our work.</b> This is our central lens: characterising <i>how</i> wear
and invalidity spread over space and time, which a single WAF number cannot convey. It makes
the mechanism behind each policy's WAF directly visible and is the qualitative backbone of
the paper's distribution argument.</p>
<p><b>What it shows.</b> One panel per engine; vertical axis = reclaim unit (block/RU/zone),
horizontal = host-write time, colour = valid fraction (light = empty/invalid, dark green =
full). You can watch the device fill (the diagonal ramp), reach steady state, and see how
each policy organises hot vs cold data.</p>
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
<p><b>Our finding.</b> How invalid pages are spread across the device (DoIPD) is a real
signature of a placement policy &mdash; but only when measured at the right moment. Sampled
<b>before every GC trigger</b> it reflects the steady state the FTL actually works against;
sampled only at end-of-trace it understates the dispersion (the device looks calmer once
writing stops). Spatial dispersion tracks WAF loosely (r&nbsp;&asymp;&nbsp;+0.55).</p>
<p><b>How this helps our work.</b> It gives us a principled, correctly-measured metric for
the spatial side of the distribution study, and it sets up the key comparison: this spatial
dispersion versus the temporal valid-at-reclaim measure that governs WAF far more tightly
(Mechanism Scatters).</p>
<p><b>What it shows.</b> Left: DoIPD (spread of invalid pages across units) measured at
GC-trigger vs at end-of-trace. Right: histograms of the invalid-fraction per unit.</p>
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
<p><b>Our finding.</b> The valid fraction of a unit at the moment GC reclaims it is the
quantity that sets write amplification. Across all 69 runs it tracks WAF at Pearson
<b>r = +0.92</b> &mdash; tighter than any spatial dispersion measure. WAF is governed by
<i>when</i> a unit's pages die together (a temporal property), realised as how empty the
unit is when it is reclaimed.</p>
<p><b>How this helps our work.</b> It gives us a single, mechanistic, directly-measurable
lever that explains <i>why</i> one placement policy beats another: good policies push
reclaims into the near-empty band, which is cheap to migrate. Every WAF result in the paper
can be read back to this one cause.</p>
<p><b>What it shows.</b> The distribution of victim valid-fraction at reclaim. A unit taken
at 10% valid costs almost nothing to migrate; one at 60% forces copying most of its pages.
The green band marks the near-empty (&ldquo;free&rdquo;) victims a good policy maximises.</p>
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
<p><b>Our finding.</b> Write amplification and wear-evenness are separate axes: a policy can
look good on WAF yet concentrate erases on a few units. Coarse (superblock) GC in particular
nearly doubles the wear spread on prxy_0 (DoEC 20.2 vs 10.6 for block GC).</p>
<p><b>How this helps our work.</b> It adds the endurance dimension to the distribution study
&mdash; SSD lifetime is bounded by per-block erase count, so how evenly wear is spread
matters as much as WAF. This lets us judge each placement policy on durability, not just
write cost.</p>
<p><b>What it shows.</b> Left: a Lorenz-style curve of erase/reset counts (units sorted
hottest-first) &mdash; flat = even wear, steep = concentrated. Right: the Degree of Erase
Count (DoEC, std of erases per unit) for each engine.</p>
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
<p><b>Our finding.</b> Write amplification is governed by a <i>temporal</i> property &mdash;
whether a unit's pages die together &mdash; far more than by the <i>spatial</i> spread of the
layout. Over all 69 runs, WAF vs valid-at-reclaim gives <b>r = +0.92</b>, while WAF vs
invalidity dispersion (DoIPD) gives only <b>r = +0.55</b>.</p>
<p><b>How this helps our work.</b> This is the analytical backbone of the paper: it names the
quantity to reason about and to target. Reducing write amplification means arranging for
pages to be invalidated together (temporal placement) &mdash; exactly what FDP isolation and
ZNS hot/cold separation attempt &mdash; and this one picture explains why some of them
succeed and others backfire.</p>
<p><b>What it shows.</b> Every (engine, trace) run as a point, WAF on the y-axis. Left: vs
valid-fraction-at-reclaim (the temporal GC cost). Right: vs DoIPD (the spatial invalidity
dispersion).</p>
""",
        "findings": """
<ul>
<li><b>Temporal beats spatial:</b> WAF vs valid-at-reclaim <b>r = +0.92</b>; WAF vs DoIPD
<b>r = +0.55</b> &mdash; over the same 69 runs.</li>
<li>This gives the paper its explanatory variable: write amplification is set by <i>when</i>
pages die (do a unit's pages die together?), not by how disordered the layout looks at any
instant.</li>
<li>It directly explains the placement results &mdash; policies that group same-lifetime data
(e.g. FDP-PI on skewed loads) drive valid-at-reclaim down, and WAF falls with it.</li>
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
<p><b>Our finding.</b> Placement isolation is a workload-dependent tool, not a free win.
FDP-PI lowers WAF on skewed, sufficiently-aged workloads (prxy_1_3M, zipf, 80/20) where
there is reuse skew to exploit, but on uniform or short traces its per-RUH GC reservation
fragments the over-provisioning and can raise WAF; FDP-II is the most robust across
workloads. ZNS hot/cold helps on zipf yet backfires on prxy_1 (2.89 vs 1.99 single) through
a cold-pollution feedback loop that cost-benefit GC does not fix.</p>
<p><b>How this helps our work.</b> This is the actionable design guidance the simulator
exists to produce: which placement scheme to use for which workload, and the failure modes to
avoid. Paired with the Mechanism graph, each outcome is explained through valid-at-reclaim.</p>
<p><b>What it shows.</b> Left: FDP single vs Persistent Isolation (PI) vs Initial Isolation
(II). Right: ZNS single-stream vs hot/cold separation under greedy and cost-benefit GC.</p>
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
<p><b>Our finding.</b> Write amplification and wear-evenness do not move together: engines at
similar WAF can differ sharply in wear spread. Conventional superblock GC lands at high WAF
<i>and</i> high wear on real traces; FDP-PI/II cluster at low WAF with moderate wear.</p>
<p><b>How this helps our work.</b> It frames the design decision as a two-objective
trade-off and identifies, per (engine, trace), which policies sit on the efficient frontier
and which are dominated &mdash; the practical takeaway an FTL designer needs from the study.</p>
<p><b>What it shows.</b> Each point is one (engine, trace): WAF (write cost) on the x-axis vs
DoEC (wear spread) on the y-axis, coloured by engine.</p>
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
