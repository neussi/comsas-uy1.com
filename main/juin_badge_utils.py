"""
juin_badge_utils.py — Badge J.U.IN 2026 v3
Layout précis sans superposition. Toutes les zones calculées de bas en haut.
"""

import os
import math
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image, ImageOps, ImageDraw


# ── Palette ──────────────────────────────────────────────────────────────────
C_NUIT       = colors.Color(26/255,  26/255,  46/255)
C_NUIT2      = colors.Color(45/255,  10/255,  30/255)
C_ROSE       = colors.Color(233/255, 30/255,  99/255)
C_ORANGE     = colors.Color(255/255, 152/255, 0/255)
C_ROSE_SOFT  = colors.Color(255/255, 111/255, 168/255)
C_WHITE      = colors.white
C_LIGHT      = colors.Color(0.98, 0.96, 0.97)
C_GREY       = colors.Color(0.55, 0.55, 0.60)

# ── Zones (mm depuis le bas) ─────────────────────────────────────────────────
Z_FOOTER_H    = 17.0   # hauteur footer foncé
Z_LOGO_H      = 15.0   # hauteur bande logos
Z_LOGO_BASE   = Z_FOOTER_H                    # 17mm
Z_LOGO_TOP    = Z_FOOTER_H + Z_LOGO_H         # 32mm
Z_BODY_MARGIN = 3.0    # marge entre dernier élément corps et bande logos
Z_HDR_H       = 62.0   # hauteur header
Z_PHOTO_D     = 26.0   # diamètre photo
Z_PHOTO_R     = Z_PHOTO_D / 2                 # 13mm
Z_WAVE_Y      = 148.0 - Z_HDR_H               # 86mm  — ligne de vague = centre photo
Z_BODY_TOP    = Z_WAVE_Y - Z_PHOTO_R          # 73mm  — bas de la photo


def _rgb(c):
    return (int(c.red * 255), int(c.green * 255), int(c.blue * 255))


def _grad_buf(w_px, h_px, c1, c2, vertical=True):
    img = Image.new('RGB', (max(1, w_px), max(1, h_px)))
    steps = h_px if vertical else w_px
    for i in range(max(1, steps)):
        t = i / max(steps - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        if vertical:
            img.paste((r, g, b), (0, i, max(1, w_px), i + 1))
        else:
            img.paste((r, g, b), (i, 0, i + 1, max(1, h_px)))
    buf = BytesIO(); img.save(buf, 'PNG'); buf.seek(0)
    return buf


def _grad_rect(p, x, y, w, h, c1, c2, radius=0, vertical=False):
    buf = _grad_buf(max(1, int(w / mm * 8)), max(1, int(h / mm * 8)),
                    _rgb(c1), _rgb(c2), vertical=vertical)
    if radius > 0:
        p.saveState()
        clip = p.beginPath()
        clip.roundRect(x, y, w, h, radius)
        p.clipPath(clip, stroke=0)
        p.drawImage(ImageReader(buf), x, y, width=w, height=h, mask='auto')
        p.restoreState()
    else:
        p.drawImage(ImageReader(buf), x, y, width=w, height=h, mask='auto')


def _grad_line(p, x0, y, x1, lw=1.5, steps=40):
    p.setLineWidth(lw)
    L = x1 - x0
    for i in range(steps):
        t = i / steps
        r = int(_rgb(C_ROSE)[0] + (_rgb(C_ORANGE)[0] - _rgb(C_ROSE)[0]) * t)
        g = int(_rgb(C_ROSE)[1] + (_rgb(C_ORANGE)[1] - _rgb(C_ROSE)[1]) * t)
        b = int(_rgb(C_ROSE)[2] + (_rgb(C_ORANGE)[2] - _rgb(C_ROSE)[2]) * t)
        p.setStrokeColorRGB(r / 255, g / 255, b / 255)
        p.line(x0 + t * L, y, x0 + (t + 1 / steps) * L, y)


def _grad_ring(p, cx, cy, r_in, r_out, steps=100):
    lw = r_out - r_in
    r_mid = (r_in + r_out) / 2
    p.setLineWidth(lw)
    for i in range(steps):
        t = i / steps
        r = int(_rgb(C_ROSE)[0] + (_rgb(C_ORANGE)[0] - _rgb(C_ROSE)[0]) * t)
        g = int(_rgb(C_ROSE)[1] + (_rgb(C_ORANGE)[1] - _rgb(C_ROSE)[1]) * t)
        b = int(_rgb(C_ROSE)[2] + (_rgb(C_ORANGE)[2] - _rgb(C_ROSE)[2]) * t)
        a1 = i * 2 * math.pi / steps
        a2 = (i + 1.5) * 2 * math.pi / steps
        p.setStrokeColorRGB(r / 255, g / 255, b / 255)
        p.line(cx + r_mid * math.cos(a1), cy + r_mid * math.sin(a1),
               cx + r_mid * math.cos(a2), cy + r_mid * math.sin(a2))


def _circular_photo(img_path, size=600):
    try:
        img = Image.open(img_path).convert("RGBA")
        img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask=mask)
        return out
    except Exception as e:
        print(f"[Badge] Photo error: {e}")
        return None


