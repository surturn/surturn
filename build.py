"""Builds every SVG asset for the surturn profile README, in dark and light themes.

Fonts are subset per file to only the glyphs that file uses and embedded as
base64 WOFF2, so the SVGs render identically everywhere with zero network calls.
"""
import base64, io, os, textwrap
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
OUT = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(f"{OUT}/cards", exist_ok=True)

FONTS = {
    ("Overpass", 400): "overpass-400.ttf",
    ("Overpass", 600): "overpass-600.ttf",
    ("Overpass", 800): "overpass-800.ttf",
    ("Overpass Mono", 500): "overpassmono-500.ttf",
}
_loaded = {k: TTFont(f"{FONT_DIR}/{v}") for k, v in FONTS.items()}

def text_width(s, size, family="Overpass", weight=600):
    f = _loaded[(family, weight)]
    cmap, hmtx, upem = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in s) * size / upem

def wrap(s, size, max_w, weight=400):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, size, weight=weight) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def font_css(used):
    """used: dict[(family, weight)] -> set of chars"""
    css = []
    for (fam, wt), chars in used.items():
        if not chars:
            continue
        opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga"]
        sub = subset.Subsetter(opts)
        font = TTFont(f"{FONT_DIR}/{FONTS[(fam, wt)]}")
        sub.populate(text="".join(sorted(chars | {" "})))
        sub.subset(font)
        buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(css)

class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.body, self.css, self.used = [], [], {k: set() for k in FONTS}
    def add(self, s): self.body.append(s)
    def text(self, x, y, s, size, fill, weight=600, family="Overpass", anchor="start", extra="", spacing=0):
        """Draws text as outlined glyph paths. GitHub serves SVGs with a CSP that blocks
        embedded fonts, so real outlines are the only way the typeface survives."""
        if "letter-spacing" in extra:
            spacing = float(extra.split('"')[1]); extra = ""
        f = _loaded[(family, weight)]
        cmap, hmtx, gs, upem = f.getBestCmap(), f["hmtx"], f.getGlyphSet(), f["head"].unitsPerEm
        k = size / upem
        w = text_width(s, size, family, weight) + spacing * (len(s) - 1)
        cx = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        for ch in s:
            g = cmap.get(ord(ch), cmap[ord("?")])
            gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
            cx += hmtx[g][0] * k + spacing
        self.add(f'<path d="{pen.getCommands()}" fill="{fill}"/>')
    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-label="{escape(self.title)}">\n'
                f'<title>{escape(self.title)}</title>\n<style>\n'
                + "\n".join(self.css) +
                "\n@media (prefers-reduced-motion: reduce){*{animation:none!important}}\n</style>\n"
                + "\n".join(self.body) + "\n</svg>\n")

# ------------------------------------------------------------------ palette
THEMES = {
    "dark": dict(bg="#0F1A2A", surface="#15233A", edge="#23354F", text="#E8EEF5",
                 muted="#8FA3BA", faint="#1B2B44",
                 amber="#F2A93B", teal="#3FB6A8", green="#86C25F", coral="#E86A5C", slate="#7D8FA6"),
    "light": dict(bg="#EEF2F6", surface="#FFFFFF", edge="#D3DCE6", text="#13223A",
                  muted="#56677D", faint="#E2E8EF",
                  amber="#D08912", teal="#1C8F82", green="#4C9530", coral="#CC4636", slate="#7A8BA0"),
}
LINES = [("amber", "Edtech"), ("teal", "Fintech"), ("green", "Agritech"), ("coral", "Events and retail")]

