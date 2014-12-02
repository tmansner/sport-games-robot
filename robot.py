#!/usr/bin/python

""" 
	Version history:
	================
	
	-------------------------------------------------
	30.7.2014	| 0.1	| initial version
	02.12.2014  | 0.2   | converted for python 3.x
	-------------------------------------------------
	
	About:
	==================	
	This is a simple script that can be used to place multiple wagers from input file in to Veikkaus gaming system. 
	Purpose of this script is to demonstrate how the JSON API provided by Veikkaus website works. Following functionality
	is included:
	
	- login
	- moniveto (multiscore) wagers
	
	
	Notes:
	==================	
	This script requires 'requests' package from http://docs.python-requests.org/en/latest/ for session management, ensuring that the 
	site cookies are always properly included in the requests. 
	
	Using a http-client framework that supports authenticated sessions (i.e. cookies) out of the box is highly recommended.
	Veikkaus' website may change the cookies (names and content) unnoticed, and the clients (browsers or custom scripts), shall always use the
	cookies accordingly. It is not only the authentication, but also other requests may set and/or update the cookies. 
	Misbehavior may force us to close your gaming account.
	
	Requests that do not require authentication can be made "without session". However, making the requests as authenticated provides
	us valuable information on how you use the provided services, and thus further helps us to develop it to suite your needs better. 


	Usage:
	==================	
	How to display usage: 
	robot.py -h
	
	How to request winshares for set of Vakio (SPORT) boards:
	robot.py -a WINSHARE -g SPORT -d 12345 -f sport_input.txt
	
	How to list open draws for moniveto (MULTISORE):
	robot.py -a LIST_DRAWS -g MULTISCORE
	
	How to place moniveto (MULTISCORE) wagers for draw number 12345:
	robot.py -a PLAY -g MULTISCORE -d 12345 -u myaccount -p p4ssw0rd -f multiscore_input.txt -s 20


	It is possible to run multiple instances of this robot. But it is recommended to run maximum of 5 robots at a same time for a single account.
	This is because debiting the single account becomes the bottleneck for robot-wagering, and multiple instances do no longer provide the benefit in speed.	
	
""" 

import sys
import requests
import json
import copy
import time
import datetime
import getopt

# requests.packages.urllib3.disable_warnings()

""" 
	properties
	
"""

# number of wagers sent in a single request
basket_size=25

# the veikkaus site address
host="https://www.veikkaus.fi"

# required headers
headers = {
	'Content-type':'application/json',
	'Accept':'application/json',
	'X-ESA-APi-Key':'ROBOT'
}

# wager teamplate with common fields
wager_template = {
	"type":"NORMAL",
	"drawId":"",
	"gameName":"",
	"selections":[],
	"stake":0
}

"""
	get account balance

"""
def get_balance ( session ):
	r = session.get(host + "/api/latest/players/self/account", verify=True, headers=headers)
	j = r.json()
	return j["balances"]["CASH"]["balance"], j["balances"]["CASH"]["frozenBalance"]

"""
	Create winshare request for vakio. 
	For most of the games, the odds are provided as flat files. It is highly recommended to use those as long as they are available. 

	Vakio winshare request takes only the "selections" as input, so we can reuse the create_sport_wager code.
	
"""
def get_sport_winshare ( draw, matches ):
	# the winshare request takes nearly similar request, so lets use create_sport_wager, and copy selections to winshare_req
	wager_req = create_sport_wager("", 0, matches )
	winshare_req = {
		"selections":wager_req["selections"]
	}
	
	r = requests.post(host + "/api/v1/sport-games/draws/SPORT/"+draw+"/winshares", verify=True, data=json.dumps(winshare_req), headers=headers)
	j = r.json()
	for winshare in j["winShares"]:
		# each winshare has only one selection that contains the board (outcomes)
		
		board = []
		for selection in winshare["selections"]:
			for outcome in selection["outcomes"]:
				b = ""
				if "home" in outcome:
					b += "1"
				elif "tie" in outcome:
					b += "x"
				elif "away" in outcome:
					b += "2"
				board.append(b)
		print("value=%d,numberOfBets=%d,board=%s" % (winshare["value"], winshare["numberOfBets"],",".join(board)))


