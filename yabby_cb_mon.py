import requests
import pandas as pd
import datetime as dt

# dates and times
today = dt.date.today()
start_date = f"{(today - dt.timedelta(days=today.weekday()+7)).strftime('%m-%d-%y')} 00:00"
end_date = f"{(today - dt.timedelta(days=today.weekday()+1)).strftime('%m-%d-%y')} 23:59"

# api basics
cert_path = r'certificates/mccyabby.pem' # need absolute pathing
main_url = "https://admin.yabbycasino.com/YABBYECVSUGMOQMOIPQO/RTGWebAPI/"

# terms
min_loss = 33
min_deposits = 0
max_ratio = 100
min_reward = 1

# initiation prompt
print("Monday Cashback Rewards Module started:")
print("==========================")

if input("Skip processing rewards (for testing purposes)? [Y/N]: ") == 'Y'.casefold():
    testing = False
    print("NOT A DRILL - REWARDS WILL BE PROCESSED!")
else:
    testing = True
    print("Testing mode ON - rewards WILL NOT be processed.")

print("Terms setup:")
print(f"Minimum Loss: ${min_loss}")
print(f"Minimum Deposits: ${min_deposits}")
print(f"Maximum WDs/DEPs Ratio: {max_ratio}%")
print(f"Minimum Reward: ${min_reward}")
print("==========================")

# get depositors for last week
print(f"Getting depositors from {start_date} to {end_date}...")
r = requests.get(url=main_url+"api/reports/depositors", params={'startDate':start_date, 'endDate':end_date}, cert=cert_path)

df1 = pd.DataFrame(r.json()) # make a dataframe from received list of dictionaries
df1 = df1.drop(['casino_name', 'last_name', 'day_phone_number', 'evening_phone_number', 'full_address', 'address_2', 'city', 'country', 'zip_code', 'net_cash_position', 'signup_date', 'signup_skin', 'last_game_date', 'birth_date'], axis=1) # drop unnecessary columns

for index, row in df1.iterrows(): # iterate through dataframe rows [depositors]
    # define login
    login = row['login']
    player_class = row['player_class']
    # eligible column
    df1.at[index, 'eligible'] = True
    
    # check eligibility
    if row['account_status'] == 'DEACTIVED':
        print(f"{login} is deactivated.")
        df1.at[index, 'eligible'] = False
        continue
    if row['ban_status'] == 'BANNED':
        print(f"{login} is banned.")
        df1.at[index, 'eligible'] = False
        continue
    if player_class.casefold() == 'Bonus Abuser' or player_class.casefold() == 'Bonus Hunter':
        print(f"{login} is an abuser.")
        df1.at[index, 'eligible'] = False
        continue
    if player_class.casefold() == 'New'.casefold():
        print(f"{login} not VIP yet.")
        df1.at[index, 'eligible'] = False
        continue        
    
    # get playerID
    r = requests.get(url=main_url+ "api/accounts/playerid", params={'login':login}, cert=cert_path)
    pid = r.json().rstrip()
    
    # get player finance report
    r = requests.get(url=main_url+f"/api/players/{pid}/balance-summary", params={'startDate':start_date, 'endDate':end_date}, cert=cert_path)
    deposits = r.json()[0]['real_deposits_amount']
    withdrawals = r.json()[0]['real_withdrawals_amount']
    loss = deposits - withdrawals # losses
    ratio = withdrawals/deposits # ratio of withdrawals to deposits
    
    df1.at[index, 'deposits'] = deposits
    df1.at[index, 'withdrawals'] = withdrawals
    df1.at[index, 'loss'] = loss
    
    # check if terms are met
    if deposits < min_deposits:
        print(f'{login} ineligible - deposits below minimum [${min_deposits}].')
        df1.at[index, 'eligible'] = False
        continue
    if loss < min_loss:
        print(f'{login} ineligible - loss below minimum [${min_loss}].')
        df1.at[index, 'eligible'] = False
        continue
    if ratio * 100 >= max_ratio:
        print(f'{login} ineligible - withdrawls ratio above maximum [{max_ratio}%].')
        df1.at[index, 'eligible'] = False
        continue
    
    # calculate reward
    if player_class.casefold() == 'Rookie'.casefold(): reward = 0.03 * loss
    elif player_class.casefold() == 'Pro'.casefold(): reward = 0.04 * loss
    elif player_class.casefold() == 'Star'.casefold(): reward = 0.05 * loss
    elif player_class.casefold() == 'Prestige'.casefold(): reward = 0.08 * loss
    elif player_class.casefold() == 'Hall of Fame'.casefold(): reward = 0.1 * loss

    if reward < min_reward:
        print(f'{login} ineligible - reward below minimum [${min_reward}].')
        df1.at[index, 'eligible'] = False
        continue

    df1.at[index, 'reward'] = reward

df1.to_csv('data.csv')