#! /usr/bin/python

import sys
sys.path.append('..')

from misc.elemmap import ElementMap

def doTest():
	elems = ElementMap()
	elems.addElement(1, 'hello')
	elems.addElement(2, 'world')
	elems.addElement(3, '!!!')
	
	print elems.elemDict
	
	elems.updateElement(3, '~~~')
	
	print elems.getElement(3)
	
	print elems.isElementExisted(3)
	print elems.isElementExisted(str(3))
	
	elems.delElement(3)
	
	print elems.elemDict
	
	elems.delElement(4)
		
if __name__ == '__main__':
	doTest()
