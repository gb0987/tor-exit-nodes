# task

Write a program that allows the security engineering team to query an API with a given IPv4 or IPv6 address and receive
an acknowledgement if it is a Tor exit node

# requirements

List of Tor exit nodes can be obtained from https://secureupdates.checkpoint.com/IP-list/TOR.txt  
This list contains IPv4 and IPv6

## expected functionality 

- Program is portable (suggest using Docker or Terraform/AWS CDK to deploy to AWS free tier)
- The API must front every request (every request made to program must transit through the API)
- Three types of requests:
  - Search for exact IP address
  - Retrieve full list
  - Delete exact IP address from list
- Program must persist data between restarts or during an outage
- Data should be refreshed on a schedule
- Minimum supporting documentation (instructions to set up your program and how to make requests to your API)
  
## time

48 hrs

# notes
We need to send requests to https://secureupdates.checkpoint.com/IP-list/TOR.txt on a schedule to refresh our db, probably on the same schedule that it gets updated if that can be found. For now, daily.

API must front every request just means that the program can only be accessed through the API?

Minimum supporting documentation I will probably just make as I go even just to help myself!