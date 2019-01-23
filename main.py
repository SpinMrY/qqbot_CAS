import re
import os
import json
import time
import urllib
import random
import requests
import websocket
import threading
import subprocess

qbot_api_event_url="ws://"
qbot_api_post_url="http://"

MasterID = ''
calc_index = 0

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

def qbot_send_msg(user_id, message):
    print("\n<send_private_msg>")
    print("posting private message")    
    print(message)
    post = qbot_api_post_url + "send_msg"
    api_payload = {
        'user_id': user_id,
        'message': message
    }
    res = requests.post(post, data=api_payload)
    print(res)
    print('</send_private_msg>\n')

def qbot_send_gmsg(group_id, message):
    print("\n<send_group_msg>")
    print("posting group message")    
    print(message)
    post = qbot_api_post_url + "send_group_msg"
    api_payload = {
        'group_id': group_id,
        'message': message
    }
    res = requests.post(post, data=api_payload)
    print(res)
    print('</send_group_msg>\n')

class ext_calc:
    def __init__(self, expr):
        self.status = 1
        start_index = expr.find('calc ')
        words = [ 'system', 'do', 'while', 'if', 'block', 'read', 'stringout', 'system', 'file']
        for word in words:
            if word in expr:
                self.status = -1
                self.result = '噫,你想对咱做什么!'
        expr = expr[start_index+5:]
        print(expr)
        self.expr = expr

    def getret(self):
        #写的十分丑陋,勿喷QAQ
        if self.status == -1:
            return
        global calc_index
        calc_index = calc_index + 1
        file_name = "tmpfile" + str(calc_index)
        cmd = 'stringout("%s",%s);quit();\r' % (file_name,self.expr)
        cmd = 'echo "' + cmd + '" | maxima'
        print(cmd)
        result = subprocess.getoutput(cmd)
        result = subprocess.getoutput('cat \$' + file_name)
        if len(result) == 0 or 'cat:' in result:
            self.result = '咱还计算不出来你写的东西呢'
            return
        self.result = result.replace('\n','').replace(';','')
        os.system("rm \$tmpfile*")
        
class ext_ipip:
    def __init__(self, ipaddr):
        start_index = ipaddr.index("ip")
        ip = ipaddr[start_index+2:].replace(" ", "")
        self.addr = ip
        self.result = '您要查询的地址为 ' + str(self.addr) + '\n'

    def get_ip_info(self):
        FFhead={}
        FFhead['User-Agent'] = random.choice(USER_AGENTS)
        r = requests.get('https://www.ipip.net/ip/{}.html'.format(self.addr), headers = FFhead).text
        address = re.search(r'地理位置.*?;">(.*?)</span>', r, re.S)
        operator = re.search(r'运营商.*?;">(.*?)</span>', r, re.S)
        time = re.search(r'时区.*?;">(.*?)</span>', r, re.S)
        wrap = re.search(r'地区中心经纬度.*?;">(.*?)</span>', r, re.S)
        if address:
            ip_info = '\n咱在ipip.net上查到了呢\n查询地址 : ' + self.addr + '\n' + '地理位置 : ' + address.group(1) + '\n'
            if operator:
                ip_info = ip_info + '所有者/运营商 : ' + operator.group(1) + '\n'
            if time:
                ip_info = ip_info + '时区 : ' + time.group(1) + '\n'
            if wrap:
                ip_info = ip_info + '地区中心经纬度:' + wrap.group(1) + '\n'
            self.result = ip_info.strip('\n')
        else:
            self.result = "查询失败...咱也不知道这个地址在哪里呢~"    
            
class qbot_event:
    def __init__(self, source_json):
        print("\n<process_event>\n")
        event_json = json.loads(source_json)
        self.post_type = event_json['post_type']
        print(event_json)
        if event_json['post_type'] == 'message':
            message = event_json
            self.msg_type = message['message_type']
            self.sender = message['sender']['user_id']
            if self.msg_type == 'group':
                self.group_id = message['group_id']
            else:
                self.group_id = 0
            self.msg = message['message']
            if self.sender == MasterID:
                self.is_master == True
        elif event_json['post_type'] == 'request':
            self.req_type = event_json['request_type']
            self.flag = event_json['flag']

    def process_request(self):
        if self.req_type == 'friend':
            post = qbot_api_post_url + "set_friend_add_request"
        elif self.req_type == 'group':
            post = qbot_api_post_url + "set_group_add_request"
        
        print("\n<receive_request>")
        print("receive a new request!")    
        api_payload = {
            'flag': self.flag,
            'approve': True,
            'remark' : 'qbot添加好友'
        }
        res = requests.post(post, data=api_payload)
        print(res)
        print('</receive_request>\n')
        print('\n</process_event>')

        
    def process_message(self):
        print('sender:' + str(self.sender))
        print('send message:' + self.msg)
        print('send group id:' + str(self.group_id))
        
        if (self.msg[0] == '%'):
            msg = self.msg
            if '%ip' in msg:
                query_ip = ext_ipip(msg)
                query_ip.get_ip_info()
                print(query_ip.result)
                if self.msg_type == 'group':
                    qbot_send_gmsg(self.group_id, query_ip.result)
                elif self.msg_type == 'private':
                    qbot_send_msg(self.sender, query_ip.result)
            elif '%calc' in msg:
                calc = ext_calc(msg)
                calc.getret()
                if self.msg_type == 'group':
                    qbot_send_gmsg(self.group_id, calc.result)
                elif self.msg_type == 'private':
                    qbot_send_msg(self.sender, calc.result)
                     
            elif '%image' in msg:
                pass

            elif '%help' in msg:
                message = '咱是spinmry计算姬β1.0!用法如下:\n<计算代数系统>\n%calc [表达式]\n<IP信息查询>\n%ip [IP地址/域名]\n咱还会继续努力学会更多新技能的!'
                if self.msg_type == 'group':
                    qbot_send_gmsg(self.group_id, message)
                elif self.msg_type == 'private':
                    qbot_send_msg(self.sender, message)
                    
            else:
                if self.msg_type == 'group':
                    qbot_send_gmsg(self.group_id, "咱不知道你在说什么呢?")
                elif self.msg_type == 'private':
                    qbot_send_msg(self.sender, "咱不知道你在说什么呢?")
        print('\n</process_event>')

def qbot_listen_process(event):
    event = qbot_event(event)
    if event.post_type == 'request':
        event.process_request()
    elif event.post_type == 'message':
        event.process_message()

def qbot_listen_on_message(event_ws, event):
    th = threading.Thread(target=qbot_listen_process, name="NewEvent", args=(event,))
    th.start()
    
def qbot_listen_on_error(event_ws, error):
    print(error)

def qbot_listen_on_close(event_ws):
    print("API Websocket closed.")

def main():
    websocket.enableTrace(True)
    event_ws = websocket.WebSocketApp(
        qbot_api_event_url,
        on_message = qbot_listen_on_message,
        on_error = qbot_listen_on_error,
        on_close = qbot_listen_on_close
    )
    event_ws.run_forever()

main()
