import re

import pdfplumber


def extract_text(filename: str) -> str:
    """Pull raw text out of every page of the PDF and join it into one string."""
    with pdfplumber.open(filename) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return fix_drop_caps(text)


# Some documents render a decorative oversized first letter of each hymn
# paragraph as its own separate text block, so pdfplumber reads it as a
# line containing just that one letter, followed by a line starting with
# the rest of the word (e.g. "A\ns they heard" instead of "As they heard").
# These are the letters that legitimately ARE complete one-letter English
# words on their own ("O Lord", "I lift my eyes") — for these, the
# line-break is coincidental (the drop-cap decorated a word that just
# happens to be one letter long) and the space must stay. Every other
# isolated capital letter gets glued back onto the word that follows it.
STANDALONE_DROP_CAP_WORDS = {"O", "I"}


def fix_drop_caps(text: str) -> str:
    """
    Repairs the drop-cap artifact described above. (?m) makes ^ match the
    start of every line, not just the start of the whole string, so this
    finds every line that is exactly one capital letter followed
    immediately by a newline, where the NEXT line starts with a lowercase
    letter (confirming it's a word continuation, not a new sentence).
    """
    def merge(match: re.Match) -> str:
        letter = match.group(1)
        if letter in STANDALONE_DROP_CAP_WORDS:
            return match.group(0)  # leave the letter, newline, and space alone
        return letter  # drop the newline so it glues onto the next word

    return re.sub(r"(?m)^([A-Z])\n(?=[a-z])", merge, text)


def _find_local_repeat(letters: str, seed_len: int = 25, max_gap: int = 450) -> tuple[int, int, int] | None:
    """
    Scans a letters-only string for a stretch of at least `seed_len`
    characters that reappears again within `max_gap` characters. Returns
    (earlier_start, later_start, match_length), or None if nothing repeats.

    Works by remembering, for every `seed_len`-character window, the first
    position it was seen at. The first time a window repeats, that's our
    match start; from there we just keep extending character-by-character
    for as long as both copies keep agreeing.
    """
    seen: dict[str, int] = {}
    n = len(letters)
    for i in range(n - seed_len + 1):
        window = letters[i:i + seed_len]
        earlier = seen.get(window)
        if earlier is not None and i - earlier <= max_gap:
            length = seed_len
            while i + length < n and letters[earlier + length] == letters[i + length]:
                length += 1
            return earlier, i, length
        seen.setdefault(window, i)
    return None


def remove_garbled_duplicates(text: str) -> str:
    """
    Some source documents render a stretch of hymn text twice in a row:
    once garbled (words run together with no spaces — looks like an
    overlapping/duplicate text layer in the PDF) and then immediately
    again with normal spacing. This finds a repeated stretch of at least
    25 letters (ignoring spaces, punctuation, and case, since the garbled
    copy is missing spaces the clean one has) and deletes everything from
    the start of the earlier, garbled copy up to the start of the later,
    properly-spaced copy — keeping the clean version.

    IMPORTANT: some verses genuinely repeat a phrase on purpose (e.g.
    "From the morning watch until night; from the morning watch until
    night, let Israel hope in the Lord." — that repetition is real Psalm
    text, not a rendering glitch). The two cases are told apart by word
    count: the garbled copy has noticeably FEWER space-separated words
    than the clean copy for the same underlying letters (because it's
    missing spaces); an intentional repeat has the same word count both
    times. Only remove the match if that gap is present.
    """
    # Build a letters-only, lowercase view of the text, but remember which
    # original character index each of those letters came from, so a match
    # found in the stripped-down version can be mapped back to real cut
    # points in the actual text.
    positions = []
    letters_only = []
    for i, ch in enumerate(text):
        if ch.isalpha():
            letters_only.append(ch.lower())
            positions.append(i)
    letters = "".join(letters_only)

    match = _find_local_repeat(letters)
    if match is None:
        return text

    earlier, later, length = match
    cut_start = positions[earlier]
    cut_end = positions[later]

    # length is measured in normalized letters — positions[x + length - 1] is
    # the last matched letter's real index for each copy, so +1 gives the
    # real end index of that copy's span in the original text.
    earlier_span_end = positions[earlier + length - 1] + 1
    later_span_end = positions[later + length - 1] + 1
    earlier_word_count = len(text[cut_start:earlier_span_end].split())
    later_word_count = len(text[cut_end:later_span_end].split())

    if later_word_count <= earlier_word_count:
        # No sign the earlier copy is missing spaces
        # intentional repeat and leave the text alone.
        return text
    return text[:cut_start] + text[cut_end:]


