###### MPLNET Library:  Julian Date and Conversion Functions
###		built to mimic isodate and julian from MPLNET IDL library
###


import datetime, jdcal, re
import numpy as np

__version__ = '0.0.1'

### Function accepts Gregorian date, or date and time, and returns Julian date (days since 1 Jan 4713 BC). Day fraction is included by default, turn by setting integer = 1 or True
###		Function accepts the following inputs:
###			Julian date (float or long integer)
###			String date and times:
###				"YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS", "YYYY-MM-DDTHH:MM:SSZ", and compressed versions "YYYYMMDD", "YYYYMMDDHHMMSS"
###				Date must be provided, time is optional. Seconds (SS) may be omitted, and will be filled with "00" if so.
###			datetime: a datetime.datetime or datetime.date object, will convert to julian
###
###	 Inputs:
###				dt:  primary input. Can be anyone of the accepted inputs above
###				
###				Optional Inputs (do use with dt, either input with dt or one of these):
###					yyyy, mm, dd:  integer or string values date (if string must include the leading zero for values < 10)
###					hh, mn (minute), ss:  integer or string values for time (if string must include the leading zero for values < 10)
###					date: one of the accepted string date values above
###					time: one of the accepted string time values above
###					now: if set (!= None), will return current time in Julian date/time (must not be set with any other input above)
###					unix: input a unix timestamp instead of inputs above, converts to Julian date/time
###						local: only used for unix timestamp input. Will interpret time using local server setting. (default)
###						utc: only used for unix timestamp input. Will convert local server time to UTC. If local is already UTC has no effect. NOTE: GALION server uses UTC time.
###
###
###	 Controls:
###				integer:  if set, will return date only in long integer
###				verbose:  if set, will print messages to stdout
###
###  Examples:
###		
###				julian.julian(now=True)
###				2459975.105590278
###				julian.julian("20230129")
###				2459973.5
###				julian.julian("2023-01-29")
###				2459973.5
###				julian.julian("20230129140346")
###				2459974.085949074
###				julian.julian("2023-01-29 14:03:46")
###				2459974.085949074
###				julian.julian("2023-01-29T14:03:46Z")
###				2459974.085949074
###				julian.julian("2023-01-29 14:03:46",integer=True)
###				2459974
###				julian.julian(unix=1675527780.9688556,utc=True)
###				2459980.1826388887
###
###
###	Written: EJ Welton	2023-01-30
###		Last Updated: EJ Welton 2023-01-30
###		Last Updated: EJ Welton 2023-02-05
###			added support for using an converting from unix timestamps to julian date/time
###		Last Updated: EJ Welton 2023-02-13
###			fixed bug with input of an integer for dt, now returns integer value
###		Last Updated: EJ Welton 2025-04-15
###			added support for inputting python datetime objects (as dt), will convert them to julian
###		Last Updated: EJ Welton 2025-05-13
###			fixed bugs related to inputing a numpy float or int
###				julian now returns the same variable (including type), and isodate works correctly
###
def	julian(dt=None,yyyy=None,mm=None,dd=None,hh=None,mn=None,ss=None,date=None,time=None,now=None,integer=None,unix=None,local=None,utc=None,verbose=None):
	
	if unix != None and dt != None:
		if verbose != None:
			print("ERROR: julian.julian: cannot set both dt and unix times")
		return None
		
	if unix != None:
		dt = unixtotimestr(unix,local=local,utc=utc)
	
	if dt != None:
		
		if (isinstance(dt,datetime.datetime) or isinstance(dt,datetime.date) or isinstance(dt,datetime.time)):
			dt = datetimetostr(dt,verbose=verbose)
			if (dt == None):
				return dt
		
		if type(dt) == float or type(dt) == int or isinstance(dt, np.floating) or isinstance(dt, np.integer):
			return dt
		
		if now != None:
			if verbose != None:
				print("ERROR: julian.julian: cannot set date and time and now. Either date and time OR now")
			return None
		
		if " " in dt:
			# DATE TIME
			# get date and time separately, then follows as if submitted individually
			tmp = dt.split(" ")
			date = tmp[0]
			if len(tmp) == 2:
				time = tmp[1]
			else:
				time = "00:00:00"
			
		else:
			# DATETIME or "2007-04-05T14:30Z"
			# get date and time separately, then follows as if submitted individually
			
			if "-" in dt and ":" in dt and "T" in dt:
				# YYYY-MM-DDTHH:MMZ OR YYYY-MM-DDTHH:MM:SSZ
				tmp = dt.split("T")
				date = tmp[0]
				tmp2 = tmp[1].split("Z")
				time = tmp2[0]
				tmp = time.split(":")
				if len(tmp) < 3:
					time = time+":00"
					
			else:
				if "-" in dt:
					# date only in YYYY-MM-DD format
					date = dt
					time = "00:00:00"
				else:
					# compressed YYYYMMDDHHMMSS
					yyyy = dt[0:4]
					mm = dt[4:6]
					dd = dt[6:8]
					if len(dt) > 8:
						hh = dt[8:10]
						mn = dt[10:12]
						if len(dt) == 14:
							ss = dt[12:14]
						else:
							ss = "00"
					else:
						hh = 0
						mn = 0
						ss = 0
			
			
	else:
		
		if (yyyy == None and mm == None and dd == None) and date == None and now == None:
			if verbose != None:
				print("ERROR: julian.julian: must enter date or year, month, and day (integers) or date ('YYYYMMDD' or 'YYYY-MM-DD')")
			return None
	
		if (yyyy == None or mm == None or dd == None) and date == None and now == None:
			if verbose != None:
				print("ERROR: julian.julian: must enter year, month, and day (integers)")
			return None
	
		if (yyyy != None or mm != None or dd != None) and date != None and now == None:
			if verbose != None:
				print("ERROR: julian.julian: must enter date or year, month, and day (integers) or date ('YYYYMMDD' or 'YYYY-MM-DD'). Not both.")
			return None
	
	
	if (hh != None or mn != None or ss != None) and time != None and now == None:
		if verbose != None:
			print("ERROR: julian.julian: if doing time then must set hour, minute and second (integers) or time ('HH:MM:SS'), not both.")
		return None
	
	if now != None:	
		tday = datetime.datetime.now()
		
		frac = (float(tday.hour)+((float(tday.minute)+(float(tday.second)/60.0))/60.0))/24.0
		
		jday = sum(jdcal.gcal2jd(tday.year, tday.month, tday.day))+frac
	
	else:
		
		if date != None:
			tmp = "".join(date.split("-"))
			year = int(tmp[0:4])
			month = int(tmp[4:6])
			day = int(tmp[6:8])
		else:
			year = int(yyyy)
			month = int(mm)
			day = int(dd)
		
		if time != None:
			tmp = "".join(time.split(":"))
			if len(tmp) != 6:
				tmp = tmp+"00"
			hour = float(tmp[0:2])
			minute = float(tmp[2:4])
			second = float(tmp[4:6])
		else:
			if hh == None:
				hour = 0.0
			else:
				hour = float(hh)
			if mn == None:
				minute = 0.0
			else:
				minute = float(mn)
			if ss == None:
				second = 0.0
			else:
				second = float(ss)
		
		frac = (hour+((minute+(second/60.0))/60.0))/24.0
		jday = sum(jdcal.gcal2jd(year, month, day))+frac
		
	if integer != None:
		jday = int(np.round(jday))
	
	return jday
	
	

