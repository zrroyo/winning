#-*- coding:utf-8 -*-

'''
Author: Zhengwang Ruan <ruan.zhengwang@gmail.com>

数据导入子系统命令行处理模块
'''

import sys
sys.path.append('..')
import os

from optparse import OptionParser
from db.sql import *
from misc.debug import *

debug = None	#调试接口

#删除数据表
def doDropTables (
	imp, 	#数据导入接口（IMPORTER）
	tables,	#数据表，以逗号分隔
	):
	tableSet = tables.split(',')
	
	for table in tableSet:
		imp.dropDataTable(table)
		print "Dropped '%s'. " % table

#列出可用的数据表
def doListTables (
	database,	#数据库
	):
	db = SQL()
	db.connect(database)
	
	strSql = 'show tables'
	db.execSql(strSql)
	
	res = list(db.fetch('all'))
	
	print "\nAll tables in '%s:'\n" % database
	for test in res:
		print test[0]
	
	db.close()

#返回指定的数据导入接口
def getImpoter (
	type,		#待导入的数据记录类型
	database,	#待导入的数据库
	dbgMode = False	#是否调试
	):
	#默认类型
	import whHacker
	imp = whHacker.WenhuaHackImporter(database, debug = dbgMode)
	
	if type == 'wh':
		return imp
	elif type == 'tb':
		import tb
		imp = tb.TBImporter(database, debug = dbgMode)
	else:
		debug.dbg("Unsupported data format!")
	
	return imp

#返回数据的类型（文件或目录）
def getSourceType (
	path,	#路径
	):
	if os.path.isfile(path):
		return 'file'
	elif os.path.isdir(path):
		return 'directory'
	else:
		return 'Unknown'

#需要数据源
def requireSource (
	source,	#数据源
	):
	if not source:
		debug.error("Date records source is required, '-s file|dir'.")
		return True
	
	return False

#需要数据表
def requireTable (
	table,	#数据表
	):
	if not table:
		debug.error("Destination table is required, '-t table1'.")
		return True
	
	return False

#需要附加参数
def requireExtra (
	extra,	#数据表
	):
	if not table:
		debug.error("Extra info is required, '-e 5/8/2015'.")
		return True
	
	return False

#IMPORTER子系统命令行选项解析主函数
def importerOptionsHandler (
	options,	#命令选项
	args,		#命令参数
	):
	#调试接口
	global debug
	debug = Debug('Import', options.debug)
	
	#数据库名不能为空
	if options.database is None:
		debug.error("Please specify database using '-b'.")
		return
	
	#得到与数据类型对应的导入接口
	imp = getImpoter(type = options.type, 
			database = options.database,
			dbgMode = options.debug)
	if imp is None:
		return
	
	#依指定删除数据表
	if options.drop:
		debug.dbg("Dropping '%s' from database '%s'..." % (options.drop, options.database))
		doDropTables(imp, options.drop)
	
	#列出可用数据库
	if options.list:
		doListTables (options.database)
		return
	
	'''
	依工作模式完成不同操作
	'''
	
	source = options.source
	table = options.table
	extra = options.extra
	
	if options.mode == 'new':
		'''
		从数据文件导入新表
		'''
		#数据源和目的数据表必须指定
		if (requireSource(source) or requireTable(table)):
			return
		
		#数据源必须为文件
		if getSourceType(source) != 'file':
			debug.error("A data records file is required.")
			return
		
		print "\nImporting records from '%s' to '%s'...\n" % (source, table)
		
		#调用导入接口导入数据
		return imp.newImport(file = source, 
					table = table, 
					timeFilters = extra)
		
	elif options.mode == 'append':
		'''
		从数据文件或目录追加数据
		'''
		#数据源必须指定
		if (requireSource(source)):
			return
		
		#不同的数据源对应不同模式
		sourceType = getSourceType(source)
		if sourceType == 'file':
			#数据表必须指定
			if (requireTable(table)):
				return
			
			return imp.appendRecordsFromFile(file = source, 
							table = table, 
							endTime = extra)
		elif sourceType == 'directory':
			return imp.appendRecordsFromDir(directory = source, 
							endTime = extra)
		else:
			debug.error("Found bad source type, only a file or directory is valid.")
			return
		
	elif options.mode == 'update':
		'''
		依数据文件记录更新数据表
		'''
		#数据源和目的数据表必须指定
		if (requireSource(source) or requireTable(table)):
			return
		
		#数据源必须为文件
		if getSourceType(source) != 'file':
			debug.error("A data records file is required.")
			return
			
		print "\nUpdating records to '%s'...\n" % (table)
		
		#调用导入接口导入数据
		return imp.updateRecordsFromFile(file, table)
		
	elif options.mode == 'subtable':
		'''
		从数据表中提取部分数据生成新表
		'''
		#开始（截止时间）必须指定
		if (requireExtra(extra)):
			debug.error("The time to start (and end) must be given with option '-e'.")
			return
		
		#数据表（源表、目的表）必须指定
		if (requireTable(table)):
			return
		
		table = options.table.split(',')
		if len(table) == 1:
			debug.error("Please specify two data tables like '-t m09,m1309'.")
			return
			
		time = extra.split(',')
		endDate = None
		if len(time) == 2:
			endDate = time[1]
		
		debug.dbg('%s, %s' % (time, table))
		
		print "\nExporting '%s' to '%s' from '%s' to '%s'...\n" % (
				table[0], table[1], time[0], endDate if endDate else 'Now' )
		
		#调用导入接口导入数据
		imp.partReimport(table[0], table[1], time[0], endDate)
		
	elif options.mode is None:
		debug.error("Import mode is required here. ")
	else:
		debug.error("Found unkonwn mode '%s'" % options.mode)

# Importer subsystem Option Parser.
def importerOptionsParser (parser):
	parser.add_option('-b', '--database', dest='database', 
			help='The database in which operations need to be done.')
	parser.add_option('-s', '--source', dest='source', 
			help='The source (file or directory) to import records from.')
	parser.add_option('-t', '--table', dest='table', 
			help='The data table to which to import data records.')
	parser.add_option('-m', '--mode', dest='mode', 
			help='Importer mode: new, append, update, subtable, etc.')
	parser.add_option('-d', '--drop', dest='drop', 
			help='Drop a table from database.')
	parser.add_option('-T', '--type', dest='type', 
			help='The type of the data records to be imported.')
	parser.add_option('-e', '--extra', dest='extra', 
			help='Extra contains details used with other options if needed.')
	parser.add_option('-l', '--list', action="store_true", dest='list', 
			help='List all tables in database.')
	parser.add_option('-D', '--debug', action="store_true", dest='debug', default=False,
			help='Extra contains details used with other options if needed.')
	
	(options, args) = parser.parse_args()

	importerOptionsHandler(options, args)
	