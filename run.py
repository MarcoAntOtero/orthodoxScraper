if __name__ == "__main__":
    from datetime import date

    from download_weekly_pdf import download_vespers_pdf
    from extract_sections import parse_document
    from send_email import send_email
    from write_pdf import build_pdf

    today = date.today()
    source_path = f"vespers_{today.year}_{today.month:02d}_{today.day:02d}.pdf"
    download_vespers_pdf(today.year, today.month, today.day, source_path)

    data = parse_document(source_path)
    bulletin_path = build_pdf(data, output_path="output.pdf")

    send_email(
        to="oterom935@gmail.com",  # placeholder for your own email address
        cc="oterom935@gmail.com",
        subject=f"Vespers Variable {today.year}",
        body=f"Attached. {today.month:02d}-{today.day:02d} {today.year}",
        attachment_path=bulletin_path,
    )