### Function accepts Julian dates (floats or integers, days since 1 Jan 4713 BC), or Gregorian date (or date and time) and returns date (or date and time) as string (see approved string formats below)
###		Function accepts the following inputs:
###			Julian date (float or long integer)
###			String date and times:
###				"YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS", "YYYY-MM-DDTHH:MM:SSZ", and compressed versions "YYYYMMDD", "YYYYMMDDHHMMSS"
###				Date must be provided, time is optional. Seconds (SS) may be omitted, and will be filled with "00" if so.
###			datetime: a datetime.datetime or datetime.date object, will convert to julian
###
###	 Inputs:
###				dt:  primary input. Can be anyone of the accepted inputs above
###				
###				Optional Inputs (do use with dt, either input with dt or one of these):
###					yyyy, mm, dd:  integer or string values date (if string must include the leading zero for values < 10)
###					hh, mn (minute), ss:  integer or string values for time (if string must include the leading zero for values < 10)
###					now: if set (!= None), will return current time in Julian date/time (must not be set with any other input above)
###					unix: input a unix timestamp instead of inputs above, converts to Julian date/time
###						local: only used for unix timestamp input. Will interpret time using local server setting. (default)
###						utc: only used for unix timestamp input. Will convert local server time to UTC. If local is already UTC has no effect. NOTE: GALION server uses UTC time.
###
###	 Controls:
###				date: if set (!= None), will only return date portion of string (NOTE: different use than with julian function)
###				time: if set (!= None), will only return time portion of string (NOTE: different use than with julian function)
###				iso:  if set, will return string with ISO format:  "YYYY-MM-DDTHH:MM:SSZ"
###				compressed:  if set, will return date with compressed format: one of "YYYYMMDD", "YYYYMMDDHHMMSS", "HHMMSS" depending on other control settings
###				decimal: if set, will return time with seconds including N decimal places to account for fractional seconds
###							default is decimal = 0, thus seconds are reported as whole numbers (rounded to its fraction if exists)
###
###  NOTE:  if iso and compressed are NOT set (the default), then strings are returned with one of following:  "YYYY-MM-DD", "YYYY-MM-DD HH:MM:SS", or "HH:MM:SS" depending on other control settings
###
###  Examples:
###		
###		julian.isodate(2459955.0870717596)
###		'2023-01-10 14:05:23'
###		julian.isodate(now=True)
###		'2023-01-30 15:29:08'
###		julian.isodate("20230129")
###		'2023-01-29 00:00:00'
###		julian.isodate("20230129",date=1)
###		'2023-01-29'
###		julian.isodate("20230129140346",iso=1)
###		'2023-01-29T14:03:46Z'
###		julian.isodate("2023-01-29 14:03:46",time=1)
###		'14:03:00'
###		julian.isodate("2023-01-29 14:03:46",time=1,compressed=1)
###		'140300'
###		julian.isodate("2023-01-29T14:03:46Z",compressed=1)
###		'20230129140346'
###		julian.isodate(now=1,decimal=6)
###		'2023-02-03 22:23:06.999987'
###		julian.isodate(now=1,decimal=15,compressed=1) # can be helpful as a temporary filename stamp, if use enough decimal places it will be unique name and has creation date/time in name
###		'20230203222306.999987305428437'
###		julian.isodate(unix=1675527780.9688556,utc=True)
###		'2023-02-04 16:23:00'
###
###
###	Written: EJ Welton	2023-01-30
###		Last Updated: EJ Welton 2023-01-30
###		Last Updated: EJ Welton 2023-02-03
###			added support for decimal. Which will display seconds with N decimal places for fractional seconds.
###		Last Updated: EJ Welton 2023-02-05
###			added support for using an converting from unix timestamps to julian date/time
###		Last Updated: EJ Welton 2023-02-13
###			fixed bug with input of integer value, now returns string date
###		Last Updated: EJ Welton 2025-04-15
###			added support for inputting python datetime objects (as dt), will convert them to julian
###

