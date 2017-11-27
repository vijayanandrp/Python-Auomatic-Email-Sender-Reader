#!/usr/bin/env python3.5
# coding: utf-8


from emails import send_email
from template import email_subject, email_message_html, email_message_plain

# list
to = ['vijay.anandp@informationcorners.com']         # feed your email address
cc = ['vijay.anandp@informationcorners.com']
bcc = ['vijay.anandp@informationcorners.com']

# list - file path to be attached in email
attachment = ['thankyou.jpg']

send_email(to=to, cc=cc, subject=email_subject, attachments=attachment,
           message=email_message_plain, html=False)

send_email(to=to, cc=cc, subject=email_subject, attachments=attachment,
           message=email_message_html, html=True)
