# -*- coding: utf-8 -*-
"""
-------------------------------------------------
作者：pk哥
公众号：Python知识圈
代码解析详见公众号：Python知识圈。
日期：2018/12/31
如疑问或需转载，请联系微信号：dyw520520，备注来意，谢谢。
-------------------------------------------------
修订：Archiew
日期：2019/01/03
备注：优化抢票流程
"""
from splinter.browser import Browser
from time import sleep
import traceback
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import os

# 页面查找元素延时
DELAY = 25
site_type = {
    '无座': (10, '1'),
    '硬座': (9, '1'),
    '软座': (8, '2'),
    '硬卧': (7, '3'),
    '动卧': (6, 'F'),
    '软卧': (5, '4'),
    '高级软卧': (4, '6'),
    '二等': (3, 'O'),
    '一等': (2, 'M'),
    '商务': (1, '9'),
}

# 实现自动购票的类
class Buy_Tickets(object):
    # 定义实例属性，初始化
    def __init__(self, username, passwd, order, type_, passengers, dtime, starts, ends, myemail, req):
        self.username = username
        self.passwd = passwd
        self.order = str(order).upper()     # 车次，0代表所有车次
        self.type = type_
        self.passengers = passengers        # 购票乘客名，学生票需要在名字后面备注，比如：张三(学生)
        self.starts = starts                # 起始站
        self.ends = ends                    # 终到站
        self.dtime = dtime                  # 订票日期
        self.to_email = myemail
        self.req = max(min(5, req), 1)
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.initMy_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
        self.driver_name = 'chrome'
        self.executable_path = r'./chromedriver.exe'

    # 登录功能实现
    def login(self):
        self.driver.visit(self.login_url)
        # sleep(0.5)
        self.driver.fill('loginUserDTO.user_name', self.username)
        self.driver.fill('userDTO.password', self.passwd)
        print('请在浏览器中输入验证码并点击登录...')
        while self.driver.url != self.initMy_url:
            pass
        print('恭喜，完成验证！')

    def sendMail(self):
        mail_title = '抢票成功！赶紧去支付！！'   # 邮件标题
        mail_content = '抢票成功了！赶紧去支付！！抢票成功了！赶紧去支付！！'  # 邮件内容
        send_email = '发件邮箱'
        try:
            msg = MIMEText(mail_content, "plain", 'utf-8')      # 发送邮件内容
            msg["Subject"] = Header(mail_title, 'utf-8')        # 发送邮件主题/标题
            msg["From"] = formataddr([send_email, send_email])  # 邮件发送方
            msg["To"] = formataddr([self.to_email, self.to_email])        # 邮件接收方
            s = smtplib.SMTP('发件邮箱服务器', 25)
            # s = smtplib.SMTP_SSL('发件邮箱服务器', 465)
            s.login(send_email, '发件邮箱密码')                  # 登录邮箱，这里的第二个参数为qq邮箱授权码，不要填你的登录密码
            s.sendmail(send_email, [self.to_email, ], msg.as_string())  # 发送方，接收方，发送消息
            s.quit()                                            # 退出邮箱
            print("抢票通知邮件发送成功！")
        except Exception as e:
            print("邮件发送失败~~", e)

    # 点击功能
    def click(self, element):
        if element:
            # print(element.html)
            element.click()

    # 查找页面元素
    def findelement(self, driver, find_by, element):
        res = None
        count = 0
        while True:
            count += 1
            if count>DELAY:
                print('查找元素超时！')
                break
            sleep(0.2)
            try:
                if find_by == 'id':
                    res = driver.find_by_id(element)
                elif find_by == 'tag':
                    res = driver.find_by_tag(element)
                elif find_by == 'text':
                    res = driver.find_by_text(element)
                elif find_by == 'value':
                    res = driver.find_by_value(element)
                elif find_by == 'xpath':
                    res = driver.find_by_xpath(element)
                break
            except:
                continue
        return res

    # 检查有无余票
    def check_ticket(self):
        # raise Exception
        count = 0
        if self.order == '0':        # 未指定车次序号，按从上到下顺序查找
            while self.driver.url == self.ticket_url:
                count += 1
                self.findelement(self.driver,'id','query_ticket').click()
                sleep(self.req)
                print('第%d次查询...'%count)
                i = 0
                table = self.findelement(self.driver, 'id', 'queryLeftTable')
                trs = self.findelement(table,'tag','tr')
                if trs:
                    for tr in trs:
                        if i%2==0:
                            td = self.findelement(tr,'tag','td')[site_type[self.type][0]]
                            # print(td.html)
                            if '-' in td.html or '无' in td.html or '*' in td.html:    # 无票
                                pass
                            else:
                                tr = self.findelement(table,'tag','tr')[i]
                                print('已选车次：', self.findelement(tr,'tag','a')[0].html)
                                tr = self.findelement(table,'tag','tr')[i]
                                self.findelement(tr,'text','预订').click()
                                return
                        i += 1
        else:
            while self.driver.url == self.ticket_url:
                count += 1
                self.click(self.findelement(self.driver,'id','query_ticket'))
                sleep(self.req)
                print('第%d次查询...'%count)
                flag = True
                i = 0
                table = self.findelement(self.driver, 'id', 'queryLeftTable')
                tr = self.findelement(table,'xpath','//tr[contains(@id,"%s")]'%self.order)    # 选定order车次对应的tr
                if not tr:
                    continue
                tr = tr[0]
                td = self.findelement(tr,'tag','td')[site_type[self.type][0]]
                if '-' in td.html or '无' in td.html or '*' in td.html:    # 无票
                    pass
                else:
                    print('已选车次：', self.findelement(tr,'tag','a')[0].html)
                    self.findelement(tr,'text','预订').click()
                    return

    # 订票
    def book_ticket(self):
        print('开始预订...')
        i = 1
        for p in self.passengers:
            print(p)
            self.findelement(self.driver,'text',p).click()
            site_value = site_type[self.type][1]
            if '学生' in p and site_type[self.type][0]<3:    # 学生票无法买二等以上的票，默认按可买票下订单
                site_value = None
            if '学生' in p:
                self.click(self.findelement(self.driver,'id','dialog_xsertcj_ok'))
            seatype = self.findelement(self.driver,'id','seatType_'+str(i))
            if not site_value:
                self.click(self.findelement(seatype,'tag','option')[0])
            elif self.findelement(seatype,'value',site_value):
                self.click(self.findelement(seatype,'value',site_value))
            i += 1
        print('提交订单...')
        self.click(self.findelement(self.driver,'id','submitOrder_id'))
        sleep(1)
        print('确认选座...')
        self.click(self.findelement(self.driver,'id','qr_submit_id'))
        print('预订成功...')
        self.sendMail()

    # 买票功能实现
    def start_buy(self):
        self.driver = Browser(driver_name=self.driver_name, executable_path=self.executable_path)
        self.driver.driver.set_window_size(1080,720)
        self.login()
        self.driver.visit(self.ticket_url)
        sleep(1)
        self.driver.cookies.add({"_jc_save_fromStation": self.starts})
        self.driver.cookies.add({"_jc_save_toStation": self.ends})
        self.driver.cookies.add({"_jc_save_fromDate": self.dtime})
        self.driver.reload()
        print('开始刷票...')
        sleep(1)
        self.check_ticket()
        sleep(1.5)
        self.book_ticket()


