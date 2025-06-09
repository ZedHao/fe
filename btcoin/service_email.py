import quopri
import re
import time
import poplib
from email.parser import BytesParser
from email import policy
from loguru import logger
import imaplib
from bs4 import BeautifulSoup

import email

import socks

import socket

import helper_sleep

# # 邮件服务器配置
# # 这两个能不能买号
IMAP_CONFIG = {
    'outlook.com': 'outlook.office365.com',
    'hotmail.com': 'imap-mail.outlook.com',
}


# 没有http请求，没有dao层了
class ServiceEmail:
    def __init__(self, cur_email_address: str, cur_email_password: str):
        # 设置代理
        # 先写死了
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 7890)
        socket.socket = socks.socksocket

        if cur_email_address is None or cur_email_password is None:
            raise Exception("email_address or email_password is None")
        if cur_email_address == '' or cur_email_password == '':
            raise Exception("email_address or email_password is emtpy")

        self.__email_address = cur_email_address
        self.__email_password = cur_email_password

        self._init_support_domain()
        self._is_support_domain()

        logger.info(f"ServiceEmail init email_address={self.__email_address} email_password={self.__email_password}")

    def _init_support_domain(self):
        # 'outlook.com' 已经无法支持了

        self._support_domain_list = [

            # 为啥firstmail的域名是这么奇怪，算了
            'bulletsmail.com',
            'fabrikamail.com',
            'exartimail.com',
            'santalmail.com', #这个域名被银河禁止了

            'firstmailler.net',
            'dfirstmail.com',
            'firstmailler.com',
            'raymanmail.com',
            'bfirstmail.com',
        ]


    def _is_support_domain(self):
        domain_name = self.__email_address.split('@')[-1]
        logger.info(f"get_galxe_code domain_name={domain_name}")
        if domain_name in self._support_domain_list:
            return
        else:
            raise  Exception(f'邮箱域名不支持 self.__email_address({self.__email_address}) self.__email_password({self.__email_password})')




    # 俄罗斯人的邮箱
    # 就最优先用这个，先用起来
    def _get_galxe_code_from_rambler(self):
        logger.info(f"rambler Started searching for messages from email...")

        domain_name = self.__email_address.split('@')[-1]
        logger.info(f"get_email_code_from_rambler domain_name={domain_name}")

        host = f'imap.{domain_name}'
        logger.info(f"get_email_code_from_rambler host={host}")

        # 设置上超时时间，才能成功链接
        rambler_client = imaplib.IMAP4_SSL(host, timeout=10)

        rambler_client.login(self.__email_address, self.__email_password)

        res, data = rambler_client.select()
        last_message_number = data[0].decode().split()[0]

        status, message_fetch = rambler_client.fetch(f"{last_message_number}", '(RFC822)')
        logger.info(f"从邮箱获取的原始信息 status={status} message_fetch={message_fetch}")

        # 这里ide提示问题，但是其实没问题
        message_contain_galxe = message_fetch[0][1]
        logger.info(f"按某种规则选择含有银河验证码的信息 message_contain_galxe={message_contain_galxe}")

        message_from_bytes = email.message_from_bytes(message_contain_galxe)
        logger.info(f"经过了byte转换的信息 message_from_bytes={message_from_bytes}")


        # 解析页面
        soup = BeautifulSoup(message_from_bytes.as_string(), 'html.parser')

        # 我自己试了试在p标签里面，而不是h1标签
        code_ret = soup.find('p').text

        logger.info(f"code_ret={code_ret} code_ret_type={type(code_ret)}")

        return code_ret

    # 放弃俄罗斯邮箱，使用微软邮箱
    # 根据卖号客服，最近微软服务器故障，所以难以使用了
    def get_galxe_code_from_outlook_with_IMAP(self):

        domain_name = self.__email_address.split('@')[-1]
        logger.info(f"get_galxe_code_from_outlook_with_IMAP domain_name={domain_name}")

        # host = 'imap-mail.outlook.com' # 买邮箱那边的host是这个，跟原代码里面的host不一样
        host = 'outlook.office365.com'  # 原代码是这个，chatgpt也推荐这个
        logger.info(f"get_galxe_code_from_outlook_with_IMAP host={host}")

        # 设置上超时时间，才能成功链接
        cur_client = imaplib.IMAP4_SSL(host, timeout=10)

        # notice 一直报错LOGIN failed，无法解决，卖号客服说是微短官方有问题，
        cur_client.login(self.__email_address, self.__email_password)

        res, data = cur_client.select()
        last_message_number = data[0].decode().split()[0]

        status, message_fetch = cur_client.fetch(f"{last_message_number}", '(RFC822)')
        logger.info(f"从邮箱获取的原始信息 status={status} message_fetch={message_fetch}")

        # 这里ide提示问题，但是其实没问题
        message_contain_galxe = message_fetch[0][1]
        logger.info(f"按某种规则选择含有银河验证码的信息 message_contain_galxe={message_contain_galxe}")

        message_from_bytes = email.message_from_bytes(message_contain_galxe)
        logger.info(f"经过了byte转换的信息 message_from_bytes={message_from_bytes}")

        # 解析页面
        soup = BeautifulSoup(message_from_bytes.as_string(), 'html.parser')

        # 我自己试了试在p标签里面，而不是h1标签
        code_ret = soup.find('p').text

        logger.info(f"get_galxe_code_from_outlook_with_IMAP code_ret={code_ret} code_ret_type={type(code_ret)}")

        return code_ret


    def _get_email_from_firstmail_with_IMAP_with_retry(self):
        max_attempts = 3  # 最大尝试次数
        for attempt in range(max_attempts):
            try:
                return self._get_email_from_firstmail_with_IMAP()
            except Exception as e:
                e_type = type(e).__name__
                e_str = str(e)
                logger.error(f" e_type({e_type}) e_str({e_str})")

                if 'EOF occurred in violation of protocol' in str(e) or \
                        e_type == 'TimeoutError':
                    logger.warning(f" 已尝试次数attempt({attempt + 1}) e({e})")
                    if attempt < max_attempts - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, f'_get_email_from_firstmail_with_IMAP_with_retry 重试中 attempt({attempt})')  # 计算等待时间并等待
                    else:
                        logger.error(f" 最大重试次数已达，仍不成功")
                        raise
                else:
                    logger.error(f"其他异常，不重试 失败,e({e})")
                    raise


    def _get_email_from_firstmail_with_IMAP(self):

        host = 'imap.firstmail.ltd'

        cur_client = imaplib.IMAP4_SSL(host, timeout=10)  # 设置上超时时间，才能成功链接

        cur_client.login(self.__email_address, self.__email_password)

        res, data = cur_client.select()
        last_message_number = data[0].decode().split()[0]
        logger.info(f'last_message_number({last_message_number})')

        if  last_message_number == '0':
            helper_sleep.wait_a_bit(20,'如果是0就返回上层再等等')
            return

        status, message_fetch = cur_client.fetch(f"{last_message_number}", '(RFC822)')
        logger.info(f"从邮箱获取的原始信息 status={status} message_fetch={message_fetch}")

        # 这里ide提示问题，但是其实没问题
        message_contain_galxe = message_fetch[0][1]
        logger.info(f"按某种规则选择含有银河验证码的信息 message_contain_galxe={message_contain_galxe}")

        decoded_body = quopri.decodestring(message_contain_galxe).decode('utf-8', errors='replace')
        logger.info(f"消除等于号试试 decoded_body={decoded_body}")


        message_from_bytes = email.message_from_bytes(message_contain_galxe)
        logger.info(f"经过了byte转换的信息 message_from_bytes={message_from_bytes}")

        # 解析页面
        soup = BeautifulSoup(message_from_bytes.as_string(), 'html.parser')

        # 我自己试了试在p标签里面，而不是h1标签
        code_ret = soup.find('p').text

        logger.info(f" code_ret={code_ret} code_ret_type={type(code_ret)}")

        return code_ret

    def _get_discord_link_from_firstmail_with_IMAP(self):

        host = 'imap.firstmail.ltd'

        cur_client = imaplib.IMAP4_SSL(host, timeout=10)  # 设置上超时时间，才能成功链接

        cur_client.login(self.__email_address, self.__email_password)

        res, data = cur_client.select()
        last_message_number = data[0].decode().split()[0]
        logger.info(f'last_message_number({last_message_number})')

        status, message_fetch = cur_client.fetch(f"{last_message_number}", '(RFC822)')
        logger.info(f"从邮箱获取的原始信息 status={status} message_fetch={message_fetch}")

        # 这里ide提示问题，但是其实没问题
        message_contain_galxe = message_fetch[0][1]
        logger.info(f" message_contain_galxe({message_contain_galxe})")

        decoded_body = quopri.decodestring(message_contain_galxe).decode('utf-8', errors='replace')
        logger.info(f"消除等于号试试 decoded_body={decoded_body}")

        match = re.search(r'Verify Email:\s*(https?://\S+)', decoded_body)
        if match:
            verify_link = match.group(1)
            logger.success(f'获取成功 verify_link({verify_link})')
        else:
            logger.warning('获取失败')

        return


    def _get_email_from_outlook_with_POP3(self):

        # 配置邮件服务器和账户信息
        POP3_SERVER = 'outlook.office365.com'  # 'pop-mail.outlook.com'  # 你的 POP3 服务器地址
        EMAIL_ACCOUNT = self.__email_address  # 你的电子邮件地址
        EMAIL_PASSWORD = self.__email_password  # 你的电子邮件密码

        # 连接到 POP3 服务器
        server = poplib.POP3_SSL(POP3_SERVER)

        # 登录到邮件账户
        server.user(EMAIL_ACCOUNT)
        """
        报错账号不存在不知道为啥
        poplib.error_proto: b'-ERR Logon failure: unknown user name or bad password.'
        """
        server.pass_(EMAIL_PASSWORD)

        # 获取邮件数量
        num_messages = len(server.list()[1])
        logger.info(f"Number of messages: {num_messages}")

        # 获取最新的 10 封邮件
        # for i in range(max(num_messages - 10, 0), num_messages):
        response, lines, octets = server.retr(num_messages)  # 索引从 1 开始

        # 将邮件内容合并为单个字节字符串
        msg_content = b'\n'.join(lines)

        # 解析邮件内容
        msg = BytesParser(policy=policy.default).parsebytes(msg_content)
        logger.info(f"msg={msg}")
        """
        报错很奇怪
        IndexError: list index out of range
        """

        # 打印邮件主题和发件人
        subject = f"Subject: {msg['subject']}"
        ret_code = subject.split(" ")[-1]
        logger.info(f"ret_code={ret_code}")

        # 退出并关闭与 POP3 服务器的连接
        server.quit()

        return ret_code

    def get_galxe_code(self):
        total_time = 0
        timeout = 600

        domain_name = self.__email_address.split('@')[-1]
        logger.info(f"get_galxe_code domain_name={domain_name}")

        while True:
            # if domain_name == 'outlook.com':
            #     code_ret = self._get_email_from_outlook_with_POP3()
            if domain_name in self._support_domain_list:
                code_ret = self._get_email_from_firstmail_with_IMAP_with_retry()
            else:
                raise Exception(f"不支持 email_address={self.__email_address} domain_name={domain_name} ")

            if code_ret is not  None and len(code_ret) == 6 and code_ret.isdigit():
                logger.success(f"code_ret={code_ret} email_address={self.__email_address} 长度等于6并且必须是数字，那么算成功")
                return code_ret
            else:
                logger.info(f"email_address={self.__email_address} code_ret={code_ret} 长度不等于6，sleep30s 重新获取 total_time={total_time}")

                total_time += 30
                time.sleep(30)
                if total_time > timeout:
                    logger.error(f"获取验证码超时 timeout={timeout}")
                    raise Exception(f"email_address={self.__email_address} 获取验证码超时")


"""
10-18买了一个号测试
uaqibyyf@bulletsmail.com:ejjebpnkS!7591
"""
if __name__ == '__main__':
    cur_ServiceEmail = ServiceEmail('wtsekene@bfirstmail.com', 'wcllganq2187')
    cur_ServiceEmail._get_discord_link_from_firstmail_with_IMAP()
