from fpdf import FPDF
from datetime import date

GLORY_BOTH_NOW_PATTERNS = [
    "Glory to the Father and to the Son and to the Holy Spirit.",
    "Both now and ever, and unto the ages of ages. Amen. ",
]


def oldToneChecker(oldTone, newTone, pdf):
    if oldTone != newTone:
        oldTone = newTone
        tone_text = f"Tone {newTone}. "
        pdf.set_text_color(255, 0, 0)
        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=tone_text)
        pdf.set_text_color(0, 0, 0)
    return oldTone


def write_glory_both_now(pdf, data, section_prefix, oldTone):
    """
    Writes the Glory/Both-now doxology for one section (stichera,
    aposticha, or apolytikion), using the same Tone (bold red) / official
    phrase (bold italic) / hymn text (regular) paragraph structure as the
    rest of the document. Handles both the combined case (one shared hymn
    serves both Glory and Both now) and the separate case (each has its
    own hymn), since extract_sections.split_glory_both_now already tells
    us which one applies via "<prefix>_combined_status".
    """
    # Not every section has a Glory/Both-now doxology every week (e.g. an
    # Apolytikion section can be just the one hymn, nothing after it) --
    # extract_sections only sets "<prefix>_glory" and "_combined_status" at
    # all when split_doxology actually found one. No entry means nothing
    # to write here, so skip rather than assuming the key exists.
    if not data['sections'][f'{section_prefix}_glory']:
        return oldTone

    combined_status = data['sections'][f'{section_prefix}_combined_status']

    if combined_status:
        combined = data['sections'][f'{section_prefix}_glory'][0]
        oldTone = oldToneChecker(oldTone, combined['tone'], pdf)

        phrase = GLORY_BOTH_NOW_PATTERNS[0] + " " + GLORY_BOTH_NOW_PATTERNS[1] + " "
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(style="BI", size=12)
        pdf.write(h=6, text=phrase)

        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=combined['combined_text'])

        print(phrase + combined['combined_text'])
    else:
        glory = data['sections'][f'{section_prefix}_glory'][0]
        oldTone = oldToneChecker(oldTone, glory['tone'], pdf)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font(style="BI", size=12)
        pdf.write(h=6, text=GLORY_BOTH_NOW_PATTERNS[0] + " ")

        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=glory['combined_text'])

        print(GLORY_BOTH_NOW_PATTERNS[0] + " " + glory['combined_text'])

        pdf.ln()
        pdf.ln(4)

        both_now = data['sections'][f'{section_prefix}_both_now'][0]
        oldTone = oldToneChecker(oldTone, both_now['tone'], pdf)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font(style="BI", size=12)
        pdf.write(h=6, text=GLORY_BOTH_NOW_PATTERNS[1] + " ")

        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=both_now['combined_text'])

        print(GLORY_BOTH_NOW_PATTERNS[1] + " " + both_now['combined_text'])

    pdf.ln()
    pdf.ln(4)
    return oldTone


STICHERA_VERSE_PATTERNS = [
    "If You, O Lord, should mark iniquities, O Lord, who shall stand? For with You there is forgiveness. ",
    "Because of Your Name have I waited for You, O Lord; my soul has waited upon Your word, my soul has hoped in the Lord. ",
    "From the morning watch until night, from the morning watch let Israel trust in the Lord. ",
    "For with the Lord there is mercy and with Him is abundant redemption, and He will deliver Israel from all his iniquities. ",
    "Praise the Lord, all you nations; praise Him, all you peoples. ",
    "For His mercy is great towards us, and the truth of the Lord endures forever. ",
]


