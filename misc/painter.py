#! /usr/bin/python
#-*- coding:utf-8 -*-

import curses
from time import sleep
#import locale
#locale.setlocale(locale.LC_ALL,"en_US.zh_CN")

#终端描绘对象
class Painter:
	def __init__ (self, poll, callback, revert=False):
		self.poll = poll
		self.callback = callback
		self.revert = revert
		self.__newPainter()
		
	#初始化curses
	def __newPainter (self, border=0):
		self.screen = curses.initscr()	#初始化curses
		self.screen.border(border)	#设置边框
		self.screen.move(1,1)		#设置初始光标位置
		
	#描绘一行
	def paintLine (self, 
		lineNo, 	#所描绘行
		output		#输出内容
		):
		self.screen.clrtoeol()
		self.screen.addstr(lineNo, 1, str(output))
		self.screen.refresh()
			
	#显示／描绘内容池里边的所有内容
	def display (self, lineStart=0):
		keys = self.poll.keys()
		if self.revert:
			keys.reverse()
		
		#self.screen.clear()
		#print keys
		i = lineStart
		for k in keys:
			try:
				#print k, self.poll[k]
				output = self.callback(self.poll[k])
				#print output
				i += 1
				self.paintLine(i, output)
			except:
				print 'Painter Exception'
				curses.endwin()
		
		#self.screen.refresh()
		
	#使用结束还原原终端
	def destroy (self):
		curses.endwin()
	
## 测试 ##
import sys

def simplePrint(a):
	return a

def doTest():
	map = {'a':'hello', 'b':'world'}
	mon = Painter(map, simplePrint, True)
	mon.display()
	sleep(5)
	mon.destroy()
	
		
def doTestCurses ():
	#v3
	myscreen = curses.initscr()
	
	myscreen.border(0)
	myscreen.addstr(12, 1, "Python curses in action!")
	myscreen.addstr(13, 1, "What an amazing Curses!")
	#myscreen.addstr(12, 25, "BADABA")
	myscreen.refresh()
	myscreen.getch()
	
	curses.endwin()
	
	#v1
	#pad = curses.newpad(100, 100)
	##  These loops fill the pad with letters; this is
	## explained in the next section
	#for y in range(0, 100):
		#for x in range(0, 100):
			#try: pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
			#except curses.error: pass
	
	##  Displays a section of the pad in the middle of the screen
	#pad.refresh( 0,0, 5,5, 20,75)
	
	#v2
	##好耶
	#for i in range(1,5):
		#print "\rHello, Gay! ",  i,
		#sys.stdout.flush()
		#sleep(1)
		
	
if __name__ == '__main__':
	#doTestCurses()
	doTest()
		