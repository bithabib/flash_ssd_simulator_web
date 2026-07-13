"""Beginner-friendly blog content explaining SSDs, the FTL, and ZNS.

Each post is a self-contained HTML fragment (with inline SVG figures so nothing
external needs to load). The blog views render these into the site's templates.
Posts are ordered as a reading path; `related` links weave them together.
"""

# --- reusable little HTML helpers -------------------------------------------
def _key(html):
    return f'<div class="keybox">{html}</div>'

def _analogy(html):
    return f'<div class="analogy"><b>Analogy.</b> {html}</div>'

def _paper(html):
    return f'<div class="paperbox"><b>In the EyanaSSDSim paper &amp; simulator.</b> {html}</div>'


# ---------------------------------------------------------------------------
# POSTS
# ---------------------------------------------------------------------------
POSTS = [

# 1 ----------------------------------------------------------------------
{
"slug": "ssd-basics",
"category": "Foundations",
"title": "What Is an SSD? Flash Memory vs. Hard Drives",
"subtitle": "Why solid-state drives behave so differently from the spinning disks they replaced.",
"html": f"""
<p>A <b>solid-state drive (SSD)</b> stores your data in <b>NAND flash memory</b> — silicon chips with
no moving parts. A traditional <b>hard disk drive (HDD)</b> stores data as magnetic patterns on
spinning platters, read by a mechanical arm. That single difference — silicon vs. spinning metal —
explains almost everything about how SSDs behave.</p>

<svg viewBox="0 0 640 150" width="100%" style="max-width:640px" class="figsvg">
  <rect x="10" y="20" width="290" height="110" fill="#fff" stroke="#888"/>
  <text x="20" y="16" font-size="12" fill="#333">HDD — spinning platter</text>
  <circle cx="150" cy="80" r="45" fill="#eee" stroke="#666"/>
  <circle cx="150" cy="80" r="6" fill="#666"/>
  <line x1="215" y1="35" x2="150" y2="80" stroke="#c33" stroke-width="3"/>
  <text x="20" y="125" font-size="10" fill="#888">arm must physically move → slow random access</text>
  <rect x="340" y="20" width="290" height="110" fill="#fff" stroke="#888"/>
  <text x="350" y="16" font-size="12" fill="#333">SSD — flash chips</text>
  <g fill="#2ca02c">
    <rect x="360" y="40" width="50" height="30"/><rect x="420" y="40" width="50" height="30"/>
    <rect x="480" y="40" width="50" height="30"/><rect x="540" y="40" width="50" height="30"/>
    <rect x="360" y="80" width="50" height="30"/><rect x="420" y="80" width="50" height="30"/>
    <rect x="480" y="80" width="50" height="30"/><rect x="540" y="80" width="50" height="30"/>
  </g>
  <text x="350" y="125" font-size="10" fill="#888">no moving parts → fast, parallel access</text>
</svg>
<div class="cap">HDDs pay a mechanical seek cost for random access; SSDs read any location almost instantly.</div>

<h3>What flash memory can and cannot do</h3>
<p>Flash memory has one deeply important quirk that shapes the entire design of an SSD:
<b>you cannot overwrite data in place.</b> Once a location holds data, you must <i>erase</i> it
before you can write to it again — and erase happens in large chunks, not per byte.</p>

{_key("A flash cell can be <b>programmed</b> (written) quickly, but to reset it you must <b>erase</b> a whole <b>block</b> of thousands of cells at once. Reads are fast, writes are slower, erases are slowest and coarse-grained.")}

{_analogy("Think of a flash block like a page written in <b>pen</b>, not pencil. You can fill empty lines, but to change a line you must photocopy the lines you want to keep onto a fresh page and shred the old one. That copy-and-shred cycle is the heart of how SSDs work.")}

<h3>Why this matters</h3>
<p>Because overwriting is impossible, an SSD constantly plays a shell game: it writes new data to
fresh space, marks the old copy as <b>stale (invalid)</b>, and later reclaims that stale space by
erasing whole blocks. Managing that game well — with minimal extra writes and even wear — is what
separates a good SSD from a bad one, and it's exactly what the EyanaSSDSim simulator lets you watch.</p>

{_paper("The whole simulator exists to make these invisible internal mechanics <i>visible</i>. Everything else in this blog builds on this one fact: flash can't be overwritten in place.")}

<p>Next: <a href="/blog/flash-hierarchy">how flash is physically organized</a> into cells, pages,
blocks, planes, dies, and channels.</p>
""",
"related": ["flash-hierarchy", "read-write-erase", "zns"],
},

# 2 ----------------------------------------------------------------------
{
"slug": "flash-hierarchy",
"category": "Foundations",
"title": "Inside the Chip: Cells, Pages, Blocks, Planes, Dies, Channels",
"subtitle": "The physical hierarchy of a flash SSD — and why every level exists.",
"html": f"""
<p>An SSD is built from a strict physical hierarchy. Understanding it is the key to understanding
everything else, because operations happen at <i>different</i> levels: you <b>read/write pages</b>,
but you <b>erase blocks</b>, and you gain speed through <b>parallel channels</b>.</p>

<svg viewBox="0 0 700 210" width="100%" style="max-width:700px" class="figsvg">
  <rect x="8" y="24" width="684" height="176" fill="#fafafa" stroke="#333"/>
  <text x="12" y="18" font-size="12">Channel (parallel bus)</text>
  <rect x="20" y="36" width="320" height="150" fill="#eef4fb" stroke="#1f77b4"/>
  <text x="26" y="50" font-size="11" fill="#1f77b4">Chip → Die → Plane</text>
  <rect x="32" y="58" width="296" height="120" fill="#f3f8ee" stroke="#2ca02c"/>
  <text x="38" y="72" font-size="10" fill="#2ca02c">Plane holds many Blocks</text>
  <g stroke="#333" fill="#cde3c0">
    <rect x="42" y="82" width="60" height="86"/><rect x="112" y="82" width="60" height="86"/>
    <rect x="182" y="82" width="60" height="86"/><rect x="252" y="82" width="60" height="86"/>
  </g>
  <text x="46" y="94" font-size="9">Block</text>
  <g fill="#2ca02c"><rect x="46" y="98" width="52" height="6"/><rect x="46" y="106" width="52" height="6"/>
     <rect x="46" y="114" width="52" height="6"/><rect x="46" y="122" width="52" height="6"/></g>
  <text x="46" y="150" font-size="8" fill="#555">rows = Pages</text>
  <text x="360" y="60" font-size="11" fill="#888">…more channels run in parallel…</text>
  <g fill="#1f77b4"><rect x="360" y="70" width="14" height="110"/><rect x="380" y="70" width="14" height="110"/>
     <rect x="400" y="70" width="14" height="110"/></g>
</svg>
<div class="cap">A page lives in a block, blocks live in a plane, planes in a die, dies in a chip, chips on a channel.</div>

<h3>The levels, smallest to largest</h3>
<ul>
  <li><b>Cell</b> — one transistor holding 1–4 bits (SLC/MLC/TLC/QLC). The atom of storage.</li>
  <li><b>Page</b> — the smallest unit you can <b>read or write</b>. Typically 4–16&nbsp;KB.</li>
  <li><b>Block</b> — the smallest unit you can <b>erase</b>. Hundreds to thousands of pages.</li>
  <li><b>Plane</b> — a group of blocks that can operate somewhat independently.</li>
  <li><b>Die (LUN)</b> — one or more planes; the unit that executes a command.</li>
  <li><b>Chip / package</b> — one or more dies sharing a package.</li>
  <li><b>Channel</b> — a bus connecting several chips to the controller; channels run <b>in parallel</b>.</li>
</ul>

{_key("Remember the mismatch: the <b>read/write unit is a page</b>, but the <b>erase unit is a whole block</b>. This size mismatch is the root cause of garbage collection and write amplification.")}

<h3>Why so many levels? Parallelism.</h3>
<p>Each channel, die, and plane can work at the same time. Spreading writes across them is how an SSD
reaches gigabytes per second from chips that are individually slow. <i>How</i> you spread data across
these units is called the <a href="/blog/data-placement">allocation scheme</a>, and choosing it well
is one of the paper's central questions.</p>

{_analogy("A supermarket with one cashier is slow no matter how fast they scan. Open 8 lanes (channels) with 4 baggers each (dies/planes) and throughput multiplies. The SSD controller is the manager deciding which lane each customer joins.")}

{_paper("On the <a href='/stream'>Live Simulator</a> you choose Channels, Chips, Dies, Planes, Blocks/plane, and Pages/block yourself. The nested grid you see is exactly this hierarchy — each small square is one block, grouped by plane → die → chip → channel.")}
""",
"related": ["read-write-erase", "data-placement", "ssd-basics"],
},

# 3 ----------------------------------------------------------------------
{
"slug": "read-write-erase",
"category": "Foundations",
"title": "The Big Asymmetry: Read, Program, and Erase",
"subtitle": "Why writing to an SSD is never as simple as it sounds.",
"html": f"""
<p>Flash supports three operations, and they are wildly asymmetric in <b>granularity</b> and
<b>speed</b>. This asymmetry is the single most important thing to internalize about SSDs.</p>

<table class="btable">
<tr><th>Operation</th><th>Unit</th><th>Relative speed</th><th>Notes</th></tr>
<tr><td><b>Read</b></td><td>page</td><td>fastest (~tens of µs)</td><td>random reads are cheap</td></tr>
<tr><td><b>Program (write)</b></td><td>page</td><td>slower (~hundreds of µs)</td><td>only onto an <i>erased</i> page</td></tr>
<tr><td><b>Erase</b></td><td>block</td><td>slowest (~ms)</td><td>resets a whole block of pages</td></tr>
</table>

<h3>The rule that changes everything</h3>
{_key("You can only program a page that is currently <b>erased</b>. You cannot overwrite a page that already holds data. To reuse it, you must erase its <b>entire block</b> first.")}

<p>So what happens when software "overwrites" a file? The SSD does <b>not</b> edit the old page.
Instead it:</p>
<ol>
  <li>writes the new data to a <b>fresh, already-erased page</b> somewhere else,</li>
  <li>updates its map so the logical address now points to the new page, and</li>
  <li>marks the old page as <b>invalid (stale)</b> — dead data that still occupies space.</li>
</ol>

<svg viewBox="0 0 640 170" width="100%" style="max-width:640px" class="figsvg">
  <text x="10" y="16" font-size="12">"Overwrite page A" — what really happens</text>
  <rect x="20" y="30" width="120" height="120" fill="#fff" stroke="#333"/>
  <text x="26" y="26" font-size="10" fill="#555">Block (before)</text>
  <rect x="30" y="40" width="100" height="22" fill="#2ca02c"/><text x="60" y="56" font-size="11" fill="#fff">A (valid)</text>
  <rect x="30" y="66" width="100" height="22" fill="#2ca02c"/><text x="60" y="82" font-size="11" fill="#fff">B</text>
  <rect x="30" y="92" width="100" height="22" fill="#eee" stroke="#ccc"/><text x="55" y="108" font-size="10" fill="#999">erased</text>
  <text x="160" y="95" font-size="22" fill="#888">&#8594;</text>
  <rect x="200" y="30" width="120" height="120" fill="#fff" stroke="#333"/>
  <text x="206" y="26" font-size="10" fill="#555">Block (after)</text>
  <rect x="210" y="40" width="100" height="22" fill="#888"/><text x="230" y="56" font-size="10" fill="#fff">A (INVALID)</text>
  <rect x="210" y="66" width="100" height="22" fill="#2ca02c"/><text x="250" y="82" font-size="11" fill="#fff">B</text>
  <rect x="210" y="92" width="100" height="22" fill="#2ca02c"/><text x="228" y="108" font-size="11" fill="#fff">A' (new)</text>
  <text x="345" y="80" font-size="11" fill="#c33">old A is now dead weight —</text>
  <text x="345" y="98" font-size="11" fill="#c33">it wastes space until the</text>
  <text x="345" y="116" font-size="11" fill="#c33">whole block is erased.</text>
</svg>
<div class="cap">An "overwrite" leaves a stale copy behind. Those stale pages accumulate until garbage collection reclaims them.</div>

<p>Over time, blocks fill up with a mix of <b>valid</b> and <b>invalid</b> pages. Eventually the SSD
runs low on erased space and must clean up — that's <a href="/blog/garbage-collection">garbage
collection</a>. And the cleanup itself causes extra writes, which is
<a href="/blog/write-amplification">write amplification</a>.</p>

{_paper("In the Live Simulator's block grid, this is precisely the color you see: a block darkens/greens according to how many of its pages are <b>invalid</b>. Watching blocks fill with stale pages and then snap back to empty after an erase <i>is</i> this asymmetry in action.")}
""",
"related": ["garbage-collection", "write-amplification", "ftl"],
},

# 4 ----------------------------------------------------------------------
{
"slug": "ftl",
"category": "The FTL at Work",
"title": "The Flash Translation Layer (FTL) and Address Mapping",
"subtitle": "The tiny operating system inside every SSD that hides flash's quirks.",
"html": f"""
<p>Your computer thinks it's talking to a simple array of numbered blocks — <b>logical block
addresses</b> (LBAs), or in page terms, <b>logical page numbers (LPNs)</b>. But flash can't be
overwritten in place, so those logical addresses can't map to fixed physical locations. The
<b>Flash Translation Layer (FTL)</b> is the firmware that bridges this gap.</p>

{_key("The FTL keeps a <b>mapping table</b>: logical page number (what the host asks for) → physical page number (where the data actually lives). Every write picks a fresh physical page and updates this table.")}

<svg viewBox="0 0 660 160" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">Host asks for LPN 42 → FTL looks up where it really is</text>
  <rect x="20" y="30" width="120" height="40" fill="#eef4fb" stroke="#1f77b4"/>
  <text x="35" y="55" font-size="12">Host: write LPN 42</text>
  <text x="150" y="55" font-size="20" fill="#888">&#8594;</text>
  <rect x="185" y="30" width="180" height="110" fill="#fff" stroke="#333"/>
  <text x="191" y="26" font-size="10" fill="#555">Mapping table (LPN→PPN)</text>
  <g font-size="11" fill="#333">
    <text x="195" y="50">41 → 1180</text><text x="195" y="70">42 → 9007  (updated!)</text>
    <text x="195" y="90">43 → 502</text><text x="195" y="110">…</text>
  </g>
  <text x="372" y="90" font-size="20" fill="#888">&#8594;</text>
  <rect x="410" y="30" width="230" height="110" fill="#f3f8ee" stroke="#2ca02c"/>
  <text x="416" y="26" font-size="10" fill="#555">Flash (log-structured writes)</text>
  <g fill="#888"><rect x="420" y="40" width="30" height="16"/></g><text x="455" y="52" font-size="9" fill="#888">old PPN 3300 (now invalid)</text>
  <g fill="#2ca02c"><rect x="420" y="100" width="30" height="16"/></g><text x="455" y="112" font-size="9" fill="#2ca02c">new PPN 9007 (valid)</text>
</svg>
<div class="cap">Writes are appended to fresh pages (log-structured); the table is repointed and the old page becomes invalid.</div>

<h3>Log-structured writing</h3>
<p>Because every write goes to a fresh erased page, the FTL effectively writes data like a
never-ending journal — always appending. This is called <b>log-structured</b> writing. It's fast
(no searching for a spot), but it steadily consumes erased pages and leaves invalid ones behind,
which is why garbage collection is unavoidable.</p>

<h3>What the FTL is responsible for</h3>
<ul>
  <li><b>Address mapping</b> — the LPN→PPN table above.</li>
  <li><b>Data placement</b> — which channel/die/plane a write goes to (the <a href="/blog/data-placement">allocation scheme</a>).</li>
  <li><b>Garbage collection</b> — reclaiming invalid pages by erasing blocks.</li>
  <li><b>Wear leveling</b> — spreading erases so no block dies early.</li>
</ul>

{_analogy("The FTL is a hotel concierge. Guests (logical addresses) never know or care which physical room they're in; the concierge keeps a ledger and can move guests between rooms freely, as long as the ledger stays correct.")}

{_paper("EyanaSSDSim implements a real FTL: a forward map (LPN→PPN), a reverse map (PPN→LPN) used during garbage collection, and per-block valid/invalid counters. The simulator's correctness depends on keeping these consistent — a class of bug the paper's rebuilt engine specifically fixed.")}
""",
"related": ["garbage-collection", "data-placement", "read-write-erase"],
},

# 5 ----------------------------------------------------------------------
{
"slug": "garbage-collection",
"category": "The FTL at Work",
"title": "Garbage Collection: Cleaning Up Stale Data",
"subtitle": "How the SSD reclaims space — and why it can never be free.",
"html": f"""
<p>Every overwrite leaves a stale (invalid) page behind. Eventually the SSD runs low on erased pages
to write into. <b>Garbage collection (GC)</b> is the process that reclaims that wasted space — but
because erase works on whole blocks, GC must first rescue any still-valid pages.</p>

<h3>The GC cycle</h3>
<ol>
  <li><b>Pick a victim block</b> — usually the one with the <i>fewest valid pages</i> (most garbage to reclaim).</li>
  <li><b>Migrate</b> the victim's still-valid pages by copying them to a fresh block.</li>
  <li><b>Erase</b> the victim block, returning it to the pool of free, writable blocks.</li>
</ol>

<svg viewBox="0 0 660 170" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">Greedy GC: reclaim the block with the least valid data</text>
  <rect x="20" y="30" width="90" height="120" fill="#fff" stroke="#c33" stroke-width="2"/>
  <text x="24" y="26" font-size="10" fill="#c33">Victim</text>
  <rect x="28" y="40" width="74" height="18" fill="#888"/><rect x="28" y="60" width="74" height="18" fill="#888"/>
  <rect x="28" y="80" width="74" height="18" fill="#2ca02c"/><rect x="28" y="100" width="74" height="18" fill="#888"/>
  <rect x="28" y="120" width="74" height="18" fill="#888"/>
  <text x="115" y="80" font-size="9" fill="#2ca02c">1 valid,</text><text x="115" y="94" font-size="9" fill="#888">4 invalid</text>
  <text x="180" y="95" font-size="18" fill="#888">&#8594; migrate valid</text>
  <rect x="330" y="30" width="90" height="120" fill="#fff" stroke="#2ca02c"/>
  <text x="334" y="26" font-size="10" fill="#2ca02c">Fresh block</text>
  <rect x="338" y="40" width="74" height="18" fill="#2ca02c"/>
  <text x="430" y="95" font-size="18" fill="#888">→ erase victim</text>
  <rect x="560" y="30" width="90" height="120" fill="#eee" stroke="#999" stroke-dasharray="4"/>
  <text x="566" y="95" font-size="11" fill="#999">free again</text>
</svg>
<div class="cap">GC copies the one valid page out, then erases the block. That extra copy is the cost of cleaning.</div>

{_key("GC is <b>not free</b>: rescuing valid pages means extra physical writes that the host never asked for. The more valid data a victim holds, the more copying — and the higher the <a href='/blog/write-amplification'>write amplification</a>.")}

<h3>Victim-selection policies</h3>
<ul>
  <li><b>Greedy</b> — always pick the block with the fewest valid pages. Simple and usually excellent.</li>
  <li><b>Cost–benefit</b> — also favor blocks whose data is "cold" (hasn't changed in a while), so you don't keep re-collecting hot data.</li>
  <li><b>FIFO</b> — reclaim the oldest block. Cheap to track, but ignores how much garbage a block holds.</li>
</ul>

{_analogy("GC is like defragmenting a parking garage that can only demolish and rebuild an entire floor at a time. Before you demolish a floor, you must drive out every car still in use — and every one of those drives is wasted effort you'd rather avoid.")}

<h3>When does GC run?</h3>
<p>GC kicks in when free space falls below a threshold (a <b>watermark</b>). If the drive is nearly
full of valid data, victims hold lots of valid pages, copying explodes, and both performance and
endurance suffer. This is why SSDs reserve hidden spare capacity —
<a href="/blog/over-provisioning">over-provisioning</a>.</p>

{_paper("EyanaSSDSim supports greedy, cost–benefit, and FIFO policies and reports the resulting write amplification for each. On the Live Simulator you literally watch victim blocks lose their valid pages, get erased (snap to white/free), and rejoin the pool.")}
""",
"related": ["write-amplification", "over-provisioning", "ftl"],
},

# 6 ----------------------------------------------------------------------
{
"slug": "write-amplification",
"category": "Performance &amp; Endurance",
"title": "Write Amplification (WAF): The Hidden Write Tax",
"subtitle": "Why writing 1 GB to an SSD can cost it 2 GB of real flash writes.",
"html": f"""
<p><b>Write amplification</b> is the ratio between the data actually written to the flash and the data
the host asked to write. Garbage collection copies valid pages around, so the flash always writes
<i>more</i> than the host requested.</p>

{_key("<div class='formula'>WAF = (host writes + GC copy writes) / host writes</div> A WAF of 1.0 is perfect (no extra writes). A WAF of 3.0 means every 1 GB from the host costs 3 GB of real flash wear.")}

<svg viewBox="0 0 640 130" width="100%" style="max-width:640px" class="figsvg">
  <text x="10" y="16" font-size="12">Host wrote 100 pages, but flash actually wrote 250</text>
  <rect x="20" y="30" width="200" height="26" fill="#2ca02c"/><text x="30" y="48" font-size="12" fill="#fff">host writes (100)</text>
  <rect x="20" y="70" width="200" height="26" fill="#2ca02c"/><rect x="220" y="70" width="300" height="26" fill="#c66"/>
  <text x="30" y="88" font-size="12" fill="#fff">host (100)</text><text x="300" y="88" font-size="12" fill="#fff">GC copies (150)</text>
  <text x="530" y="88" font-size="14" fill="#333">WAF = 2.5</text>
</svg>
<div class="cap">Every GC copy is a write the host never requested — pure overhead that wears the flash and steals bandwidth.</div>

<h3>Why you should care</h3>
<ul>
  <li><b>Endurance</b> — flash cells survive a limited number of erase cycles. Higher WAF burns through that budget faster, shortening drive life.</li>
  <li><b>Performance</b> — GC copies compete with your real writes for flash bandwidth, causing latency spikes.</li>
  <li><b>Energy</b> — every extra write costs power.</li>
</ul>

<h3>What makes WAF worse (or better)</h3>
<ul>
  <li><b>Fuller drive</b> → victims hold more valid data → more copying → higher WAF.</li>
  <li><b>More <a href="/blog/over-provisioning">over-provisioning</a></b> → emptier victims → lower WAF.</li>
  <li><b>Random/skewed writes</b> → mixed hot &amp; cold data in the same block → more copying.</li>
  <li><b>Smart data placement &amp; GC policy</b> → separates hot from cold → lower WAF.</li>
</ul>

{_analogy("WAF is like moving house every time you buy one new book: you keep re-packing and re-carrying all the books you already owned. The ratio of total books carried to new books bought is your amplification.")}

{_paper("Write amplification is <i>the</i> headline metric in EyanaSSDSim. The Live Simulator plots WAF live as a trace replays; the paper compares WAF across workloads, over-provisioning levels, GC policies, and — crucially — between a conventional SSD and <a href='/blog/zns'>ZNS</a>.")}
""",
"related": ["over-provisioning", "garbage-collection", "zns"],
},

# 7 ----------------------------------------------------------------------
{
"slug": "over-provisioning",
"category": "Performance &amp; Endurance",
"title": "Over-Provisioning: Spare Space That Buys Performance",
"subtitle": "The hidden capacity that keeps garbage collection cheap.",
"html": f"""
<p>A "512&nbsp;GB" SSD usually contains more than 512&nbsp;GB of flash. The extra, hidden capacity is
<b>over-provisioning (OP)</b> — spare space the host can never use directly, reserved so the FTL always
has room to maneuver during garbage collection.</p>

{_key("<div class='formula'>OP = (physical capacity − usable capacity) / usable capacity</div> Typical consumer drives reserve ~7%; enterprise drives ic often 28% or more. More OP → lower write amplification, but less usable space.")}

<svg viewBox="0 0 640 90" width="100%" style="max-width:640px" class="figsvg">
  <text x="10" y="16" font-size="12">Physical flash capacity</text>
  <rect x="20" y="26" width="470" height="34" fill="#2ca02c"/><text x="180" y="48" font-size="12" fill="#fff">user-visible capacity</text>
  <rect x="490" y="26" width="130" height="34" fill="#1f77b4"/><text x="500" y="48" font-size="11" fill="#fff">spare (OP)</text>
  <text x="20" y="78" font-size="10" fill="#888">The spare is always erased and ready — it gives GC empty blocks to copy into.</text>
</svg>
<div class="cap">The spare pool means victims can be emptier on average, so GC copies fewer valid pages.</div>

<h3>Why a little spare space helps so much</h3>
<p>Imagine a drive that is 100% full of valid data. To reclaim any block, GC would have to copy
almost all of it — catastrophic amplification. Now reserve 20% as spare: the drive only ever holds
80% valid data, so the average victim is far emptier, and each cleanup copies much less. A small
percentage of reserved space produces a <b>large</b> drop in write amplification. The relationship
is non-linear — the first few percent of OP help the most.</p>

{_analogy("Over-provisioning is the empty space you leave in a sliding tile puzzle. With one empty tile you can rearrange everything; with zero empty tiles the puzzle is frozen. That one gap makes all the movement possible.")}

{_paper("On the Live Simulator, the <b>Over-provisioning</b> dropdown (10% / 20% / 25%) changes exactly this reserve. Run the same trace at different OP levels and watch the WAF curve drop as OP rises — one of the clearest cause-and-effect demonstrations the tool offers.")}
""",
"related": ["write-amplification", "garbage-collection"],
},

# 8 ----------------------------------------------------------------------
{
"slug": "wear-leveling",
"category": "Performance &amp; Endurance",
"title": "Endurance, Wear, and Wear Leveling",
"subtitle": "Flash cells wear out — the trick is to make them wear out evenly.",
"html": f"""
<p>Each flash block tolerates only a limited number of <b>program/erase (P/E) cycles</b> — a few
thousand for modern TLC/QLC, tens of thousands for older SLC. After that, the block becomes
unreliable. <b>Wear leveling</b> is the FTL's job of spreading erases evenly so no single block dies
long before the others.</p>

{_key("If some blocks are erased constantly (hot data) while others sit untouched (cold data), the hot blocks wear out early and the drive fails — even though most of the flash is barely used. Wear leveling prevents this <b>uneven wear</b>.")}

<svg viewBox="0 0 660 150" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">Erase counts across 10 blocks</text>
  <text x="20" y="34" font-size="11" fill="#c33">Poor wear leveling (uneven)</text>
  <g fill="#c33">
    <rect x="20" y="40" width="16" height="40"/><rect x="40" y="66" width="16" height="14"/><rect x="60" y="70" width="16" height="10"/>
    <rect x="80" y="44" width="16" height="36"/><rect x="100" y="72" width="16" height="8"/><rect x="120" y="70" width="16" height="10"/>
    <rect x="140" y="42" width="16" height="38"/><rect x="160" y="73" width="16" height="7"/><rect x="180" y="71" width="16" height="9"/><rect x="200" y="68" width="16" height="12"/>
  </g>
  <text x="360" y="34" font-size="11" fill="#2ca02c">Good wear leveling (even)</text>
  <g fill="#2ca02c">
    <rect x="360" y="58" width="16" height="22"/><rect x="380" y="56" width="16" height="24"/><rect x="400" y="58" width="16" height="22"/>
    <rect x="420" y="57" width="16" height="23"/><rect x="440" y="58" width="16" height="22"/><rect x="460" y="56" width="16" height="24"/>
    <rect x="480" y="58" width="16" height="22"/><rect x="500" y="57" width="16" height="23"/><rect x="520" y="58" width="16" height="22"/><rect x="540" y="56" width="16" height="24"/>
  </g>
</svg>
<div class="cap">Same total erases, very different lifespans. The even distribution (right) lasts far longer.</div>

<h3>How the FTL levels wear</h3>
<ul>
  <li><b>Dynamic wear leveling</b> — always write new data to the least-worn free blocks.</li>
  <li><b>Static wear leveling</b> — occasionally move <i>cold</i> data off low-wear blocks so they can take a turn being written.</li>
  <li><b>Good data placement</b> — spreading writes across all channels/dies/planes naturally evens things out.</li>
</ul>

{_analogy("Rotate your car tires and they all wear together, lasting the life of the set. Never rotate, and the front tires bald out while the rears look new — you replace the whole set early because of two tires.")}

<p>Measuring how <i>even</i> wear is takes real math — see
<a href="/blog/wear-metrics">Measuring Wear Evenness: CV, Gini, and Fourier</a>.</p>

{_paper("EyanaSSDSim tracks the erase count of every block and reports the distribution. The Live Simulator shows an <b>erase-count distribution</b> chart and a <b>wear-evenness (CV)</b> curve; the paper uses these to compare how different allocation schemes balance wear.")}
""",
"related": ["wear-metrics", "data-placement", "garbage-collection"],
},

# 9 ----------------------------------------------------------------------
{
"slug": "wear-metrics",
"category": "Performance &amp; Endurance",
"title": "Measuring Wear Evenness: CV, Gini, and Fourier",
"subtitle": "Turning a cloud of erase counts into a single, comparable number.",
"html": f"""
<p>"The wear is more even" is a claim you need to <i>measure</i>. Given the erase count of every
block, how do you summarize how balanced (or lopsided) the wear is? EyanaSSDSim uses several
complementary metrics.</p>

<h3>Coefficient of Variation (CV)</h3>
{_key("<div class='formula'>CV = standard deviation of erase counts / mean erase count</div> CV is the spread relative to the average. <b>CV = 0</b> means perfectly even wear (every block erased the same number of times). Higher CV = more lopsided. Because it's normalized by the mean, you can compare CV across drives of different ages.")}

<h3>Gini coefficient</h3>
<p>Borrowed from economics (where it measures income inequality), the <b>Gini coefficient</b> ranges
from 0 (perfect equality — all blocks worn equally) to 1 (total inequality — one block does all the
work). It's robust and intuitive: a Gini of 0.1 is very even; 0.6 is badly skewed.</p>

<svg viewBox="0 0 640 140" width="100%" style="max-width:640px" class="figsvg">
  <text x="10" y="16" font-size="12">Lorenz curve — how the Gini coefficient sees wear</text>
  <line x1="40" y1="120" x2="40" y2="20" stroke="#333"/><line x1="40" y1="120" x2="240" y2="120" stroke="#333"/>
  <line x1="40" y1="120" x2="240" y2="20" stroke="#2ca02c" stroke-dasharray="4"/>
  <path d="M40,120 Q160,110 240,20" fill="none" stroke="#c33" stroke-width="2"/>
  <text x="245" y="24" font-size="10" fill="#2ca02c">perfectly even</text>
  <text x="150" y="105" font-size="10" fill="#c33">actual (skewed)</text>
  <text x="300" y="60" font-size="11" fill="#555">Gini = area between the two curves.</text>
  <text x="300" y="78" font-size="11" fill="#555">Bigger gap → more uneven wear.</text>
</svg>
<div class="cap">The further the red curve bows from the diagonal, the more unevenly the erases are distributed.</div>

<h3>Fourier / spatial spread</h3>
<p>CV and Gini tell you <i>how much</i> wear varies, but not <i>where</i>. Two drives can share a CV
yet wear very differently in space — one with a few scattered hot blocks, another with a whole hot
region. A <b>Fourier</b> analysis of the erase-count map captures this spatial structure: it reveals
periodic or clustered wear patterns that a single spread number would miss.</p>

{_analogy("CV and Gini are like reporting a city's income inequality. Fourier is like the <i>map</i> of where the rich and poor neighborhoods actually are — same inequality number, very different city layouts.")}

{_paper("The paper reports Degree of Erase-Count balance via CV and Gini, plus a Fourier amplitude spread, to argue that a chosen allocation scheme spreads wear both <i>evenly</i> (low CV/Gini) and <i>without spatial hot-spots</i> (low Fourier spread). The Live Simulator shows the CV curve in real time.")}
""",
"related": ["wear-leveling", "data-placement"],
},

# 10 ---------------------------------------------------------------------
{
"slug": "data-placement",
"category": "Advanced",
"title": "Data Placement &amp; Allocation Schemes (S1–S6)",
"subtitle": "Which channel, die, and plane should each write go to? It matters more than you'd think.",
"html": f"""
<p>When the FTL receives a write, it must choose <i>where</i> in the physical hierarchy to put it:
which <b>channel</b>, <b>chip</b>, <b>die</b>, and <b>plane</b>. The rule it uses is the <b>allocation
(data-placement) scheme</b>. A good scheme maximizes parallelism <i>and</i> spreads wear evenly; a bad
one leaves channels idle or hammers a few blocks.</p>

{_key("An allocation scheme decides the <b>order</b> in which the four parallel dimensions (channel, chip, die, plane) are cycled as consecutive logical pages arrive. Different orders = different striping = different parallelism and wear behavior.")}

<svg viewBox="0 0 660 120" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">Consecutive writes striped across 4 channels (good parallelism)</text>
  <g font-size="11">
    <rect x="20" y="30" width="120" height="60" fill="#eef4fb" stroke="#1f77b4"/><text x="55" y="46" fill="#1f77b4">Ch 0</text>
    <rect x="160" y="30" width="120" height="60" fill="#eef4fb" stroke="#1f77b4"/><text x="195" y="46" fill="#1f77b4">Ch 1</text>
    <rect x="300" y="30" width="120" height="60" fill="#eef4fb" stroke="#1f77b4"/><text x="335" y="46" fill="#1f77b4">Ch 2</text>
    <rect x="440" y="30" width="120" height="60" fill="#eef4fb" stroke="#1f77b4"/><text x="475" y="46" fill="#1f77b4">Ch 3</text>
  </g>
  <g fill="#2ca02c" font-size="9">
    <rect x="30" y="60" width="20" height="20"/><text x="33" y="74" fill="#fff">0</text>
    <rect x="170" y="60" width="20" height="20"/><text x="173" y="74" fill="#fff">1</text>
    <rect x="310" y="60" width="20" height="20"/><text x="313" y="74" fill="#fff">2</text>
    <rect x="450" y="60" width="20" height="20"/><text x="453" y="74" fill="#fff">3</text>
    <rect x="55" y="60" width="20" height="20"/><text x="58" y="74" fill="#fff">4</text>
    <rect x="195" y="60" width="20" height="20"/><text x="198" y="74" fill="#fff">5</text>
  </g>
  <text x="20" y="108" font-size="10" fill="#888">Pages 0,1,2,3 hit four different channels → all four work at once.</text>
</svg>
<div class="cap">Striping consecutive pages across channels first keeps every channel busy — maximum throughput.</div>

<h3>The six static schemes</h3>
<p>The paper studies six placement orders, labeled <b>S1–S6</b>. Each is a different priority order of
the four dimensions, e.g.:</p>
<table class="btable">
<tr><th>Scheme</th><th>Priority order (first dimension varies fastest)</th></tr>
<tr><td>S1</td><td>Chip → Die → Plane → Channel</td></tr>
<tr><td>S2</td><td>Channel → Chip → Die → Plane</td></tr>
<tr><td>S3</td><td>Channel → Plane → Chip → Die</td></tr>
<tr><td>S4</td><td>Channel → Die → Chip → Plane</td></tr>
<tr><td>S5</td><td>Channel → Plane → Die → Chip</td></tr>
<tr><td>S6</td><td>Channel → Die → Plane → Chip</td></tr>
</table>

{_key("A subtle but important rule: you need at least <b>2 chips</b> for all six schemes to be genuinely different. With a single chip, some schemes become mathematically identical (S2≡S4, S3≡S5) — an error that can invalidate a comparison.")}

{_analogy("It's like dealing cards to players around a table. Do you give each player one card before looping back (spread the load), or deal one player their whole hand first (pile it up)? Same cards, very different balance.")}

{_paper("This is a core contribution of the paper: comparing S1–S6 on write amplification and wear evenness. That's why the Live Simulator <b>requires Chips ≥ 2</b> — so the scheme comparison stays valid. The nested grid lets you see the striping directly.")}
""",
"related": ["flash-hierarchy", "wear-leveling", "wear-metrics"],
},

# 11 ---------------------------------------------------------------------
{
"slug": "zns",
"category": "Advanced",
"title": "Zoned Namespaces (ZNS): Giving the Host Control",
"subtitle": "A newer kind of SSD that trades convenience for dramatically lower write amplification.",
"html": f"""
<p>A conventional SSD hides all its complexity behind the FTL — the host just writes anywhere and the
drive sorts it out. <b>Zoned Namespace (ZNS)</b> SSDs take a different deal: they expose the flash as
<b>zones</b> that must be written <b>sequentially</b>, and they hand garbage collection responsibility
to the <b>host</b>. In return, write amplification can drop close to the ideal 1.0.</p>

{_key("A <b>zone</b> is a large region of blocks with one rule: you may only append to it in order (a moving <b>write pointer</b>), and to reuse it you must <b>reset the whole zone</b> at once. The device does <b>no</b> garbage collection itself.")}

<svg viewBox="0 0 660 150" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">A zone: append-only, then reset the whole thing</text>
  <rect x="20" y="30" width="500" height="40" fill="#fff" stroke="#333"/>
  <rect x="20" y="30" width="300" height="40" fill="#2ca02c"/>
  <text x="120" y="55" font-size="12" fill="#fff">written (sequential)</text>
  <line x1="320" y1="24" x2="320" y2="76" stroke="#c33" stroke-width="2"/>
  <text x="325" y="22" font-size="10" fill="#c33">write pointer</text>
  <text x="360" y="55" font-size="11" fill="#999">must stay erased →</text>
  <text x="20" y="100" font-size="11" fill="#555">To rewrite: RESET the entire zone (erase all its blocks) and start over at the top.</text>
  <text x="20" y="122" font-size="11" fill="#1f77b4">Because a zone resets as a unit, there's no mixed valid/invalid mess to clean up mid-zone.</text>
</svg>
<div class="cap">No in-place updates, no random writes — just append and whole-zone reset. Simpler flash, smarter host.</div>

<h3>Why ZNS lowers write amplification</h3>
<p>On a conventional SSD, hot and cold data get mixed inside the same blocks, so garbage collection
constantly copies cold data just to reclaim space near hot data. ZNS lets the host place data
deliberately — and the biggest win is <b>hot/cold separation</b>:</p>
<ul>
  <li>Put frequently-updated (<b>hot</b>) data in its own zones. They fill entirely with soon-to-be-dead data, so when reset, almost nothing needs saving.</li>
  <li>Put write-once (<b>cold</b>) data in separate zones. They stay valid and are rarely reset.</li>
</ul>

{_key("With hot and cold data physically separated, a hot zone becomes nearly all-invalid before reset → almost zero pages to migrate → write amplification approaches <b>1.0</b>. A conventional device can't do this without host hints.")}

{_analogy("Conventional GC is a recycling bin where paper, glass, and food scraps are mixed — every time you empty it you must sort out the still-good items. ZNS gives you separate bins up front, so emptying the 'trash' bin means just tipping it out — nothing to rescue.")}

<h3>The trade-off</h3>
<p>ZNS isn't free lunch. The host (or file system / database) must be <b>zone-aware</b>: it has to
write sequentially, track zones, and run its own garbage collection. That's more software complexity
in exchange for lower amplification, more predictable latency, and longer flash life.</p>

{_paper("The Live Simulator has a full <b>ZNS mode</b>. Pick it, choose Blocks/zone, and toggle <b>hot/cold separation</b>. On a real trace, conventional WAF ≈ 2.4 while ZNS hot/cold drops to ≈ 1.1 — you can watch individual zones fill, get chosen for reset, and clear. This is the follow-up direction the paper discusses.")}
""",
"related": ["write-amplification", "garbage-collection", "fdp"],
},

# 12 ----------------------------------------------------------------------
{
"slug": "fdp",
"category": "Advanced",
"title": "Flexible Data Placement (FDP): Hints Instead of Rules",
"subtitle": "A gentle way to cut write amplification — the host gives the SSD little hints, and the SSD still does the cleanup.",
"html": f"""
<p>By now you know the villain of SSD performance:
<a href="/blog/write-amplification">write amplification</a>. A normal SSD runs its own
<a href="/blog/garbage-collection">garbage collection</a>, but it has no idea which of your data
changes often (<b>hot</b>) and which almost never changes (<b>cold</b>). So it mixes them in the same
blocks. When it cleans a block, it must copy out the cold data that happened to sit next to the hot
data &mdash; extra writes you never asked for.</p>

<p><b>Flexible Data Placement (FDP)</b> fixes this with the lightest possible touch: the host adds a
tiny <b>hint</b> to each write saying roughly &ldquo;this belongs with that.&rdquo; The SSD uses the
hint to keep similar data together &mdash; and still does its own cleanup.</p>

{_key("The host tags each write with a <b>placement handle</b> (officially a <i>Reclaim Unit Handle</i>, RUH) &mdash; think of it as a label like &ldquo;hot&rdquo; or &ldquo;cold.&rdquo; The SSD groups all writes with the same label into the same <b>Reclaim Unit (RU)</b>, a dedicated region of flash.")}

<svg viewBox="0 0 660 180" width="100%" style="max-width:660px" class="figsvg">
  <text x="10" y="16" font-size="12">Host tags each write; the device groups same-tagged data into one Reclaim Unit</text>
  <g font-size="11">
    <rect x="20" y="34" width="120" height="24" fill="#fdecec" stroke="#d62728"/><text x="30" y="50" fill="#d62728">write (hot)</text>
    <rect x="20" y="66" width="120" height="24" fill="#eaf1fb" stroke="#1f77b4"/><text x="30" y="82" fill="#1f77b4">write (cold)</text>
    <rect x="20" y="98" width="120" height="24" fill="#fdecec" stroke="#d62728"/><text x="30" y="114" fill="#d62728">write (hot)</text>
  </g>
  <text x="150" y="80" font-size="20" fill="#888">&#8594;</text>
  <rect x="190" y="30" width="200" height="46" fill="#fff" stroke="#d62728"/>
  <text x="196" y="26" font-size="10" fill="#d62728">Hot RU (fills with soon-dead data)</text>
  <g fill="#d62728"><rect x="196" y="40" width="24" height="26"/><rect x="224" y="40" width="24" height="26"/><rect x="252" y="40" width="24" height="26"/></g>
  <rect x="190" y="96" width="200" height="46" fill="#fff" stroke="#1f77b4"/>
  <text x="196" y="92" font-size="10" fill="#1f77b4">Cold RU (write-once, stays valid)</text>
  <g fill="#2ca02c"><rect x="196" y="106" width="24" height="26"/><rect x="224" y="106" width="24" height="26"/></g>
  <text x="410" y="56" font-size="11" fill="#555">Cleaning the hot RU copies</text>
  <text x="410" y="72" font-size="11" fill="#555">almost nothing &rarr; WAF &rarr; 1.0.</text>
  <text x="410" y="118" font-size="11" fill="#555">Cold RU is never cleaned.</text>
</svg>
<div class="cap">Same-labelled data lands together, so a hot RU fills with soon-dead data and is reclaimed with almost no copying.</div>

<h3>Why grouping cuts write amplification</h3>
<p>Because all the hot data sits in <b>hot RUs</b>, those units fill with data that is about to be
overwritten. By the time the SSD cleans a hot RU, nearly every page is already invalid &rarr; it
copies almost nothing &rarr; write amplification drops toward the ideal <b>1.0</b>. Meanwhile the
<b>cold RUs</b> hold write-once data that just sits there and never needs cleaning.</p>

{_analogy("FDP is <b>labelled recycling bins</b>. A conventional SSD is one bin for everything &mdash; the facility must hand-sort it. FDP gives you paper / glass / trash bins up front: the facility still runs the machines, but each bin empties cleanly. (<a href='/blog/zns'>ZNS</a>, by contrast, is running the whole recycling plant yourself.)")}

<h3>The big difference from ZNS</h3>
<p>This is the key beginner point: <b>with FDP the device still does the garbage collection.</b> The
host only gives <i>hints</i>, and it can still write anywhere in any order. So FDP keeps the ordinary
SSD interface &mdash; your software barely changes. <a href="/blog/zns">ZNS</a> is stricter and more
powerful (host-managed, strictly sequential zones) but demands far more of the software.</p>

<h3>One extra knob: II vs PI</h3>
<p>When the SSD cleans a reclaim unit and finds a few pages still alive, where do those survivors go?</p>
<ul>
  <li><b>Initially Isolated (II)</b> &mdash; all survivors are swept into one shared cleanup area. Simple, and <b>robust when spare space is tight</b>.</li>
  <li><b>Persistently Isolated (PI)</b> &mdash; each label's survivors stay with their own label, keeping the separation perfectly pure. <b>Best when there is plenty of spare space</b>, but it can backfire when space is scarce.</li>
</ul>
<p>It's a real trade-off with no universal winner &mdash; exactly the kind of thing the simulator lets you explore.</p>

{_paper("The <a href='/stream'>Live Simulator</a> has an <b>FDP mode</b> (Conventional / FDP / ZNS). Toggle the hot/cold hint and watch reclaim units fill and clear. The academic reference for FDP is the <b>WARP</b> study (USENIX FAST 2026), the first open emulator and characterisation of real FDP SSDs.")}

<p>Next, see all three side by side:
<a href="/blog/conventional-zns-fdp">Conventional vs ZNS vs FDP &mdash; Who Cleans Up?</a></p>
""",
"related": ["zns", "conventional-zns-fdp", "write-amplification"],
},

# 13 ----------------------------------------------------------------------
{
"slug": "conventional-zns-fdp",
"category": "Advanced",
"title": "Conventional vs ZNS vs FDP: Who Cleans Up?",
"subtitle": "The one picture that makes all three click — a spectrum from &lsquo;the device does everything&rsquo; to &lsquo;the host does everything&rsquo;.",
"html": f"""
<p>Three ways to run a flash SSD sound complicated, but one question separates them:
<b>who is responsible for garbage collection, and how much does the software have to help?</b>
Line them up on that single axis and it all clicks.</p>

<svg viewBox="0 0 680 120" width="100%" style="max-width:680px" class="figsvg">
  <line x1="40" y1="60" x2="640" y2="60" stroke="#bbb" stroke-width="2"/>
  <text x="40" y="95" font-size="11" fill="#888">device does the work</text>
  <text x="540" y="95" font-size="11" fill="#888">host does the work</text>
  <g text-anchor="middle" font-size="12">
    <circle cx="90" cy="60" r="8" fill="#2ca02c"/><text x="90" y="40" fill="#2ca02c">Conventional</text><text x="90" y="80" font-size="10" fill="#666">device GC</text>
    <circle cx="340" cy="60" r="8" fill="#ff7f0e"/><text x="340" y="40" fill="#ff7f0e">FDP</text><text x="340" y="80" font-size="10" fill="#666">device GC + host hints</text>
    <circle cx="590" cy="60" r="8" fill="#1f77b4"/><text x="590" y="40" fill="#1f77b4">ZNS</text><text x="590" y="80" font-size="10" fill="#666">host GC, zones</text>
  </g>
</svg>
<div class="cap">The device does everything on the left; the host takes over on the right. FDP sits in the middle.</div>

<table class="btable">
<tr><th></th><th>Conventional</th><th>FDP</th><th>ZNS</th></tr>
<tr><td><b>Who does garbage collection?</b></td><td>the device</td><td><b>the device</b></td><td>the host</td></tr>
<tr><td><b>What the host must do</b></td><td>nothing</td><td>add a hint per write</td><td>manage zones &amp; run GC</td></tr>
<tr><td><b>Write rule</b></td><td>write anywhere</td><td>write anywhere (+ hint)</td><td>strictly sequential</td></tr>
<tr><td><b>Software change</b></td><td>none</td><td>small</td><td>large</td></tr>
<tr><td><b>Typical write amplification</b></td><td>highest</td><td>low</td><td>lowest</td></tr>
</table>

<h3>One line each</h3>
<ul>
  <li><b>Conventional</b> &mdash; full service: you write wherever you like and the drive figures out cleanup by itself. Easiest, but it mixes hot and cold data, so it wastes the most writes.</li>
  <li><b>FDP</b> &mdash; you add a small label to each write; the drive still cleans up, but now keeps similar data together, so it wastes far less. Your software barely changes.</li>
  <li><b>ZNS</b> &mdash; you write in strict order into zones and do the cleanup yourself. Most efficient of all, but your software has to be zone-aware.</li>
</ul>

{_analogy("Hotel housekeeping. <b>Conventional</b> = full service: you leave and they clean however they like. <b>FDP</b> = you leave your recycling pre-sorted so cleaning is faster. <b>ZNS</b> = you clean your own room and just hand back the key.")}

<h3>When would you pick each?</h3>
<ul>
  <li><b>Conventional</b>: everyday drives, where simplicity matters more than squeezing out every last write.</li>
  <li><b>FDP</b>: data centres that want lower write amplification and longer flash life <i>without</i> rewriting their software &mdash; today's industry sweet spot.</li>
  <li><b>ZNS</b>: systems already built around logs and zones (databases, log-structured file systems) that can invest in host-managed placement for the best possible efficiency.</li>
</ul>

{_paper("Run all three in the <a href='/stream'>Live Simulator</a> on the same trace and compare WAF directly. EyanaSSDSim implements a conventional FTL, a host-managed ZNS engine, and an FDP engine aligned to the FEMU/WARP model.")}

<p>Deep dives: <a href="/blog/fdp">FDP</a> &middot; <a href="/blog/zns">ZNS</a> &middot;
<a href="/blog/garbage-collection">Garbage Collection</a> &middot;
<a href="/blog/write-amplification">Write Amplification</a>.</p>
""",
"related": ["fdp", "zns", "garbage-collection"],
},

# 14 ---------------------------------------------------------------------
{
"slug": "eyanassdsim",
"category": "The Paper",
"title": "How EyanaSSDSim Models All of This",
"subtitle": "Tying every concept together — and how to read the paper and use the simulator.",
"html": f"""
<p>Now that you understand the pieces, here's how they assemble into EyanaSSDSim — the simulator and
the paper — and how to explore them yourself.</p>

<h3>What the simulator actually does</h3>
<p>EyanaSSDSim replays a <b>workload</b> (a synthetic pattern, or a real disk <b>trace</b>) through a
faithful model of an SSD: a configurable flash <a href="/blog/flash-hierarchy">hierarchy</a>, an
<a href="/blog/ftl">FTL</a> with log-structured mapping, a chosen
<a href="/blog/data-placement">allocation scheme</a>, and a
<a href="/blog/garbage-collection">garbage collector</a>. It then measures the outcomes you now know
matter:</p>
<ul>
  <li><a href="/blog/write-amplification">Write amplification</a> — the headline efficiency number.</li>
  <li><a href="/blog/wear-metrics">Wear evenness</a> — CV, Gini, and Fourier spread of erase counts.</li>
  <li>Behavior under different <a href="/blog/over-provisioning">over-provisioning</a> levels, GC policies, and workloads.</li>
  <li>A conventional SSD vs. a <a href="/blog/zns">ZNS</a> device with host-managed GC.</li>
</ul>

{_key("The point of the tool is to make invisible internal mechanics <b>visible and measurable</b>, so design choices (placement, OP, GC policy, ZNS) can be compared on equal footing.")}

<h3>Reading the paper with this background</h3>
<table class="btable">
<tr><th>When the paper mentions…</th><th>Recall the post…</th></tr>
<tr><td>WAF, write amplification</td><td><a href="/blog/write-amplification">The Hidden Write Tax</a></td></tr>
<tr><td>Over-provisioning / OP ratio</td><td><a href="/blog/over-provisioning">Spare Space</a></td></tr>
<tr><td>Greedy / cost–benefit GC</td><td><a href="/blog/garbage-collection">Garbage Collection</a></td></tr>
<tr><td>Allocation schemes S1–S6</td><td><a href="/blog/data-placement">Data Placement</a></td></tr>
<tr><td>CV, Gini, Fourier / DoEC</td><td><a href="/blog/wear-metrics">Measuring Wear Evenness</a></td></tr>
<tr><td>Zones, host GC, hot/cold</td><td><a href="/blog/zns">Zoned Namespaces</a></td></tr>
</table>

<h3>Try it yourself</h3>
<p>Open the <a href="/stream"><b>Live Simulator</b></a>:</p>
<ol>
  <li>Pick a trace (start with the built-in <code>zns_hotcold_demo.csv</code>).</li>
  <li>Set the <a href="/blog/flash-hierarchy">geometry</a> (Channels, Chips≥2, Dies, Planes, Blocks/plane, Pages/block).</li>
  <li>Watch blocks accumulate invalid pages, then get erased by GC; watch the WAF and wear curves live.</li>
  <li>Switch to <b>ZNS mode</b>, toggle hot/cold separation, and compare the write amplification.</li>
</ol>

{_analogy("You've read the flight manual; now take the controls. The simulator is the flight simulator — safe to experiment, and every dial you turn maps to a concept you just learned.")}

{_paper("This blog exists because the paper's own reviewers valued clarity for newcomers. If anything here helped a concept click, that's the goal — understanding first, numbers second.")}

<p>Start from the top: <a href="/blog/ssd-basics">What Is an SSD?</a> — or jump to any topic from the
list on the left.</p>
""",
"related": ["ssd-basics", "zns", "write-amplification"],
},

]

# --- derived lookups --------------------------------------------------------
POSTS_BY_SLUG = {p["slug"]: p for p in POSTS}

# category → posts, preserving first-seen order
CATEGORIES = []
for _p in POSTS:
    if _p["category"] not in CATEGORIES:
        CATEGORIES.append(_p["category"])
