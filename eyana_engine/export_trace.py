"""Export a dense-remapped trace to a binary uint32 file so the FEMU replayer and
the simulator drive the IDENTICAL LBA sequence.  Also prints the matching device
geometry (so FEMU bbssd == sim device).

Usage: python -m eyana_engine.export_trace <trace> <msr|etw> <cap> <out.bin>
"""
import sys, numpy as np
from . import workloads

OP, PPB, PLANES = 0.25, 64, 16

def main():
    path, kind, cap, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    gen = workloads.etw_trace_writes(path) if kind == "etw" else workloads.msr_trace_writes(path)
    remap, seq = {}, []
    for lpn in gen:
        d = remap.get(lpn)
        if d is None:
            d = len(remap); remap[lpn] = d
        seq.append(d)
        if len(seq) >= cap:
            break
    seq = np.array(seq, dtype=np.uint32)
    nuniq = len(remap)
    # device geometry matching real_eval.make_cfg
    total_pages = int(round(nuniq / (1 - OP) / PPB)) * PPB
    total_blocks = total_pages // PPB
    bpp = max(8, int(round(total_blocks / PLANES)))
    total_blocks = PLANES * bpp
    total_pages = total_blocks * PPB
    logical = int(total_pages * (1 - OP))
    seq.tofile(out)
    print(f"wrote {out}: {len(seq):,} writes, {nuniq:,} unique pages")
    print(f"GEOMETRY  planes={PLANES} blocks_per_plane={bpp} pages_per_block={PPB} "
          f"total_blocks={total_blocks} total_pages={total_pages} logical={logical} OP={OP}")
    # FEMU bbssd mapping: nchs*luns_per_ch*pls_per_lun = planes
    print(f"FEMU  nchs=4 luns_per_ch=4 pls_per_lun=1 (=16 planes)  blks_per_pl={bpp} "
          f"pgs_per_blk={PPB}  devsz_mb={total_pages*4096//1024//1024}  "
          f"fold_logical={logical}")

if __name__ == "__main__":
    main()