def	isodate(dt=None,yyyy=None,mm=None,dd=None,hh=None,mn=None,ss=None,date=None,time=None,now=None,iso=None,decimal=0,compressed=None,unix=None,local=None,utc=None,verbose=None):
	
	
	if unix != None and dt != None:
		if verbose != None:
			print("ERROR: julian.isodate: cannot set both dt and unix times")
		return None
		
	if unix != None:
		dt = unixtotimestr(unix,local=local,utc=utc)
	
	jdcalbase = 2400000.5
	
	if now != None:
		dt = julian(now=1)
	
	ssformat = "{:."+str(int(decimal))+"f}"
	
	if (isinstance(dt,datetime.datetime) or isinstance(dt,datetime.date) or isinstance(dt,datetime.time)):
			dt = datetimetostr(dt,verbose=verbose)
			if (dt == None):
				return dt
	
	if type(dt) == int or isinstance(dt, np.integer):
		date = True
	
	if type(dt) == float or type(dt) == int or isinstance(dt, np.floating) or isinstance(dt, np.integer):
		
		delta = dt - jdcalbase
		jd = jdcal.jd2gcal(jdcalbase, delta)
	
		year = str(jd[0])
		if jd[1] < 10.0:
			month = "0"+str(jd[1])
		else:
			month = str(jd[1])
		if jd[2] < 10.0:
			day = "0"+str(jd[2])
		else:
			day = str(jd[2])
		
		frac = jd[3]
		tmp = float(frac)*24.0
		hh = np.floor(tmp)
		tmp = (tmp - hh)*60.0
		mn = np.floor(tmp)
		tmp = (tmp - mn)*60.0
		if decimal == None:
			ss = int(np.floor(tmp))
		else:
			ss = tmp
	
		if hh < 10.0:
			hh = "0"+str(int(hh))
		else:
			hh = str(int(hh))
		if mn < 10.0:
			mn = "0"+str(int(mn))
		else:
			mn = str(int(mn))
		if ss < 10.0:
			ss = "0"+ssformat.format(ss)
		else:
			ss = ssformat.format(ss)
	
	if type(dt) == str:
		
		if " " in dt:
			# YYYY-MM-DD HH:MM:SS
			tmp = dt.split(" ")
			dates = tmp[0]
			year = dates[0:4]
			month = dates[5:7]
			day = dates[8:10]
				
			if len(tmp) == 2:
				times = tmp[1]
				hh = times[0:2]
				mn = times[3:5]
				if len(times) >= 8:
					ss = float(times[6:])
				else:
					ss = "00"
			else:
				hh = "00"
				mn = "00"
				ss = "00"
			
		else:
		
			# DATETIME or "2007-04-05T14:30Z"
			if "-" in dt and ":" in dt and "T" in dt:
				# YYYY-MM-DDTHH:MMZ OR YYYY-MM-DDTHH:MM:SSZ
				tmp = dt.split("T")
				dates = tmp[0]
				tmp2 = tmp[1].split("Z")
				times = tmp2[0]
				tmp = dates.split("-")
				year = tmp[0]
				month = tmp[1]
				day = tmp[2]
				tmp = times.split(":")
				hh = tmp[0]
				mn = tmp[1]
				if len(tmp) == 3:
					ss = tmp[2]
				else:
					ss = "00"
			
			# YYYY-MM-DD
			if "-" in dt and len(dt) == 10:
				year = dt[0:4]
				month = dt[5:7]
				day = dt[8:10]
				hh = "00"
				mn = "00"
				ss = "00"
					
			# compressed YYYYMMDD
			# compressed YYYYMMDDHHMM
			# compressed YYYYMMDDHHMMSS
			if "-" not in dt and ":" not in dt and "T" not in dt:
				year = dt[0:4]
				month = dt[4:6]
				day = dt[6:8]
				if len(dt) > 8:
					hh = dt[8:10]
					mn = dt[10:12]
					if len(dt) >= 14:
						ss = float(dt[12:])
					else:
						ss = "00"
				else:
					hh = "00"
					mn = "00"
					ss = "00"
		
		
		sstmp = float(ss)
		if sstmp < 10.0:
			ss = "0"+ssformat.format(sstmp)
		else:
			ss = ssformat.format(sstmp)
		
	
	d = year+"-"+month+"-"+day
	t = hh+":"+mn+":"+ss
	dc = year+month+day
	tc = hh+mn+ss
	
	if iso != None:
		result = d+"T"+t+"Z"
	else:
		if date != None:
			t = ""
			tc = ""
		if time != None:
			d = ""
			dc = ""
		
		if compressed == None:
			result = d+" "+t
		else:
			result = dc+tc
		
	result = result.strip()
	
	#print(year,month,day,hh,mn,ss)
	#print(result)
	
	return result



