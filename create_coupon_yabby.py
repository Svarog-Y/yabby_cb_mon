import requests
from random import choice
from string import digits, ascii_letters
import datetime as dt

def create_coupon(login, reward):
    # api basics
    cert_path = r'certificates/mccyabby.pem' # need absolute pathing
    main_url = "https://admin.yabbycasino.com/YABBYECVSUGMOQMOIPQO/RTGWebAPI/"

    # define payload
    coupon_code = "CB-MON-"+"".join([choice(ascii_letters + digits) for n in range(7)]).upper() # create random coupon code
    start_today = dt.date.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ") # required time format
    end_today = (dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") # required time format
    comment = f"Monday Cashback reward for {login} | 10x WAG | 10x MCO | All NP Games Allowed" # coupon comment

    payload={"redeem_amount":reward,"play_through_amount":reward*10,"can_be_referred":True,"limit_withdrawals":"fixed_amount","limit_withdrawals_fixed_amount":reward*10,"limit_withdrawals_multiple_deposit":0,"limit_withdrawals_code":"string","disable_all_net_progressives":True,"earnings_restricted_to_deposit":False,"free_spin_deposit_list":None,"previous_coupon_id":0,"minimum_bonus_balance_type":"no_limit","minimum_bonus_balance":0,"require_deposit_fixed_amount_on_redemption":False,"play_through_free_spin_wins":0,"wager_bonus":0,"free_spins_configuration":None,"coupon_code":coupon_code,"date_valid_start":start_today,"date_valid_end":end_today,"user_id":0,"method_list":"string","redeem_zero":0,"redeem_verified_email":True,"redeem_new_players":False,"comment":comment,"associated_affiliate_id":None,"redeem_for_affiliate_id":None,"schedule_days_of_week":None,"schedule_start_time":0,"schedule_duration_minutes":3599,"published":False,"allow_redemption_from":["download"],"allowed_skin_list":[],"exclude_player_class":None,"player_filters":{"days_since_sign_up":{"type":"string","value":{}},"days_since_birthday":{"type":"string","value":{}},"days_since_first_deposit":{"type":"string","value":{}},"days_since_last_deposit":{"type":"string","value":{}},"countries_to_exclude":[],"exclude_coupons":[],"currencies":["USD","AUD","EUR"]},"sim_percent":0,"count_days_deposit":0,"count_days_play":0,"game_play_through_list":[]}

    print(f"-- creating coupon for {login}...")
    while True: # attempt multiple times if coupon code exists
        r=requests.post(url=main_url+"api/v2/coupons/bonus-balance/single-use/fixed-amount-on-redemption", json=payload, cert=cert_path)
        if r.status_code == 200: 
          print(f"---- success!")
          return True # if successful, end function
        elif r.json()['Status'] == "coupon_code_already_exists": # if coupon code exists
            print(f"---- {coupon_code} already exists... generating new coupon code...")
            coupon_code = "CB-MON-"+"".join([choice(ascii_letters + digits) for n in range(7)]).upper() # randomize new code
            payload["coupon_code"] = coupon_code # input new coupon code
            continue # repeat
        else:
          print(f"---- failed: {r.status_code}")
          print(f"---- {r.text}")
          return False # coupon creation failed