def strip_leading_title_and_tone(text: str) -> str:
    """
    Removes a leading title + Mode/Tone marker (e.g. "For the
    Myrrhbearers.\nMode pl. 2.\n") from the very start of a hymn's text,
    leaving just the hymn prose itself. Needed for the Glory/Both-now
    shared text specifically -- unlike the per-tone chunks split_by_tone
    produces (where that prefix is expected/kept), this text comes from
    split_doxology cutting the section at "Glory.", so nothing has
    stripped its own leading label yet.

    ".*?" is non-greedy, so it matches as LITTLE text as possible before
    the Mode/Tone marker -- meaning this works whether there's a title
    line first ("For the Myrrhbearers.\nMode pl. 2.") or the marker is
    the very first thing ("Mode 2.\nWhen he took down...").
    """
    match = re.match(r".*?(?:Grave Mode\.|(?:Mode|Tone)\s*(?:pl\.\s*\d+|\d+)\.?)\s*", text, re.IGNORECASE | re.DOTALL)
    if match:
        return text[match.end():].strip()
    return text.strip()


# Matches a trailing source citation ("From Pentecostarion - - -") and/or
# category label ("For the Apostles.") at the very end of a hymn's text.
# Both describe whatever hymn comes NEXT in the document, but since
# split_by_tone draws each chunk's boundary right at the following "Mode
# N." marker (not before these lines), they end up glued onto the tail of
# the CURRENT chunk instead. Both pieces are optional so this safely
# no-ops (just trims trailing whitespace) when neither is present.
TRAILING_LABEL_PATTERN = re.compile(
    r"\s*(?:From \w+ - - -\s*)?(?:For the \w+\.\s*)?$",
    re.IGNORECASE,
)


def strip_trailing_labels(text: str) -> str:
    return TRAILING_LABEL_PATTERN.sub("", text).strip()


def strip_citation_brackets(text: str) -> str:
    """
    Removes translator/source citation tags like "[SAAS]" or "[SD]" from
    displayed text. Only call this AFTER any splitting logic that needed
    those brackets as a boundary marker (see _split_verse_from_rest) --
    stripping them earlier removes the only reliable signal that function
    has for some documents.
    """
    return re.sub(r"\s*\[[A-Z]+\]\s*", " ", text).strip()


def clean_doxology_text(text: str) -> str:
    """Full cleanup pipeline for Glory/Both-now shared hymn text."""
    return strip_leading_title_and_tone(strip_citation_brackets(strip_trailing_labels(text)))


def clean_prayer_text(text: str) -> str:
    """Full cleanup pipeline for a verse's prayer text."""
    return strip_citation_brackets(strip_trailing_labels(text))


# The Stichera always use the same 6 verses
STICHERA_VERSE_PATTERNS = [
    r"If You, O Lord, should mark (?:transgression|iniquities), O Lord, who (?:would|shall) stand\? "
    r"For (?:there is forgiveness with You|with You there is forgiveness)\.",

    r"Because of Your (?:law|Name)(?:, O Lord,)? (?:have I waited for You|I waited for You)[;,] "
    r"my soul (?:has waited|waited) (?:upon|for) Your word[.,]?\s*my soul (?:has hoped|hopes|hoped) in the Lord\.",

    r"From the morning watch until night[;,] from the morning watch(?: until night)?,? "
    r"let Israel (?:trust|hope) in the Lord\.",

    r"For (?:with )?the Lord there is mercy,? and with Him is abundant redemption[;,] "
    r"and He (?:shall|will) (?:redeem|deliver) Israel from all his (?:transgressions|iniquities)\.",

    r"Praise the Lord, all you (?:Gentiles|nations); praise Him, all you peoples\.",

    r"For His mercy (?:rules over us|is great towards us)[;,] and(?: the)? truth of the Lord endures forever\.",
]


def split_verse_prayer(tone_chunk_text: str) -> list[dict]:
    """
    Splits one tone's stichera text into {"verse": ..., "prayer": ...} pairs.
    Finds every known Psalm-129 verse pattern in the chunk, then treats
    everything between one verse and the next (or the end of the chunk) as
    that verse's hymn/prayer text.
    """
    # Collapse newlines to spaces first — the verse patterns are written as
    # if the text were one continuous line, but pdfplumber breaks lines
    # wherever the PDF happened to wrap, which can land mid-verse.
    cleaned = re.sub(r"\s+", " ", tone_chunk_text).strip()

    matches = []
    for pattern in STICHERA_VERSE_PATTERNS:
        m = re.search(pattern, cleaned, re.IGNORECASE)
        if m:
            matches.append(m)

    # Patterns aren't necessarily written/found in document order (we loop
    # over our own pattern list, not the text), so sort by where each one
    # actually landed in the chunk.
    matches.sort(key=lambda m: m.start())

    pairs = []
    for i, m in enumerate(matches):
        verse = m.group(0)
        # This verse's prayer runs from right after the verse to wherever
        # the NEXT verse starts, or to the end of the chunk if this is the
        # last verse found.
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        prayer = cleaned[m.end():end].strip()
        pairs.append({"verse": verse, "prayer": prayer})
    return pairs