### Function converts unix time stamp (float or int) to ISO time string "YYYY-MM-DDTHH:MM:SSZ"
###
###		Inputs:
###				unix: unix time stamp
###
###		Optional Inputs:
###				local:	default setting = True. Uses whatever the local time type is on server. NOTE: GALION server uses UTC as local time. No need to set utc flag for ops on GALION server.
###				utc:  default setting = False. Converts local unix time to UTC. Has no effect if local time was already using UTC.
###				
###	Written: EJ Welton	2023-02-05
###		Last Updated: EJ Welton 2023-02-05
###
def	unixtotimestr(unix,local=None,utc=None):
	if unix == None:
		return None
	if local != None and utc != None:
		return None
	if local == None and utc == None:
		local = True
	if utc != None:
		t = datetime.datetime.utcfromtimestamp(unix).strftime('%Y-%m-%dT%H:%M:%SZ')
	if local != None:
		t = datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%dT%H:%M:%SZ')
	return t


### Function converts datetime.datetime or datetime.date to time string "YYYY-MM-DD HH:MM:SS"
###
###		Inputs:
###				datetime object
###
###		Optional Inputs:
###				isodate string format
###				
###	Written: EJ Welton	2025-04-15
###
def	datetimetostr(dt,verbose=False):
	if (isinstance(dt,datetime.datetime)):
		newdt = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
	elif(isinstance(dt,datetime.date)):
		newdt = dt.strftime("%Y-%m-%d")
	elif(isinstance(dt,datetime.time)):
		if verbose != None:
			print("ERROR: julian.julian: must enter date and time, not only time.")
		return None
	return newdt


