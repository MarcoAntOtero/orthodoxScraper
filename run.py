if __name__ == "__main__":
    import time
    import traceback
    import socket
    from datetime import date

    from download_weekly_pdf import download_vespers_pdf
    from extract_sections import parse_document
    from send_email import send_email
    from write_pdf import build_pdf

    NOTIFY_EMAIL = "mo934@georgetown.edu"
    today = date.today()
    max_attempts = 5
    attempts = 0
    timeout = 600  # seconds or 10 mins
    while attempts < max_attempts:
        attempts += 1
        try:
            start_time = time.time()
            while True:
                try:
                    # Check the actual host this pipeline depends on, not an
                    # arbitrary "well-known" IP -- 1.1.1.1 (Cloudflare, not
                    # Google despite the old comment) turned out to be
                    # blocked on this network even with normal internet
                    # access, which would have made this check ALWAYS time
                    # out regardless of real connectivity.
                    conn = socket.create_connection(("dcs.goarch.org", 443), timeout=5)
                    conn.close()
                    break
                except Exception as e:
                    if time.time() - start_time > timeout:
                        raise Exception("Timeout waiting for internet connection") from e
                    time.sleep(1)

            #should reach here only after a successful connection to the internet
            print("Connected to the internet successfully.")
            source_path = f"vespers_{today.year}_{today.month:02d}_{today.day:02d}.pdf"
            download_vespers_pdf(today.year, today.month, today.day, source_path)

            data = parse_document(source_path)
            bulletin_path = build_pdf(data, output_path="output.pdf")

            send_email(
                to=NOTIFY_EMAIL,
                cc=NOTIFY_EMAIL,
                subject=f"Vespers Variable {today.year}",
                body=f"Attached. {today.month:02d}-{today.day:02d} {today.year}",
                attachment_path=bulletin_path,
            )
            break  # Exit the retry loop if everything succeeded
        except Exception:
            # Any failure above (download, extraction, PDF build, or the
            # bulletin email itself) lands here. Print it so it's still in
            # run.err.log for local debugging, then try to notify by email --
            # this runs unattended via launchd, so a silent failure would
            # otherwise go unnoticed until someone asks "where's the bulletin?"
            error_details = traceback.format_exc()
            print(error_details)

            try:
                send_email(
                    to=NOTIFY_EMAIL,
                    subject=f"Vespers Automation FAILED - {today.year}-{today.month:02d}-{today.day:02d}",
                    body=(
                        "The weekly Vespers bulletin script failed to run today.\n\n"
                        f"Error:\n{error_details}"
                    ),
                )
            except Exception:
                # If even the notification email fails (e.g. the Gmail token
                # itself is broken), there's nothing left to do but make sure
                # this is visible in the error log for whenever it's checked.
                print("Additionally failed to send the failure notification email:")
                print(traceback.format_exc())
