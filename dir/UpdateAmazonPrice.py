import json
from pyquery import PyQuery as pq
import requests
import time
from email.headerregistry import Address
from email.message import EmailMessage
import smtplib

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
    email_address = ""
    email_password = ""

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
            print("Possible internet error!")
            return False

        html_contents = page.text

        # Debug: Dump html content into a html file
        with open("test.html",'w', encoding='utf-8') as f:
            f.write(html_contents)

        d = pq(html_contents)

        price = d('#priceblock_ourprice').html()
        title = d('#productTitle').html().strip()
        
        if(price == None or title == None):
            interrupted = True
            msg = create_email_message(
                from_address=email_address,
                to_address=to_address,
                subject='Amazon Read Error',
                body= "Reading Error with url: " + key,
            )
        
            with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
                smtp_server.ehlo()
                smtp_server.starttls()
                smtp_server.login(email_address, email_password)
                smtp_server.send_message(msg)
            
            print("Reading Error!")

        else:
            if (float(price[1:]) != data[key]):
                changed = True
                msg = create_email_message(
                    from_address=email_address,
                    to_address=to_address,
                    subject='Amazon Price Update: ' + title,
                    body= "Your product " + title + " price changed from $" + str(data[key]) + " to " + price + ".",
                )
        
                with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(email_address, email_password)
                    smtp_server.send_message(msg)
                data[key] = float(price[1:])
                print("Price Change!")
            else:
                print("Nothing happened!")

    if changed:
        with open("price_list.json",'w') as f:
            json.dump(data, f, indent=4)
        changed = False

    if interrupted:
        return False
    
    return True