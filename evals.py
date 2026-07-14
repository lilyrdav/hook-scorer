import json, statistics
from scorer import score_hook

GOLD_STANDARD = [
  {"hook": "Introducing our new premium skincare collection.", "expected_overall": 1},
  {"hook": "I fired my accountant after I found this app.", "expected_overall": 5},
  {"hook": "This cut my grocery bill by $312 a month.", "expected_overall": 5},
  {"hook": "Save money on groceries with our amazing app.", "expected_overall": 2},
  {"hook": "Three things your dentist won't tell you.", "expected_overall": 4},
  {"hook": "Our company was founded in 2019 with a simple mission.", "expected_overall": 1},
  {"hook": "Hi, I'm Bob and I'm the founder of Company X.", "expected_overall": 1},
  {"hook": "This app helped me save over $200 on groceries last month.", "expected_overall": 3},
  {"hook": "Most people brush their teeth wrong.", "expected_overall": 3},
  {"hook": "I stopped drinking coffee for 30 days.", "expected_overall": 3},
  {"hook": "Transform your skin with the power of nature.", "expected_overall": 2},
  {"hook": "You won't believe what happened next.", "expected_overall": 2},
  {"hook": "I cancelled my gym membership six months ago. I'm in better shape now.", "expected_overall": 4},
  {"hook": "My accountant told me to stop doing this. he was wrong.", "expected_overall": 4},
  {"hook": "I threw out $600 of skincare last month. My skin's never been clearer.", "expected_overall": 5}
]

def run_evals():
  errors, rows = [], []
  for case in GOLD_STANDARD:
    result = score_hook(case["hook"])
    err = abs(result["overall"] - case["expected_overall"])
    errors.append(err)
    rows.append((case["hook"], case["expected_overall"], result["overall"], err))

  print(f"{'HOOK': <75}{'EXP':<5}{'GOT':<5}{'ERR'}")
  for r in rows:
    print(f"{r[0]:<75}{r[1]:<5}{r[2]:<5}{r[3]}")
  print(f"\nMean absolute error: {statistics.mean(errors):.2f}")
  print(f"Exact agreement: {sum(1 for e in errors if e == 0)}/{len(errors)}")

if __name__ == "__main__":
  run_evals()