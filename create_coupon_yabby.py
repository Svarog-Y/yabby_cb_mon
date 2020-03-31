import requests

# api basics
cert_path = r'certificates/mccyabby.pem' # need absolute pathing
main_url = "https://admin.yabbycasino.com/YABBYECVSUGMOQMOIPQO/RTGWebAPI/"

payload = r"""{
  "redeem_amount": 10,
  "play_through_amount": 99999,
  "can_be_referred": true,
  "limit_withdrawals": "fixed_amount",
  "limit_withdrawals_fixed_amount": 1,
  "limit_withdrawals_multiple_deposit": 0,
  "limit_withdrawals_code": "string",
  "disable_all_net_progressives": true,
  "earnings_restricted_to_deposit": false,
  "free_spin_deposit_list": null,
  "previous_coupon_id": 0,
  "minimum_bonus_balance_type": "no_limit",
  "minimum_bonus_balance": 0,
  "require_deposit_fixed_amount_on_redemption": false,
  "play_through_free_spin_wins": 0,
  "wager_bonus": 0,
  "free_spins_configuration": {
  },
  "coupon_code": "TEST-API-C12",
  "date_valid_start": "2020-03-30T18:02:09.590Z",
  "date_valid_end": "2020-03-31T18:02:09.590Z",
  "user_id": 0,
  "method_list": "string",
  "redeem_zero": 0,
  "redeem_verified_email": true,
  "redeem_new_players": false,
  "comment": "API Test",
  "associated_affiliate_id": null,
  "redeem_for_affiliate_id": null,
  "schedule_days_of_week": null,
  "schedule_start_time": 0,
  "schedule_duration_minutes": 0,
  "published": false,
  "allow_redemption_from": [
    "download"
  ],
  "allowed_skin_list": [
  ],
  "exclude_player_class": null,
  "player_filters": {
    "days_since_sign_up": {
      "type": "string",
      "value": {}
    },
    "days_since_birthday": {
      "type": "string",
      "value": {}
    },
    "days_since_first_deposit": {
      "type": "string",
      "value": {}
    },
    "days_since_last_deposit": {
      "type": "string",
      "value": {}
    },
    "countries_to_exclude": [
    ],
    "exclude_coupons": [
    ],
    "currencies": [
      "USD",
      "AUD",
      "EUR",
      "ZAR"
    ]
  },
  "sim_percent": 0,
  "count_days_deposit": 0,
  "count_days_play": 0,
  "game_play_through_list": [
  ]
}"""

#[
#      "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
#  ]