# apartmentwatcher
A small script to gather pricing / unit availability of three different apartment complexes in Seattle. It then stores this data into a database and notifies you via email if there are any price changes, apartments taken off the market, or new apartments on the market.
This script is the source for a google cloud function. The cloud function can be configured to run at whatever interval (I chose twice a day) using pub/sub.

## Requires
This requires a mailgun and google cloud account.