def _split_verse_from_rest(segment: str) -> tuple[str, str]:
    """
    Given the text right after one "Verse:" label (up to the next "Verse:"
    or the end of the chunk), figures out where the psalm verse itself ends
    and the hymn/prayer text begins.

    Two signals, tried in order:
    1. A citation bracket like "[SAAS]" or "[SD]" — present in the fuller
       source documents, and it sits exactly at the verse/prayer boundary.
    2. If there's no bracket (plain bulletin-style documents don't have
       them), fall back to the last "." before the first "*" in the
       segment — hymn prayers use "*" as an internal pause mark, psalm
       verses don't, so the sentence-ending period just before the first
       "*" is a reasonable stand-in boundary.
    """
    bracket_match = re.search(r"\[[A-Z]+\]", segment)
    asterisk_pos = segment.find("*")

    if bracket_match and (asterisk_pos == -1 or bracket_match.start() < asterisk_pos):
        verse = segment[:bracket_match.start()].strip()
        prayer = segment[bracket_match.end():].strip()
        return verse, prayer

    if asterisk_pos != -1:
        period_pos = segment.rfind(".", 0, asterisk_pos)
        if period_pos != -1:
            verse = segment[:period_pos + 1].strip()
            prayer = segment[period_pos + 1:].strip()
            return verse, prayer

    # No bracket and no "*" found at all — can't tell where the verse ends,
    # so treat the whole thing as the verse with no separated prayer.
    return segment.strip(), ""


def split_aposticha_verses(tone_chunk_text: str) -> list[dict]:
    """
    Splits an aposticha tone's text using the literal "Verse:" label —
    unlike Stichera, Aposticha verses change week to week (different Psalm
    depending on the day), so there's no fixed wording to match against.
    The document itself marks each inserted verse with "Verse:", so we
    anchor on that instead.

    Any text before the first "Verse:" is the section's opening hymn,
    which isn't preceded by its own verse — returned with an empty
    "verse" field.
    """
    cleaned = re.sub(r"\s+", " ", tone_chunk_text).strip() # cleaned of whole chunk, not just the verse/prayer segments

    # Every place "Verse:" appears, in document order.
    verse_matches = list(re.finditer(r"Verse:\s*", cleaned, re.IGNORECASE))

    pairs = []

    # if there are no verses at all, the whole chunk is just one hymn/prayer with no verse.
    intro_end = verse_matches[0].start() if verse_matches else len(cleaned)
    # This intro text is captured straight from the start of the chunk,
    # which -- same as split_by_tone's chunks generally -- still has its
    # leading "<Title>.\nMode N." prefix attached (e.g. "Mode 2. For the
    # Cross."). Strip it here so it doesn't end up in the displayed prayer.
    intro_text = strip_leading_title_and_tone(cleaned[:intro_end])
    if intro_text:
        pairs.append({"verse": "", "prayer": intro_text})

    for i, m in enumerate(verse_matches):
        # Everything up to the NEXT "Verse:" (or end of chunk) belongs to
        # this verse — it still mixes the verse and its prayer together,
        # which _split_verse_from_rest then teases apart.
        segment_end = verse_matches[i + 1].start() if i + 1 < len(verse_matches) else len(cleaned) # check if this is the last verse, if so, the end of the segment is the end of the cleaned text
        segment = cleaned[m.end():segment_end]# segment is from the end of the current "Verse:" label to the start of the next "Verse:" label (or the end of the cleaned text if this is the last verse)
        verse, prayer = _split_verse_from_rest(segment)
        pairs.append({"verse": verse, "prayer": prayer})

    return pairs


def get_metadata(text: str) -> dict:
    """
    Pull the memory of which saint.
    """
    # No ^/$ here — this one is allowed to match "Memory of ..." wherever
    # it sits in the text, not just at a line boundary.
    memory_match = re.search(r"(Memory of .+)", text)

    return {
        "memory": memory_match.group(1).strip() if memory_match else "",
    }


