# Menu translation toolkit

This folder is how `assets/menu-ru.pdf` (the Russian version of the full
restaurant menu) was built, and it's set up so the same process can be
repeated for the remaining site languages: German (de), French (fr),
Polish (pl), and Hebrew (he).

## What's already done

The hard part — transcribing the entire menu from `assets/menu.pdf` (a
23-page scanned PDF with **no text layer**, so nothing was copy-pasteable)
— is finished. `menu_ru_data.py` contains every dish name, section
header, description, price, and EU allergen code from the whole menu,
already split into English + Russian pairs. For a new language, you're
translating from the English already sitting in that file, not
re-reading the scanned PDF from scratch.

`menu_pages/` contains all 23 pages of `assets/menu.pdf` pre-rendered as
PNGs (`page01.png` ... `page23.png`) — needed for the "photo gallery"
pages the render script reuses as-is (see below).

## How the menu is structured

The original scanned menu alternates between **text-listing pages**
(bilingual EN/EL, dish names + prices + allergen codes) and **photo
gallery pages** (just food photos with English captions, no
translatable text of their own — they visually repeat dishes already
named on the adjacent text page). Only 13 of the 23 pages are actual
text content; the other 10 are pure photo pages. `menu_ru_data.py`'s
`PAGES` list holds the 12 translatable content blocks (13 source pages,
minus the allergen table which is handled separately) in order.

The rendered PDF, for each language, is:

1. Cover page (opening hours, phone, allergy notice — EN + target language)
2. For each of the 12 content sections: the translated text-listing page,
   then (if that section had one) its matching photo-gallery page,
   reused unchanged from `menu_pages/` with a small bilingual banner
   added ("Dish names & prices are on the previous page") since the
   photos' own captions stay English-only — captioning each individual
   photo in the target language was tried and abandoned; see "Why not
   per-photo captions" below.
3. Allergen key page (all 14 EU allergen categories, EN + target language)

## How to add a new language

1. **Copy the data file**: `cp menu_ru_data.py menu_de_data.py` (or fr/pl/he).
   Go through every string in the new file and replace the Russian text
   with your target language, keeping the English side untouched.
   Leave prices and allergen codes (e.g. `"2,4,6"`) exactly as-is —
   they're not translated, just copied through.
2. **Copy the render script**: `cp render_menu_ru.py render_menu_de.py`.
   Change:
   - The `from menu_ru_data import ...` line to import from your new
     `menu_XX_data.py` instead.
   - The output filename (`out = os.path.join(REPO_DIR, "assets", "menu-ru.pdf")`)
     to `menu-de.pdf` (etc).
   - The banner text on the photo pages (`"Dish names & prices are on
     the previous page"` / its translation) to your target language.
   - **German/French/Polish**: these are Latin-script, so `Poppins-*.ttf`
     (already in `fonts/`) has the glyphs — you can swap the `RU()` font
     helper to use `F("Poppins-Regular.ttf", size)` etc. instead of
     `NON_LATIN_FONT` if you want it fully on-brand, though Arial Unicode
     (currently used for the RU parts) works fine for these languages too
     and needs no change.
   - **Hebrew**: needs real right-to-left handling that this script does
     **not** currently have (Russian, German, French, Polish are all
     left-to-right, so the existing centered-text layout "just works" for
     them). You'll need to: reverse Hebrew strings for correct glyph
     order (the site's own JS does this — see `rtl-text` handling in
     `../../index.html`), and decide whether prices/allergen codes stay
     LTR-embedded within an RTL line. Test carefully with real Hebrew
     text before trusting the output.
3. **Run it**: `python3 render_menu_XX.py` from inside this folder. It
   writes straight to `../../assets/menu-XX.pdf`.
4. **Check it**: open the PDF and look through all 24 pages. Specifically
   check for: text overflowing its column, any leftover Cyrillic-looking
   placeholder text you forgot to translate, and that every price/code
   still matches the English column.
5. **Wire it into the site**: in `../../index.html`, find
   `applyLanguage()` in the `<script>` and add a line to the
   `menuPdfByLang` map, e.g.:
   ```js
   var menuPdfByLang = { ru: 'assets/menu-ru.pdf', de: 'assets/menu-de.pdf' };
   ```
   Languages not in this map fall back to the original `assets/menu.pdf`
   (EN/EL) automatically — that's intentional, not a bug, until each
   language gets its own translated PDF.
6. **Verify the JS still parses**: this site has a history of one bad
   character silently breaking ALL translations sitewide (an unescaped
   apostrophe once did this). Before pushing, extract the `<script>`
   block and run it through Node/a browser to confirm it's still valid
   JavaScript. Don't skip this step.

## Design notes (keep these consistent across languages)

- Page size: every page must render at the **same pixel width**
  (`W * 2` where `W` is defined near the top of the script) at the same
  PDF `resolution=200.0`. Mixing resolutions makes some pages look
  physically smaller than others in PDF viewers — this happened once
  already (photo pages were left at native scan resolution while text
  pages were upscaled) and was a real, confusing bug. If you change
  anything about page sizing, sanity-check with:
  ```python
  import fitz
  doc = fitz.open("assets/menu-XX.pdf")
  print(set((p.rect.width) for p in doc))  # should be ONE value
  ```
- Brand colors/fonts come from the same palette as the website
  (`RED #c8102e`, `RED_DARK #8f0c20`, `Poppins` for English, `Shojumaru`
  for the restaurant name on the cover) — keep new languages visually
  identical, just with translated text.
- Text pages: English on top (bold, black), translation below it
  (smaller, red), matching the original menu's own EN/EL pairing style.

## Why not per-photo captions?

An earlier attempt tried covering each photo's original English caption
with a freshly rendered EN + [language] caption, detected via pixel
analysis of the scanned image (finding the gap between the food photo
and its caption text). This got most rows working but kept surfacing
new edge cases — two-line captions, rows where the photo's own shadows
confused the detector, inconsistent gaps between photo and caption
across different pages — each fix uncovered a new failure elsewhere.
Given the time cost of chasing every edge case across 39 photo rows, we
settled on the simpler, reliably-correct banner approach described
above instead. If you want to revisit per-photo captions, the
now-unused row-detection code is a reasonable starting point but expect
to spend real time on it — search git history for `find_caption_top` if
you want that starting point back.