def _initials_avatar(name, size=600):
    parts = name.split()
    initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else '')).upper()
    bg = Image.new('RGB', (size, size))
    for i in range(size):
        t = i / (size - 1)
        r = int(_rgb(C_ROSE)[0] + (_rgb(C_ORANGE)[0] - _rgb(C_ROSE)[0]) * t)
        g = int(_rgb(C_ROSE)[1] + (_rgb(C_ORANGE)[1] - _rgb(C_ROSE)[1]) * t)
        b = int(_rgb(C_ROSE)[2] + (_rgb(C_ORANGE)[2] - _rgb(C_ROSE)[2]) * t)
        bg.paste((r, g, b), (0, i, size, i + 1))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    draw = ImageDraw.Draw(out)
    fs = size // 3
    try:
        from PIL import ImageFont
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)
        bbox = draw.textbbox((0, 0), initials, font=font)
        draw.text(((size - (bbox[2] - bbox[0])) // 2 - bbox[0],
                   (size - (bbox[3] - bbox[1])) // 2 - bbox[1]),
                  initials, fill=(255, 255, 255, 255), font=font)
    except Exception:
        pass
    return out


def _logo_circle(path, size_px=120, fallback_text="", fallback_color=(50, 50, 80)):
    """Load logo as circular PIL image, with solid-color fallback."""
    img = None
    if path and os.path.exists(path):
        try:
            raw = Image.open(path).convert("RGBA")
            raw = ImageOps.fit(raw, (size_px, size_px), centering=(0.5, 0.5))
            img = raw
        except Exception as e:
            print(f"[Badge] Logo {path}: {e}")

    if img is None:
        # Fallback: colored circle with text
        img = Image.new('RGBA', (size_px, size_px), (0, 0, 0, 0))
        bg = Image.new('RGB', (size_px, size_px), fallback_color)
        mask_bg = Image.new('L', (size_px, size_px), 0)
        ImageDraw.Draw(mask_bg).ellipse((0, 0, size_px, size_px), fill=255)
        img.paste(bg, (0, 0), mask_bg)
        draw = ImageDraw.Draw(img)
        txt = fallback_text[:3].upper()
        fs = size_px // 4
        try:
            from PIL import ImageFont
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)
            bb = draw.textbbox((0, 0), txt, font=font)
            draw.text(((size_px - (bb[2] - bb[0])) // 2 - bb[0],
                       (size_px - (bb[3] - bb[1])) // 2 - bb[1]),
                      txt, fill=(255, 255, 255, 220), font=font)
        except Exception:
            pass
    else:
        # Circular clip on real logo
        mask_c = Image.new('L', (size_px, size_px), 0)
        ImageDraw.Draw(mask_c).ellipse((2, 2, size_px - 2, size_px - 2), fill=255)
        clipped = Image.new('RGBA', (size_px, size_px), (0, 0, 0, 0))
        clipped.paste(img, (0, 0), mask_c)
        img = clipped

    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return ImageReader(buf)


# ─────────────────────────────────────────────────────────────────────────────
#  MOTEUR DE DESSIN
# ─────────────────────────────────────────────────────────────────────────────

def build_badge(
    buffer,
    nom_prenom, commission_code, commission_name,
    role, etablissement, niveau,
    edition_number=20, photo_path=None,
    partner_logo_paths=None,
    comsas_logo_path=None      # chemin vers static/images/comsas.png
):
    """Dessine un badge A6 dans `buffer` (BytesIO)."""
    width, height = A6   # 297.6pt × 419.5pt  (105mm × 148mm)
    p = canvas.Canvas(buffer, pagesize=A6)
    p.setTitle(f"Badge J.U.IN {edition_number}e Édition — {nom_prenom}")

    # Conversions pratiques
    W  = width
    H  = height

    # Zones en points (depuis le BAS)
    footer_h     = Z_FOOTER_H   * mm
    logo_h       = Z_LOGO_H     * mm
    logo_base    = Z_LOGO_BASE  * mm   # bas de la bande logos
    logo_top     = Z_LOGO_TOP   * mm   # haut de la bande logos
    hdr_h        = Z_HDR_H      * mm
    photo_d      = Z_PHOTO_D    * mm
    photo_r      = Z_PHOTO_R    * mm
    wave_y       = Z_WAVE_Y     * mm   # = centre photo
    body_top     = Z_BODY_TOP   * mm   # = bas de la photo

    # ── 1. Fond ───────────────────────────────────────────────────────────────
    p.setFillColor(C_LIGHT)
    p.rect(0, 0, W, H, fill=1, stroke=0)

    # Watermark
    p.saveState()
    p.setFillColor(colors.Color(233/255, 30/255, 99/255, 0.025))
    p.setFont("Helvetica-Bold", 55)
    p.translate(W / 2, H / 2); p.rotate(32)
    p.drawCentredString(0, 0, "J.U.IN")
    p.restoreState()

    # ── 2. Header avec vague ──────────────────────────────────────────────────
    wave_amp = 7 * mm
    p.saveState()
    hdr_clip = p.beginPath()
    hdr_clip.moveTo(0, H)
    hdr_clip.lineTo(W, H)
    hdr_clip.lineTo(W, wave_y)
    hdr_clip.curveTo(W * 0.75, wave_y + wave_amp,
                     W * 0.25, wave_y - wave_amp,
                     0, wave_y)
    hdr_clip.close()
    p.clipPath(hdr_clip, stroke=0)
    _grad_rect(p, 0, wave_y - wave_amp, W, hdr_h + wave_amp * 2,
               C_NUIT, C_NUIT2, vertical=False)
    p.restoreState()

    # Bande accent rose (gauche)
    ACC_W = 5.5 * mm
    p.saveState()
    acc_clip = p.beginPath()
    acc_clip.moveTo(0, H)
    acc_clip.lineTo(ACC_W, H)
    acc_clip.lineTo(ACC_W, wave_y + 10 * mm)
    acc_clip.curveTo(ACC_W, wave_y + 2 * mm, 0, wave_y + 0.5 * mm, 0, wave_y)
    acc_clip.close()
    p.clipPath(acc_clip, stroke=0)
    _grad_rect(p, 0, wave_y, ACC_W, hdr_h, C_ROSE, C_ORANGE, vertical=True)
    p.restoreState()

    # ── 3. Logo COM.S.AS (image) ──────────────────────────────────────────────
    LOGO_SZ_HDR = 13 * mm   # taille du logo affiché
    lx = 9 * mm
    ly = H - 7.5 * mm - LOGO_SZ_HDR
    logo_cx = lx + LOGO_SZ_HDR / 2
    logo_cy = ly + LOGO_SZ_HDR / 2

    # 1. Ombre douce
    p.setFillColor(colors.Color(0, 0, 0, 0.25))
    p.circle(logo_cx + 0.5*mm, logo_cy - 0.5*mm,
             LOGO_SZ_HDR / 2 + 1.2 * mm, fill=1, stroke=0)

    # 2. Cercle blanc SOLIDE (opaque) — fond du logo
    p.setFillColor(colors.white)
    p.circle(logo_cx, logo_cy, LOGO_SZ_HDR / 2 + 1.0 * mm, fill=1, stroke=0)

    # 3. Anneau fin gradient rose→orange
    ring_r_in  = LOGO_SZ_HDR / 2 + 0.8 * mm
    ring_r_out = LOGO_SZ_HDR / 2 + 1.8 * mm
    import math as _math
    lw_ring = ring_r_out - ring_r_in
    r_mid   = (ring_r_in + ring_r_out) / 2
    steps_r = 60
    p.setLineWidth(lw_ring)
    for i in range(steps_r):
        t  = i / steps_r
        rc = int(_rgb(C_ROSE)[0] + (_rgb(C_ORANGE)[0] - _rgb(C_ROSE)[0]) * t)
        gc = int(_rgb(C_ROSE)[1] + (_rgb(C_ORANGE)[1] - _rgb(C_ROSE)[1]) * t)
        bc = int(_rgb(C_ROSE)[2] + (_rgb(C_ORANGE)[2] - _rgb(C_ROSE)[2]) * t)
        a1 = i     * 2 * _math.pi / steps_r
        a2 = (i+1.5) * 2 * _math.pi / steps_r
        p.setStrokeColorRGB(rc/255, gc/255, bc/255)
        p.line(logo_cx + r_mid*_math.cos(a1), logo_cy + r_mid*_math.sin(a1),
               logo_cx + r_mid*_math.cos(a2), logo_cy + r_mid*_math.sin(a2))

    # 4. Dessin du logo sur le fond blanc — clipé en cercle
    comsas_logo = None
    if comsas_logo_path and os.path.exists(comsas_logo_path):
        try:
            # Pré-traiter avec PIL : rogner en cercle sur fond blanc
            raw = Image.open(comsas_logo_path).convert("RGBA")
            sz  = 300
            raw = ImageOps.fit(raw, (sz, sz), centering=(0.5, 0.5))
            # Fond blanc
            bg_white = Image.new('RGBA', (sz, sz), (255, 255, 255, 255))
            bg_white.paste(raw, (0, 0), raw)
            # Clip circulaire
            cmask = Image.new('L', (sz, sz), 0)
            ImageDraw.Draw(cmask).ellipse((0, 0, sz, sz), fill=255)
            result = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
            result.paste(bg_white, (0, 0), cmask)
            logo_buf = BytesIO()
            result.save(logo_buf, 'PNG')
            logo_buf.seek(0)
            comsas_logo = ImageReader(logo_buf)
        except Exception as e:
            print(f"[Badge] Logo COMSAS: {e}")

    if comsas_logo:
        p.drawImage(comsas_logo, lx, ly,
                    width=LOGO_SZ_HDR, height=LOGO_SZ_HDR,
                    mask='auto', preserveAspectRatio=True)
    else:
        # Fallback : initiales sur fond blanc
        p.setFillColor(C_ROSE); p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(logo_cx, logo_cy - 1.5 * mm, "CS")

    # 5. Texte à droite du logo
    tx = lx + LOGO_SZ_HDR + 3 * mm
    ty = logo_cy + 2 * mm
    p.setFillColor(C_WHITE); p.setFont("Helvetica-Bold", 10.5)
    p.drawString(tx, ty, "COM.S.AS")
    p.setFillColor(C_ROSE_SOFT); p.setFont("Helvetica", 5.8)
    p.drawString(tx, ty - 4 * mm, "Computer Science Association")

    # 6. Ligne séparatrice
    p.setStrokeColor(colors.Color(1, 1, 1, 0.10)); p.setLineWidth(0.4)
    p.line(lx, ly - 2.5 * mm, W - 7 * mm, ly - 2.5 * mm)

    # ── 4. Badge édition (haut-droit) ─────────────────────────────────────────
    ed_w, ed_h = 24 * mm, 8 * mm
    ed_x = W - ed_w - 5 * mm
    ed_y = H - 15 * mm
    _grad_rect(p, ed_x, ed_y, ed_w, ed_h, C_ROSE, C_ORANGE,
               radius=3 * mm, vertical=False)
    p.setFillColor(C_WHITE); p.setFont("Helvetica-Bold", 6.8)
    p.drawCentredString(ed_x + ed_w / 2, ed_y + 2.5 * mm, f"{edition_number}e EDITION")

    # ── 5. Titre J.U.IN 2026 ──────────────────────────────────────────────────
    # Positionné dans la partie haute du header, bien au-dessus de la photo
    titre_y    = H - 37 * mm
    sous_titre_y = titre_y - 6 * mm

    p.setFillColor(C_WHITE); p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(W / 2, titre_y, "J.U.IN 2026")

    p.setFillColor(C_ROSE_SOFT); p.setFont("Helvetica", 6.5)
    p.drawCentredString(W / 2, sous_titre_y,
                        "Journées Universitaires de l'Informatique")

    # ── 6. Photo circulaire ───────────────────────────────────────────────────
    cx = W / 2
    cy = wave_y   # centre = sur la vague

    # Ombre
    p.saveState()
    p.setFillColor(colors.Color(0, 0, 0, 0.10))
    p.circle(cx + 0.6 * mm, cy - 1.2 * mm, photo_r + 2.2 * mm, fill=1, stroke=0)
    p.restoreState()

    # Anneau gradient
    _grad_ring(p, cx, cy, photo_r + 0.8 * mm, photo_r + 2.6 * mm, steps=100)
    # Anneau blanc
    p.setStrokeColor(C_WHITE); p.setLineWidth(1.8)
    p.circle(cx, cy, photo_r + 0.3 * mm, fill=0, stroke=1)

    # Image
    if photo_path and os.path.exists(photo_path):
        circ = _circular_photo(photo_path, 600)
    else:
        circ = None
    if circ is None:
        circ = _initials_avatar(nom_prenom, 600)

    ph_buf = BytesIO(); circ.save(ph_buf, 'PNG'); ph_buf.seek(0)
    p.saveState()
    cp = p.beginPath(); cp.circle(cx, cy, photo_r)
    p.clipPath(cp, stroke=0)
    p.drawImage(ImageReader(ph_buf), cx - photo_r, cy - photo_r,
                width=photo_d, height=photo_d, mask='auto')
    p.restoreState()

    # ══════════════════════════════════════════════════════════════════════════
    # CORPS — construction de BAS EN HAUT depuis logo_top
    # Chaque élément est positionné avec un curseur Y qui monte
    # ══════════════════════════════════════════════════════════════════════════
    MARGIN_TOP_LOGO = 1.5 * mm   # espace entre logos et 1er élément du corps

    # Curseur Y : part du haut de la bande logos + marge
    cursor = logo_top + MARGIN_TOP_LOGO

    # ── A. Pill établissement & niveau ────────────────────────────────────────
    SC_H = 6.5 * mm
    sc_text = f"{etablissement}  ·  {niveau}"
    sc_w = stringWidth(sc_text, "Helvetica", 7.5) + 8 * mm
    sc_x = (W - sc_w) / 2

    p.setFillColor(colors.Color(0.90, 0.86, 0.88))
    p.roundRect(sc_x, cursor, sc_w, SC_H, SC_H / 2, fill=1, stroke=0)
    p.setFillColor(C_NUIT); p.setFont("Helvetica", 7.5)
    p.drawCentredString(W / 2, cursor + SC_H / 2 - 1.5 * mm, sc_text)

    cursor += SC_H + 3 * mm   # avance le curseur

    # ── B. Nom commission ─────────────────────────────────────────────────────
    COMM_FS = 8.5
    for fs in [8.5, 7.5, 6.5]:
        if stringWidth(commission_name, "Helvetica", fs) <= W - 12 * mm:
            COMM_FS = fs; break
    p.setFillColor(C_GREY); p.setFont("Helvetica", COMM_FS)
    p.drawCentredString(W / 2, cursor, commission_name)
    cursor += COMM_FS * 0.352778 * mm + 3 * mm   # ~hauteur texte + gap

    # ── C. Rôle ───────────────────────────────────────────────────────────────
    p.setFillColor(C_ROSE); p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(W / 2, cursor, role.upper())
    cursor += 9 * 0.352778 * mm + 4 * mm

    # ── D. Nom complet ────────────────────────────────────────────────────────
    name_upper = nom_prenom.upper()
    chosen_fs = 16
    for fs in [16, 13, 11, 9]:
        if stringWidth(name_upper, "Helvetica-Bold", fs) <= W - 10 * mm:
            chosen_fs = fs; break
    p.setFillColor(C_NUIT); p.setFont("Helvetica-Bold", chosen_fs)
    p.drawCentredString(W / 2, cursor, name_upper)

    # Ligne gradient sous le nom
    lw_line = min(stringWidth(name_upper, "Helvetica-Bold", chosen_fs) + 8 * mm,
                  W - 14 * mm)
    _grad_line(p, (W - lw_line) / 2, cursor - 2.5 * mm, (W + lw_line) / 2, lw=1.5)
    cursor += chosen_fs * 0.352778 * mm + 4 * mm

    # ── E. Pill commission ────────────────────────────────────────────────────
    PILL_H = 7 * mm
    pill_w = stringWidth(commission_code, "Helvetica-Bold", 9) + 10 * mm
    pill_x = (W - pill_w) / 2
    _grad_rect(p, pill_x, cursor, pill_w, PILL_H,
               C_ROSE, C_ORANGE, radius=PILL_H / 2, vertical=False)
    p.setFillColor(C_WHITE); p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(W / 2, cursor + PILL_H / 2 - 1.5 * mm, commission_code)
    cursor += PILL_H   # fin du contenu corps — doit être <= body_top

    # Vérification (debug)
    print(f"  cursor après corps : {cursor/mm:.1f}mm | body_top : {body_top/mm:.1f}mm")
    if cursor > body_top:
        print(f"  ⚠ Dépassement de {(cursor-body_top)/mm:.1f}mm — réduire les gaps")

    # ══════════════════════════════════════════════════════════════════════════
    # LOGOS PARTENAIRES
    # ══════════════════════════════════════════════════════════════════════════
    SEP_Y = logo_top - 0.5 * mm
    p.setStrokeColor(colors.Color(233/255, 30/255, 99/255, 0.20))
    p.setLineWidth(0.5)
    p.line(8 * mm, SEP_Y, W - 8 * mm, SEP_Y)

    # Label
    label_y = logo_top - 3.5 * mm
    p.setFillColor(C_GREY); p.setFont("Helvetica", 5.2)
    p.drawCentredString(W / 2, label_y, "ÉTABLISSEMENTS PARTENAIRES")

    # 4 logos centrés dans la bande
    LOGO_SZ   = 9 * mm     # taille affichée
    LOGO_GAP  = 3.5 * mm
    total_lw  = 4 * LOGO_SZ + 3 * LOGO_GAP
    logo_sx   = (W - total_lw) / 2
    logo_y    = logo_base + (logo_h - LOGO_SZ) / 2 - 2 * mm  # centré vertikalement

    fallback_colors = {
        'uy1':        (26,  26,  46),
        'enspy':      (6,   78,  59),
        'saint-jean': (76,  29,  149),
        'supptic':    (146, 64,  14),
    }
    logo_keys   = ['uy1', 'enspy', 'saint-jean', 'supptic']
    logo_labels = ['UY1', 'ENSPY', 'SJ', 'SUP']

    paths = partner_logo_paths or {}
    for i, (key, lbl) in enumerate(zip(logo_keys, logo_labels)):
        lx_l = logo_sx + i * (LOGO_SZ + LOGO_GAP)
        reader = _logo_circle(
            paths.get(key),
            size_px=120,
            fallback_text=lbl,
            fallback_color=fallback_colors[key]
        )
        p.drawImage(reader, lx_l, logo_y,
                    width=LOGO_SZ, height=LOGO_SZ, mask='auto')

    # ══════════════════════════════════════════════════════════════════════════
    # FOOTER DÉGRADÉ
    # ══════════════════════════════════════════════════════════════════════════
    ft_wave = 4 * mm
    p.saveState()
    ft_clip = p.beginPath()
    ft_clip.moveTo(0, 0)
    ft_clip.lineTo(W, 0)
    ft_clip.lineTo(W, footer_h)
    ft_clip.curveTo(W * 0.75, footer_h + ft_wave,
                    W * 0.25, footer_h - ft_wave,
                    0, footer_h)
    ft_clip.close()
    p.clipPath(ft_clip, stroke=0)
    _grad_rect(p, 0, 0, W, footer_h + ft_wave, C_NUIT2, C_NUIT, vertical=False)
    p.restoreState()

    # Ligne gradient
    _grad_line(p, 0, 1 * mm, W, lw=2.5)

    # Texte footer
    p.setFillColor(C_WHITE); p.setFont("Helvetica-Bold", 6.8)
    p.drawCentredString(W / 2, 10 * mm,
                        f"J.U.IN {edition_number}e Édition  —  01–05 Juin 2026  —  UY1, Yaoundé")
    p.setFillColor(C_ROSE_SOFT); p.setFont("Helvetica", 6)
    p.drawCentredString(W / 2, 6 * mm, "Coder  •  Innover  •  Entreprendre")

    # Dots déco
    p.setFillColor(C_ROSE);   p.circle(7 * mm,   8 * mm, 1.4 * mm, fill=1, stroke=0)
    p.setFillColor(C_ORANGE); p.circle(W - 7 * mm, 8 * mm, 1.4 * mm, fill=1, stroke=0)

    p.showPage()
    p.save()
    buffer.seek(0)


# ── DJANGO WRAPPER ────────────────────────────────────────────────────────────
def generate_juin_commission_badge(application):
    """Génère le badge PDF et le stocke via default_storage. Retourne l'URL."""
    try:
        from django.core.files.storage import default_storage
        from django.conf import settings

        edition        = application.commission.edition
        edition_number = getattr(edition, 'edition_number', 20)

        base_dir    = str(getattr(settings, 'BASE_DIR', ''))
        partner_dir = os.path.join(base_dir, 'static', 'images', 'partners')
        partner_logos = {
            'uy1':        os.path.join(partner_dir, 'uy1.png'),
            'enspy':      os.path.join(partner_dir, 'enspy.png'),
            'saint-jean': os.path.join(partner_dir, 'saint-jean.png'),
            'supptic':    os.path.join(partner_dir, 'supptic.png'),
        }
        comsas_logo = os.path.join(base_dir, 'static', 'images', 'comsas.png')

        buffer = BytesIO()
        build_badge(
            buffer             = buffer,
            nom_prenom         = application.nom_prenom,
            commission_code    = application.commission.code,
            commission_name    = application.commission.name,
            role               = application.get_commission_role_display(),
            etablissement      = application.get_etablissement_display(),
            niveau             = application.niveau,
            edition_number     = edition_number,
            photo_path         = application.photo.path if application.photo else None,
            partner_logo_paths = partner_logos,
            comsas_logo_path   = comsas_logo,
        )

        path = f'juin/badges/juin_badge_{application.pk}.pdf'
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, buffer)
        return default_storage.url(path)

    except Exception as e:
        import traceback
        print(f"[JUIN Badge] Erreur : {e}")
        traceback.print_exc()
        return None


