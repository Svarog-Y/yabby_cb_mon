import requests
import pandas as pd
import datetime as dt
from time import sleep
from sys import exit
from random import choice
from string import digits, ascii_letters

#email imports
from ssl import create_default_context
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cert_path = r'certificates/mccyabby.pem' # need absolute pathing
main_url = "https://admin.yabbycasino.com/YABBYECVSUGMOQMOIPQO/RTGWebAPI/"

def get(call, params, description):
    print(f"-- get {description}...")
    for n in range(3):
        r = requests.get(url=main_url+call, params=params, cert=cert_path)
        if r.status_code == 200:
            print(f"----> success!")
            return r.json()
        else:
            print(f"----> failed: {r.status_code}")
            print(f"---- {r.text}")
            if n == 2:
                print(f"----> request failed: get {description}")
                return False
            print(f"-- get {description} attempt {n+1}...")

def create_coupon(login, reward):
    # define payload
    # required time formats
    start_today = dt.date.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ") 
    end_today = (dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # necessary coupon details
    coupon_code = "CB-MON-"+"".join([choice(ascii_letters + digits) for n in range(7)]).upper() 
    comment = f"Monday Cashback reward for {login} | 10x WAG | 10x MCO | All NP Games Allowed" # coupon comment

    payload={"redeem_amount":reward,"play_through_amount":reward*10,"can_be_referred":True,"limit_withdrawals":"fixed_amount","limit_withdrawals_fixed_amount":reward*10,"limit_withdrawals_multiple_deposit":0,"limit_withdrawals_code":"string","disable_all_net_progressives":True,"earnings_restricted_to_deposit":False,"free_spin_deposit_list":None,"previous_coupon_id":0,"minimum_bonus_balance_type":"no_limit","minimum_bonus_balance":0,"require_deposit_fixed_amount_on_redemption":False,"play_through_free_spin_wins":0,"wager_bonus":0,"free_spins_configuration":None,"coupon_code":coupon_code,"date_valid_start":start_today,"date_valid_end":end_today,"user_id":0,"method_list":"string","redeem_zero":0,"redeem_verified_email":True,"redeem_new_players":False,"comment":comment,"associated_affiliate_id":None,"redeem_for_affiliate_id":None,"schedule_days_of_week":None,"schedule_start_time":0,"schedule_duration_minutes":3599,"published":False,"allow_redemption_from":["download"],"allowed_skin_list":[],"exclude_player_class":None,"player_filters":{"days_since_sign_up":{"type":"string","value":{}},"days_since_birthday":{"type":"string","value":{}},"days_since_first_deposit":{"type":"string","value":{}},"days_since_last_deposit":{"type":"string","value":{}},"countries_to_exclude":[],"exclude_coupons":[],"currencies":["USD","AUD","EUR"]},"sim_percent":0,"count_days_deposit":0,"count_days_play":0,"game_play_through_list":[]}

    while True: # attempt multiple times if coupon code exists
        print(f"-- create {coupon_code}...")
        r=requests.post(url=main_url+"api/v2/coupons/bonus-balance/single-use/fixed-amount-on-redemption", json=payload, cert=cert_path)
        if r.status_code == 200: 
          print(f"----> success!")
          return coupon_code # if successful, end function
        elif r.json()['Status'] == "coupon_code_already_exists": # if coupon code exists
            print(f"----> {coupon_code} already exists. generating new coupon code...")
            coupon_code = "CB-MON-"+"".join([choice(ascii_letters + digits) for n in range(7)]).upper() # randomize new code
            payload["coupon_code"] = coupon_code # input new coupon code
            continue # repeat
        else:
          print(f"----> failed: {r.status_code}")
          print(f"---- {r.text}")
          return False # coupon creation failed

def redeem_coupon(pid, coupon_code):
    # check balance first
    balance = get(f"api/players/{pid}/balance",{'forMoney':'True'}, "active balance") # check active balance
    if balance == False: # call failed (soft failure)
        return 0
    elif balance[0]['balance'] >= 1: # active balance (pending reward)
        print("----> player has active balance")
        return 0
    
    # now redeem coupon
    print(f"-- redeem {coupon_code}...")
    r = requests.post(url=main_url+f'api/v2/players/{pid}/coupons',params={'couponCode':coupon_code, 'redeem':True, 'ignorePlayerRestrictions':True},cert=cert_path)
    if r.status_code == 200: # redemption success
        print("----> success!")
        return True
    elif r.json()['Status'] == 'player_excluded_from_redeeming_all_coupons': # ineligible
        print("----> excluded from coupons")
        return False
    elif r.json()['Status'] == 'previous_coupon_pending':
        print("----> previous coupon pending")
        return 0 # active balance (pending reward)
    else:
        print(f"----> failed: {r.status_code}")
        print(f"---- {r.text}")
        return 0 # call failed (soft failure)

def place_comment(pid, reward, coupon_code=""):
    print(f"-- add event log comment...")
    r = requests.put(url=main_url+f"api/players/{pid}/comp-points",data={'comment':f'<font color="orange"><b>Monday Cashback Pending (${reward}):</b></font> <a href="couponPlayerRedeem.asp?PID={pid}&amp;couponCode={coupon_code}&amp;show=1">{coupon_code}</a>'},cert=cert_path)
    if r.status_code == 200:
        print("----> success!")
    else: 
        print(f"----> failed: {r.status_code}")
        print(f"---- {r.text}")

def send_email(status, firstname, email):
    smtp_server = "mail.yabbycasino.com"
    sender_email = "promotions@yabbycasino.com"
    password = "TZPjAzhRyTdZ"
    cas_text = "Yabby Promotions"
    subject = f"{firstname.title()}, your Monday Cashback is ready."
    filename = "yabby.csv" # for attachement part

    if status == 1: # Processed Message Content
        print(f"-- sending 'processed reward' to {email}")
        text = """\
        Dear %s,
        Hope you are well.
        Thank you for your patronage. Your Monday Cashback has been processed to your account. We hope it brings you luck!
        Please let us know if you need any assistance.
        Sincerely,
        Ethan
        Yabby Casino
        24/7 Live Support
        Chat: www.yabbycasino.com
        E-mail: support@yabbycasino.com
        Phone: 1-800-876-3456""" % (firstname.title(),)
        html="""\
        <html>
            <body>
                <p>
                    Dear %s,
                    <br><br>Hope you are well.
                    <br><br>Thank you for your patronage. <b>Your Monday Cashback has been processed to your account.</b> We hope it brings you luck!
                    <br><br>Please let us know if you need any assistance.
                    <br><br>Sincerely,
                    <br>Ethan
                    <br><b>Yabby Casino</b>
                    <br><br><i>24/7 Live Support
                    <br>Chat: www.yabbycasino.com
                    <br>E-mail: support@yabbycasino.com
                    <br>Phone: 1-800-876-3456</i>
                </p>
            </body>
        </html>
        """ % (firstname.title(),)
    elif status == 2: # Pending Message Content
        print(f"-- sending 'pending reward' email to {email}")
        text = """\
        Dear %s,
        Hope you are well.
        Thank you for your patronage. Your Monday Cashback has been prepared for your account! We didn't add it just yet so as not to disturb your current play.
        Once you are done, be sure contact our friendly Customer Service team, and they will have it added to your account. We hope it will prove lucky!
        Please let us know if you need any assistance.
        Sincerely,
        Ethan
        Yabby Casino
        24/7 Live Support
        Chat: www.yabbycasino.com
        E-mail: support@yabbycasino.com
        Phone: 1-800-876-3456""" % (firstname.title(),)
        html="""\
        <html>
            <body>
                <p>
                    Dear %s,
                    <br><br>Hope you are well.
                    <br><br>Thank you for your patronage. <b>Your Monday Cashback has been prepared for your account!</b> We didn't add it just yet so as not to disturb your current play.
                    <br><br>Once you are done, be sure contact our friendly Customer Service team, and they will have it added to your account. We hope it will prove lucky!
                    <br><br>Please let us know if you need any assistance.
                    <br><br>Sincerely,
                    <br>Ethan
                    <br><b>Yabby Casino</b>
                    <br><br><i>24/7 Live Support
                    <br>Chat: www.yabbycasino.com
                    <br>E-mail: support@yabbycasino.com
                    <br>Phone: 1-800-876-3456</i>
                </p>
            </body>
        </html>
        """ % (firstname.title(),)
    elif status == 3: # Report Message Content
        pass

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{cas_text} <{sender_email}>"
    message["To"] = email
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    port = 465
    context = create_default_context()
    with SMTP_SSL(host=smtp_server,port=port,context=context) as s:
        try:
            s.login(sender_email, password)
            s.sendmail(from_addr=sender_email, to_addrs=email, msg=message.as_string())
            print("----> success!")
        except Exception as e:
            print(f"----> failed: {e}")

# testing part

coupon_code = create_coupon("hamster", 1)
redeem_coupon("hamster", coupon_code)

coupon_code = create_coupon("blackpot09", 1)
redeem_coupon("10000332", coupon_code)

#place_comment("10000332", 15, "TESTAPICOMMENT")
#place_comment("hamster", 72)

#ADD REWARD, #ADD API