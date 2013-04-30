#!/usr/bin/python
import sys
sys.path.append("..")
import trade

def test_trade():

	trd = trade.Trade('futures', 'trade_rec1')

	trd.openTrade('T0001', 'm1305', '2013-1-14 14:35:48', 'D', '1,2,3', 3360, 3, 'Increase greatly', 0, 'Danger')
	trd.openDTrade('T0001', 'm1305', '2013-1-14 14:35:48', '1,2,3', 3360, 3, 'Increase greatly', 0, 'Danger')
	trd.tradeOver('T0001', 'm1305', '2013-1-17 14:35:38', 'D', '2,3', 3390, 2)

	trd.openTrade('T0002', 'm1305', '2013-1-18 14:35:48', 'K', '1,2', 3350, 2, 'Descrease sharply', 0, 'Danger')
	trd.openKTrade('T0002', 'm1305', '2013-1-18 14:35:48', '1,2', 3350, 2, 'Descrease sharply', 0, 'Danger')
	trd.tradeOver('T0002', 'm1305', '2013-1-19 14:35:38', 'K', '2', 3390, 1)

if __name__ == '__main__':
	test_trade()
