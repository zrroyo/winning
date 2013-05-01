#!/usr/bin/python

import sys
sys.path.append('..')
import strategy.turt1 as TURT

#turt = TURT.Turt1('m1305', 'm1305_k_test', 'm1305_trade_rec', 'futures')
#turt.query()
#print turt.dataTable, turt.database, turt.tradeTable
#print turt.test

#turt.atr('m1305_day_k_test')
#turt.atr()


#print turt.dateSet.curDate(), turt.dateSet.getSetNextDate(), turt.dateSet.getSetNextDate()
#time = turt.dateSet
#print time.curDate()
#time.setCurDate('2012-07-23')
#print time.curDate(), turt.dateSet.curDate()

#turt.Test()

#turt = TURT.Turt1('m1305', 'm1305_k_test', 'm1305_trade_rec', 'futures')
#turt.setAttrs(3, 1, 40)
##turt.setAttrs(3, 1, 80)
##turt.setAttrs(3, 1, 120)
#turt.run()
#turt.showProfit()

turt = TURT.Turt1('rb1309', 'rb09_test', 'rb09_test_rec', 'futures')
turt.setAttrs(3, 1, 40)
#turt.setAttrs(3, 1, 80)
#turt.setAttrs(3, 1, 120)
turt.run()
turt.showProfit()