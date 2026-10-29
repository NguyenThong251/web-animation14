#!/usr/bin/env python3
"""Rebase the captured michelangelus mirror onto a GitHub Pages subpath.

The origin is a Next.js Pages-Router build (Turbopack) compiled with
basePath="" and served at the domain root, so every same-origin reference is
root-absolute. GitHub Pages serves the project at /<repo>/, so this script
copies public/ -> <out>/ and rewrites, in the copy only:

  HTML   root-absolute attrs (href/src/...) -> /<repo>/...; the /images/ and
         /videos/ paths inside __NEXT_DATA__; adds "assetPrefix" to
         __NEXT_DATA__ (Next's own hook: the route loader fetches page chunks
         from `${assetPrefix}/_next/...`).
  JSON   /_next/data/*.json page props: the same /images/ + /videos/ paths.
  JS     Turbopack runtime chunk base "/_next/"; the router's compiled-in
         basePath helpers (hasBasePath / addBasePath / removeBasePath /
         Router.basePath) so Link hrefs, data fetches and the initial asPath
         all carry the subpath; hard-coded WebGL asset literals ("/assets/",
         draco/basis decoders, animated favicon frames).

Every patch asserts its exact match count so a changed bundle fails loudly
instead of deploying a half-rebased site.

Usage: python3 scripts/subpath.py /web-animation13 _site
"""
import re
import shutil
import sys
from pathlib import Path

BASE = sys.argv[1].rstrip("/")
OUT = Path(sys.argv[2])
SRC = Path(__file__).resolve().parent.parent / "public"
CHUNKS = OUT / "_next/static/immutable/chunks"

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
(OUT / ".nojekyll").touch()


def patch(path, old, new, count, regex=False):
    s = path.read_text()
    n = len(re.findall(old, s)) if regex else s.count(old)
    if n != count:
        sys.exit(f"{path.relative_to(OUT)}: expected {count}x {old!r}, found {n}")
    s = re.sub(old, new, s) if regex else s.replace(old, new)
    path.write_text(s)


# HTML pages
for page in sorted(OUT.glob("*.html")):
    s = page.read_text()
    # attrs pointing at the site root (not protocol-relative //host)
    s = re.sub(r'\b(href|src|srcSet|poster|content)="/(?!/)', rf'\1="{BASE}/', s)
    s = s.replace('"/images/', f'"{BASE}/images/').replace('"/videos/', f'"{BASE}/videos/')
    if s.count('"buildId":"') != 1:
        sys.exit(f"{page.name}: __NEXT_DATA__ buildId not found exactly once")
    s = s.replace('"buildId":"', f'"assetPrefix":"{BASE}","buildId":"')
    page.write_text(s)

# getStaticProps payloads used on client-side navigation
for data in sorted(OUT.glob("_next/data/*/*.json")):
    s = data.read_text()
    data.write_text(s.replace('"/images/', f'"{BASE}/images/').replace('"/videos/', f'"{BASE}/videos/'))

# Turbopack runtime: base URL every lazy chunk is loaded from
for rt in sorted(CHUNKS.glob("turbopack-*.js")):
    patch(rt, 'r="/_next/"', f'r="{BASE}/_next/"', 1)

# Next.js client router: compiled-in basePath ""
router = CHUNKS / "3emkzd1tx-f16.js"
patch(router, 'pathHasPrefix)(e,"")', f'pathHasPrefix)(e,"{BASE}")', 1)  # hasBasePath
patch(router, 'addPathPrefix)(e,"")', f'addPathPrefix)(e,"{BASE}")', 1)  # addBasePath
patch(  # removeBasePath: identity when basePath=="" -> Next's real slice
    router,
    'function n(e){return e}e.i(19441),Object.defineProperty(r,"__esModule",{value:!0}),Object.defineProperty(r,"removeBasePath"',
    'function n(e){return(e=e.slice(%d)).startsWith("/")?e:"/"+e}e.i(19441),Object.defineProperty(r,"__esModule",{value:!0}),Object.defineProperty(r,"removeBasePath"' % len(BASE),
    1,
)
patch(router, 'this.basePath=""', f'this.basePath="{BASE}"', 1)

# App bundle: WebGL models/textures/MSDF atlases, three.js decoders, favicon frames
app = CHUNKS / "1veq2k-9qm_qo.js"
patch(app, '"/assets/', f'"{BASE}/assets/', 13)
patch(app, '"/_next/static/immutable/media/', f'"{BASE}/_next/static/immutable/media/', 7)
patch(app, "`/favicon-frames/", f"`{BASE}/favicon-frames/", 1)

# nothing root-absolute may survive in the pages' attributes
for page in OUT.glob("*.html"):
    left = re.findall(r'\b(?:href|src)="/(?!/)[^"]*"', page.read_text())
    left = [x for x in left if not x.split('"')[1].startswith(BASE + "/") and x.split('"')[1] != BASE + "/"]
    if left:
        sys.exit(f"{page.name}: un-rebased refs {left[:5]}")
print(f"rebased {SRC} -> {OUT} for {BASE}")
