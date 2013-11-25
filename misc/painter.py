#! /usr/bin/python
#-*- coding:utf-8 -*-

import curses
from time import sleep
import locale
locale.setlocale(locale.LC_ALL,"")

#终端描绘对象
class Painter:
	def __init__ (self):
		#初始化curses
		curses.initscr()	#初始化curses
		
	def newWindow (self, height, width, beginY, beginX, border=0):
		win = curses.newwin(height, width, beginY, beginX)
		win.border(border)	#设置边框
		win.move(1,1)		#设置初始光标位置
		win.refresh()
		return win
			
	#描绘一行
	def paintLine (self,
		window,		#描绘窗口
		lineNo, 	#所描绘行
		output		#输出内容
		):
		window.move(lineNo,1)
		window.clrtoeol()
		window.addstr(lineNo, 1, str(output))
		window.refresh()
		
	#使用结束还原原终端
	def destroy (self):
		curses.endwin()
	
## 测试 ##
import sys

def doTest():
	map = {'a':'hello', 'b':'world'}
	mon = Painter()
	window = mon.newWindow(20, 100, 0, 1)
	try:
		mon.paintLine(window, 1, map['a'])
		mon.paintLine(window, 2, map['b'])
		window.getch()
		mon.destroy()
	except:
		mon.destroy()
		
def doTestCurses ():
	##v3
	#myscreen = curses.initscr()
	
	#myscreen.border(0)
	#myscreen.addstr(12, 1, "Python curses in action!")
	#myscreen.addstr(13, 1, "What an amazing Curses!")
	##myscreen.addstr(12, 25, "BADABA")
	#myscreen.refresh()
	#myscreen.getch()
	
	#curses.endwin()
	
	##v1
	#curses.initscr()
	#pad = curses.newpad(100, 100)
	##  These loops fill the pad with letters; this is
	## explained in the next section
	#for y in range(0, 100):
		#for x in range(0, 100):
			#try: pad.addch(y,x, ord('a') + (x*x+y*y) % 26 )
			#except curses.error: pass
	
	##  Displays a section of the pad in the middle of the screen
	#pad.refresh( 0,0, 5,5, 20,75)
	#curses.endwin()
	
	#v2
	##好耶
	#for i in range(1,5):
		#print "\rHello, Gay! ",  i,
		#sys.stdout.flush()
		#sleep(1)
		
	#v4
	screen = curses.initscr()
	#screen.addstr(0, 1, 'Test Curses')
	win1 = curses.newwin(20, 100, 0, 1)
	win1.border(0)
	for x in range(1, 10):
		win1.addstr(x, 1, 'hello world')
	win1.refresh()
	
	win2 = curses.newwin(20, 22, 0, 101)
	win2.border(0)
	for x in range(1, 10):
		win2.addstr(x, 1, 'hello world2')
	win2.refresh()
		
	win3 = curses.newwin(12, 100, 20, 1)
	win3.border(0)
	for x in range(1, 10):
		win3.addstr(x, 1, 'hello world3')
	win3.refresh()
		
	win1.getch()
	curses.endwin()
		
	
if __name__ == '__main__':
	#doTestCurses()
	doTest()
		