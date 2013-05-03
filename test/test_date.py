#!/usr/bin/python
import sys
sys.path.append("..")
import date

def test_date():
	"""
	2012-05-31
	2012-06-01
	2012-06-04
	2012-06-05
	2012-06-06
	127
	2012-12-04
	2012-12-03
	2012-12-05
	None
	2012-12-27
	None
	2012-06-01
	True
	False
	True
	False
	2012-06-12 next 5 days: 2012-06-19
	2012-06-22 next 3 days: 2012-06-27
	2012-12-26 next 5 days: None
	2012-06-12 prev 5 days: 2012-06-05
	2012-06-22 prev 3 days: 2012-06-19
	2012-05-31 prev 5 days: None
	"""
	time = date.Date('futures', 'm1305_day_k')
	res = time.curDate()
	print res
	#res = time.nextDate()
	#print res
	res = time.getSetNextDate()
	print res
	res = time.getSetNextDate()
	print res
	res = time.getSetNextDate()
	print res
	res = time.getSetNextDate()
	print res
	res = time.setCurDate('2012-12-04')
	print res
	res = time.curDate()
	print res
	#res = time.nextDate()
	#print res

	res = time.prevDate('2012-12-04')
	print res
	res = time.nextDate('2012-12-04')
	print res
		
	res = time.nextDate('2012-12-28')
	print res
	res = time.prevDate('2012-12-28')
	print res	
	res = time.prevDate('2012-05-31')
	print res
	res = time.nextDate('2012-05-31')
	print res
	
	res = time.isFirstDate('2012-05-31')
	print res
	res = time.isFirstDate('2012-12-28')
	print res	
	res = time.isLastDate('2012-12-28')
	print res
	res = time.isLastDate('2012-05-31')
	print res
	
	print '2012-06-12 next 5 days: %s' % time.getDateNextDays('2012-06-12', 5)
	print '2012-06-22 next 3 days: %s' % time.getDateNextDays('2012-06-22', 3)
	print '2012-12-26 next 5 days: %s' % time.getDateNextDays('2012-12-26', 5)
	
	print '2012-06-12 prev 5 days: %s' % time.getDatePrevDays('2012-06-12', 5)
	print '2012-06-22 prev 3 days: %s' % time.getDatePrevDays('2012-06-22', 3)
	print '2012-05-31 prev 5 days: %s' % time.getDatePrevDays('2012-05-31', 5)

if __name__=='__main__':
	test_date()