# ------------------------------------------------------------------ header
def header(t):
    P = THEMES[t]
    s = SVG(1280, 440, "Sydney Kamau. Systems engineer and founder of Invonics Technologies, Nairobi. "
                       "A transit map connects his products through Invonics.")
    s.add(f'<rect width="1280" height="440" rx="20" fill="{P["bg"]}"/>')
    # faint survey grid behind the map
    s.add(f'<g stroke="{P["faint"]}" stroke-width="1">' +
          "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="440"/>' for x in range(660, 1280, 40)) +
          "".join(f'<line x1="640" y1="{y}" x2="1280" y2="{y}"/>' for y in range(20, 440, 40)) + "</g>")

    # left column
    s.text(64, 168, "Sydney Kamau", 68, P["text"], 800, extra='letter-spacing="-1.5"')
    s.text(66, 212, "Systems engineer and founder", 26, P["muted"], 600)
    s.text(66, 268, "Building software for the network", 22, P["text"], 400)
    s.text(66, 298, "Africa actually has.", 22, P["text"], 400)
    s.text(66, 342, "Nairobi, Kenya", 17, P["muted"], 600)
    # legend
    x = 66
    for key, name in LINES:
        s.add(f'<rect x="{x}" y="381" width="26" height="6" rx="3" fill="{P[key]}"/>')
        s.text(x + 34, 390, name, 16, P["muted"], 600)
        x += 34 + text_width(name, 16) + 22

    # transit map (translated right)
    paths = {
        "amber": "M 600 70 H 690 L 800 180 H 920 L 1030 70 H 1230",
        "teal":  "M 560 205 H 1230",
        "green": "M 600 340 H 690 L 800 230 H 920 L 1030 340 H 1230",
        "coral": "M 560 390 H 675 L 810 255 H 910 L 1045 390 H 1230",
    }
    stations = [  # (line, x, y, label, label_dx, label_dy, anchor)
        ("amber", 1110, 70, "AssetFlow Schools", 0, -20, "middle"),
        ("teal", 630, 205, "Risiti", 0, -18, "middle"),
        ("teal", 1110, 205, "LuckLotter", 0, -18, "middle"),
        ("green", 1110, 340, "FarmAssist", 0, -18, "middle"),
        ("coral", 625, 390, "Eventify", 0, -18, "middle"),
        ("coral", 1110, 390, "Retail analytics", 0, 30, "middle"),
        ("amber", 640, 70, "CampusMarket", 0, -20, "middle"),
    ]
    s.add('<clipPath id="frame"><rect width="1280" height="440" rx="20"/></clipPath>')
    g = ['<g clip-path="url(#frame)"><g transform="translate(80,0)">']
    for key, d in paths.items():
        g.append(f'<path id="line-{key}" d="{d}" fill="none" stroke="{P[key]}" stroke-width="9" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
    s.add("\n".join(g))
    for key, x, y, label, dx, dy, anc in stations:
        s.add(f'<circle cx="{x}" cy="{y}" r="8" fill="{P["bg"]}" stroke="{P[key]}" stroke-width="4"/>')
        s.text(x + dx, y + dy, label, 17, P["text"], 600, anchor=anc)
    # trains: one per line, staggered, the single moving element in the header
    durs = {"amber": 9, "teal": 7, "green": 10, "coral": 8.5}
    for i, key in enumerate(["amber", "teal", "green", "coral"]):
        for k in range(2):
            begin = -(i * 1.7 + k * durs[key] / 2)
            s.add(f'<rect x="-9" y="-4" width="18" height="8" rx="4" fill="{P["text"]}">'
                  f'<animateMotion dur="{durs[key]}s" begin="{begin:.2f}s" repeatCount="indefinite" rotate="auto">'
                  f'<mpath href="#line-{key}"/></animateMotion></rect>')
    s.add(f'<rect x="843" y="164" width="34" height="108" rx="17" fill="{P["bg"]}" stroke="{P["text"]}" stroke-width="4"/>')
    s.text(860, 144, "Invonics", 19, P["text"], 800, anchor="middle")
    s.add("</g></g>")
    return s.render()

# ------------------------------------------------------------------ now running board
NOW = [
    ("amber", "AssetFlow Schools", "In beta across several schools", "live"),
    ("green", "FarmAssist", "Building the WhatsApp diagnosis channel", "building"),
    ("slate", "Digital twin", "RAG pipeline in progress", "building"),
    ("slate", "Re-engagement engine", "n8n and AI prototype for a streaming client", "building"),
    ("teal", "Next stop", "Backend engineering internships", "open"),
]
STATUS = {"live": ("Live", "green"), "building": ("Building", "amber"), "open": ("Open", "teal"),
          "planned": ("Planned", "slate"), "handed": ("In production", "green"), "beta": ("In beta", "green"), "testing": ("In testing", "teal")}

def board(t):
    P = THEMES[t]
    row_h, top = 66, 100
    h = top + row_h * len(NOW) + 28
    s = SVG(1280, h, "Now running: " + "; ".join(f"{n}, {d}" for _, n, d, _ in NOW))
    s.css.append(".row{opacity:0;transform-box:fill-box;transform-origin:center;"
                 "animation:flap .55s cubic-bezier(.2,.8,.2,1) forwards}"
                 "@keyframes flap{0%{opacity:0;transform:scaleY(0)}60%{opacity:1;transform:scaleY(1.06)}"
                 "100%{opacity:1;transform:scaleY(1)}}"
                 ".blink{animation:blink 1.6s steps(1) infinite}@keyframes blink{50%{opacity:.25}}")
    s.add(f'<rect width="1280" height="{h}" rx="20" fill="{P["bg"]}"/>')
    s.text(48, 60, "Now running", 34, P["text"], 800)
    cols = (48, 400, 1080)
    s.text(cols[0] + 34, top - 8, "Service", 15, P["muted"], 600)
    s.text(cols[1], top - 8, "Where it is", 15, P["muted"], 600)
    s.text(1232, top - 8, "Status", 15, P["muted"], 600, anchor="end")
    for i, (key, name, desc, st) in enumerate(NOW):
        y = top + i * row_h
        label, skey = STATUS[st]
        s.add(f'<g class="row" style="animation-delay:{0.25 + i * 0.18:.2f}s">')
        s.add(f'<rect x="32" y="{y + 6}" width="1216" height="{row_h - 10}" rx="10" fill="{P["surface"]}" stroke="{P["edge"]}"/>')
        s.add(f'<rect x="48" y="{y + 29}" width="22" height="8" rx="4" fill="{P[key]}"/>')
        s.text(cols[0] + 34, y + 41, name, 22, P["text"], 800)
        s.text(cols[1], y + 41, desc, 21, P["text"], 400)
        pw = text_width(label, 16) + 42
        s.add(f'<rect x="{1232 - pw}" y="{y + 17}" width="{pw}" height="32" rx="16" fill="none" stroke="{P["edge"]}"/>')
        cls = ' class="blink"' if st in ("building", "open") else ""
        s.add(f'<circle{cls} cx="{1232 - pw + 18}" cy="{y + 33}" r="6" fill="{P[skey]}"/>')
        s.text(1232 - 14, y + 39, label, 16, P["text"], 600, anchor="end")
        s.add("</g>")
    return s.render()

# ------------------------------------------------------------------ project cards
PROJECTS = [
    ("assetflow", "AssetFlow Schools", "amber", "beta",
     "Multi-tenant SaaS that tracks school assets with QR codes, built for theft prevention, loss tracking and audit-ready records.",
     ["React", "Django", "PostgreSQL", "Celery", "Redis", "R2"]),
    ("eventify", "Eventify", "coral", "handed",
     "Fraud-hardened ticketing, security audited for ticket attacks and offline gate-scan reconciliation. Now run by a partner.",
     ["Material 3", "Offline scanning", "Security audited"]),
    ("farmassist", "FarmAssist", "green", "building",
     "Crop disease diagnosis from one leaf photo, delivered over WhatsApp so farmers never install an app.",
     ["TypeScript", "Express", "Prisma", "BullMQ", "OpenAI Vision"]),
    ("risiti", "Risiti", "teal", "planned",
     "Offline-capable eTIMS compliance rail that brings Kenya's informal B2B traders into tax compliance.",
     ["Kotlin", "Spring Boot", "Offline-first"]),
    ("lucklotter", "LuckLotter", "teal", "testing",
     "Retention system for a banking software vendor. Rules-based detection tracks each customer's transaction rhythm and flags drift.",
     ["Angular", "Spring Boot", "PostgreSQL", "Docker"]),
    ("retail", "Retail analytics", "coral", "planned",
     "Privacy-first in-store analytics. Video is processed at the edge, so raw footage never leaves the shop.",
     ["YOLO11n", "Edge inference", "Privacy by design"]),
]
SECTOR = dict(LINES)

def card(t, slug, name, key, st, desc, stack):
    P = THEMES[t]
    W, H = 620, 320
    s = SVG(W, H, f"{name}. {desc} Stack: {', '.join(stack)}.")
    s.add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{P["surface"]}" stroke="{P["edge"]}" stroke-width="2"/>')
    # line strip with station, like a route sign
    s.add(f'<clipPath id="clip-{slug}"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/></clipPath>')
    s.add(f'<rect x="0" y="0" width="{W}" height="11" fill="{P[key]}" clip-path="url(#clip-{slug})"/>')
    s.text(30, 68, name, 34, P["text"], 800, extra='letter-spacing="-.4"')
    s.text(30, 98, f"{SECTOR[key] if key in SECTOR else ''} line", 17, P["muted"], 600)
    label, skey = STATUS[st]
    pw = text_width(label, 17) + 44
    s.add(f'<rect x="{W - 30 - pw}" y="38" width="{pw}" height="34" rx="17" fill="none" stroke="{P["edge"]}" stroke-width="1.5"/>')
    s.add(f'<circle cx="{W - 30 - pw + 16}" cy="55" r="6" fill="{P[skey]}"/>')
    s.text(W - 44, 61, label, 17, P["text"], 600, anchor="end")
    for i, line in enumerate(wrap(desc, 21, W - 60)):
        s.text(30, 146 + i * 30, line, 21, P["text"], 400)
    x = 30
    for chip in stack:
        cw = text_width(chip, 16) + 26
        s.add(f'<rect x="{x}" y="{H - 62}" width="{cw}" height="36" rx="9" fill="{P["bg"]}" stroke="{P["edge"]}"/>')
        s.text(x + 13, H - 38, chip, 16, P["muted"], 600)
        x += cw + 8
    assert x < W - 20, f"chips overflow on {name}"
    return s.render()

# ------------------------------------------------------------------ stack board
STACK = [
    ("Languages", ["Kotlin", "Java", "Python", "TypeScript", "JavaScript", "PHP"]),
    ("Backend", ["Spring Boot", "Django", "Express", "Celery", "BullMQ", "Webhooks"]),
    ("Frontend and mobile", ["React", "Angular", "Jetpack Compose", "Tailwind", "Framer Motion", "Three.js"]),
    ("Data", ["PostgreSQL", "Redis", "Prisma", "Firebase"]),
    ("Infrastructure", ["Docker Compose", "Cloudflare R2", "Sentry", "Grafana Loki"]),
    ("AI and automation", ["OpenAI API", "RAG", "YOLO", "n8n", "WhatsApp Cloud API"]),
]
def stack(t):
    P = THEMES[t]
    row_h, top = 72, 104
    h = top + row_h * len(STACK) + 20
    s = SVG(1280, h, "Tech stack. " + " ".join(f"{k}: {', '.join(v)}." for k, v in STACK))
    s.add(f'<rect width="1280" height="{h}" rx="20" fill="{P["bg"]}"/>')
    s.text(48, 60, "What I build with", 34, P["text"], 800)
    for i, (layer, items) in enumerate(STACK):
        y = top + i * row_h
        if i:
            s.add(f'<line x1="48" y1="{y - 8}" x2="1232" y2="{y - 8}" stroke="{P["edge"]}"/>')
        s.text(48, y + 34, layer, 18, P["muted"], 600)
        x = 290
        for it in items:
            cw = text_width(it, 17) + 28
            s.add(f'<rect x="{x}" y="{y + 9}" width="{cw}" height="38" rx="10" fill="{P["surface"]}" stroke="{P["edge"]}"/>')
            s.text(x + 14, y + 34, it, 17, P["text"], 600)
            x += cw + 10
        assert x < 1240, f"stack overflow {layer}"
    return s.render()

# ------------------------------------------------------------------ write
for t in THEMES:
    open(f"{OUT}/header-{t}.svg", "w").write(header(t))
    open(f"{OUT}/now-{t}.svg", "w").write(board(t))
    open(f"{OUT}/stack-{t}.svg", "w").write(stack(t))
    for slug, name, key, st, desc, st_ in PROJECTS:
        open(f"{OUT}/cards/{slug}-{t}.svg", "w").write(card(t, slug, name, key, st, desc, st_))
print("built", sum(len(f) for _, _, f in os.walk(OUT)), "files")
