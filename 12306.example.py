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
备注：
"""
from splinter.browser import Browser
from time import sleep
import traceback
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import os

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
        self.order = str(order)                  # 车次，0代表所有车次
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
        sleep(1)
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
            s = smtplib.SMTP('发件邮箱服务器', 25)               # 根据所用邮箱来选择
            # s = smtplib.SMTP_SSL('发件邮箱服务器', 465)
            s.login(send_email, '发件邮箱密码')                  # 登录邮箱，这里的第二个参数为qq邮箱授权码，不要填你的登录密码
            s.sendmail(send_email, [self.to_email, ], msg.as_string())  # 发送方，接收方，发送消息
            s.quit()                                            # 退出邮箱
            print("抢票通知邮件发送成功！")
        except Exception as e:
            print("邮件发送失败~~", e)

    # 点击功能
    def click(self, element):
        while True:
            try:
                element.click()
                break
            except:
                continue


    # 买票功能实现
    def start_buy(self):
        self.driver = Browser(driver_name=self.driver_name, executable_path=self.executable_path)
        # 窗口大小的操作
        self.driver.driver.set_window_size(1200,960)
        self.login()
        self.driver.visit(self.ticket_url)
        try:
            if True:
                print('开始刷票...')
                # 加载查询信息
                self.driver.cookies.add({"_jc_save_fromStation": self.starts})
                self.driver.cookies.add({"_jc_save_toStation": self.ends})
                self.driver.cookies.add({"_jc_save_fromDate": self.dtime})
                self.driver.reload()
                sleep(1)
                count = 0
                if self.order == '0':
                    while self.driver.url == self.ticket_url:
                        self.click(self.driver.find_by_id('query_ticket'))
                        count += 1
                        print('第%d次点击查询...' % count)
                        sleep(self.req)
                        i = 0
                        try:
                            flag = False
                            for tr in self.driver.find_by_id('queryLeftTable').find_by_tag('tr'):
                                if i%2==0:
                                    td = tr.find_by_tag('td')[site_type[self.type][0]]
                                    # print(td.html)
                                    if '-' in td.html or '无' in td.html or '*' in td.html:
                                        pass
                                    else:
                                        self.click(self.driver.find_by_id('queryLeftTable').find_by_tag('tr')[i].find_by_text('预订'))
                                        print('已选车次：', tr.find_by_tag('a')[0].html, self.type)
                                        flag = True
                                        break   # 跳出for循环
                                i += 1
                            if True:
                                break   # 跳出while循环
                        except Exception as e:
                            print(e, '预订失败...')
                            continue
                        # sleep(self.req)
                else:
                    while self.driver.url == self.ticket_url:
                        self.click(self.driver.find_by_id('query_ticket'))
                        count += 1
                        print('第%d次点击查询...' % count)
                        sleep(self.req)
                        i = 0
                        try:
                            tr = self.driver.find_by_id('queryLeftTable').find_by_tag('tr')[(int(self.order)-1)*2]
                            td = tr.find_by_tag('td')[site_type[self.type][0]]
                            if '-' in td.html or '无' in td.html or '*' in td.html:
                                pass
                            else:
                                self.click(tr.find_by_text('预订'))
                                break
                        except Exception as e:
                            print(e, '预订失败...')
                            continue
                        # sleep(self.req)
                sleep(2)
                print('开始预订...')
                print('选择乘车人：', self.passengers)
                i = 1
                for p in self.passengers:
                    self.click(self.driver.find_by_text(p).last)
                    site_value = site_type[self.type][1]
                    if '学生' in p and site_type[self.type][0]<3:    # 学生票无法买二等以上的票，默认按可买票下订单
                        site_value = None
                    sleep(0.5)
                    if p[-1] == ')':
                        self.click(self.driver.find_by_id('dialog_xsertcj_ok'))
                    type = self.driver.find_by_id('seatType_'+str(i))
                    if not site_value:
                        self.click(type.find_by_tag('option')[0])
                    elif type.find_by_value(site_value):
                        self.click(type.find_by_value(site_value))
                    i += 1
                sleep(2)
                print('提交订单...')
                self.click(self.driver.find_by_id('submitOrder_id'))
                sleep(1)
                print('确认选座...')
                self.click(self.driver.find_by_id('qr_submit_id'))
                print('预订成功...')
                self.sendMail()
        except Exception as e:
            print(e)

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
        exit(-1)
    from_ = start.encode('unicode_escape').decode().replace('\\', '%')+'%2c'+from_
    to_ = end.encode('unicode_escape').decode().replace('\\', '%')+'%2c'+to_
    return from_, to_

if __name__ == '__main__':
    _ = os.system('cls')
    username = input('用户名：').replace(' ', '')   # 用户名
    password = input('密码：').replace(' ','')      # 密码
    order = input('车次序号【0代表全部车次】：').replace(' ', '')           # 车次选择，0代表所有车次
    type_ = input('车票类型【无座/硬座/软座/硬卧/动卧/软卧/高级软卧/一等/二等/商务】：').replace(' ', '')   # 车票类型，0:无座 1:硬座 2:软座 3:硬卧 5:软卧
    passengers = input('乘车人【学生票输入示例：张三(学生)】,多个人用+隔开：').replace(' ', '')
    passengers = passengers.split('+')
    dtime = input('乘车日期【示例：2019-01-30】：').replace(' ', '')
    start = input('起始站：').replace(' ', '')
    end   = input('终到站：').replace(' ', '')
    myemail = input('用于接收邮件的邮箱(请将public@archiew.top设置为白名单)：').replace(' ', '')
    frq = float(input('刷票频率(1.0~5.0)秒：'))
    _ = os.system('cls')

    start,end = getStation(start, end)

    Buy_Tickets(username, password, order, type_, passengers, dtime, start, end, myemail, frq).start_buy()