def get_juin_badge_path(application):
    try:
        from django.core.files.storage import default_storage
        path = f'juin/badges/juin_badge_{application.pk}.pdf'
        return default_storage.path(path) if default_storage.exists(path) else None
    except Exception:
        return None


# ── DEMO STANDALONE ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    LOGO_DIR = "/home/claude/partner_logos"
    partner_logos = {
        'uy1':        os.path.join(LOGO_DIR, 'uy1.png'),
        'enspy':      os.path.join(LOGO_DIR, 'enspy.png'),
        'saint-jean': os.path.join(LOGO_DIR, 'saint-jean.png'),
        'supptic':    os.path.join(LOGO_DIR, 'supptic.png'),
    }
    # Pour la démo on crée un logo COMSAS placeholder
    comsas_demo = os.path.join(LOGO_DIR, 'comsas_demo.png')
    if not os.path.exists(comsas_demo):
        from PIL import ImageDraw, ImageFont
        sz = 200
        img = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
        bg = Image.new('RGB', (sz, sz), (233, 30, 99))
        mask = Image.new('L', (sz, sz), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, sz, sz), fill=255)
        img.paste(bg, (0, 0), mask)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
            bb = draw.textbbox((0, 0), "CS", font=font)
            draw.text(((sz-(bb[2]-bb[0]))//2, (sz-(bb[3]-bb[1]))//2),
                      "CS", fill=(255, 255, 255, 255), font=font)
        except Exception:
            pass
        img.save(comsas_demo)

    photo = "/mnt/user-data/uploads/1773520502729_image.png"

    cases = [
        ("NEUSSI NJIETCHEU Patrice", "CELLCOM-JUIN", "Communication & Marketing",
         "Membre", "UY1 — Dépt. Informatique (COM.S.AS)", "M1",
         photo, "juin_badge_patrice.pdf"),

        ("MFENJOU ANAS CHERIF", "PI-JUIN", "Partenariats & Sponsors",
         "Président du Comité", "UY1 — Fac. des Sciences", "L3",
         None, "juin_badge_president.pdf"),

        ("ISABELLE NISHIMWE", "CA-JUIN", "Commission Administrative",
         "Présidente Adjointe", "SUP'PTIC", "L3",
         None, "juin_badge_isabelle.pdf"),

        ("CHAMENI LEUDJIEU STIVE", "PROTO-JUIN", "Projets & Expositions",
         "Chef de Commission", "ENSPY", "M1",
         None, "juin_badge_stive.pdf"),
    ]

    for nom, code, cname, role, etab, niv, ph, fname in cases:
        buf = BytesIO()
        build_badge(buf, nom, code, cname, role, etab, niv,
                    edition_number=20, photo_path=ph,
                    partner_logo_paths=partner_logos,
                    comsas_logo_path=comsas_demo)
        out = f"/mnt/user-data/outputs/{fname}"
        with open(out, 'wb') as f:
            f.write(buf.getvalue())
        print(f"[✓] {fname}")