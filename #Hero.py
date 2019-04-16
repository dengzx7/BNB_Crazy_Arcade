import json

data = {
	'bubble_nums':		1,						# 初始泡泡数量
	'max_bubble_nums':	5,						# 最大泡泡数量
	'speed':			1.25,					# 初始速度
	'max_speed':		2.25,					# 最大速度
	'power':			1,						# 初始泡泡威力
	'max_power':		6,						# 最大泡泡威力
}
data_dic = {
	'bazzi': 	[1, 5, 1.50, 3.25, 1, 6],
	'cappi':	[1, 5, 1.25, 2.50, 2, 7],
	'luxcappi':	[2, 6, 1.50, 3.00, 2, 8], 
	'marid':	[2, 6, 1.25, 2.75, 1, 7],	
	'luxmarid':	[3, 7, 1.50, 3.00, 1, 7],
	'dao':		[2, 6, 1.25, 2.75, 1, 7],
}
 
filename = 'data\\hero.json'
with open(filename, 'w') as f_obj:
	json.dump(data_dic, f_obj)