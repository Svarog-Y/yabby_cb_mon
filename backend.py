import requests


def get_date_opened(backend, certificate, player_id):
    while True:
        try:
            r = requests.get(url=backend + f"players/{player_id}", params={"playerId": player_id}, cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet and start again.                  ")
            if restart():
                return None
            else:
                continue

        if r.status_code == 200:
            return r.json()["account"]["date_opened"]
        else:
            print(f"Get Date Opened for {player_id} failed! {r.status_code}                                            "
                  f"{r.text}\n")
            if restart():
                return None


def get_player_id(backend, certificate, username):
    while True:
        try:
            r = requests.get(url=backend + "accounts/playerid", params={"login": username}, cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet and start again.                  ")
            if restart():
                return None
            else:
                continue

        if r.status_code == 200:
            return r.json().strip()
        elif r.status_code == 404:
            return 404
        elif r.status_code == 401:
            print("Certificate failure - Please contact Stefan.                                                       ")
            input(">> Press enter to continue. ")
            return None
        else:
            print(f"Get Player ID for {username} failed! {r.status_code}                                               "
                  f"{r.text}\n")
            if restart():
                return None


def get_balance(backend, certificate, player_id):
    while True:
        try:
            r = requests.get(url=backend + f"players/{player_id}/balance", params={"forMoney": True}, cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet!                                  ")
            if restart():
                return None
            else:
                continue

        if r.status_code == 200:
            return r.json()[0]['balance']
        else:
            print(f"Get Balance failed ({r.status_code})!                                                              "
                  f"{r.text}\n")
            if restart():
                return None


def active_coupon(backend, certificate, player_id):
    while True:
        try:
            r = requests.get(url=backend + f"players/{player_id}/coupons/active", cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet!                                  ")
            if restart():
                return None
            else:
                continue

        if r.status_code == 200:
            return True
        elif r.status_code == 204:
            return False

        else:
            print(f"Active Coupon check failed ({r.status_code}).                                                      "
                  f"{r.text}\n")
            if restart():
                return None


def pending_withdrawal(backend, certificate, username):
    parameters = {"login": username,
                  "startDate": "1-1-30",
                  "endDate": "1-1-30"}

    while True:
        try:
            r = requests.get(url=backend + "cashier/cashback", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("\nInternet connection problem detected! Please check your internet and try again.                  ")
            if restart():
                raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Pending Withdrawals."
                                "Please retry later.")  # restart
            else:
                continue

        if r.status_code == 200:
            return r.json()["has_pending_withdrawal"]

        print(f"[Tech] Pending Withdrawal check failed ({r.status_code}).                                              "
              f"{r.text}\n")
        if restart():
            raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Pending Withdrawals."
                            "Please retry later.")  # restart


def get_transactions(backend, certificate, player_id, start_date, end_date):
    parameters = {"skinId": 1,
                  "startDate": start_date,
                  "endDate": end_date,
                  "playerId": player_id}

    while True:
        try:
            r = requests.get(url=backend + "reports/transactions", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet and try again.                    ")
            if restart():
                return None  # reset application
            else:
                continue

        if r.status_code == 200:
            return r.json()

        print(f"Get Transactions failed ({r.status_code}).                                                             "
              f"{r.text}\n")
        if restart():
            return None  # reset application


def get_bank_methods(backend, certificate):
    while True:
        try:
            r = requests.get(url=backend + "cashier/banking-methods", cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet and try again.                    ")
            reset = input(">> Press enter to try again, or type 'skip' to continue "
                          "(this step isn't necessary right now): ")
            if reset.casefold() == "skip".casefold():
                return None
            else:
                continue

        if r.status_code == 200:
            return r.json()

        print(f"Get Banking Methods failed ({r.status_code}).                                                         ")
        reset = input(">> Press enter to try again, or type 'skip' to continue (this step isn't necessary right now): ")
        if reset.casefold() == "skip".casefold():
            return None


def get_coupon_category(backend, certificate, coupon_code, start_date, end_date):
    parameters = {"startDate": start_date,
                  "endDate": end_date,
                  "couponStatus": "redemption",
                  "couponCode": coupon_code
                  }

    while True:
        try:
            r = requests.get(url=backend + "v2/players/coupons", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("\nInternet connection problem detected! Please check your internet and try again.                  ")
            if restart():
                raise Exception(f"[technical] Failed getting {coupon_code} type. Please retry later.")  # restart
            else:
                continue

        if r.status_code == 200:
            if r.json()[0]["redemption_type"] == "fixed_amount_on_redemption":
                return True
            else:
                return False

        print(f"[technical] Get {coupon_code} Type failed ({r.status_code}).                                           "
              f"{r.text}\n")
        if restart():
            raise Exception(f"[technical] Failed getting {coupon_code} type. Manual Cashback Needed.")  # restart


def check_boost(start_date, end_date, username, backend, certificate):
    parameters = {"login": username,
                  "startDate": start_date,
                  "endDate": end_date,
                  "isLastDeposit": True}

    while True:
        try:
            r = requests.get(url=backend + "cashier/cashback", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("\nInternet connection problem detected! Please check your internet and try again.                  ")
            if restart():
                raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Deposit Boost."
                                "Please retry later.")  # restart
            else:
                continue

        if r.status_code == 200:
            if r.json()["sum_bonus_deposits"] > 0:
                return True
            else:
                return False

        print(f"[Tech] Deposit Boost check failed ({r.status_code}).                                                   "
              f"{r.text}\n")
        if restart():
            raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Deposit Boost.                                   "
                            "Please retry later.")  # restart


def get_gaming_activity(start_time, end_time, player_id, backend, certificate):
    parameters = {"playerId": player_id,
                  "startDate": start_time,
                  "endDate": end_time,
                  "forMoney": True}

    while True:
        try:
            r = requests.get(url=backend + f"players/{player_id}/gaming-activity", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("\nInternet connection problem detected! Please check your internet and try again.                  ")
            if restart():
                raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Gaming Activity."
                                "Please retry later.")  # restart
            else:
                continue

        if r.status_code == 200:
            return r.json()

        print(f"[Tech] Gaming Activity check failed ({r.status_code}).                                                 "
              f"{r.text}\n")
        if restart():
            raise Exception(f"[Tech] FATAL EXCEPTION: Failed checking Gaming Activity."
                            "Please retry later.")  # restart


def get_game_list(backend, certificate):
    parameters = {"enabledOnly":False}
    while True:
        try:
            r = requests.get(url=backend + "games", params=parameters, cert=certificate)
        except requests.ConnectionError:
            print("Internet connection problem detected! Please check your internet and try again.                    ")
            reset = input(">> Press enter to try again, or type 'skip' to continue "
                          "(this step isn't necessary right now): ")
            if reset.casefold() == "skip".casefold():
                return None
            else:
                continue

        if r.status_code == 200:
            return r.json()

        print(f"[Tech] Get Game List failed ({r.status_code}).                                                        ")
        reset = input(">> Press enter to try again, or type 'skip' to continue (this step isn't necessary right now): ")
        if reset.casefold() == "skip".casefold():
            return None


def restart():
    reset = input(">> Press enter to try again, or type 'r' to restart: ")
    if reset.casefold() == "r".casefold():
        return True
    else:
        return False
