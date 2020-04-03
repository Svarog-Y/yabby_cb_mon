################### TERMS ###################
min_loss = 33
min_deposits = 0
max_ratio = 100
min_reward = 1
################### TERMS ###################

import requests
import pandas as pd
import datetime as dt
from sys import exit
from pathlib import Path
from random import choice
from string import digits, ascii_letters

# email imports
from ssl import create_default_context
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# root directory
root = Path.cwd()

# dates and times
today = dt.date.today()
start_date = f"{(today - dt.timedelta(days=today.weekday()+7)).strftime('%m-%d-%y')} 00:00"
end_date = f"{(today - dt.timedelta(days=today.weekday()+1)).strftime('%m-%d-%y')} 23:59"
# api basics
cert_path = str(root/'certificates'/'mccyabby.pem')
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
            print(f"-- retry get {description} [{n+1}/2]...")

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
    # check active balance first
    balance = get(f"api/players/{pid}/balance",{'forMoney':'True'}, "active balance") # check active balance
    if balance == False: # if balance call fails -> soft failure
        return 0
    elif balance[0]['balance'] >= 1: # has active balance
        print("----> player has active balance")
        return 2
    
    # redeem coupon
    print(f"-- redeem {coupon_code}...")
    r = requests.post(url=main_url+f'api/v2/players/{pid}/coupons',params={'couponCode':coupon_code, 'redeem':True, 'ignorePlayerRestrictions':True},cert=cert_path)
    if r.status_code == 200:
        print("----> success!")
        return 1
    elif r.json()['Status'] == 'player_excluded_from_redeeming_all_coupons': # ineligible
        print("----> excluded from coupons")
        return 3
    elif r.json()['Status'] == 'previous_coupon_pending': # has active balance
        print("----> previous coupon pending")
        return 2
    else: # if redeem coupon call fails -> soft failure
        print(f"----> failed: {r.status_code}") 
        print(f"---- {r.text}")
        return 0

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
        print(f"-- send 'processed reward' to {email}...")
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
        print(f"-- send 'pending reward' email to {email}...")
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
            return False
            
# initiation prompt
print("\nMonday Cashback Rewards Module started:")
terms=["====================================================", "Terms setup:", f"Minimum Loss: ${min_loss}", f"Minimum Deposits: ${min_deposits}", f"Minimum Reward: ${min_reward}", f"Maximum WDs/DEPs Ratio: {max_ratio}%"]
for item in terms:
    print(item)

# for testing purposes
if input("Skip processing rewards (for testing purposes)? [Y/N]: ") == 'N'.casefold(): # process rewards
    testing = False
    print("NOT A DRILL - REWARDS WILL BE PROCESSED!")
    if input("Proceed? [Y/N]: ") == 'N'.casefold(): # double check
        testing = True
        print("Testing mode ON - rewards WILL NOT be processed.")
else: # testing mode
    testing = True
    print("Testing mode ON - rewards WILL NOT be processed.")
print("====================================================")

# get depositors for last week
print(f"-- get depositors report [{start_date} to {end_date}]...")
for n in range(5): # attempt 5 times
    r = requests.get(url=main_url+"api/reports/depositors", params={'startDate':start_date, 'endDate':end_date}, cert=cert_path)
    if r.status_code == 200:
        total = len(r.json()) # get depositor count
        df1 = pd.DataFrame(r.json()) # make a dataframe from received list of dictionaries
        df1 = df1.drop(['casino_name', 'last_name', 'day_phone_number', 'evening_phone_number', 'full_address', 'address_2', 'city', 'country', 'zip_code', 'net_cash_position', 'signup_date', 'signup_skin', 'last_game_date', 'birth_date'], axis=1) # drop unnecessary columns
        print(f"----> success! {total} depositors in total.")
        break
    else:
        print(f"---- failed: {r.status_code}")
        print(f"---- {r.text}")
        if n == 4: exit("---------------\nFailed getting depositors 5 times.\nPlease check certificates and internet connection.\n---------------")
        print(f"-- get depositors attempt {n+1}...")

