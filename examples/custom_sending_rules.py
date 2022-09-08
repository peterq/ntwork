# -*- coding: utf-8 -*-
import sys
import time

import ntwork

wework = ntwork.WeWork()

# 打开pc企业微信, smart: 是否管理已经登录的微信
wework.open(smart=True)


class MsgInfo:
    """消息详情属性类"""

    def __init__(self, wework_instance: ntwork.WeWork, message):
        self.response_message = message
        self.data = message["data"]
        self.wework_instance = wework_instance

    '''获取消息内各个属性值的方法'''

    def get_sender_userid(self) -> str:
        """获取消息发送人的id"""
        sender_user_id = self.data["sender"]
        return sender_user_id

    def get_sender_name(self) -> str:
        """获取消息发送人的账号名称"""
        sender_name = self.data["sender_name"]
        return sender_name

    def get_my_id(self) -> str:
        """获取自己（bot）的id"""
        my_id = self.wework_instance.get_login_info()["user_id"]
        return my_id

    def get_conversation_id(self) -> str:
        """获取会话id"""
        conversation_id = self.data["conversation_id"]
        return conversation_id

    def get_msg_content(self) -> str:
        """获取消息内容"""
        msg_content = self.data["content"]
        return msg_content

    def get_msg_timestamp(self) -> str:
        """获取消息发送的时间戳"""
        msg_timestamp = self.data["send_time"]
        return msg_timestamp

    def get_at_list(self) -> list:
        """获取消息内发送人@的成员列表"""
        at_list = self.data["at_list"]
        return at_list

    '''消息来源'''

    def from_group(self) -> bool:
        """判断消息是否为群组消息，是返回True，不是返回False"""
        if "R:" in self.get_conversation_id():
            return True
        else:
            return False

    def from_private(self) -> bool:
        """判断消息是否为私聊消息，是返回True，不是返回False"""
        if "S:" in self.get_conversation_id():
            return True
        else:
            return False

    def at_me(self) -> bool:
        """判断消息内容中是否包含@自己，是返回True，不是返回False"""
        if self.get_at_list():
            for member in self.get_at_list():
                if self.get_my_id() in member["user_id"]:
                    return True
                else:
                    return False
        else:
            return False

    def not_me(self) -> bool:
        """判断发送消息的人是否不为自己，是返回True，不是返回False"""
        if self.get_sender_userid() != self.get_my_id():
            return True
        else:
            return False


class MsgRules(MsgInfo):
    """
    消息响应规则类
    GROUP ：只接收群组消息
    PRIVATE ：只接收私聊消息
    BOTH ：接收群组和私聊消息
    """
    GROUP = None
    PRIVATE = None
    BOTH = None

    def only_group(self) -> bool:
        """判断是否仅接收全部群组消息，是返回True，不是返回False"""
        if self.not_me() and not self.from_private() and self.from_group():
            return True
        else:
            return False

    def only_private(self) -> bool:
        """判断是否仅接收全部私聊消息，是返回True，不是返回False"""
        if self.not_me() and not self.from_group() and self.from_private():
            return True
        else:
            return False

    def __both(self) -> bool:
        """判断是否接收全部群组消息与私聊消息，是返回True，不是返回False"""
        if self.not_me():
            return True
        else:
            return False

    def from_userid(self, cmd: str) -> bool:
        """判断消息是否来源于指定发送人id，是返回True，不是返回False"""
        if cmd == self.get_sender_userid():
            return True
        else:
            return False

    def from_name(self, cmd: str) -> bool:
        """判断消息是否来源于指定发送人账号用户名，是返回True，不是返回False"""
        if cmd == self.get_sender_name():
            return True
        else:
            return False

    def __init__(self, wework_instance: ntwork.WeWork, message):
        super().__init__(wework_instance, message)
        self.GROUP = self.only_group()
        self.PRIVATE = self.only_private()
        self.BOTH = self.__both()

    def rule_type(self, rule):
        """消息响应规则类型选择器"""
        rules = None
        if rule == 'PRIVATE':
            rules = self.PRIVATE
        if rule == 'GROUP':
            rules = self.GROUP
        if rule == 'BOTH':
            rules = self.BOTH
        return rules


class Cmd(MsgInfo):
    """自定义命令判定容器类"""

    def cmd_starts(self, cmd: str) -> bool:
        """判断消息内容是否以指定字符串开头，是返回True，不是返回False"""
        if self.get_msg_content().startswith(cmd):
            return True
        else:
            return False

    def cmd_ends(self, cmd: str) -> bool:
        """判断消息是否以指定字符串结尾，是返回True，不是返回False"""
        if self.get_msg_content().endswith(cmd):
            return True
        else:
            return False

    def cmd_contains(self, cmd: str) -> bool:
        """判断消息是否包含指定字符串，是返回True，不是返回False"""
        if cmd in self.get_msg_content():
            return True
        else:
            return False


'''会话配置'''
Reply = '获取菜单成功！'  # 返回的消息内容
Rules = 'PRIVATE'  # 消息响应规则
Command = '/菜单'  # 自定义命令


def reply_msg(wework_instance: ntwork.WeWork, message, cmd=Command, rules=Rules, reply=Reply):
    """自定义消息体控制器 根据配置返回一条消息"""
    # 消息类实例化
    conversation = MsgInfo(wework_instance, message).get_conversation_id()  # 实例化消息属性类并获取会话id
    msg_rules = MsgRules(wework_instance, message)  # 实例化消息响应规则类
    cmd_params = Cmd(wework_instance, message)  # 实例化自定义命令类

    rules_handle = msg_rules.rule_type(rules)  # 使用消息响应类型选择器
    cmd_handle = cmd_params.cmd_starts(cmd)  # 使用自定义命令判定容器

    if rules_handle and cmd_handle:
        wework.send_text(conversation, reply)  # 符合条件则向指定会话发送指定消息


# 监听接收文本消息
wework.on(ntwork.MT_RECV_TEXT_MSG, reply_msg)

# 以下是为了让程序不结束，如果有用于PyQt等有主循环消息的框架，可以去除下面代码
try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    ntwork.exit_()
    sys.exit()
