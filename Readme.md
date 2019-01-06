12306抢票小程序
===
### requirments:
```
altgraph==0.16.1
future==0.17.1
macholib==1.11
pefile==2018.8.8
PyInstaller==3.4
pywin32-ctypes==0.2.0
selenium==3.141.0
six==1.12.0
splinter==0.10.0
urllib3==1.24.1
```
[chromedriver.exe](http://npm.taobao.org/mirrors/chromedriver/)

### 说明
本代码是在pk哥(公众号：Python知识圈)已有代码基础上做了修改，现已具备以下功能：  
>12306网站登录  
>可选车次、车票类型、乘车人、乘车日期、起始站点、抢票频率(1.0~5.0s)  
>抢到票后邮件通知  

`station_name.js`文件是从12306官网下载的用于对输入的车站名进行编码转换的文件。

### 思路
借助splinter和chromedriver.exe进行自动化操作，除登录验证码需要人为操作外，整个抢票过程全都是自动化完成。  
登录部分是通过自动化输入用户名和密码实现。  
抢票过程：  
将起始站和乘车日期信息写进cookies中，点击`查询`按钮，根据查询结果和输入的信息进行抢票。  
抢到票后直接下单，并通过邮件通知。  
