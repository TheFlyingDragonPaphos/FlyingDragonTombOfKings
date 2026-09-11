# -*- coding: utf-8 -*-
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from menu_he_data import COVER, PAGES, ALLERGENS
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

RED = (200, 16, 46)
RED_DARK = (143, 12, 32)
INK = (32, 21, 18)
MUTED = (110, 95, 87)
CREAM = (253, 250, 246)
PAPER = (255, 255, 255)

FONT_DIR = os.path.join(SCRIPT_DIR, "fonts") + "/"
NON_LATIN_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

def F(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

def RU(size, bold=False):
    # Kept this name for continuity with render_menu_ru.py -- this is the
    # "non-Latin-script font" helper, used here for Hebrew.
    return ImageFont.truetype(NON_LATIN_FONT, size)

def HE(text):
    # PIL draws strictly left-to-right regardless of the string's natural
    # reading direction. get_display() reorders Hebrew into the correct
    # VISUAL order for that LTR drawing, while correctly leaving embedded
    # LTR runs (numbers, allergen codes) in place. Always call this right
    # before handing Hebrew text to d.text() -- never draw raw Hebrew.
    return get_display(text)

W, H = 1240, 1754  # ~A4 at 150dpi baseline; we export at 2x for print
MARGIN = 90

def wrap_text(d, text, font, max_width):
    # Operates on LOGICAL-order text. Word-advance widths are order
    # independent (Hebrew has no cursive joining), so measuring the
    # un-reordered string is accurate for wrapping; bidi reordering is
    # applied per finished line at draw time via HE().
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def new_page():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    return img, d

def render_cover(logo_path):
    img, d = new_page()
    cx = W // 2
    f_info = F("Poppins-Medium.ttf", 20)
    f_hours = F("Poppins-Bold.ttf", 24)
    f_hours_he = RU(22)
    f_call = F("Poppins-Medium.ttf", 22)
    f_call_he = RU(20)
    f_phone = F("Poppins-Black.ttf", 40)
    f_name = F("Shojumaru-Regular.ttf", 46)
    f_sub = F("Poppins-Medium.ttf", 26)
    f_menu_he = RU(70)
    f_info_he = RU(18)

    y = 90
    for line in COVER["allergy_en"].split("\n"):
        w = d.textlength(line, font=f_info)
        d.text((cx - w/2, y), line, font=f_info, fill=RED)
        y += 28
    y += 8
    for line in COVER["allergy_he"].split("\n"):
        vis = HE(line)
        w = d.textlength(vis, font=f_info_he)
        d.text((cx - w/2, y), vis, font=f_info_he, fill=RED_DARK)
        y += 28

    y += 60
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((260, 260), Image.LANCZOS)
    img.paste(logo, (cx - logo.width//2, y), logo)
    y += logo.height + 40

    text = "The Flying Dragon"
    w = d.textlength(text, font=f_name)
    d.text((cx - w/2, y), text, font=f_name, fill=RED)
    y += 60
    text = "Asian Kitchen Restaurant"
    w = d.textlength(text, font=f_sub)
    d.text((cx - w/2, y), text, font=f_sub, fill=INK)
    y += 70

    for line in COVER["hours_en"].split("\n"):
        w = d.textlength(line, font=f_hours) if line.isupper() else d.textlength(line, font=f_call)
        f = f_hours if line.isupper() else f_call
        d.text((cx - w/2, y), line, font=f, fill=INK)
        y += 30
    y += 6
    for line in COVER["hours_he"].split("\n"):
        is_label = line.strip().startswith("שעות")
        f = f_hours_he if is_label else f_call_he
        vis = HE(line)
        w = d.textlength(vis, font=f)
        d.text((cx - w/2, y), vis, font=f, fill=MUTED)
        y += 30

    y += 40
    w = d.textlength(COVER["call_en"], font=f_call)
    d.text((cx - w/2, y), COVER["call_en"], font=f_call, fill=INK)
    y += 30
    vis = HE(COVER["call_he"])
    w = d.textlength(vis, font=f_call_he)
    d.text((cx - w/2, y), vis, font=f_call_he, fill=MUTED)
    y += 40
    w = d.textlength(COVER["phone"], font=f_phone)
    d.text((cx - w/2, y), COVER["phone"], font=f_phone, fill=RED)
    y += 90

    vis = HE(COVER["menu_word_he"])
    w = d.textlength(vis, font=f_menu_he)
    d.text((cx - w/2, y), vis, font=f_menu_he, fill=RED)
    y += 100
    vis = HE(COVER["discount_he"])
    w = d.textlength(vis, font=f_call_he)
    d.text((cx - w/2, y), vis, font=f_call_he, fill=MUTED)

    return img

def render_content_page(blocks, page_label):
    img, d = new_page()
    x = MARGIN
    right = W - MARGIN
    y = 70
    max_w = W - 2*MARGIN

    # Line heights/gaps here are tuned so the worst-case page (25 blocks,
    # e.g. Appetisers/Pork-Chicken-Duck) fits within the page with margin
    # to spare -- kept identical to the (fixed) render_menu_ru.py numbers.
    # A looser version of these constants silently dropped the last 1-2
    # items on most pages (the `if y > H - 80: break` below cut them off
    # with no visible error). Do not loosen these without re-running the
    # per-page overflow check.
    f_h1 = F("Poppins-Black.ttf", 34)
    f_h1_he = RU(20)
    f_h2 = F("Poppins-Bold.ttf", 22)
    f_h2_he = RU(16)
    f_name = F("Poppins-Bold.ttf", 19)
    f_name_he = RU(16)
    f_desc = F("Poppins-Regular.ttf", 15)
    f_desc_he = RU(14)
    f_price = F("Poppins-Bold.ttf", 21)

    d.text((x, y), page_label, font=F("Poppins-Medium.ttf", 15), fill=(190, 178, 168))
    y += 34

    def draw_he_right(text, font, fill, yy):
        vis = HE(text)
        w = d.textlength(vis, font=font)
        d.text((right - w, yy), vis, font=font, fill=fill)

    for block in blocks:
        kind = block[0]
        if kind == "header":
            _, en, he = block
            d.text((x, y), en, font=f_h1, fill=RED)
            y += 40
            draw_he_right(he, f_h1_he, RED_DARK, y)
            y += 34
            d.line([(x, y), (right, y)], fill=(224, 214, 204), width=2)
            y += 14
        elif kind == "subheader":
            _, en, he, extra = block
            for line in wrap_text(d, en, f_h2, max_w):
                d.text((x, y), line, font=f_h2, fill=RED)
                y += 28
            for line in wrap_text(d, he, f_h2_he, max_w):
                draw_he_right(line, f_h2_he, RED_DARK, y)
                y += 22
            if extra:
                for line in wrap_text(d, extra, f_desc, max_w):
                    d.text((x, y), line, font=f_desc, fill=MUTED)
                    y += 20
            y += 6
        elif kind == "item":
            _, name_en, name_he, desc_en, desc_he, codes, price = block
            label = name_en
            if codes:
                label += f"  ({codes})"
            avail_w = max_w - 130
            lines = wrap_text(d, label, f_name, avail_w)
            d.text((x, y), lines[0], font=f_name, fill=INK)
            if price:
                pw = d.textlength(price, font=f_price)
                d.text((right - pw, y), price, font=f_price, fill=RED_DARK)
            y += 23
            for extra_line in lines[1:]:
                d.text((x, y), extra_line, font=f_name, fill=INK)
                y += 23
            for line in wrap_text(d, name_he, f_name_he, max_w):
                draw_he_right(line, f_name_he, (70, 60, 55), y)
                y += 21
            if desc_en:
                for line in wrap_text(d, desc_en, f_desc, max_w):
                    d.text((x, y), line, font=f_desc, fill=MUTED)
                    y += 17
            if desc_he:
                for line in wrap_text(d, desc_he, f_desc_he, max_w):
                    draw_he_right(line, f_desc_he, (150, 120, 115), y)
                    y += 17
            y += 6
        elif kind == "note":
            pass

        if y > H - 80:
            break

    return img

def render_allergen_page():
    img, d = new_page()
    x = MARGIN
    right = W - MARGIN
    y = 70
    f_h1 = F("Poppins-Black.ttf", 32)
    f_h1_he = RU(28)
    d.text((x, y), "Allergens |", font=f_h1, fill=RED)
    en_w = d.textlength("Allergens | ", font=f_h1)
    vis = HE("אלרגנים")
    d.text((x + en_w, y + 4), vis, font=f_h1_he, fill=RED)
    y += 60

    card = [x, y, right, y + 680]
    d.rounded_rectangle(card, radius=16, fill=RED)
    ty = y + 30
    f_num = F("Poppins-Black.ttf", 16)
    f_txt = F("Poppins-Medium.ttf", 16)
    f_txt_he = RU(15)
    col_w = (card[2] - card[0] - 60) // 2
    col1_x = x + 30
    col2_x = x + 30 + col_w + 30
    cy1 = ty
    cy2 = ty
    for i, (num, en, he) in enumerate(ALLERGENS):
        col_x = col1_x if i % 2 == 0 else col2_x
        cy = cy1 if i % 2 == 0 else cy2
        d.rounded_rectangle([col_x, cy, col_x+24, cy+24], radius=5, fill=(255,255,255))
        nw = d.textlength(num, font=f_num)
        d.text((col_x + 12 - nw/2, cy+3), num, font=f_num, fill=RED_DARK)
        col_right = col_x + col_w
        lines_en = wrap_text(d, en, f_txt, col_w - 36)
        lines_he = wrap_text(d, he, f_txt_he, col_w - 36)
        ly = cy
        for line in lines_en:
            d.text((col_x + 34, ly), line, font=f_txt, fill=(255,255,255))
            ly += 20
        for line in lines_he:
            vis_l = HE(line)
            lw = d.textlength(vis_l, font=f_txt_he)
            d.text((col_right - lw, ly), vis_l, font=f_txt_he, fill=(255, 220, 220))
            ly += 20
        ly += 14
        if i % 2 == 0:
            cy1 = ly
        else:
            cy2 = ly

    return img

PHOTO_DIR = os.path.join(SCRIPT_DIR, "menu_pages") + "/"

def load_photo_page(num):
    photo = Image.open(f"{PHOTO_DIR}page{num:02d}.png").convert("RGB")
    target_w = W * 2
    scale = target_w / photo.width
    photo = photo.resize((target_w, int(photo.height * scale)), Image.LANCZOS)

    banner_h = 140
    canvas = Image.new("RGB", (target_w, photo.height + banner_h), CREAM)
    d = ImageDraw.Draw(canvas)
    f_en = F("Poppins-Bold.ttf", 40)
    f_he = RU(36)
    en = "Dish names & prices are on the previous page"
    he = "שמות המנות והמחירים מופיעים בעמוד הקודם"
    ew = d.textlength(en, font=f_en)
    d.text((target_w/2 - ew/2, 34), en, font=f_en, fill=RED)
    vis = HE(he)
    rw = d.textlength(vis, font=f_he)
    d.text((target_w/2 - rw/2, 84), vis, font=f_he, fill=RED_DARK)
    canvas.paste(photo, (0, banner_h))
    return canvas

def load_dessert_photos():
    page23 = Image.open(f"{PHOTO_DIR}page23.png").convert("RGB")
    return page23.crop((0, 355, page23.width, 825))

REPO_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # tools/menu-translation -> repo root

def main():
    logo_path = os.path.join(REPO_DIR, "assets", "logo.png")
    pages = [render_cover(logo_path)]
    labels = ["Soups & Salads", "Appetisers", "Thai Dishes", "Bao Buns & Szechuan",
              "Pork, Chicken, Duck", "Seafood & Vegetarian", "Rice & Noodles",
              "Vegan Menu", "Vegan Mains", "Sushi Menu", "Set Menus & Extras", "Desserts"]
    photo_after = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, None, None]

    for blocks, label, photo_num in zip(PAGES, labels, photo_after):
        content_page = render_content_page(blocks, label)
        if label == "Desserts":
            dessert_photos = load_dessert_photos()
            target_w = W - 2*MARGIN
            scale = target_w / dessert_photos.width
            dessert_photos = dessert_photos.resize(
                (target_w, int(dessert_photos.height * scale)), Image.LANCZOS)
            content_page.paste(dessert_photos, (MARGIN, H - dessert_photos.height - 60))
        pages.append(content_page)
        if photo_num:
            pages.append(load_photo_page(photo_num))
    pages.append(render_allergen_page())

    out = os.path.join(REPO_DIR, "assets", "menu-he.pdf")
    target_w = W * 2
    hi_pages = []
    for p in pages:
        if p.width != target_w:
            scale = target_w / p.width
            p = p.resize((target_w, int(p.height * scale)), Image.LANCZOS)
        hi_pages.append(p)
    hi_pages[0].save(out, "PDF", resolution=200.0, save_all=True, append_images=hi_pages[1:])
    print("saved", out, "pages:", len(pages))

if __name__ == "__main__":
    main()
