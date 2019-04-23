# BNB_Crazy_Arcade
SYSU Python Game Project<br>
基于pygame的集单人、联网、休闲模式于一体的泡泡堂游戏

## 项目成员与分工
* 邓宗湘：道具模块(props)、AI模块(AIModel)
* 杨仲恒：泡泡模块(bubbles)、联机模式(netMode)
* 姚振杰：地图模块(plats)、休闲模式(pushBoxMode)
* 张仲岳：人物模块(characters)、UI及动画设计

## 项目环境
编程语言：python3.6<br>
游戏框架：python pygame<br>
操作系统：Windows 10<br>

## 运行方式
Clone后在当前目录下执行命令
* 单人模式
```
> python BNB.py
```
* 联机模式
打开cmd执行ipconfig找到本机的ipv4地址，将settings.py文件下的server_name列表中的ip地址替换为本机的ipv4地址，接着执行命令<br>
```
> python server.py
```
此时可以看到如下图，表明server已经打开。<br>
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%87%86%E5%A4%87%E5%B0%B1%E7%BB%AA.PNG" width="400">
</div>

接着再次打开cmd窗口cd到文件目录，按照玩家数量依次执行client.py。<br>
例如**双人对战**，需要依次重新打开cmd窗口到文件目录，并执行如下命令<br>
```
> python client1.py
> python client2.py
```

对client1选择 联机模式->创建房间<br>
对client2选择 联机模式->更新房间->进入已创建的房间<br>
最终两个玩家进入了同一个游戏房间，接着就可以开始游戏实现双人对战了。<br>
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E8%81%94%E6%9C%BA%E6%A8%A1%E5%BC%8F%E6%88%BF%E9%97%B4.PNG" width="700">
</div>

## 项目功能
我们根据实际，实现了以下功能的需求。
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E5%8A%9F%E8%83%BD%E8%A1%A8.png" width="800">
</div>

## 系统框图
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E7%B3%BB%E7%BB%9F%E6%A1%86%E5%9B%BE.png" width="600">
</div>

## 项目展示
### 游戏界面
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E6%B8%B8%E6%88%8F%E7%95%8C%E9%9D%A2.PNG" width="700">
</div>

### 单人模式
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E5%8D%95%E4%BA%BA%E6%A8%A1%E5%BC%8F1.PNG" width="700">
</div>
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E5%8D%95%E4%BA%BA%E6%A8%A1%E5%BC%8F2.PNG" width="700">
</div>
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E5%8D%95%E4%BA%BA%E6%A8%A1%E5%BC%8F3.PNG" width="700">
</div>
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E5%8D%95%E4%BA%BA%E6%A8%A1%E5%BC%8F4.PNG" width="700">
</div>

### 联机模式
(image)

### 休闲模式
<div align=center>
<img src="https://github.com/dengzx7/BNB_Crazy_Arcade/blob/master/images2/%E4%BC%91%E9%97%B2%E6%A8%A1%E5%BC%8F.PNG" width="700">
</div>



