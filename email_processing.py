import imaplib
import email
from email.header import decode_header
import os

IMAP_SERVER = ""
EMAIL_ACCOUNT = ""
EMAIL_PASSWORD = ""

# dir to save attachments
ATTACHMENTS_DIR = "attachments"

# if not exist make new folder
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

def fetch_attachments():
    # Logoging
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    #download all unread messages
    status, messages = mail.search(None, "UNSEEN")  # Możesz użyć "ALL" zamiast "UNSEEN"

    for msg_id in messages[0].split():
        # download email
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes) and encoding:
                    subject = subject.decode(encoding)

                print(f"📩 new email: {subject}")

                # processing attachments
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        filename, encoding = decode_header(filename)[0]
                        if isinstance(filename, bytes) and encoding:
                            filename = filename.decode(encoding)

                        filepath = os.path.join(ATTACHMENTS_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))

                        print(f"✅ Załącznik zapisany: {filepath}")

    mail.logout()


def delete_unread_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")


    status, messages = mail.search(None, "UNSEEN")

    print(messages)
    if messages[0]:
        for msg_id in messages[0].split():
            # checking message as deleted
            mail.store(msg_id, "+FLAGS", "\\Deleted")
            print(f"🗑️ Usunięto wiadomość ID: {msg_id.decode()}")

        # erase from bin
        mail.expunge()
    else:
        print("✅ Brak nieprzeczytanych wiadomości do usunięcia.")

    mail.logout()
if __name__ == "__main__":
    delete_unread_emails()
