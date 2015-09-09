
#!/usr/bin/env python3
"""
Fetch a week of tweets
"""

from datetime import datetime, timedelta, date
from .tasks import pega_tweets

# Data inicial da captura

today = datetime.fromordinal(date.today().toordinal())
week_ago = datetime.fromordinal(date.today().toordinal())-timedelta(8)

pega_tweets.delay(week_ago.isoformat(), today.isoformat(), ['3304557', '3303302', '3106200', '4104808'], "A90")

