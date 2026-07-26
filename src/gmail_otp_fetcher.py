import imaplib
import email
import re
import time
import os


def get_linkedin_otp_from_gmail(
    gmail_user: str,
    gmail_app_password: str,
    max_wait_seconds: int = 60,
    poll_interval: int = 5,
) -> str | None:
    """
    Polling inbox Gmail untuk mencari email OTP dari LinkedIn,
    lalu extract kode OTP-nya (biasanya 6 digit angka).

    Args:
        gmail_user: alamat email gmail (mis. "akuncrawler@gmail.com")
        gmail_app_password: App Password 16-karakter dari Google Account
        max_wait_seconds: total waktu tunggu maksimal sebelum menyerah
        poll_interval: jeda antar pengecekan inbox (detik)

    Returns:
        Kode OTP (string) kalau ketemu, None kalau timeout.
    """
    deadline = time.time() + max_wait_seconds

    while time.time() < deadline:
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login(gmail_user, gmail_app_password)
            imap.select("INBOX")

            # Cari email dari LinkedIn yang UNSEEN (belum dibaca), paling baru
            status, messages = imap.search(
                None, '(UNSEEN FROM "security-noreply@linkedin.com")'
            )

            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                latest_email_id = email_ids[-1]  # ambil yang paling baru

                status, msg_data = imap.fetch(latest_email_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Ambil body email (handle plain text & html)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode(
                                "utf-8", errors="ignore"
                            )
                            break
                        elif content_type == "text/html" and not body:
                            body = part.get_payload(decode=True).decode(
                                "utf-8", errors="ignore"
                            )
                else:
                    body = msg.get_payload(decode=True).decode(
                        "utf-8", errors="ignore"
                    )

                # Cari pola 6 digit angka (format umum OTP LinkedIn)
                match = re.search(r"\b(\d{6})\b", body)
                if match:
                    otp_code = match.group(1)
                    imap.logout()
                    return otp_code

            imap.logout()

        except Exception as e:
            print(f"[ERROR] Gagal cek email OTP: {e}")

        print(f"[INFO] OTP belum ketemu, cek lagi dalam {poll_interval}s...")
        time.sleep(poll_interval)

    print("[WARNING] Timeout - OTP tidak ditemukan dalam waktu yang ditentukan.")
    return None


# Contoh pemakaian
if __name__ == "__main__":
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

    otp = get_linkedin_otp_from_gmail(GMAIL_USER, GMAIL_APP_PASSWORD)
    if otp:
        print(f"[INFO] OTP ditemukan: {otp}")
    else:
        print("[ERROR] OTP tidak ditemukan.")
