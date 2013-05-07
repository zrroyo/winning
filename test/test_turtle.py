#! /usr/bin/python

import sys
sys.path.append('..')
import strategy.turtle as Turt

turt = Turt.Turtle('m1305', 'm1305_k_test', 'm1305_trade_rec', 'futures')

#tr = turt.tr('2012-12-28')
#print tr

#tr = turt.tr('2012-05-31')
#print tr

#turt.updateAtrFromTo('m1305_day_k_test', '2012-05-31', '2012-07-26', 28)

#turt.atr('m1305_day_k_test')
#turt.atr()

#turt.openPosition()

print turt.highestBeforeDate('2012-07-23', 4)
print turt.lowestBeforeDate('2012-07-23', 4)
print turt.highestBeforeDate('2012-07-23', 5)
print turt.lowestBeforeDate('2012-07-23', 5)

