# web-animation14

**🔴 Live demo: <https://nguyenthong251.github.io/web-animation14/>**

Bản clone 1:1 (static mirror) của [michelangelus.studiogusto.com](https://michelangelus.studiogusto.com/) — trang giới thiệu typeface **Michelangelus** do Studiogusto® thiết kế cho Fabbrica di San Pietro in Vaticano (phân phối bởi Microsoft) — phục vụ mục đích học tập / nghiên cứu kỹ thuật. Toàn bộ hình ảnh, font, model 3D, nội dung và thiết kế thuộc về chủ sở hữu gốc.

## Stack (khớp site gốc)

- **Next.js Pages Router** build bằng **Turbopack** (`/_next/static/immutable/`, `__NEXT_DATA__`, `getStaticProps` → `/_next/data/<buildId>/*.json`), nội dung từ **WordPress headless** (ACF, Yoast)
- **Three.js r184 / WebGL** — scene 3D (model glTF *hands*, *Pietà*, *St. Peter* + Draco), texture **KTX2/Basis**, chữ **MSDF** (atlas `Michelangelus-*.json/png`), depth map / reveal mask
- **GSAP + ScrollTrigger** + **Lenis** smooth scroll (section sticky 190–700 lvh)
- Font **Michelangelus** Regular / Italic / Bold / Bold Italic (woff2 self-host, `next/font/local`)
- Favicon động 40 frame vẽ lên canvas
- 3 route: `/`, `/cookie-technical-data-notice`, `/terms-conditions` (+ trang 404)

## Chạy local

```bash
npm run dev    # http://localhost:4300  (node server.mjs public 4300)
```

## Deploy

`public/` là bản build gốc chép nguyên byte. Khác biệt duy nhất so với origin: `GTM_ID` trong bundle được đặt rỗng (app tự có guard `GTM_ID && <GoogleTagManager>`), để bản clone không bắn analytics của Studiogusto (pixel `p.studiogusto.com` trả 403 cho domain lạ).

GitHub Pages phục vụ ở subpath `/web-animation14/`, trong khi build gốc dùng path tuyệt đối + `basePath ""` compile cứng. Workflow chạy [`scripts/subpath.py`](scripts/subpath.py) để rebase bản copy `_site/`: attr HTML, `__NEXT_DATA__` (+ `assetPrefix`), page props `/_next/data`, base chunk của Turbopack runtime, 4 helper `basePath` của router Next và các literal asset WebGL. Mỗi patch assert số lần match → bundle đổi là build fail chứ không deploy nửa vời.