def build_pdf(data: dict, output_path: str = "output.pdf") -> str:
    """
    Builds the formatted Vespers bulletin PDF from an already-extracted
    `data` dict (see extract_sections.parse_document) and writes it to
    output_path. Returns output_path so callers can chain it straight
    into e.g. send_email(attachment_path=...).
    """
    pdf = FPDF()

    pdf.add_page()
    pdf.add_font("Times New Roman", "", "TimesNewRoman.ttf")
    pdf.add_font("Times New Roman", "B", "TimesNewRomanBold.ttf")
    pdf.add_font("Times New Roman", "I", "TimesNewRomanItalic.ttf")
    pdf.add_font("Times New Roman", "BI", "TimesNewRomanBoldItalic.ttf")
    pdf.set_font("Times New Roman", size=12)

    # Header: Church Name
    header_text = "Georgetown Orthodox Christian Fellowship"
    print(header_text)
    pdf.multi_cell(w=0, h=6, text=header_text, align='C', new_x="LMARGIN", new_y="NEXT")

    # Date
    date_text = "Vespers: " + date.today().strftime("%A, %B %d, %Y")
    print(date_text)
    pdf.multi_cell(w=0, h=6, text=date_text, align='C', new_x="LMARGIN", new_y="NEXT")

    # Memory of Saint (In Red)
    pdf.set_text_color(255, 0, 0)
    print(data['metadata']['memory'])
    pdf.multi_cell(w=0, h=6, text=data['metadata']['memory'], align='C', new_x="LMARGIN", new_y="NEXT")

    # Instructions (In Italics & Black)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(style="I", size=12)
    instructions_text = "Feel free to read or chant during the service!"
    print(instructions_text)
    pdf.multi_cell(w=0, h=6, text=instructions_text, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Stichera Section and title
    pdf.set_font(style='U', size=12)
    pdf.set_text_color(255, 0, 0)
    print("Stichera")
    pdf.multi_cell(w=0, h=6, text="Stichera", align='L', new_x="LMARGIN", new_y="NEXT")
    oldTone = None

    # Loop through the stichera
    for i, verse_prayer in enumerate(data['sections']['stichera']):
        printed_paragraph = []

        if verse_prayer['tone'] != oldTone:
            oldTone = oldToneChecker(oldTone, verse_prayer['tone'], pdf)
            printed_paragraph.append(f"Tone {verse_prayer['tone']}. ")

        # Verses are Bold + Italic ("BI") -- distinct from the tone label
        # (Bold only, in red) and the prayer text that follows (regular).
        printed_paragraph.append(STICHERA_VERSE_PATTERNS[i])
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(style="BI", size=12)
        pdf.write(h=6, text=STICHERA_VERSE_PATTERNS[i])

        printed_paragraph.append(verse_prayer['prayer'])
        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=verse_prayer['prayer'])

        print("".join(printed_paragraph))

        pdf.ln()
        pdf.ln(4)

    oldTone = write_glory_both_now(pdf, data, "stichera", oldTone)

    # Aposticha now
    pdf.set_text_color(255, 0, 0)
    pdf.set_font(style='U', size=12)
    pdf.multi_cell(w=0, h=6, text="Aposticha", align='L', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(style="", size=12)
    pdf.write(h=6, text=f"Tone {data['sections']['aposticha'][0]['tone']} ")
    pdf.set_text_color(0, 0, 0)
    pdf.write(h=6, text=data['sections']['aposticha'][0]['prayer'])
    pdf.ln()
    pdf.ln(4)

    for i, verse_prayer in enumerate(data['sections']['aposticha'][1:]):
        oldTone = oldToneChecker(oldTone, verse_prayer['tone'], pdf)  # check tone change and print if necessary
        pdf.set_font(style="BI", size=12)
        pdf.write(h=6, text=verse_prayer['verse'])

        pdf.set_font(style="", size=12)
        pdf.write(h=6, text=verse_prayer['prayer'])

        pdf.ln()
        pdf.ln(4)

    oldTone = write_glory_both_now(pdf, data, "aposticha", oldTone)

    # Apolytikion now
    pdf.ln()
    pdf.ln(4)
    pdf.set_text_color(255, 0, 0)
    pdf.set_font(style='U', size=12)
    pdf.multi_cell(w=0, h=6, text="Apolytikion", align='L', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(style="", size=12)
    pdf.write(h=6, text=f"Tone {data['sections']['apolytikion'][0]['tone']} ")
    pdf.set_text_color(0, 0, 0)
    pdf.write(h=6, text=data['sections']['apolytikion'][0]['text'])
    pdf.ln()
    pdf.ln(4)

    oldTone = write_glory_both_now(pdf, data, "apolytikion", oldTone)

    # Troparion for Mary of Egypt
    pdf.ln()
    pdf.ln(4)
    pdf.set_text_color(255, 0, 0)
    pdf.set_font(style='U', size=12)
    pdf.write(h=6, text="Troparion for Mary of Egypt ")
    pdf.set_font(style="", size=12)
    pdf.write(h=6, text="Tone 8 ")
    pdf.set_text_color(0, 0, 0)
    pdf.write(h=6, text="In you the image was preserved with exactness, O Mother; "
              "for taking up your cross, you did follow Christ, and by your de"
              "eds you did teach us to overlook the flesh, for it passes away, "
              "but to attend to the soul since it is immortal. Wherefore, O righteous "
              "Mary, your spirit rejoices with the Angels.")

    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    from extract_sections import parse_document

    build_pdf(parse_document("For_vespers_variable.pdf"))