"""
	Creates a vakio (sport) wager, for which the selections of row like:
	2,1x2,x,1,x,2,x,1,x,2,12,x
	... look like this:
	 
	{
		"systemBetType":"SYSTEM",
		"outcomes":[
			{"away":{"selected":true}},
			{"home":{"selected":true},"tie":{"selected":true},"away":{"selected":true}},
			{"tie":{"selected":true}},
			{"home":{"selected":true}},
			{"tie":{"selected":true}},
			{"away":{"selected":true}},
			{"tie":{"selected":true}},
			{"home":{"selected":true}},
			{"tie":{"selected":true}},
			{"away":{"selected":true}},
			{"home":{"selected":true},"away":{"selected":true}},
			{"tie":{"selected":true}}
		]
	} 

	Note: the marks that are not selected can be omitted. But from implementation point of view, it may be easier to send those as well (as done below).

"""
def create_sport_wager ( draw, stake, matches ):
	wager_req = copy.deepcopy(wager_template)
	wager_req["gameName"] = "SPORT"
	wager_req["drawId"] = draw
	wager_req["stake"] = stake
	
	## this implementation supports only one row (selection) per wager
	selection = {
		"systemBetType":"SYSTEM",
		"outcomes":[]
	}
	
	for match in matches:
		## outcome template defines each option.
		outcome = {
			"home":{ "selected": False },
			"tie":{ "selected": False },
			"away":{ "selected": False },
		}
		
		## change the options as selected based on chosen marks
		for m in match:
			if m == "1":
				outcome["home"]["selected"] = True;
			elif m == "x":
				outcome["tie"]["selected"] = True;
			elif m == "2":
				outcome["away"]["selected"] = True;

		## add outcome to selection
		selection["outcomes"].append(outcome)
		
	## ... and the selection to wager request
	wager_req["selections"].append(selection)
	return wager_req


"""
	Create a moniveto (multiscore) wager, for which the selections look like this: 
	{
		"systemBetType":"SYSTEM",
		"score":{"home":[1],"away":[2]}
	},{
		"systemBetType":"SYSTEM",
		"score":{"home":[2],"away":[3]}
	},{
		"systemBetType":"SYSTEM",
		"score":{"home":[3],"away":[4,5,6]}
	}

"""
def create_multiscore_wager ( draw, stake, matches ):
	wager_req = copy.deepcopy(wager_template)
	wager_req["gameName"] = "MULTISCORE"
	wager_req["drawId"] = draw
	wager_req["stake"] = stake
	
	for match in matches:
		home, away = match.split("-")
		selection = {
			"systemBetType":"SYSTEM",
			"score":{"home":[], "away":[]}
		}
		selection["score"]["home"] = list(map(int, home.split(",")))
		selection["score"]["away"] = list(map(int, away.split(",")))
		wager_req["selections"].append(selection)
	
	# print(json.dumps(wager_req, indent=4, sort_keys=True))
	return wager_req

""" 
	Places wagers on the system. Prints out the serial numbers of all accpeted wagers and error codes for rejected wagers. 

"""
def place_wagers ( wager_basket, session ):
	rt = time.time()
	r = session.post(host + "/api/v1/sport-games/wagers", verify=True, data=json.dumps(wager_basket), headers=headers)
	rt = time.time() - rt;

	if r.status_code == 200:
		for wager in r.json():
			if wager["status"] == "REJECTED":
				print(">> REJECTED with error: %s" % (json.dumps(wager["error"])))
			elif wager["status"] == "ACCEPTED":
				print(">> ACCEPTED with serial: %s" % (wager["serialNumber"]))
				
		print("%s - placed %d wagers in %.3f seconds" % (datetime.datetime.now(), len(wager_basket), rt))
	else:
		print("Request failed:\n" + r.text)


