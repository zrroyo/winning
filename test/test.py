#!/usr/bin/python

#===Test Data====#

#import data

#dat = data.Data('futures', 'm1305_day_k')
#res = dat.M('2012-12-20', 'Close', 5)
#print res
#res = dat.M5('2012-12-20', 'Close')
#print res
#res = dat.M('2012-12-20', 'Open', 2)
#print res
#res = dat.M('2012-12-20', 'Close', 10)
#print res
#res = dat.M('2012-05-31', 'Close', 2)
#print res
#res = dat.M5('2012-05-31', 'Close')
#print res

#res = dat.M5('2013-01-11 14:55', 'Close')
#print res


#===Test Date====#

#import date

#time = date.Date('futures', 'm1305_day_k')
#res = time.curDate()
#print res
#res = time.nextDate()
#print res
#res = time.getSetNextDate()
#print res
#res = time.getSetNextDate()
#print res
#res = time.getSetNextDate()
#print res
#res = time.getSetNextDate()
#print res
#res = time.setCurDate('2012-12-04')
#print res
#res = time.curDate()
#print res
#res = time.nextDate()
#print res


#===Test simulation=====#

#import date
#import data

#time = date.Date('futures', 'm1305_day_k')
#curDay = time.curDate()

#dat = data.Data('futures', 'm1305_day_k')

#while curDay is not None:
	#print curDay, dat.M(curDay, 'Close', 1), dat.M5(curDay, 'Close')
	#if dat.M(curDay, 'Close', 1) < dat.M5(curDay, 'Close'):
		#print curDay
	#curDay = time.getSetNextDate()
		
	
#while curDay is not None:
	#print curDay, dat.M(curDay, 'Close', 1), dat.M10(curDay, 'Close')
	#if dat.M(curDay, 'Close', 1) < dat.M10(curDay, 'Close'):
		#print curDay
	#curDay = time.getSetNextDate()
	
	
#while curDay is not None:
	#print curDay, dat.M(curDay, 'Close', 1), dat.M20(curDay, 'Close')
	#if dat.M(curDay, 'Close', 1) < dat.M20(curDay, 'Close'):
		#print curDay
	#curDay = time.getSetNextDate()
	
#time.setCurDate('2012-12-03')
#print time.curDate(), time.prevDate(), time.nextDate()
#time.setCurDate('2012-12-03')
#print time.curDate(), time.getSetNextDate(), time.curDate()
#time.setCurDate('2012-12-03')
#print time.curDate(), time.getSetPrevDate(), time.curDate()

	

#===Test Trade=====#

#import trade

#trd = trade.Trade('futures', 'trade_rec1')

#trd.openTrade('T0001', 'm1305', '2013-1-14 14:35:48', 'D', '1,2,3', 3360, 3, 'Increase greatly', 0, 'Danger')
#trd.openDTrade('T0001', 'm1305', '2013-1-14 14:35:48', '1,2,3', 3360, 3, 'Increase greatly', 0, 'Danger')
#trd.tradeOver('T0001', 'm1305', '2013-1-17 14:35:38', 'D', '2,3', 3390, 2)

#trd.openTrade('T0002', 'm1305', '2013-1-18 14:35:48', 'K', '1,2', 3350, 2, 'Descrease sharply', 0, 'Danger')
#trd.openKTrade('T0002', 'm1305', '2013-1-18 14:35:48', '1,2', 3350, 2, 'Descrease sharply', 0, 'Danger')
#trd.tradeOver('T0002', 'm1305', '2013-1-19 14:35:38', 'K', '2', 3390, 1)

#===Test drop table=====#

#import db.mysqldb as sql
#import trade
#trd = trade.Trade('futures', 'trade_rec4')
#db = sql.MYSQL("localhost", "root", "19851117", 'futures')
#db.connect()
#db.drop('trade_rec4')



