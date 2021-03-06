import json
from pyquery import PyQuery as pq
import requests
import time
from email.headerregistry import Address
from email.message import EmailMessage
import smtplib
import datetime

def log(name, msg):
	print("[" + datetime.datetime.now().strftime("%Y/%m/%d, %I:%M%p") + "] \n\t" + name  + "\n" + msg + "\n\n")

def create_email_message(from_address, to_address, subject, body):
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content(body)
    return msg

def amazonPriceUpdate():
    # Gmail sender details
    # To do
    email_address = "mars@marstanjx.com"
    email_password = "cFW4Ew9fg5iL"
    mail_server = "smtp.ipage.com"

    # Recipent
    to_address = (
        Address(display_name='Mars USC', username='jianxuat', domain='usc.edu'),
    )

    with open('price_list.json') as f:
        data = json.load(f)

    interrupted = False
    changed = False

    for key in data:
        url = key

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        # Possible internet error
        try:
            page = requests.get(url,headers=headers)
        except:
            log("", "Possible internet error!")
            return False

        html_contents = page.text

        # Debug: Dump html content into a html file
        with open("test.html",'w', encoding='utf-8') as f:
            f.write(html_contents)

        d = pq(html_contents)

        price = d('#priceblock_ourprice').html()
        title = d('#productTitle').html()
        
        if(price == None or title == None):
            log("", "Reading Error!")
            interrupted = True

        else:
            title =  title.strip()
            if (float(price[1:]) != data[key]):
                log(title, "Price Change Detected!")
                changed = True
                msg = create_email_message(
                    from_address=email_address,
                    to_address=to_address,
                    subject='Amazon Price Update: ' + title,
                    body= "Your product " + title + " price changed from $" + str(data[key]) + " to " + price + ".",
                )
        
                with smtplib.SMTP(mail_server, port=587) as smtp_server:
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(email_address, email_password)
                    smtp_server.send_message(msg)
                data[key] = float(price[1:])
                log(title, "Email Sent!")
            else:
                log(title, "Nothing happened!")

    if changed:
        with open("price_list.json",'w') as f:
            json.dump(data, f, indent=4)
        changed = False

    if interrupted:
        return False
    
    return True