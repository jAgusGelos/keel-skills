#!/usr/bin/env python3
"""progress.py <plan.md> <status.json> <out.html>: render the pass progress page from the plan rows.

<status.json> maps a case id to [status, note] for cases the plan does not yet close ("partial", "pending").
"""
from pathlib import Path
import html, json, re, sys
from datetime import datetime

plan, status_file, out = sys.argv[1:4]
extra = json.loads(Path(status_file).read_text())
rows = []
for line in Path(plan).read_text().splitlines(keepends=True):
    m = re.match(r"\| (QA-\d+) \| (.*?) \| ", line)
    if not m:
        continue
    qa, title = m.group(1), m.group(2)
    cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
    actual, bug = cells[-2].strip(), cells[-1].strip()
    pre = cells[4] if len(cells) > 4 else ""
    # The roles are the backticked names in the Preconditions cell's leading "Role:" sentence.
    role_clause = re.search(r"Roles?:(.*?)(?:\.\s|\.$|<br>|$)", pre)
    roles = ", ".join(dict.fromkeys(re.findall(r"`([^`]+)`", role_clause.group(1)))) if role_clause else ""
    roles = roles or "-"
    if actual.startswith("pass"):
        st, note = "pass", actual[len("pass"):].lstrip(" :-")
    elif actual.startswith("bug"):
        st, note = "bug", actual[len("bug"):].lstrip(" :-")
    elif qa in extra:
        st, note = extra[qa]
    else:
        st, note = "pending", ""
    rows.append((qa, re.sub(r"`", "", title), roles, st, note.replace("<br>", " "), bug))

labels = {"pass": "Pass", "bug": "Bug", "partial": "Partly run", "pending": "Not run"}
count = {k: sum(1 for r in rows if r[3] == k) for k in labels}
total = len(rows)
done = count["pass"] + count["bug"]
bar = "".join(f'<span class="seg {k}" style="flex:{count[k]}" title="{labels[k]}: {count[k]}"></span>' for k in labels if count[k])
tiles = "".join(f'<div class="tile"><span class="dot {k}"></span><b>{count[k]}</b><span>{labels[k]}</span></div>' for k in labels)
body = "".join(
    f'<tr class="{st}"><td class="id">{qa}</td><td><div class="t">{html.escape(t)}</div>'
    + (f'<div class="n">{html.escape(n)}</div>' if n else "")
    + (f'<div class="b">{html.escape(b)}</div>' if b else "")
    + f'</td><td class="r">{html.escape(r)}</td><td><span class="pill {st}">{labels[st]}</span></td></tr>'
    for qa, t, r, st, n, b in rows
)
stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
page = f"""<title>QA Pass Progress</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root {{ --ground:#f4f6f5; --panel:#ffffff; --ink:#18201d; --muted:#5d6b66; --line:#dde3e0;
  --pass:#1f8a5b; --pass-bg:#e2f3ea; --bug:#c2412d; --bug-bg:#fbe6e1; --partial:#a86b0c; --partial-bg:#fbefd7; --pending:#6b7b86; --pending-bg:#e8edf0; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ color-scheme:dark; --ground:#111614; --panel:#18201d; --ink:#e6ece9; --muted:#9aa8a2; --line:#2a3531;
  --pass:#4cc28a; --pass-bg:#16362a; --bug:#f07a64; --bug-bg:#3c1d17; --partial:#e5a93f; --partial-bg:#3a2c12; --pending:#9aabb6; --pending-bg:#232d33; }} }}
:root[data-theme="dark"] {{ color-scheme:dark; --ground:#111614; --panel:#18201d; --ink:#e6ece9; --muted:#9aa8a2; --line:#2a3531;
  --pass:#4cc28a; --pass-bg:#16362a; --bug:#f07a64; --bug-bg:#3c1d17; --partial:#e5a93f; --partial-bg:#3a2c12; --pending:#9aabb6; --pending-bg:#232d33; }}
body {{ background:var(--ground); color:var(--ink); font:15px/1.5 "IBM Plex Sans", system-ui, sans-serif; }}
.wrap {{ max-width:1100px; margin:0 auto; padding:32px 16px 48px; display:grid; gap:24px; }}
h1 {{ font-size:26px; font-weight:600; margin:0; text-wrap:balance; }}
.sub {{ color:var(--muted); margin:4px 0 0; }}
.mono {{ font-family:"IBM Plex Mono", ui-monospace, monospace; }}
.head {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:end; gap:12px; }}
.big {{ font-size:40px; font-weight:600; font-variant-numeric:tabular-nums; line-height:1; }}
.big small {{ font-size:16px; color:var(--muted); font-weight:500; }}
.bar {{ display:flex; height:12px; border-radius:6px; overflow:hidden; background:var(--line); gap:2px; }}
.seg.pass {{ background:var(--pass); }} .seg.bug {{ background:var(--bug); }} .seg.partial {{ background:var(--partial); }} .seg.pending {{ background:var(--pending); opacity:.45; }}
.tiles {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px 14px; display:flex; align-items:center; gap:8px; }}
.tile b {{ font-size:20px; font-variant-numeric:tabular-nums; }} .tile span:last-child {{ color:var(--muted); }}
.dot {{ width:10px; height:10px; border-radius:50%; }} .dot.pass {{ background:var(--pass); }} .dot.bug {{ background:var(--bug); }} .dot.partial {{ background:var(--partial); }} .dot.pending {{ background:var(--pending); }}
.scroll {{ overflow-x:auto; background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
table {{ width:100%; border-collapse:collapse; min-width:640px; }}
th {{ text-align:left; font-size:12px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); font-weight:500; padding:10px 14px; border-bottom:1px solid var(--line); }}
td {{ padding:10px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
td.id {{ font-family:"IBM Plex Mono", ui-monospace, monospace; white-space:nowrap; font-size:13px; padding-top:12px; }}
td.r {{ color:var(--muted); font-size:13px; }}
.t {{ font-weight:500; }} .n {{ color:var(--muted); font-size:13px; margin-top:2px; }} .b {{ font-size:13px; margin-top:2px; color:var(--bug); }}
.pill {{ display:inline-block; white-space:nowrap; font-size:12px; font-weight:600; padding:2px 10px; border-radius:999px; }}
.pill.pass {{ color:var(--pass); background:var(--pass-bg); }} .pill.bug {{ color:var(--bug); background:var(--bug-bg); }}
.pill.partial {{ color:var(--partial); background:var(--partial-bg); }} .pill.pending {{ color:var(--pending); background:var(--pending-bg); }}
tr.pending .t {{ color:var(--muted); font-weight:400; }}
@media (max-width:640px) {{ .tiles {{ grid-template-columns:repeat(2, 1fr); }} }}
</style>
<div class="wrap">
  <div class="head">
    <div><h1>QA pass {html.escape(plan.rsplit("/", 1)[-1].removesuffix(".md"))}</h1>
    <p class="sub">Plan <span class="mono">{html.escape(plan.rsplit("/", 1)[-1])}</span> · local app · updated {stamp}</p></div>
    <div class="big">{done}<small> / {total} run</small></div>
  </div>
  <div class="bar" role="img" aria-label="{done} of {total} cases run">{bar}</div>
  <div class="tiles">{tiles}</div>
  <div class="scroll"><table>
    <thead><tr><th>Case</th><th>Test</th><th>Roles</th><th>Status</th></tr></thead>
    <tbody>{body}</tbody>
  </table></div>
</div>
"""
Path(out).write_text(page)
print(f"{done}/{total} run", count)