"""
	Logins to veikkaus website, and returns the session object.
	It is important to use same session for all requests, so that the session cookies are handled properly.  
	If you want to manage the cookies manually, you have to take all the cookies from each response (even wagering) and update them accordingly. 

"""
def login (username, password): 
	s = requests.Session()
	login_req = {"type":"STANDARD_LOGIN","login":username,"password":password}
	r = s.post(host + "/api/v1/sessions", verify=True, data=json.dumps(login_req), headers=headers)
	if r.status_code == 200:
		return s
	else:
		raise Exception("Authentication failed", r.status_code)

"""
	Parse arguments. 

"""
def parse_arguments ( arguments ):
	optlist, args = getopt.getopt(arguments, 'ha:u:p:g:d:f:s:')
	params = {
		"username":"",
		"passowrd":"",
		"game":"",
		"draw":"",
		"input":"",
		"stake":0
	}
	for o, a in optlist:
		if o == '-h':
			print("-h prints this help")
			print("-a <action> (PLAY, WINSHARE, LIST_DRAWS)")
			print("-u <username>")
			print("-p <password>")
			print("-g <game> (MULTISCORE, SCORE, SPORT)")
			print("-d <draw number>")
			print("-f <input file> containing the wagers")
			print("-s <stake> (in cents, same stake used for all wagers)")
			sys.exit(0)
		elif o == '-a':
			params["action"] = a
		elif o == '-u':
			params["username"] = a
		elif o == '-p':
			params["password"] = a
		elif o == '-g':
			params["game"] = a
		elif o == '-d':
			params["draw"] = a
		elif o == '-f':
			params["input"] = a
		elif o == '-s':
			params["stake"] = int(a)
	return params
	
"""
	Lists open draws
	The request only takes game name as an input, e.g.
	This implementation only prints common fields such as game name, index, draw and status. 
	More (game specific) details are available in the returned JSON document. 

"""
def list_draws ( params ):
	r = requests.get(host + "/api/v1/sport-games/draws?game-names="+params["game"], verify=True, headers=headers)
	if r.status_code == 200:
		try:
			j = r.json()
			for draw in j["draws"]:
				print("game: %s, index: %s, draw: %s, status: %s" % (draw["gameName"],draw["brandName"],draw["id"],draw["status"]))
		except: 
			print("request failed: " + r.text)
	else:
		print("request failed: " + r.text)

"""
	Places the wagers based on input file.
	Groups max 'basket_size' wagers in a single request. 
	Prints out balance and reserved funds in the end. 

	Note: that having non-zero reserved funds indicates that some wagers may be 'fuzzy', and it is uncertain if the wagers are accepted or not. 
	The possibly fuzzy wagers are confirmed at latest in the next day.

"""
def play ( params ):
	session = login(params["username"], params["password"])
	f = open(params["input"],"r")
	
	wager_basket = []
	for line in f:
		if line.startswith("#"): continue
		wager_req = copy.deepcopy(wager_template)
		if params["game"] == "MULTISCORE":
			wager_req = create_multiscore_wager(params["draw"], params["stake"], line.split(";"))
		elif params["game"] == "SPORT":
			wager_req = create_sport_wager(params["draw"], params["stake"], line.split(";"))

		wager_basket.append(wager_req)
		
		if len(wager_basket) >= basket_size:
			place_wagers(wager_basket, session)
			wager_basket = []
	
	if len(wager_basket) > 0:
		place_wagers(wager_basket, session)
		wager_basket = []

	balance, frozen = get_balance( session )
	print("\n\taccount balance: %.2f\n\treserved funds (unconfirmed): %.2f" % (balance/100.0, frozen/100.0))

"""
	Performs winshare request for each set of wagers from input file
	
"""
def winshare ( params ):
	f = open(params["input"],"r")
	
	for line in f:
		if line.startswith("#"): continue
		if params["game"] == "SPORT":
			 get_sport_winshare(params["draw"], line.split(";"))

"""
	Robot main function
	- login
	- read the wagers from input file
	- places wagers 

"""
def robot( arguments ): 
	params = parse_arguments( arguments )
	
	if params["action"] == "LIST_DRAWS":
		list_draws(params)
	elif params["action"] == "PLAY":
		play(params)
	elif params["action"] == "WINSHARE":
		winshare(params)

"""
	MAIN

"""
if __name__ == "__main__":
	robot(sys.argv[1:])
