import tkinter as tk
from socket import *
from email.base64mime import body_encode

smtp_server = "smtp.qq.com"
smtp_port = 587

from_address = "1961133414@qq.com"
username = "1961133414@qq.com"
password = "unrupkfieilnbbaj"

drafts = []
sent_emails = []

def send_email():
    recipients = to_entry.get().split(',')
    subject = subject_entry.get()
    message = message_text.get("1.0", "end-1c")

    try:
        for recipient in recipients:
            client_socket = socket(AF_INET,SOCK_STREAM)
            client_socket.connect((smtp_server, smtp_port))
            recv = client_socket.recv(1024).decode()

            if recv[:3] != '220':
                result_label.config(text="220 reply not received from server.")
                client_socket.close()
                return

            helo_command = 'HELO QQ\r\n'
            client_socket.send(helo_command.encode())
            recv1 = client_socket.recv(1024).decode()

            if recv1[:3] != '250':
                result_label.config(text="250 reply not received from server.")
                client_socket.close()
                return

            user_pass_encode64 = body_encode(f"\0{username}\0{password}".encode('ascii'), eol='')
            auth_command = f'AUTH PLAIN {user_pass_encode64}\r\n'
            client_socket.sendall(auth_command.encode())
            recv2 = client_socket.recv(1024).decode()

            if recv2[:3] != '235':
                result_label.config(text="Authentication failed.")
                client_socket.close()
                return

            mail_from = f"MAIL FROM: <{from_address}>\r\n"
            client_socket.send(mail_from.encode())
            recv3 = client_socket.recv(1024).decode()
            rcpt_to = f"RCPT TO: <{recipient.strip()}>\r\n"
            client_socket.send(rcpt_to.encode())
            recv4 = client_socket.recv(1024).decode()

            if recv3[:3] != '250':
                result_label.config(text="MAIL FROM command failed.")
                client_socket.close()
                return
            if recv4[:3] != '250':
                result_label.config(text="RCPT TO command failed.")
                client_socket.close()
                return

            data_command = 'DATA\r\n'
            client_socket.send(data_command.encode())
            recv5 = client_socket.recv(1024).decode()

            if recv5[:3] != '354':
                result_label.config(text="DATA command failed.")
                client_socket.close()
                return

            client_socket.send(f"from: {from_address}\r\nto: {recipient.strip()}\r\nsubject: {subject}\r\n\r\n{message}\r\n.\r\n".encode())
            recv6 = client_socket.recv(1024).decode()

            if recv6[:3] != '250':
                result_label.config(text="Email could not be sent."+recv6[:3])
            else:
                result_label.config(text=f"Email sent to {recipient.strip()} successfully.")

            sent_emails.append((recipient.strip(), subject, message))

            quit_command = 'QUIT\r\n'
            client_socket.send(quit_command.encode())
            recv7 = client_socket.recv(1024).decode()
            client_socket.close()

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def save_draft():
    recipients = to_entry.get()
    subject = subject_entry.get()
    message = message_text.get("1.0", "end-1c")

    # Save the draft to a list
    drafts.append((recipients, subject, message))

    result_label.config(text="Draft saved successfully.")

def open_draft(index):
    if 0 <= index < len(drafts):
        recipients, subject, message = drafts[index]
        show_draft_window(recipients, subject, message)
    else:
        result_label.config(text="Draft not found.")

def open_sent_email(index):
    if 0 <= index < len(sent_emails):
        recipient, subject, message = sent_emails[index]
        show_sent_email_window(recipient, subject, message)
    else:
        result_label.config(text="Sent email not found.")

def show_draft_window(recipients, subject, message):
    draft_window = tk.Toplevel()
    draft_window.title(f"Draft Email")

    draft_recipients_label = tk.Label(draft_window, text=f"To: {recipients}")
    draft_recipients_label.pack()

    draft_subject_label = tk.Label(draft_window, text=f"Subject: {subject}")
    draft_subject_label.pack()

    draft_message_text = tk.Text(draft_window, height=10, width=40)
    draft_message_text.pack()
    draft_message_text.insert("1.0", message)

def show_sent_email_window(recipient, subject, message):
    sent_window = tk.Toplevel()
    sent_window.title(f"Sent Email to {recipient}")

    sent_subject_label = tk.Label(sent_window, text=f"Subject: {subject}")
    sent_subject_label.pack()

    sent_message_text = tk.Text(sent_window, height=10, width=40)
    sent_message_text.pack()
    sent_message_text.insert("1.0", message)

def view_drafts():
    drafts_window = tk.Toplevel()
    drafts_window.title("Drafts")

    drafts_listbox = tk.Listbox(drafts_window)
    drafts_listbox.pack()

    for i, draft in enumerate(drafts):
        recipients, subject, message = draft
        drafts_listbox.insert(i + 1, subject)

    view_button = tk.Button(drafts_window, text="View Draft", command=lambda: open_draft(drafts_listbox.curselection()[0]))
    view_button.pack()

def view_sent_emails():
    sent_window = tk.Toplevel()
    sent_window.title("Sent Emails")

    sent_listbox = tk.Listbox(sent_window)
    sent_listbox.pack()

    for i, sent_email in enumerate(sent_emails):
        recipient, subject, _ = sent_email
        sent_listbox.insert(i + 1, f"To: {recipient}, Subject: {subject}")

    view_button = tk.Button(sent_window, text="View Sent Email", command=lambda: open_sent_email(sent_listbox.curselection()[0]))
    view_button.pack()


root = tk.Tk()
root.title("SMTP Client")

to_label = tk.Label(root, text="To:\n Note:Separate multiple emails with commas(,)")
to_label.pack()
to_entry = tk.Entry(root)
to_entry.pack()

subject_label = tk.Label(root, text="Subject:")
subject_label.pack()
subject_entry = tk.Entry(root)
subject_entry.pack()

message_label = tk.Label(root, text="Message:")
message_label.pack()
message_text = tk.Text(root, height=10, width=40)
message_text.pack()

send_button = tk.Button(root, text="Send Email", command=send_email)
send_button.pack()

save_draft_button = tk.Button(root, text="Save Draft", command=save_draft)
save_draft_button.pack()

view_sent_button = tk.Button(root, text="View Sent Emails", command=view_sent_emails)
view_sent_button.pack()

view_drafts_button = tk.Button(root, text="View Drafts", command=view_drafts)
view_drafts_button.pack()

result_label = tk.Label(root, text="", fg="green")
result_label.pack()

root.mainloop()