def get_section(text: str, start_label: str, end_label: str | None) -> str:
    """
    Grab everything between two anchor regex patterns, e.g.
    start_label=r"Apolytikion\." end_label=r"Aposticha of the Feast\."
    Pass end_label=None to grab everything to the end of the text.
    """
    # Find where start_label first occurs. re.DOTALL makes "." (if the
    # pattern uses it) match newlines too — not needed for a simple literal
    # label, but harmless to leave on. re.IGNORECASE so "apolytikion" and
    # "Apolytikion" both match.
    start_match = re.search(start_label, text, re.IGNORECASE | re.DOTALL)
    if not start_match:
        return ""

    # .end() = the index right AFTER the matched label, so "tail" is
    # everything in the document following the label (the label itself
    # is not included in the result).
    tail = text[start_match.end():]

    if end_label is None:
        return tail.strip()

    # Search again, but only within "tail" (not the whole document) so an
    # end_label that appears earlier elsewhere in the doc can't cut things
    # short. .start() = where the end label BEGINS, so it's excluded too.
    end_match = re.search(end_label, tail, re.IGNORECASE | re.DOTALL)
    if end_match:
        tail = tail[:end_match.start()]
    return tail.strip()


def get_tone(section_text: str) -> str:
    """
    Find the Mode/Tone number within a section.
    Returns just the number/string.
    """
    # (?:Mode|Tone)      "Mode" OR "Tone" — the (?:...) means "group these
    #                    for the alternation, but don't capture it" (we
    #                    don't need to know which word was used).
    # \s*                optional whitespace ("Mode2." and "Mode 2." both work)
    # (pl\.\s*\d+|\d+)   THIS is the one real capture group — either
    #                    "pl. 4" style (plagal modes) or a plain number.
    #                    Whichever branch matches becomes group(1).
    # \.?                an optional trailing period
    grave_mode = re.compile(r"Grave Mode\.", re.IGNORECASE).search(section_text)
    if grave_mode:
        return "Grave"
    match = re.search(r"(?:Mode|Tone)\s*(?:pl\.\s*)?(\d+)\.?", section_text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def split_by_tone(section_text: str) -> list[str]:
    """
    Splits a section into one chunk per Mode/Tone marker found in it.
    If the section only has one tone, returns a single-item list (the
    whole section unchanged). If it has two or more (e.g. a saint's
    stichera in one tone, the feast's in another), returns one chunk per
    tone, each starting at its own "Mode N." / "Tone N" marker.
    """
    # Same pattern as get_tone, but no capture group needed here — we only
    # care about the position of each match, not the number itself.
    TONE_PATTERN = re.compile(r"(?:Mode|Tone)\s*(?:pl\.\s*\d+|\d+)\.?", re.IGNORECASE)

    # re.search stops at the first hit. re.finditer instead returns every
    matches = list(TONE_PATTERN.finditer(section_text))

    if len(matches) <= 1:
        return [section_text]

    chunks = []
    for i, match in enumerate(matches):
        # Each chunk starts where this tone marker starts...
        start = match.start()
        # ...and ends where the NEXT tone marker starts (or the end of the
        # section, if this is the last one).
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        chunks.append(section_text[start:end].strip())
    return chunks


def split_glory_both_now(section_text: str) -> dict:
    """
    Figure out whether "Glory." and "Both now." are combined (one shared
    hymn follows both markers) or separate (each has its own hymn text
    after it, elsewhere in the section).
    """
    # First check the COMBINED case: literally "Glory." then "Both now."
    # back to back (with only whitespace between). If this matches, there's
    # only one hymn after it and it serves both.
    combined_match = re.search(r"Glory\.\s*Both now\.", section_text, re.IGNORECASE)
    if combined_match:
        shared_text = section_text[combined_match.end():].strip()
        shared_tone = get_tone(shared_text)
        return {
            "combined": True,
            "glory_text": shared_text,
            "glory_tone": shared_tone,
            "both_now_text": shared_text,
            "both_now_tone": shared_tone,
        }

    # Not combined — the two markers are separate, and each is followed by
    # its own, different hymn text later in the section.
    glory_match = re.search(r"Glory\.", section_text, re.IGNORECASE)
    both_now_match = re.search(r"Both now\.", section_text, re.IGNORECASE)

    glory_text = ""
    both_now_text = ""

    if glory_match:
        # Glory's hymn text runs from right after "Glory." up to wherever
        # "Both now." starts (if it exists at all in this section).
        stop = both_now_match.start() if both_now_match else len(section_text)
        glory_text = section_text[glory_match.end():stop].strip()
        glory_tone = get_tone(glory_text)

    if both_now_match:
        # Both now's hymn text runs from right after "Both now." to the
        # end of the section.
        both_now_text = section_text[both_now_match.end():].strip()
        both_now_tone = get_tone(both_now_text)

    return {
        "combined": False,
        "glory_text": glory_text,
        "glory_tone": glory_tone if glory_match else "",
        "both_now_text": both_now_text,
        "both_now_tone": both_now_tone if both_now_match else "",
    }


def split_doxology(section_text: str) -> tuple[str, dict | None]:
    """
    Cuts a section's text at the first "Glory." into (hymns_before_it,
    doxology_info). This avoids guessing which tone-chunk the doxology
    ends up in — its position isn't fixed (it can land in the first,
    middle, or last tone-chunk depending on the document), so cutting on
    the raw text BEFORE splitting by tone sidesteps the problem entirely.
    Returns (section_text, None) unchanged if there's no Glory at all.
    """
    glory_match = re.search(r"Glory\.", section_text, re.IGNORECASE)
    if not glory_match:
        return section_text, None
    hymns_text = section_text[:glory_match.start()]
    doxology_text = section_text[glory_match.start():]
    return hymns_text, split_glory_both_now(doxology_text)


def _assemble_doxology(sections: dict, key: str, doxology: dict | None) -> None:
    """
    Stores a section's Glory/Both-now data under "<key>_glory",
    "<key>_both_now", and "<key>_combined_status". Shared by all three
    sections (stichera/aposticha/apolytikion) since split_doxology()
    always returns the same shape regardless of which section it came
    from -- only the dict key prefix differs.
    """
    if not doxology:
        return
    sections[f"{key}_glory"].append({
        "tone": doxology["glory_tone"],
        "combined_text": clean_doxology_text(doxology["glory_text"]),
    })
    sections[f"{key}_both_now"].append({
        "tone": doxology["both_now_tone"],
        "combined_text": clean_doxology_text(doxology["both_now_text"]),
    })
    sections[f"{key}_combined_status"] = doxology["combined"]


def _tone_chunks(hymns_text: str) -> list[str]:
    """
    Splits a section's hymn text into per-tone chunks, with the garbled-
    duplicate cleanup applied to each one. Shared by all three sections --
    the per-chunk (not whole-document) scoping matters here, see
    remove_garbled_duplicates()'s docstring for why.
    """
    return [remove_garbled_duplicates(chunk) for chunk in split_by_tone(hymns_text)]


def _process_verse_section(hymns_text: str, verse_split_fn) -> list[dict]:
    """
    Shared by Stichera and Aposticha, which have the identical shape once
    you swap out which verse-finding function does the splitting
    (split_verse_prayer for Stichera's fixed Psalm verses, or
    split_aposticha_verses for the "Verse:"-labeled kind). Apolytikion
    doesn't use this -- it has no verses, just tone + hymn text.
    """
    entries = []
    for chunk in _tone_chunks(hymns_text):
        tone = get_tone(chunk)
        for pair in verse_split_fn(chunk):
            entries.append({"tone": tone, "verse": pair["verse"], "prayer": clean_prayer_text(pair["prayer"])})
    return entries


def parse_document(filename: str) -> dict:
    """Tie it all together into one dict"""
    text = extract_text(filename)
    metadata = get_metadata(text)
    sections = {}
    for key in ("stichera", "aposticha", "apolytikion"):
        sections[f"{key}_glory"] = []
        sections[f"{key}_both_now"] = []

    if "Stichera" in text:
        section_text = get_section(text, r"Stichera", r"\(No Entrance\)")
        hymns_text, doxology = split_doxology(section_text)
        _assemble_doxology(sections, "stichera", doxology)
        sections["stichera"] = _process_verse_section(hymns_text, split_verse_prayer)

    if "Aposticha" in text:
        section_text = get_section(text, r"Aposticha(?:\s+of the Feast)?\.", r"Stand for the reading of prayers")
        hymns_text, doxology = split_doxology(section_text)
        _assemble_doxology(sections, "aposticha", doxology)
        sections["aposticha"] = _process_verse_section(hymns_text, split_aposticha_verses)

    if "Apolytikion" in text or "Apolytikia" in text:
        section_text = get_section(text, r"Apolytiki(?:on|a)\.", r"\(The .ektenia. litany has been omitted\.\)")
        hymns_text, doxology = split_doxology(section_text)
        _assemble_doxology(sections, "apolytikion", doxology)
        sections["apolytikion"] = [
            {"tone": get_tone(chunk), "text": clean_doxology_text(chunk)}
            for chunk in _tone_chunks(hymns_text)
        ]

    return {
        "metadata": metadata,
        "sections": sections,
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(parse_document("For_vespers_variable.pdf"))
