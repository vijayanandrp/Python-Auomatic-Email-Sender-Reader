# -*- coding: utf-8 -*-

import re
import email
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import ntpath
import nltk
import datetime

from config import smtp_email, smtp_port, smtp_server
from template import email_subject, email_message_html, email_message_plain
from logger import Logger

__authors__ = ["P. Vijay Anand"]
__email__ = "vijayanandrp@gmail.com"
__version__ = "0.010"
__status__ = "This software is inital version."
__date__ = "27, Nov 2017"

log = Logger.defaults(name="EMAIL_LIB", output_stream=False)


def read_email(email_file):
    fp = open(email_file, encoding='utf8')
    try:
        email_dump = email.message_from_file(fp)
        email_details = {}
        fetch_items = ['From', 'To', 'Subject', 'Date']
        for key in fetch_items:
            if key in ['From']:
                from_ = email_dump[key]
                email_details['Sender_Email_Address'] = ', '.join(list(set(re.findall(r'<([^<]*)>', from_))))
                email_details['Sender_Name'] = ', '.join(re.findall(r'"([^"]*)"', from_))
            elif key in ['To']:
                to = email_dump[key]
                email_details['Received_By_Name'] = re.sub(r'<([^<]*)>', '', to).strip()
                email_details['Received_Email_Address'] = ', '.join(list(set(re.findall(r'<([^<]*)>', to))))
            elif key in ['Subject']:
                decode = email.header.decode_header(email_dump['Subject'])[0]
                subject = decode[0]
                if type(subject) is bytes:
                    email_details['Subject'] = subject.decode('unicode_escape')
                else:
                    email_details['Subject'] = subject
            elif key in ['Date']:
                date_stamp = re.sub(' (\+|\-).*', '', str(email_dump[key]))
                email_details['Date'] = date_stamp
                email_details['Date_Created'] = datetime.datetime.strptime(date_stamp.strip(), '%a, %d %b %Y %H:%M:%S')

        message = ''
        if email_dump.is_multipart():
            for part in email_dump.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    message = part.get_payload(decode=True)  # decode
                    break
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            message = email_dump.get_payload(decode=True)
        if type(message) is bytes:
            message = message.decode('unicode_escape')
            if '<html' in message:
                message = re.sub('<[^<]+?>', '', message)
                message = re.sub(' +', ' ', message)
            email_details['Message'] = message
        else:
            if '<html' in message:
                message = nltk.clean_html(message)
                message = re.sub('<[^<]+?>', '', message)
                message = re.sub(r'[^\x00-\x7F]+', ' ', message)
                message = re.sub(' +', ' ', message)
            email_details['Message'] = message
        # pprint.pprint(email_details)
        return email_details
    except Exception as error:
        log.error('Unable to read Email - ' + str(error))
        return {}


def send_email(to=None, cc=None, bcc=None, subject=None, attachments=None,
               message=None, html=True):
    email_from = smtp_email
    email_to = [email_from]
    files_to_send = attachments

    # email object
    msg = MIMEMultipart()
    msg["From"] = email_from
    if to:
        to = list(set(to))
        email_to += to
        msg["To"] = ', '.join(to)
    if cc:
        cc = list(set(cc))
        email_to += cc
        msg["Cc"] = ', '.join(cc)
    if bcc:
        bcc = list(set(bcc))
        email_to += bcc
        msg["Bcc"] = ', '.join(bcc)
    if subject:
        msg["Subject"] = subject
        msg.preamble = subject
    else:
        msg["Subject"] = email_subject
        msg.preamble = email_subject

    message_type = 'plain'
    if html:
        message_type = 'html'

    if not message:
        message = email_message_html
        msg.attach(MIMEText(message, message_type))
    else:
        message = email_message_plain
        msg.attach(MIMEText(message, message_type))

    if not isinstance(files_to_send, list):
        files_to_send = [files_to_send]

    if files_to_send:
        for file_to_send in files_to_send:
            print('Preparing to send file - {}'.format(file_to_send))
            content_type, encoding = mimetypes.guess_type(file_to_send)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            maintype, subtype = content_type.split("/", 1)
            if maintype == "text":
                with open(file_to_send) as fp:
                    # Note: we should handle calculating the charset
                    attachment = MIMEText(fp.read(), _subtype=subtype)
            elif maintype == "image":
                with open(file_to_send, "rb") as fp:
                    attachment = MIMEImage(fp.read(), _subtype=subtype)
            elif maintype == "audio":
                with open(file_to_send, "rb")as fp:
                    attachment = MIMEAudio(fp.read(), _subtype=subtype)
            else:
                with open(file_to_send, "rb") as fp:
                    attachment = MIMEBase(maintype, subtype)
                    attachment.set_payload(fp.read())
                encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=ntpath.basename(file_to_send))
            msg.attach(attachment)

    try:
        smtp_obj = smtplib.SMTP(host=smtp_server, port=smtp_port, timeout=300)
        smtp_obj.sendmail(from_addr=email_from, to_addrs=list(set(email_to)), msg=msg.as_string())
        log.info("Successfully sent email to {}".format(str(email_to)))
        smtp_obj.quit()
        return True
    except smtplib.SMTPException:
        log.error("Error: unable to send email")
        return False


