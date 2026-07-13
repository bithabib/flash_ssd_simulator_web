"""Server-side trace simulation with streamed grid snapshots.

Endpoints:
  POST /api/upload_trace      -> save an uploaded trace file on the server
  GET  /api/traces            -> list saved trace files
  GET  /api/simulate          -> Server-Sent Events stream of grid snapshots
"""
import json
import os

from flask import (request, jsonify, Response, stream_with_context,
                   render_template)
from werkzeug.utils import secure_filename

from app import app
from eyana_engine.stream_sim import simulate_stream
from eyana_engine.zns_stream import simulate_zns_stream
from eyana_engine.fdp_stream import simulate_fdp_stream


@app.route("/stream")
def stream_page():
    """The server-side simulation + live grid visualization page."""
    return render_template("stream_simulator.html")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "real_data",
                          "uploaded_traces")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED = {".csv", ".txt", ".trace", ".tar", ".bz2"}


def _guess_kind(filename):
    """Pick a parser: ETW DiskIO trace vs MSR Cambridge CSV."""
    name = filename.lower()
    if "tpcc" in name or "w2k8" in name or name.endswith(".etw"):
        return "etw"
    return "msr"


@app.route("/api/upload_trace", methods=["POST"])
def api_upload_trace():
    if "trace" not in request.files:
        return jsonify({"error": "no file part 'trace'"}), 400
    f = request.files["trace"]
    if not f.filename:
        return jsonify({"error": "empty filename"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext and ext not in ALLOWED:
        return jsonify({"error": f"unsupported extension {ext}"}), 400
    safe = secure_filename(f.filename)
    path = os.path.join(UPLOAD_DIR, safe)
    f.save(path)
    return jsonify({"ok": True, "name": safe,
                    "size": os.path.getsize(path),
                    "kind": _guess_kind(safe)})


@app.route("/api/traces", methods=["GET"])
def api_list_traces():
    out = []
    for name in sorted(os.listdir(UPLOAD_DIR)):
        p = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(p):
            out.append({"name": name, "size": os.path.getsize(p),
                        "kind": _guess_kind(name)})
    return jsonify(out)


@app.route("/api/simulate", methods=["GET"])
def api_simulate():
    name = request.args.get("trace", "")
    safe = secure_filename(name)
    path = os.path.join(UPLOAD_DIR, safe)
    if not safe or not os.path.isfile(path):
        return jsonify({"error": f"trace not found: {name}"}), 404

    kind = request.args.get("kind") or _guess_kind(safe)
    op = float(request.args.get("op", 0.10))
    # 'interval' from the UI slider -> seconds of wall-clock between snapshots
    interval_sec = max(0.1, float(request.args.get("interval", 1.0)))
    limit = int(request.args.get("limit", 2_000_000))
    # user-selectable parallel geometry (mirrors the advance simulator)
    channel = int(request.args.get("channel", 2))
    chip = int(request.args.get("chip", 2))
    die = int(request.args.get("die", 2))
    plane = int(request.args.get("plane", 4))
    bpp = int(request.args.get("blocks_per_plane", 38))
    ppb = int(request.args.get("pages_per_block", 256))
    # engine: "conventional" (block-managed FTL) or "zns" (host-managed zones)
    engine = request.args.get("engine", "conventional").lower()
    hot_cold = request.args.get("hot_cold", "1") in ("1", "true", "True")
    bpz = request.args.get("blocks_per_zone")
    bpz = int(bpz) if bpz else None

    def _iter():
        if engine == "zns":
            return simulate_zns_stream(
                path, kind=kind, op=op, interval_sec=interval_sec, limit=limit,
                channel=channel, chip=chip, die=die, plane=plane,
                blocks_per_plane=bpp, pages_per_block=ppb,
                blocks_per_zone=bpz, hot_cold=hot_cold)
        if engine == "fdp":
            return simulate_fdp_stream(
                path, kind=kind, op=op, interval_sec=interval_sec, limit=limit,
                channel=channel, chip=chip, die=die, plane=plane,
                blocks_per_plane=bpp, pages_per_block=ppb, hot_cold=hot_cold)
        return simulate_stream(
            path, kind=kind, op=op, interval_sec=interval_sec, limit=limit,
            channel=channel, chip=chip, die=die, plane=plane,
            blocks_per_plane=bpp, pages_per_block=ppb)

    @stream_with_context
    def gen():
        try:
            for snap in _iter():
                yield "data: " + json.dumps(snap) + "\n\n"
            yield "event: done\ndata: {}\n\n"
        except Exception as e:  # surface engine errors to the client
            yield "event: error\ndata: " + json.dumps({"error": str(e)}) + "\n\n"

    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})