for index, row in df1.iterrows(): # iterate through dataframe rows [depositors]
    # define login
    current = index + 1 # to keep track
    login = row['login']
    player_class = row['player_class']
    # eligibility column
    df1.at[index, 'eligible'] = True
    df1.at[index, 'failed'] = False
    
    print("------------------------------")
    print(f"[{current}/{total}] {login}")

    # check eligibility
    if row['account_status'] == 'DEACTIVED':
        print(f"[{current}/{total}] {login} ineligible: deactivated.")
        df1.at[index, 'eligible'] = False
        continue
    if row['ban_status'] == 'BANNED':
        print(f"[{current}/{total}] {login} ineligible: banned.")
        df1.at[index, 'eligible'] = False
        continue
    if player_class == 'Bonus Abuser' or player_class == 'Bonus Hunter' or player_class == 'New':
        if player_class == "New": player_class = "Novice Customer" # for better reporting
        print(f"[{current}/{total}] {login} ineligible: {player_class}.")
        df1.at[index, 'eligible'] = False
        continue       
    
    # get playerID
    r = get("api/accounts/playerid",{'login':login},"player id")
    if r == False: #failed
        print(f"[{current}/{total}] {login} skipped: HARD FAIL (Get Player ID) - Moving to next customer...") # what to do with customers who failed?
        df1.at[index, 'failed'] = True
        continue # next customer
    else: pid = r.rstrip() # success
    
    # get player balance summary
    r = get(f"api/players/{pid}/balance-summary",{'startDate':start_date, 'endDate':end_date},"balance summary")
    if r == False: # failed
        print(f"[{current}/{total}] {login} skipped: HARD FAIL (Get Balance Summary) - Moving to next customer...") # what to do with customers who failed?
        df1.at[index, 'failed'] = True
        continue # next customer
    else: # success
        deposits = r[0]['real_deposits_amount']
        withdrawals = r[0]['real_withdrawals_amount']
        loss = deposits - withdrawals # losses
        ratio = withdrawals/deposits * 100 # ratio of withdrawals to deposits
        df1.at[index, 'deposits'] = deposits
        df1.at[index, 'withdrawals'] = withdrawals
        df1.at[index, 'loss'] = loss
    
    # check if terms are met
    if deposits < min_deposits:
        print(f'[{current}/{total}] {login} ineligible - deposits [${round(deposits,2)}] below minimum [${min_deposits}].')
        df1.at[index, 'eligible'] = False
        continue
    if loss < min_loss:
        print(f'[{current}/{total}] {login} ineligible - loss [${round(loss,2)}] below minimum [${min_loss}].')
        df1.at[index, 'eligible'] = False
        continue
    if ratio > max_ratio:
        print(f'[{current}/{total}] {login} ineligible - withdrawals ratio [{round(ratio,2)}%] above maximum [{max_ratio}%].')
        df1.at[index, 'eligible'] = False
        continue
    
    # calculate reward
    if player_class.casefold() == 'Rookie'.casefold(): reward = 0.03 * loss
    elif player_class.casefold() == 'Pro'.casefold(): reward = 0.04 * loss
    elif player_class.casefold() == 'Star'.casefold(): reward = 0.05 * loss
    elif player_class.casefold() == 'Prestige'.casefold(): reward = 0.08 * loss
    elif player_class.casefold() == 'Hall of Fame'.casefold(): reward = 0.1 * loss
    df1.at[index, 'reward'] = reward # record reward
    if reward < min_reward: # check reward vs terms
        print(f'[{current}/{total}] {login} ineligible - reward [${round(reward,2)}] below minimum [${min_reward}].')
        df1.at[index, 'eligible'] = False
        continue
    
    if testing: # skip to next customer
        print("-- rewards and email skipped - test mode is ON")
        continue

    coupon_code = create_coupon(login, reward) # try creating coupon
    if coupon_code == False: # if failed, put Event Log Comment and send email
        df1.at[index, 'processed'] = False
        place_comment(pid, reward)
        send_email(2, row['first_name'], row['email'])
        print(f"[{current}/{total}] {login} - failed to create a coupon so support will have to cover it. Reward amount noted on customer's event log, 'pending reward' email sent.")
    else: # if coupon was created 
        r = redeem_coupon(pid, coupon_code)
        if r == 0: # if soft failure
            df1.at[index, 'processed'] = False
            place_comment(pid, reward, coupon_code=coupon_code)
            send_email(2, row['first_name'], row['email'])
            print(f"[{current}/{total}] {login} - failed to redeem coupon so support will have to cover it. Coupon created, noted on customer's event log, 'pending reward' email sent.")
        elif r == 1: # processed
            df1.at[index, 'processed'] = True
            send_email(1, row['first_name'], row['email'])
            print(f"[{current}/{total}] {login} - sucess (Reward Processed)!")
        elif r == 2: # active balance
            df1.at[index, 'processed'] = True
            place_comment(pid, reward, coupon_code=coupon_code)
            send_email(2, row['first_name'], row['email'])
            print(f"[{current}/{total}] {login} - success (Active Balance)!")
            continue
        elif r == 3: # if excluded from coupons
            df1.at[index, 'eligible'] = False
            print(f"[{current}/{total}] {login} excluded from redeeming coupons.")
            continue

print("====================================================")
print(f"Report is saved here: {root/'data.csv'}...")
df1.to_csv(root/'data.csv')
a = input("I'm done! Enter 'q' to exit... ")
while a != "q":
    a = input("Enter 'q' to exit... ")
exit()