# 获得站台编码
def getStation(start, end):
    from_ = ''
    to_ = ''
    with open(r'./station_name.js', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if not from_ and start in line:
                from_ = line.split('|')[2]
            elif not to_ and end in line:
                to_ = line.split('|')[2]
    if not from_ or not to_:
        print('车站输入错误！')
        return None, None
    from_ = start.encode('unicode_escape').decode().replace('\\', '%')+'%2c'+from_
    to_ = end.encode('unicode_escape').decode().replace('\\', '%')+'%2c'+to_
    return from_, to_

if __name__ == '__main__':
    _ = os.system('TASKKILL /F /IM chromedriver.exe')
    _ = os.system('cls')
    print('=======================================')
    print('=====        12306抢票助手        =====')
    print('=====           Archiew           =====')
    print('===== 问题反馈：admin@archiew.top =====')
    print('=======================================')
    try:
        username = input('登录名：').replace(' ', '')   # 用户名
        password = input('密码：').replace(' ','')      # 密码
        order = input('车次【0代表全部车次】：').replace(' ', '')           # 车次选择，0代表所有车次
        type_ = input('车票类型【无座/硬座/软座/硬卧/动卧/软卧/高级软卧/一等/二等/商务】：').replace(' ', '')   # 车票类型，0:无座 1:硬座 2:软座 3:硬卧 5:软卧
        passengers = input('乘车人【学生票输入示例：张三(学生)】,多个人用+隔开：').replace(' ', '')
        passengers = passengers.split('+')
        dtime = input('乘车日期【示例：2019-01-30】：').replace(' ', '')
        while True:
            start = input('起始站【示例：北京】：').replace(' ', '')
            end   = input('终到站：').replace(' ', '')
            station = getStation(start, end)
            if None not in station:
                break
        myemail = input('用于接收邮件的邮箱(请将public@archiew.top设置为白名单)：').replace(' ', '')
        frq = input('刷票频率(1.0~5.0)秒：').strip()
        if frq == '':
            frq = 1.0
        else:
            frq = float(frq)
        _ = os.system('cls')
        Buy_Tickets(username, password, order, type_, passengers, dtime, station[0], station[1], myemail, frq).start_buy()
    except Exception as e:
        print(e)
        sleep(30)