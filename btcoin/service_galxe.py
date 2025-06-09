import asyncio
import base64
import random
import re

from datetime import datetime, timedelta, timezone
from loguru import logger
from urllib.parse import urlparse, parse_qs

import helper_logger
import service_account_aptos_storage
import service_account_evm
import service_account_aptos
import service_account_evm_storage
import service_account_header
import service_account_record_v2
import service_twitter
import service_discord
import service_captcha
import service_quiz
import service_referral_code
import service_survey
import service_email

import model_survey
import model_galxe
import dao_galxe

import helper_json
import helper_random
import helper_sleep
import helper_url

import rpc_config

# 全局字典用于存储实例
instances = {}


def get_service_instance(cur_account: service_account_evm.Account):
    # 使用账户的名称作为键来检查实例是否已经存在
    if cur_account.account_name not in instances:
        # 如果实例不存在，创建一个新的实例并将其存储在字典中
        logger.info(f"发现实例不存在，就new一个实例 {cur_account.log_info()}")
        instances[cur_account.account_name] = ServiceGalxe(cur_account)
    else:
        logger.info(f"发现实例存在，直接返回实例 {cur_account.log_info()}")
    return instances[cur_account.account_name]


class ServiceGalxe:

    def __init__(self, cur_account: service_account_evm.Account):
        self.__account = cur_account
        logger.info(f"初始化银河service account={self.__account.log_info()}")

        self.__dao_galxe = dao_galxe.DaoGalxe(self.__account.proxy, self.__account.header)

        # # 进来就先获取用户信息
        # # 如果用户存在
        # if self.check_galxe_id_exist():
        #     self.__profile = self.get_user_info()

        # 一开始是空的，需要时获取
        self.__profile = None

        # 社交系列
        self.twitter = None  # 需要推特对象处理推特相关的事情，这是一种组合的思路
        self.discord = None
        self.email = None

        self.captcha = None  # 需要验证码能力，直接组合在银河上，不需要组合在account上

        # 专属于银河的链名字和链配置的影响，别的项目可能不是这个名字
        self.__galxe_chain_name_to_chain_config = {
            # 银河里面的币安链一定是bsc大写这样的表示
            "BSC": rpc_config.BNBChainConfig,
        }

        self.cur_service_account_record_v2 = service_account_record_v2.ServiceAccountRecordV2()
        self.record = self.cur_service_account_record_v2  # 简洁重命名

        # 初始化时直接签名就完事
        # 是任何操作都必须的
        self.sign_in_v2()

    """
          ╔═══════════════════════════════════════════════════════════════════════╗
          ║ 以下是基础部分                                                     ║
          ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def address_lower(self):
        ret = self.__account.address_eip55.lower()
        return ret

    # 先小写，加evm前缀
    def address_evm_prefix_and_lower(self):
        ret = f'EVM:{self.__account.address_eip55.lower()}'  # noqa: E231
        return ret

    # 不要小写，加evm前缀
    def address_evm_prefix_and_eip55(self):
        ret = f'EVM:{self.__account.address_eip55}'  # noqa: E231
        return ret

    def __get_chain_config_by_name(self, chain_name):
        if chain_name in self.__galxe_chain_name_to_chain_config:
            return self.__galxe_chain_name_to_chain_config[chain_name]
        else:
            raise Exception(f"没有这个链配置 chain_name={chain_name}")

    def _get_evm_login_signature(self):
        time_now = datetime.now(timezone.utc).replace(tzinfo=None)

        exp_time = (time_now + timedelta(days=7)).isoformat()[:-3] + 'Z'
        iss_time = time_now.isoformat()[:-3] + 'Z'
        msg = f'galxe.com wants you to sign in with your Ethereum account:\n{self.__account.address_eip55}\n\n' \
              f'Sign in with Ethereum to the app.\n\n' \
              f'URI: https://galxe.com\n' \
              f'Version: 1\n' \
              f'Chain ID: 1\n' \
              f'Nonce: {helper_random.random_string_for_entropy(96)}\n' \
              f'Issued At: {iss_time}\n' \
              f'Expiration Time: {exp_time}'

        return msg, self.__account.sign_message(msg)

    def sign_in_v2(self):
        msg, signature = self._get_evm_login_signature()

        retries = 3  # 最大重试次数

        for attempt in range(retries):
            try:
                self.__dao_galxe.sign_in_v2(self.__account.address_eip55, msg, signature)
                break  # 成功后退出循环
            except Exception as e:
                if 'Connection reset by peer' in str(e):
                    logger.warning(f"尝试第 {attempt + 1} 次，连接被重置: {e}")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'sign_in_v2重试中')  # 计算等待时间并等待
                    else:
                        logger.error("最大重试次数已达，仍未能成功连接。")
                        raise
                else:
                    logger.error(f"请求失败: {e}")
                    raise  # 其他请求异常，不重试

        logger.info(f"用户签名登录成功 account={self.__account.log_info()}")

    def refresh_profile(self):
        self.__profile = self.__dao_galxe.get_user_info(self.__account.address)

    # 相当于是银河内部这个用户的id，mid哈哈
    def get_galxe_id(self):
        if self.__profile:
            return self.__profile['id']
        else:
            self.refresh_profile()
            return self.__profile['id']

    def has_email(self):
        if self.__profile:
            return self.__profile['hasEmail']

        else:
            self.refresh_profile()
            return self.__profile['hasEmail']

    def get_twitterUserName(self):
        if self.__profile:
            return self.__profile['twitterUserName']
        else:
            self.refresh_profile()
            return self.__profile['twitterUserName']

    def get_discordUserID(self):
        if self.__profile:
            return self.__profile['discordUserID']
        else:
            self.refresh_profile()
            return self.__profile['discordUserID']

    # def get_discordUserName(self):
    #     if self.__profile:
    #         return self.__profile['discordUserName']
    #     else:
    #         self.refresh_profile()
    #         return self.__profile['discordUserName']

    # def has_twitter(self):
    #     if self.__profile:
    #         return self.__profile['hasTwitter']

    """
          ╔═══════════════════════════════════════════════════════════════════════╗
          ║ 以下是创建账户相关的                                                         ║
          ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def check_galxe_id_exist(self):
        user_exist = self.__dao_galxe.check_galxe_id_exist(self.__account.address)
        return user_exist

    def __check_and_get_nickname(self):

        while True:

            nickname = helper_random.generate_username()

            existing = self.__dao_galxe.check_nickname_existing(nickname)

            if not existing:
                logger.info(f"昵称不存在，返回昵称 nickname={nickname}")
                return nickname
            else:
                logger.info(f"昵称已存在，重新生成昵称")

    def create_new_acc(self):
        nickname = self.__check_and_get_nickname()
        logger.info(f"创建新账户 nickname={nickname}")

        return self.__dao_galxe.dao_create_new_acc(nickname=nickname, address=self.__account.address)

    """
          ╔═══════════════════════════════════════════════════════════════════════╗
          ║ 以下是email相关的                                                         ║
          ╚═══════════════════════════════════════════════════════════════════════╝
    """

    # 这里就没有返回值了，如果失败就直接抛出异常
    def send_email(self, captcha):
        send_email_result = self.__dao_galxe.dao_send_email(self.__account.address,
                                                            email_address=self.__account.email_address,
                                                            captcha=captcha)

        if send_email_result:
            logger.success(f"发送邮件成功 account_name={self.__account.account_name} email_address={self.__account.email_address}")
        else:
            logger.error(f"发送邮件失败 account_name={self.__account.account_name} email_address={self.__account.email_address}")
            raise Exception("发送邮件失败")

    # 这里就没有返回值了，如果失败就直接抛出异常
    def confirm_email(self, galxe_code):
        confirm_email_result = self.__dao_galxe.dao_confirm_email(code=galxe_code,
                                                                  address=self.__account.address,
                                                                  email_address=self.__account.email_address)
        if confirm_email_result:
            logger.success(f"用户绑定邮箱成功 account_name={self.__account.account_name} email_address={self.__account.email_address}")
        else:
            logger.error(f"用户绑定邮箱失败 account_name={self.__account.account_name} email_address={self.__account.email_address}")
            raise Exception("用户绑定邮箱失败")

    def link_email(self):

        # 这是推特的对象
        if self.email is None:
            self.email = service_email.ServiceEmail(cur_email_address=self.__account.email_address,
                                                    cur_email_password=self.__account.email_password)

        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                cur_captcha = self.__get_captcha()
                self.send_email(cur_captcha)
                break  # 成功后退出循环
            except Exception as e:
                if 'Fail to verify recaptcha' in str(e):
                    logger.warning(f"send_email 去做重试的第({attempt + 1})次，e({e})")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'send_email 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f"send_email 最大重试次数已达，仍不成功。e({e})")
                        raise
                else:
                    logger.error(f"send_email 失败,e({e})")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试

        helper_sleep.wait_a_bit(20, '等待邮件，肯定不能马上获取邮件')
        galxe_code = self.email.get_galxe_code()
        self.confirm_email(galxe_code)
        logger.info('end')

    """
                  ╔═══════════════════════════════════════════════════════════════════════╗
                  ║ 以下是twitter相关的                                                      ║
                  ╚═══════════════════════════════════════════════════════════════════════╝
    """


    def link_twitter(self)->None:
        """
        # 如果没有银河中的推特名字是空，就去绑定
        # 如果银河中的推荐名字和token的推特名字不一样，去绑定

        :return: 现在还不需要返回值
        """

        if self.twitter is None:
            self.twitter = service_twitter.ServiceTwitter(
                twitter_auth_token=self.__account.twitter_auth_token,
                proxy=self.__account.proxy,
                header=self.__account.header,
                account_name = self.__account.account_name,
            )

        cur_galxe_twitter_username = self.get_twitterUserName()#当前的银河的推特名字

        # TODO 为什么要lower取小写啊？？我觉得大小写都可能啊？ done 实际推特的名字是有大小写的，银河也是按照大小写来记录的。但是推特接口返回的是小写的
        # 例子：当前银河的推特名字(KimberlyVa70129). token的推特名字(kimberlyva70129)
        if cur_galxe_twitter_username.lower() == self.twitter.my_username:
            # 相同就没问题，直接返回
            logger.success(f'当前的银河账号已经绑定了当前的推特，所以这次不需要任何网络操作 Twitter account already linked with this EVM address: {cur_galxe_twitter_username} {self.__account.log_info()}')
            return
        else:
            # 可能是existed_twitter_username为空
            # 可能是existed_twitter_username和self.twitter.my_username不一样
            logger.warning(f'银河的推特名字和token的推特名字不一样，需要重新绑定 cur_galxe_twitter_username({cur_galxe_twitter_username}) self.twitter.my_username({self.twitter.my_username})')

        logger.info(f'Starting link new Twitter account={self.__account.log_info()}')

        # 找到id
        galxe_id = self.get_galxe_id()
        logger.info(f'银河galxe_id={galxe_id} {self.__account.log_info()}')

        # 拼接推特文本
        tweet_text = f'Verifying my Twitter account for my #GalxeID gid:{galxe_id} @Galxe \n\n galxe.com/galxeid '
        logger.info(f'推特文本({tweet_text}) {self.__account.log_info()}')

        try:
            # 发推
            tweet_url = self.twitter.post_tweet_wrapper(tweet_text)
        except Exception as e:
            # 重复发推
            if 'Authorization: Status is a duplicate. (187)' in str(e):
                logger.info(f'Duplicate tweet. Trying to find original one {self.__account.log_info()}')
                tweet_url = self.twitter.find_posted_tweet(lambda t: tweet_text.split('\n')[0] in t)
                if tweet_url is None:
                    raise Exception("Tried to post duplicate tweet. Can't find original one")
                logger.info(f' Duplicate tweet found: {tweet_url} {self.__account.log_info()}')
            else:
                raise e
        # 随机等待
        helper_sleep.sleep_wrap(5, '发推之后等待5秒')

        # 先验证推特url
        check_twitter_account_ret = self.__dao_galxe.check_twitter_account(
            address=self.__account.address,
            tweet_url=tweet_url)
        if not check_twitter_account_ret:
            logger.error(f"check_twitter_account_ret is False tweet_url={tweet_url} {self.__account.log_info()}")
            raise Exception("check_twitter_account_ret is False")
        else:
            logger.success(f"check_twitter_account_ret is True tweet_url={tweet_url} {self.__account.log_info()}")

        # 再确认推特url
        verify_twitter_account_ret = self.__dao_galxe.verify_twitter_account(
            address=self.__account.address,
            tweet_url=tweet_url)
        if not verify_twitter_account_ret:
            logger.error(f"verify_twitter_account_ret is False tweet_url={tweet_url} {self.__account.log_info()}")
            raise Exception("verify_twitter_account_ret is False")
        else:
            logger.success(f"verify_twitter_account_ret is True tweet_url={tweet_url} {self.__account.log_info()}")


        logger.success(f"用户绑定推特成功，必须马上刷新当前内存中保存的银河用户信息，这样下次进这个函数才会在上面return account={self.__account.log_info()} ")
        self.refresh_profile()

        return

    """
                  ╔═══════════════════════════════════════════════════════════════════════╗
                  ║ 以下是dc相关的                                                         ║
                  ╚═══════════════════════════════════════════════════════════════════════╝
    """

    # 原来dc的id是通过token计算出来的
    def _get_discord_user_id(self):
        if self.__account.discord_token == '':
            raise Exception('Empty Discord token')
        token = self.__account.discord_token.split('.')[0]
        token += '=' * (4 - len(token) % 4)
        ret = str(base64.b64decode(token.encode("utf-8")), 'utf-8')
        return ret

    def link_discord(self):
        discord_user_id_from_token = self._get_discord_user_id()
        existed_discord_id = self.get_discordUserID()
        logger.info(f'银河的discord id=({existed_discord_id}) token的discord id=({discord_user_id_from_token})')

        if existed_discord_id != '':
            if existed_discord_id == discord_user_id_from_token:
                logger.info(f'银河和token的discord id一样，直接返回 ')
                return
            else:
                logger.info(f'银河和token的discord id不一样，银河的discord id={existed_discord_id} token的discord id={discord_user_id_from_token}')
        else:
            logger.info(f'银河的discord id为空，直接开始绑定')

        # dc验证连接
        discord_auth_link = self.__dao_galxe.get_social_auth_url(self.address_evm_prefix_and_lower())

        def get_query_param(url: str, name: str):
            values = parse_qs(urlparse(url).query).get(name)
            if values:
                return values[0]
            return None

        # 这个状态是啥
        state = get_query_param(discord_auth_link, 'state')
        logger.info(f'获取state=({state}) discord_auth_link=({discord_auth_link}) ')

        if self.discord is None:
            self.discord = service_discord.ServiceDiscord(self.__account.proxy)

        galxe_verify_token = self.discord.get_galxe_verify_token(
            address_evm_prefix_and_lower=self.address_evm_prefix_and_lower(),
            state=state,
            discord_token=self.__account.discord_token)
        logger.info(f'galxe_verify_token={galxe_verify_token}')

        check_discord_account_ret = self.__dao_galxe.check_discord_account(
            address_evm_prefix_and_lower=self.address_evm_prefix_and_lower(),
            state=state,
            token=galxe_verify_token)
        if not check_discord_account_ret:
            exp = Exception(f"check_discord_account_ret is False name={self.__account.log_info()}")
            logger.error(exp)
            raise exp
        else:
            logger.success(f"check_discord_account_ret is True")

        verify_discord_account_ret = self.__dao_galxe.verify_discord_account(
            address_evm_prefix_and_lower=self.address_evm_prefix_and_lower(),
            state=state,
            token=galxe_verify_token)
        if not verify_discord_account_ret:
            exp = Exception(f"verify_discord_account_ret is False name={self.__account.log_info()}")
            logger.error(exp)
            raise exp
        else:
            logger.success(f"verify_discord_account_ret is True")

    """
              ╔═══════════════════════════════════════════════════════════════════════╗
              ║ 以下是任务相关的                                                         ║
              ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def get_campaign_info(self, campaign_id):
        campaign_info = self.__dao_galxe.get_campaign_info_with_retry(self.address_lower(), campaign_id, log_detail=True)

        return campaign_info

    # 核心的任务分类执行函数
    def complete_campaign(self, campaign_id: str) -> bool:
        logger.info(f'开始执行任务 campaign_id={campaign_id} {self.__account.log_info()}')

        campaign_info = self.__dao_galxe.get_campaign_info_with_retry(self.address_lower(), campaign_id)

        self.complete_campaign_part1(campaign_info)  # TODO 其实也应该判断is_complete_campaign_success，但是暂时不做也行
        is_complete_campaign_success = self.complete_campaign_part2(campaign_info)

        return is_complete_campaign_success

    def complete_campaign_part1(self, campaign_info: dict):
        """
        "taskConfig": {
                "participateCondition": {
                    "conditionalFormula": "ANY", 优化，如果是any那就就完成一个就行
                    "eligible": false,
                    "__typename": "ParticipateCondition"

                    "conditions": [
                        {
                            "cred": {
                                "id": "3120216516093953",
                                "name": "Galxe Web3 Score - Humanity Score",
                                "type": "EVM_ADDRESS",
                                "credType": "EVM_ADDRESS",
                                "credSource": "GALXE_WEB3_SCORE",
                                "dimensionConfig": "MULTI_DIMENSION",
                                "referenceLink": "",
                                "description": "Reflect how likely a user is a real human. Users can get active on-chain, prove your social impact, show your wealth, pass face recognition to improve. Normally, a user has to be at least Level 2 to prove themselves as real human.",
                                "lastUpdate": 1696658308,
                                "lastSync": 1725252815,
                                "chain": "ETHEREUM",
                                "eligible": 0,
                                "metadata": {
                                    "visitLink": null,
                                    "twitter": null,
                                    "__typename": "CredMetadata"
                                },
                                "commonInfo": null,
                                "__typename": "Cred"
                            },
                            "attrs": [
                                {
                                    "attrName": "humanity",
                                    "operatorSymbol": ">=",
                                    "targetValue": "1",
                                    "__typename": "ExprEntityAttr"
                                }
                            ],
                            "attrFormula": "ALL",
                            "eligible": false,
        优化，
        1 如果是any那就就完成一个就行
        2 如果整体完成，直接跳过
        3 如果是护照再去执行，别的任务先忽略不执行，好像一般的必做任务都是护照
        update 9-6 遇见了一个前置任务是关注space的，牛逼，我改一下代码

        :param campaign_info:
        :return:
        """

        # 假设任务不在 campaign['taskConfig']['participateCondition']['conditions']，只在 campaign['credentialGroups']
        # update 这部分也必须执行，这些任务可能是护照相互的，是必须要完成的任务，属于前置依赖
        # 从翻译上看participateCondition，也可以翻译为参与条件，就是必须要完成这些任务
        # notice 第一部分任务在这个结构体里面 campaign['taskConfig']['participateCondition']['conditions']

        if campaign_info['taskConfig'] and campaign_info['taskConfig'].get('participateCondition') is not None:
            # 必须要完成的前置任务
            participateCondition = campaign_info['taskConfig']['participateCondition']

            logger.info(f"complete_campaign_part1 start {self.__account.log_info_v2()} participateCondition({participateCondition})")

            eligible_for_all = participateCondition['eligible']
            if eligible_for_all:
                logger.warning(f"complete_campaign_part1 如果整体上已经完成，那么直接返回就行 {self.__account.log_info_v2()}")
                return

            conditionalFormula = participateCondition['conditionalFormula']
            logger.info(f"complete_campaign_part1 conditionalFormula={conditionalFormula} {self.__account.log_info_v2()}")

            # 每一个子任务的list
            conditions = participateCondition['conditions']

            for c in conditions:
                cred = c['cred']
                attrs = c['attrs']
                eligible = c['eligible']
                if eligible:
                    logger.warning(f"complete_campaign_part1 这个任务已经完成了 cred({cred}) {self.__account.log_info_v2()}")
                    continue

                # 过滤掉不是护照的任务。我自己知道现在只做护照任务
                # 只能通过name过滤，因为银河护照和nomis的credSource是一样的，都是SUBGRAPH（子图？？啥意思？）无法区分
                cred_name = cred['name']
                if cred_name in ["Sybil Prevention Credential powered by Nomis.cc",
                                 "Galxe Web3 Score - Humanity Score",
                                 "Gitcoin Passport Score"]:
                    logger.warning(f"complete_campaign_part1 过滤掉不是护照的任务 cred({cred}) {self.__account.log_info_v2()}")
                    continue

                logger.info(f"complete_campaign_part1 cur_cred_detail c={helper_json.helper_json(c)}")

                allow = self._complete_credential(campaign_info['id'], cred, attrs)
                # TODO 其实也应该按照complete_campaign_part2去改一下
                if allow and conditionalFormula == model_galxe.ConditionRelation.ANY:
                    logger.success(f"complete_campaign_part1 完成任意一个任务就算整体完成 cred({cred}) {self.__account.log_info_v2()}")
                    return

                helper_sleep.wait_a_bit(2, '子任务的for循环间隔等待2秒')
        else:
            logger.info(f"complete_campaign_part1 part1没有任务需要执行 {self.__account.log_info_v2()}")

    def complete_campaign_part2(self, campaign_info: dict) -> bool:
        logger.info(f'start {self.__account.log_info_v2()}')
        campaign_id = campaign_info['id']

        # notice 第二部分的任务在这个里面campaign_info['credentialGroups']
        credentialGroups = campaign_info['credentialGroups']
        logger.info(f"campaign_id({campaign_id}) credentialGroups({credentialGroups}) {self.__account.log_info_v2()}")

        for credentialGroup in credentialGroups:

            # 获取当前group的any或all属性，而不是groups的
            conditionRelation = credentialGroup['conditionRelation']
            logger.info(f"campaign_id({campaign_id}) conditionRelation({conditionRelation}) {self.__account.log_info_v2()}")

            for condition, credential in zip(credentialGroup['conditions'], credentialGroup['credentials']):

                logger.info(f"campaign_id({campaign_id}) 当前要去做的子任务 credential={helper_json.helper_json(credential)} condition={helper_json.helper_json(condition)}")

                # hardcode 指定的任务不处理。这里主要是跳过需要项目方更新白名单的子任务
                if      credential['name'] in [
                    "Post Submission and Verification",
                    "Article Quest Champions",
                    'Post Submission & Verification',
                    'Survey: please create a emoji or sticker for Route-x',
                    'Survey: please create am emoji or sticker for clobx',
                    'Meme Quest Champions',
                        'Post Submission and Verification',
                        'Post Submission and Verification [ Oct 5th-Oct 13th ]',
                        'Post Submission and Verification [ Oct 14th - Oct 20th ]',
                        'Sticker Quest Champions',
                        'Video Quest Champions',
                        '',
                        '',
                        '',


                ]:
                    logger.warning(f"campaign_id({campaign_id}) credential['name']({credential['name']}) 指定的子任务就不做了")
                    continue


                eligible = condition['eligible']
                if eligible:
                    logger.warning(f"campaign_id({campaign_id}) 这个子任务已经完成了 {self.__account.log_info_v2()} credential({credential}) ")
                    continue

                allow = self._complete_credential(campaign_info['id'], credential, None)
                if conditionRelation == model_galxe.ConditionRelation.ANY:
                    if allow:
                        logger.success(f"完成任意一个任务就算整体完成 campaign_id({campaign_id}) allow({allow}) conditionRelation({conditionRelation})  {self.__account.log_info_v2()} credential({credential}) ")
                        continue
                    else:
                        logger.warning(f"任意一个任务失败，但是因为any类型而继续执行 campaign_id({campaign_id}) allow({allow}) conditionRelation({conditionRelation})  {self.__account.log_info_v2()} credential({credential}) ")
                else:
                    if allow:
                        logger.success(f"当前子任务成功，必须完成group中的每个任务 campaign_id({campaign_id}) allow({allow}) conditionRelation({conditionRelation})  {self.__account.log_info_v2()} credential({credential}) ")
                    else:
                        logger.warning(f'又是all类型又当前子任务又失败 campaign_id({campaign_id}) allow({allow}) conditionRelation({conditionRelation})  {self.__account.log_info_v2()}')
                        is_complete_campaign_success = False
                        return is_complete_campaign_success

                helper_sleep.wait_a_bit(5, 'complete_campaign_part2 子任务组credentialGroup的循环间隔等待5秒')

        logger.success(f' 执行到最后算成功 campaign_id({campaign_id}) {self.__account.log_info_v2()}')
        is_complete_campaign_success = True
        return is_complete_campaign_success

    # 完成一个子任务，按分类
    def _complete_credential(self, campaign_id, credential: dict, attrs) -> bool:
        logger.info(f' start campaign_id={campaign_id} credential={helper_json.helper_json(credential)} {self.__account.log_info_v2()}')
        need_sync = False  # 默认不需要sync

        # 什么类型的任务
        # 这些类型都是银河的官方定义的
        # 这里应该都是AddTypedCredentialItems这一步
        # python里面已经有了switch case了，这样写
        match credential['type']:
            # 答题算什么类型的任务啊？
            case model_galxe.Credential.TWITTER:

                logger.info(f' credential_type is TWITTER. account={self.__account.log_info()}')
                # 推特是单独做的，不需要后续的逻辑了
                allow = self._complete_twitter(campaign_id, credential)
                return allow

            case model_galxe.Credential.EMAIL:

                logger.info(f' credential_type is EMAIL. account={self.__account.log_info()}')
                need_sync = self._complete_email(campaign_id, credential)

            case model_galxe.Credential.EVM_ADDRESS:

                logger.info(f' credential_type is EVM_ADDRESS. account={self.__account.log_info()}')

                # 可以不允许
                need_sync = self._complete_eth(campaign_id, credential)

            case model_galxe.Credential.GALXE_ID:

                logger.info(f' credential_type is GALXE_ID. account={self.__account.log_info()}')

                need_sync = self._complete_galxe_id(campaign_id, credential, attrs)

            case model_galxe.Credential.DISCORD:

                # 直接跳过
                need_sync = False
                logger.warning(f'跳过discord任务 account={self.__account.log_info()}')

            case model_galxe.Credential.TELEGRAM:
                # 直接跳过
                need_sync = False
                logger.warning(f'跳过电报任务 account={self.__account.log_info()}')

            case model_galxe.Credential.APTOS_ADDRESS:
                logger.warning(f'不跳过APTOS任务,单独做一个逻辑 account={self.__account.log_info()}')
                allow = self._complete_aptos(campaign_id, credential)
                return allow

            case unexpected:
                raise Exception(f'{unexpected} credential type is not supported yet')

        # 判断是否需要sync这个子任务，就是SyncCredentialValue
        if need_sync:
            # update 9-2 加大到5s
            helper_sleep.wait_a_bit(7, '子任务完成之后等待7秒再sync，可能5秒不行，推特关注任务还不算成功')
            allow = self._sync_credential(campaign_id, credential['id'], credential['type'])
            # notice 记录一下这个特殊点，就是在完成any类型的credential group时，
            #  只要有一个任务完成了，万一有一个任务allow=false，也是符合预期的
            #  any在cred_group['conditionRelation']这里面判断，那么必须交给更上层去判断了，这里就不要抛出异常了

            logger.warning(f' sync_credential完成，结果是allow({allow}) credential_name({credential["name"]}) {self.__account.log_info_v2()}')
            return allow



        else:
            # 不需要need_sync时候直接算成功
            return True

    def _complete_aptos(self, campaign_id: str, credential: dict) -> bool:
        try:
            allow = self._sync_credential(campaign_id, credential['id'], credential['type'])
            logger.warning(f' sync_credential完成，结果是allow({allow}) credential_name({credential["name"]}) {self.__account.log_info_v2()}')
            return allow
        except  Exception as e:
            logger.warning(f' e({e})')
            if 'The API server used by this credential is busy' in str(e):
                logger.warning(' 遇见这个报错，在aptos场景不算异常，返回allow=false（在其他场景算异常）')
                allow = False
                return allow

    # 返回true表示需要sync
    def _complete_twitter(self, campaign_id: str, credential: dict) -> bool:
        logger.info(f' start campaign_id={campaign_id} credential={helper_json.helper_json(credential)}')

        # 如果我要做推特任务了，我确实倾向于先链接，
        # 如果已经绑定也没关系，如果被封了也能提前发现
        # 里面还初始化了twitter对象
        self.link_twitter()

        # notice 重试部分包括
        #  0 add_typed_credential我也加入了重试。因为我看网页上重试也都重做了add_typed_credential这一步
        #  1推特交互，
        #  2twitter_oauth2_status，
        #  3sync_credential_value

        retries = 5  # 最大重试次数
        for attempt in range(retries):
            if credential['credSource'] == model_galxe.CredSource.TWITTER_BULLISH:
                logger.warning(f'campaign_id({campaign_id}) TWITTER_BULLISH就不add_typed_credential 神奇了')
            else:
                logger.warning(f'campaign_id({campaign_id}) 做推特行为之前先add_typed_credential. {self.__account.log_info_v2()}')
                self.add_typed_credential(campaign_id, credential)  # add_typed_credential是必须的,可能必须得在推特前面，因为可能控制银河去搜索某个时间点之后推特信息
                logger.warning(f'campaign_id({campaign_id}) 完成了add_typed_credential，现在去做推特交互. {self.__account.log_info_v2()}')

            # TODO 怎么处理假完成就可以验证银河的情况，就当时真做，其实也可以吧
            self._complete_twitter_core(credential)

            if credential['credSource'] == model_galxe.CredSource.TWITTER_LIKE or \
                    credential['credSource'] == model_galxe.CredSource.TWITTER_RT or \
                    credential['credSource'] == model_galxe.CredSource.TWITTER_BULLISH:
                helper_sleep.wait_a_bit(0, '_complete_twitter like和rt类型的任务不等待')
            else:
                # notice 可能必须等推特索引，如果银河使用推特官方api获取其他用户的数据的话。就是那个付费100u的工具
                # update 我直接90s，之前60s可能不够
                # update 90s不够，我120s
                # update 10-12 120缩短到30，试试加速。现在这里是发推和关注任务的情况需要等待
                helper_sleep.wait_a_bit(30, '_complete_twitter 完成了推特交互，现在去sync_credential，先多等等')

            self.__dao_galxe.twitter_oauth2_status()  # TODO 这一步的意义是什么？

            captcha = self.__get_captcha()

            sync_options = self._default_sync_options(credential['id'])
            sync_options.update({
                'twitter': {
                    'campaignID': campaign_id,
                    'captcha': captcha,
                }
            })
            allow = self.__dao_galxe.sync_credential_value(sync_options, is_quiz=False)

            if allow:
                logger.success(f"campaign_id({campaign_id}) allow is true 在重试 attempt({attempt})次之后成功了 credential({credential})")
                return True
            else:
                logger.warning(f"campaign_id({campaign_id}) allow is false 去重试 attempt({attempt})次 credential({credential})")
                if attempt < retries - 1:
                    helper_sleep.calculate_backoff_time_and_sleep(attempt, '_complete_twitter重试中 间隔时间长一点', base_delay=20)  # 计算等待时间并等待
                else:
                    exp = Exception(f"campaign_id({campaign_id}) _complete_twitter 最大重试次数已达，仍不成功 attempt({attempt}) credential({credential})")
                    logger.error(exp)
                    raise exp

    def ut_check_twitter_result(self,campaign_id, credential_id  ):
        self.__dao_galxe.twitter_oauth2_status()

        captcha = self.__get_captcha()

        sync_options = self._default_sync_options(credential_id )
        sync_options.update({
            'twitter': {
                'campaignID': campaign_id,
                'captcha': captcha,
            }
        })
        allow = self.__dao_galxe.sync_credential_value(sync_options, is_quiz=False)

        logger.info(f'allow({allow})')






    def _complete_twitter_core(self, credential: dict) -> None:
        logger.info(f'start')

        credential_id = credential['id']
        logger.info(f'credential_id({credential_id})')
        if credential_id in []:
            logger.warning(f'指定的子任务可以不做直接去验证')  # hardcode
            return

        credSource = credential['credSource']
        logger.info(f'credSource({credSource})')

        match credSource:

            case model_galxe.CredSource.TWITTER_FOLLOW:
                # 直接获取连接
                user_to_follow = helper_url.get_query_param(credential['referenceLink'], 'screen_name')
                self.twitter.follow(user_to_follow)
                logger.info(f' Tweet follow end. user_to_follow={user_to_follow} {self.__account.log_info_v2()}')


            case model_galxe.CredSource.TWITTER_RT: # 转发

                referenceLink = credential['referenceLink']
                self.twitter.retweet_with_retry(referenceLink)
                logger.info(f' Tweet retweet end. referenceLink={referenceLink} {self.__account.log_info_v2()}')

            case model_galxe.CredSource.TWITTER_LIKE:

                logger.warning(f' Tweet like 点赞已经私人了，是不是可以不做？. {self.__account.log_info_v2()}')

            case model_galxe.CredSource.TWITTER_QUOTE:

                text = helper_url.get_query_param(credential['referenceLink'], 'text')
                logger.info(f' Tweet quote with text: {text}')

                tweet_link = text[text.rfind(' ') + 1:]
                logger.info(f' Tweet link: {tweet_link}')

                text = text[:text.rfind(' ')]
                logger.info(f' Tweet text: {text}')

                quote_mention_re = re.compile(r'mention \d+ friends')
                mentions = quote_mention_re.findall(credential['name'].lower())  # 从任务名字就就知道了@几个人
                logger.info(f' mentions={mentions}')

                if mentions:
                    mentions_number = int(mentions[0].split()[1])
                    # 拼接假名字
                    # notice 可能名字太假了无法银河验证，我随机选择小狐狸或者银河的推特账户去@
                    text += ''.join([f' {helper_random.choice_twitter_account()}' for _ in range(mentions_number)])
                logger.info(f' Tweet quote with text: {text}')

                text += '\n' + tweet_link  # 转帖本质就是发推，并且带链接
                logger.info(f' Tweet quote with text: {text}')

                self.twitter.post_tweet_wrapper(text)
                logger.info(f' Tweet quote end. text={text}')

            case model_galxe.CredSource.TWITTER_BULLISH:

                # 例子 "referenceLink": "https://x.com/intent/tweet?text=%40burnt_xion %23xion,%23Fractit ",
                text = helper_url.get_query_param(credential['referenceLink'], 'text')
                logger.info(f'从银河链接拿发推文案 text({text})')



                text = helper_random.generate_twitter_text() + ' ' + text #实践发现，开头是@就算回复，我才搞明白
                logger.info(f'拼接文案之后 text({text})')

                # hardcode xion的Tweet Bullish About @burnt_xion 子任务
                if credential_id =='468424340078080000':
                    text=text+'XION’s Generalized Abstraction layer is purpose-built for mass consumer adoption by enshrining UX at the protocol-level'

                self.twitter.post_tweet_wrapper(text)
                logger.info(f' TWITTER_BULLISH 发推完毕. text={text}')

            case unexpected:
                raise Exception(f'{unexpected} 推特任务类型不支持')

        logger.warning(f'end. 完成了推特交互，现在去sync_credential {self.__account.log_info_v2()}')

    # 原来邮件任务就包括的答题，看网页等等
    # 这些都是要提前配置邮箱才能进行的
    def _complete_email(self, campaign_id: str, credential: dict) -> bool:

        match credential['credSource']:
            case model_galxe.CredSource.VISIT_LINK:

                self.add_typed_credential(campaign_id, credential)
                # 看网页这种需要sync
                return True

            case model_galxe.CredSource.QUIZ:

                self.solve_quiz(credential)
                # 答题不需要sync
                return False

            case model_galxe.CredSource.WATCH_YOUTUBE:
                # 看油管需要sync
                self.add_typed_credential(campaign_id, credential)
                return True

            case model_galxe.CredSource.SURVEY:  # 自己扩展了调查类型

                self.solve_survey(credential)
                return False

            case unexpected:
                raise Exception(f'{unexpected} credential source for Email task is not supported yet')

    def solve_quiz(self, quiz_credential):
        quiz_id = quiz_credential['id']

        cur_service_quiz = service_quiz.ServiceQuiz()
        answers = cur_service_quiz.get_credential_answers(quiz_id)
        logger.success(f' answers({helper_json.helper_json(answers)})')

        sync_options = self._default_sync_options(quiz_id)
        sync_options.update(
            {'quiz':
                 {'answers': answers}
             }
        )
        logger.info(f' sync_options({helper_json.helper_json(sync_options)})')
        allow = self.__dao_galxe.sync_credential_value(sync_options, is_quiz=True)
        if not allow:
            exp = Exception(f'Failed to sync quiz answers')
            logger.error(exp)
            raise exp
        else:
            logger.success(f' end.答题成功了 allow({allow}) {self.__account.log_info_v2()}')

    # 调研我已经单独写个一个函数。包括SyncCredentialValue步骤。所以不需要上层再SyncCredentialValue
    def solve_survey(self, survey_credential):
        survey_credential_id = survey_credential['id']

        # new对一个对象
        cur_service_survey = service_survey.ServiceSurvey(self.__account.proxy, self.__account.header)
        answers = cur_service_survey.get_credential_answers(survey_credential_id)
        logger.success(f' answers({helper_json.helper_json(answers)})')

        sync_options = self._default_sync_options(survey_credential_id)
        sync_options.update(
            {'survey':
                 {'answers': answers}
             }
        )
        logger.info(f' sync_options({helper_json.helper_json(sync_options)})')
        allow = self.__dao_galxe.sync_credential_value(sync_options, is_quiz=False)

        # 看了看resp，allow好像也无所谓，就不管什么返回值都算成功
        # if not allow:
        #     exp = Exception(f'Failed to sync quiz answers')
        #     logger.error(exp)
        #     raise exp

        logger.success(f' end. 调研可以不allow，allow({allow}) {self.__account.log_info_v2()}')

    def _complete_eth(self, campaign_id: str, credential) -> bool:
        logger.info(f" start. credSource({credential['credSource']}) {self.__account.log_info_v2()}")

        match credential['credSource']:

            # evm进来也可能是看网页和答题
            case model_galxe.CredSource.VISIT_LINK:
                self.add_typed_credential(campaign_id, credential)
                return True

            case model_galxe.CredSource.QUIZ:
                self.solve_quiz(credential)
                return False

            # csv就不懂
            case model_galxe.CredSource.CSV:
                raise Exception(f'It seems like you are not eligible for custom project requirements')

            # 调研
            case model_galxe.CredSource.SURVEY:
                self.solve_survey(credential)
                return False

            # 看油管，不仅仅是email那边有，evm这里也有，必须先add_typed_credential，然后外部sync
            case model_galxe.CredSource.WATCH_YOUTUBE:
                # 看油管需要sync
                self.add_typed_credential(campaign_id, credential)
                return True

            case unexpected:
                # 不知道的类型可能也没问题
                logger.warning(f'credentialsource({unexpected}) for EVM_ADDRESS task is not supported yet 不支持也没关系，下一步去sync就行完成子任务. credential({credential})')

        logger.info(f'_complete_eth end. {self.__account.log_info_v2()}')

        # 调研我已经单独写个一个函数。其他的类型，默认情况下，必须allow，不能allow is false
        return True

    def _complete_galxe_id(self, campaign_id: str, credential: dict, attrs) -> bool:
        logger.info(f' start. credential({credential}) attrs({attrs}) {self.__account.log_info_v2()}')

        match credential['credSource']:
            # 需要关注space
            case model_galxe.CredSource.SPACE_USERS:

                logger.info(f' credSource is SPACE_USERS. account={self.__account.log_info_v2()}')
                self._follow_space(campaign_id, credential, attrs)

            case model_galxe.CredSource.CAMPAIGN_REFERRAL:

                logger.warning(f'推荐任务先跳过不做，credential_name({credential}) ')

            case unexpected:

                raise Exception(f'({unexpected}) credential source for Galxe ID task is not supported yet')

        return False

    # 关注space，判断了是否关注，然后去关注
    def _follow_space(self, campaign_id: str, credential: dict, attrs):
        """
        另一种可能的参数，就是关注之前需要有指定数量的point
         "attrs": [
        {
            "attrName": "points",
            "operatorSymbol": ">=",
            "targetValue": "5",
            "__typename": "ExprEntityAttr"
        }
        ],

        :param campaign_id:
        :param credential:
        :return:
        """
        logger.info(f' start. campaign_id={campaign_id} credential={credential} {self.__account.log_info_v2()}')

        info = self.__dao_galxe.get_campaign_info_with_retry(self.address_lower(), campaign_id)
        space = info['space']
        space_id = int(space['id'])

        # 如果没有关注，就是去关注
        if not space['isFollowing']:
            # dao层去关注，就是实际上去关注space。但是关注成功和能验证任务还是两回事
            self.__dao_galxe.follow_space(space_id)
            logger.info(f' Space {space["name"]} followed')

        sync_options = self._default_sync_options(credential['id'])
        eval_expr = sync_options.copy()

        # 如果没传，有个默认值
        if not attrs:
            attrs = [{
                'attrName': 'follow',
                'operatorSymbol': '==',
                'targetValue': '1',
                '__typename': 'ExprEntityAttr',
            }]

        eval_expr.update({
            'entityExpr': {
                'attrFormula': 'ALL',  # 其实也是需要根据上层传递的，但是直接写死应该也能用
                'attrs': attrs,  # 这里不是固定的，是根据任务变化的。所以必须使用上层传递的attrs
                'credId': credential['id'],
            },
        })
        logger.info(f' eval_expr({eval_expr})')
        self.__dao_galxe.sync_evaluate_credential_value(eval_expr, sync_options)

    def _sync_credential(self, campaign_id: str, credential_id: str, cred_type: str):
        logger.warning(f' start. campaign_id={campaign_id} credential_id={credential_id} cred_type={cred_type} {self.__account.log_info_v2()}')

        sync_options = self._default_sync_options(credential_id)

        return self.__dao_galxe.sync_credential_value(sync_options, is_quiz=False)

    def _default_sync_options(self, credential_id: str) -> dict:
        return {
            'address': self.address_evm_prefix_and_lower(),
            'credId': credential_id,
        }

    def add_typed_credential(self, campaign_id: str, credential):
        logger.warning(f' start. {self.__account.log_info_v2()} credential={credential} ')

        retries = 5  # 最大重试次数
        for attempt in range(retries):
            try:
                cur_captcha = self.__get_captcha()
                self.__dao_galxe.add_typed_credential_items(
                    address_lower=self.address_lower(),
                    campaign_id=campaign_id,
                    credential_id=credential['id'],
                    captcha=cur_captcha,
                )
                break  # 成功后退出循环
            except Exception as e:
                if '10000:failed to verify recaptcha token' in str(e):
                    logger.warning(f"add_typed_credential 重试的第{attempt + 1}次，e={e}")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'add_typed_credential 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f"add_typed_credential 最大重试次数已达，仍不成功。e={e}")
                        raise
                else:
                    logger.error(f"add_typed_credential 失败: e={e}")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试

        helper_sleep.wait_a_bit(3, f'add_typed_credential end. {self.__account.log_info_v2()}')

    def __get_captcha(self):
        if self.captcha is None:
            self.captcha = service_captcha.ServiceCaptcha(self.__account)

        cur_captcha = self.captcha.get_captcha_for_galxe_wrapper()

        return cur_captcha

    def _get_gamification_type(self, campaign):
        """
        例子
        "gamification": {
            "id": "GCp7CtvBZw",
            "type": "Points",
            "__typename": "Gamification",
            "forgeConfig": null,
            "nfts": [],
            "airdrop": null
        },
        获取这个campaign的奖励类型

        :param campaign:
        :return:
        """
        if 'gamification' not in campaign:
            return None
        ret = campaign['gamification']['type']
        logger.info(f"end. ret({ret})")
        return ret

    def _campaign_points_claimed(self, campaign) -> bool:
        """
        "whitelistInfo": {
            "address": "0x11efba5731d2367e5d2f065e7ccb449f9ff7bd24",
            "maxCount": -1,
            "usedCount": 0,
            "claimedLoyaltyPoints": 0,   已经领取的分数
            "currentPeriodClaimedLoyaltyPoints": 0, 当前周期的意义也不懂？ 已经领取的分数
            "currentPeriodMaxLoyaltyPoints": 45, 能领取的最大分数
            "__typename": "WhitelistAddress"
            },

            "loyaltyPoints": 45,  这个部分我观察也是能领取的最大分数，也是就说不做任务先显示这个分数
        :param campaign:
        :return:
        """
        # 我也不懂为什么叫做whitelistInfo
        logger.warning(f" 已经领取的分数currentPeriodClaimedLoyaltyPoints({campaign['whitelistInfo']['currentPeriodClaimedLoyaltyPoints']}) \n"
                    f"最大可领取的分数currentPeriodMaxLoyaltyPoints({campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints']}) \n"
                    f"已经领取的分数claimedLoyaltyPoints({campaign['claimedLoyaltyPoints']}) \n"
                    f"最大可领取的分数loyaltyPoints({campaign['loyaltyPoints']}) \n"
                    f"_daily_points_claimed({self._daily_points_claimed(campaign)}) \n"
                    f"{self.__account.log_info_v2()}")

        return campaign['whitelistInfo']['currentPeriodClaimedLoyaltyPoints'] >= \
            campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints'] and \
            campaign['claimedLoyaltyPoints'] >= campaign['loyaltyPoints'] and self._daily_points_claimed(campaign)

    def get_pointMintAmount(self, campaign: dict) -> int:
        currentPeriodMaxLoyaltyPoints = campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints']
        logger.info(f" currentPeriodMaxLoyaltyPoints({currentPeriodMaxLoyaltyPoints}) {self.__account.log_info_v2()}")

        currentPeriodClaimedLoyaltyPoints = campaign['whitelistInfo']['currentPeriodClaimedLoyaltyPoints']
        logger.info(f" currentPeriodClaimedLoyaltyPoints({currentPeriodClaimedLoyaltyPoints}) {self.__account.log_info_v2()}")

        pointMintAmount = currentPeriodMaxLoyaltyPoints - currentPeriodClaimedLoyaltyPoints
        logger.info(f" 要去领取的分数pointMintAmount({pointMintAmount}) {self.__account.log_info_v2()}")
        return pointMintAmount

    # 获取要mint的nft的数量
    # update 9-5 如果是已经部分领取成功了，那么就是视为全部成功，就不再领取了，原理上不清楚了，但是继续领取会因为缺参数报错
    def get_mintCount(self, campaign: dict) -> int:
        maxCount = campaign['whitelistInfo']['maxCount']
        usedCount = campaign['whitelistInfo']['usedCount']
        logger.info(f" maxCount({maxCount}) usedCount({usedCount}) {self.__account.log_info_v2()}")

        # 如果部分领取了，就不需要再领取了
        if usedCount != 0:
            logger.info(f" usedCount({usedCount}) 不为0，直接返回0 {self.__account.log_info_v2()}")
            return 0

        ret = maxCount - usedCount
        logger.info(f" 要去领取的nft的数量ret({ret}) {self.__account.log_info_v2()}")
        return ret

    def _is_daily_campaign(self, campaign):
        """
         "recurringType": "ONCE",
         campaign属性 分为每天更新的，还有一次性的
        :param campaign:
        :return:
        """
        ret = campaign.get('recurringType') == model_galxe.Recurring.DAILY
        logger.info(f" recurringType({campaign.get('recurringType')}) {self.__account.log_info_v2()}")
        return ret

    def _is_parent_campaign(self, campaign):
        """
        "type": "Points",
         为什么type可能是父亲啊？
        """
        ret = campaign.get('type') == 'Parent'
        logger.info(f" type({campaign.get('type')}) {self.__account.log_info_v2()}")

        return ret

    # 每天任务是啥意思？？
    def _daily_points_claimed(self, campaign):
        # 这个或为什么或父亲
        if not self._is_daily_campaign(campaign) or self._is_parent_campaign(campaign):
            logger.info(f"Not a daily campaign or parent campaign _is_daily_campaign({self._is_daily_campaign(campaign)})")
            return True

        if campaign['whitelistInfo']['currentPeriodClaimedLoyaltyPoints'] < \
                campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints']:
            logger.info(f"Not all daily points claimed currentPeriodClaimedLoyaltyPoints({campaign['whitelistInfo']['currentPeriodClaimedLoyaltyPoints']})"
                        f"currentPeriodMaxLoyaltyPoints({campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints']})")
            return False

        if campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints'] > 0:
            logger.info(f"All daily points claimed currentPeriodMaxLoyaltyPoints({campaign['whitelistInfo']['currentPeriodMaxLoyaltyPoints']})")
            return True

        ret = all(cg['claimedLoyaltyPoints'] > 0 for cg in campaign['credentialGroups'])
        logger.info(f"All daily points claimed ret({ret}) {self.__account.log_info_v2()}")
        return ret

    def _campaign_nft_claimed(self, campaign) -> bool:
        """
        "whitelistInfo": {
            "address": "0x11efba5731d2367e5d2f065e7ccb449f9ff7bd24",
            "maxCount": -1,
            "usedCount": 0,
            "claimedLoyaltyPoints": 0,
            "currentPeriodClaimedLoyaltyPoints": 0,
            "currentPeriodMaxLoyaltyPoints": 45,
            "__typename": "WhitelistAddress"
            },

            nft类型啊
            dc角色也算
        """
        ret = 0 < campaign['whitelistInfo']['maxCount'] <= campaign['whitelistInfo']['usedCount']

        logger.info(f" maxCount({campaign['whitelistInfo']['maxCount']}) usedCount({campaign['whitelistInfo']['usedCount']}) {self.__account.log_info_v2()}")
        logger.info(f"end. ret({ret}) true表示已经领取 false表示还没领取 {self.__account.log_info_v2()}")
        return ret

    # 直接根据campaign的信息判断要不要去领取，很牛逼
    def already_claimed(self, campaign) -> bool:
        # 获取这个campaign的奖励类型
        gamification_type = self._get_gamification_type(campaign)

        logger.info(f' gamification_type({gamification_type}) {self.__account.log_info_v2()}')
        match gamification_type:
            # 如果是分数类型
            # 那么根据_campaign_points_claimed判断是不是已经领取了
            case model_galxe.Gamification.POINTS:
                return self._campaign_points_claimed(campaign)

            # notice 这里的原理是，可能一个任务既有分数，又有nft
            #  那么gamification_type类型算nft，但是也需要判断分数是不是领取了
            #  也需要判断nft是不是领取了
            case model_galxe.Gamification.OAT | model_galxe.Gamification.DROP:
                return self._campaign_points_claimed(campaign) and self._campaign_nft_claimed(campaign)

            case model_galxe.Gamification.POINTS_MYSTERY_BOX | \
                 model_galxe.Gamification.BOUNTY | \
                 model_galxe.Gamification.DISCORD_ROLE | \
                 model_galxe.Gamification.TOKEN:
                return self._campaign_nft_claimed(campaign)

            case unexpected:
                # if HIDE_UNSUPPORTED:
                #     return False
                logger.warning(f'{unexpected} gamification type is not supported yet')
                return False

    def get_campaign_info_with_retry(self, campaign_id: str) -> dict:
        retries = 3  # 最大重试次数

        for attempt in range(retries):
            try:
                return self.__dao_galxe.get_campaign_info_with_retry(self.address_lower(), campaign_id)
            except Exception as e:
                if 'failed to get quest participation addresses' in str(e):
                    logger.warning(f"尝试第 {attempt + 1} 次，连接被重置: {e}")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'get_campaign_info重试中')  # 计算等待时间并等待
                    else:
                        logger.info("最大重试次数已达，仍未能成功连接。")
                        raise
                else:
                    logger.error(f"请求失败: {e}")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试

    def already_claimed_by_campaign_ids(self, campaign_ids: list) -> bool:
        all_done = True
        for campaign_id in campaign_ids:
            is_already_claimed = self.already_claimed_campaign(campaign_id)
            if not is_already_claimed:
                all_done = False
        return all_done

    def already_claimed_campaign(self, campaign_id: str) -> bool:
        logger.info(f' start. campaign_id({campaign_id}) {self.__account.log_info_v2()}')

        campaign = self.get_campaign_info_with_retry(campaign_id)

        if self.already_claimed(campaign):
            logger.warning(f' 根据任务详情就判断出了已经领取了 campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
            return True
        else:
            logger.warning(f' 还没完成这个任务 campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
            return False

    def claim_campaign(self, campaign_id: str) -> bool:
        logger.warning(f' start开始领取！ campaign_id({campaign_id}) {self.__account.log_info_v2()}')

        campaign = self.get_campaign_info_with_retry(campaign_id)

        # 如果已经领取就直接返回
        if self.already_claimed(campaign):
            logger.warning(f'根据任务详情就判断出了已经领取 already claimed campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
            return False

        # 如果没有领取就去领取
        logger.info(f' start 判断结果是需要去领取 campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
        claimable = False

        # 这个cred_idx，仅仅用于日志，其实没啥用
        for cred_idx, cred_group in enumerate(campaign['credentialGroups'], start=1):
            # 所有的cred_group必须完成才能领取。
            # 错啦
            # notice。这里是只有一个cred_group能领取，就直接break跳出循环去领取
            # 所以有个任务是没完成推荐的任务，但是也能领取
            if claimable:
                logger.info(f'Enough conditions eligible to claim campaign_name({campaign["name"]})')
                break

            # try:
            claimable = self._is_cred_group_claimable(cred_group, cred_idx)

            # except Exception as e:
            #     logger.error(f'Failed to check cred group#{cred_idx} for claim e={e}')

        if not claimable:
            logger.warning(f'Not enough conditions eligible to claim campaign_name({campaign["name"]})')
            return False

        # TODO 计算pointMintAmount的方法有几种，
        #  1 遍历credentialGroups，   总结：我先使用这种方法吧
        #  2 直接根据外层属性判断
        # notice，观察到pointMintAmount传了15，比实际的45要小，但是还是领取到了45分数，非常神奇
        #  但是谨慎来说，还是要计算所有的分数的，防止被银河ban了

        pointMintAmount = self.get_pointMintAmount(campaign)  # 要去领取的分数

        # 真的领取的函数
        self._claim_campaign_rewards_v2(campaign, pointMintAmount)

        logger.success(f'end. Claimed campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
        return True

    # cred_group是一个数组
    def _is_cred_group_claimable(self, cred_group, cred_idx):
        logger.info(f'start cred_group({cred_group}) cred_idx({cred_idx})')

        # if cred_group["credSource"]== model_galxe.CredSource.CAMPAIGN_REFERRAL:
        #     logger.warning(f'_is_cred_group_claimable cred_group["credSource"]({cred_group["credSource"]}) is not supported yet')
        #     return False

        points_rewards = [r for r in cred_group['rewards'] if r['rewardType'] == 'LOYALTYPOINTS']
        logger.info(f' points_rewards({points_rewards}) {self.__account.log_info_v2()}')

        only_points = len(points_rewards) == len(cred_group['rewards'])
        logger.info(f' only_points({only_points}) {self.__account.log_info_v2()}')

        # 所有可能获取的积分
        available_points = 0
        for r in points_rewards:
            logger.info(f' r({r}) {self.__account.log_info_v2()}')
            if r['expression'].isdigit():
                available_points = available_points + int(r['expression'])

        # available_points = sum(int(r['expression']) for r in points_rewards)
        logger.info(f' available_points({available_points}) {self.__account.log_info_v2()}')

        # 已经领取的积分
        claimed_points = cred_group['claimedLoyaltyPoints']
        logger.info(f' claimed_points({claimed_points}) {self.__account.log_info_v2()}')

        if claimed_points >= available_points and only_points:
            return False

        eligible = [c['eligible'] for c in cred_group['conditions']]
        logger.info(f' eligible({eligible}) {self.__account.log_info_v2()}')

        left_points = available_points - claimed_points
        logger.info(f' left_points({left_points}) {self.__account.log_info_v2()}')

        claimable = False

        logger.info(f' cred_group["conditionRelation"]({cred_group["conditionRelation"]})')
        match cred_group['conditionRelation']:
            # 完成cred_group中所有子任务才能领取
            case model_galxe.ConditionRelation.ALL:
                # all是python函数
                claimable = all(eligible)

            case model_galxe.ConditionRelation.ANY:
                # any是python函数
                claimable = any(eligible)
            case unexpected:
                logger.warning(f' {unexpected} condition relation is not supported yet')

        if not claimable:
            not_claimable_msg = ([('[+] ' if c['eligible'] == 1 else '[-] ') + c["name"]
                                  for c in cred_group["credentials"]] +
                                 [f"{left_points} points left"])
            if len(not_claimable_msg) > 1:
                not_claimable_msg[0] = ' ' + not_claimable_msg[0]
            not_claimable_msg = f'group#{cred_idx} [{" | ".join(not_claimable_msg)}]'
            not_claimable_msg = f'Not enough conditions eligible to claim {not_claimable_msg}'
            logger.warning(f' 不可以领取，原因是 not_claimable_msg({not_claimable_msg})')
        else:
            logger.warning(f' 是可以领取的 {self.__account.log_info_v2()}')

        return claimable

    # notice 暂时不删代码，等v2版本运行稳定了再删代码
    # # 真正去领取奖励的逻辑。
    # # 原版本
    # def _claim_campaign_rewards(self, campaign: dict, pointMintAmount: int):
    #     """
    #
    #     :param campaign:
    #     :param pointMintAmount:要去领取的分数
    #     :return:
    #     """
    #     # 奖励类型
    #     reward_type = campaign['gamification']['type']
    #     if reward_type is None:
    #         logger.warning(f'_claim_campaign_rewards reward_type is None')
    #         return
    #
    #     logger.info(f'_claim_campaign_rewards start campaign_name({campaign["name"]}) reward_type({reward_type}) pointMintAmount({pointMintAmount}) {self.__account.log_info_v2()}')
    #
    #     # 这一步就是领取分数，下一步才是领取nft，所以这一步没分数时要跳过
    #     if pointMintAmount > 0:
    #         claim_data_v1 = self._get_claim_data(campaign, pointMintAmount, mintCount=0)
    #     else:
    #         logger.warning(f'_claim_campaign_rewards pointMintAmount is 0, 跳过这一步骤的银河api交互')
    #         claim_data_v1 = None
    #         if reward_type == model_galxe.Gamification.POINTS:
    #             # 没必要算exp
    #             logger.warning(f'_claim_campaign_rewards reward_type is POINTS, 但是pointMintAmount是0')
    #             # exp = Exception(f'_claim_campaign_rewards reward_type({reward_type}) is POINTS, 但是pointMintAmount是0，这是不可能的')
    #             # logger.error(exp)
    #             # raise exp
    #
    #     logger.info(f'_claim_campaign_rewards claim_data_v1({claim_data_v1}) {self.__account.log_info_v2()}')
    #
    #     # claimed_points = 0
    #     # claimed_nfts = 0
    #     # nft_type = ''
    #     # 奖励的类型
    #     match reward_type:
    #         # 积分类型，积分神秘盒子类型
    #         # 积分神秘盒子本质就是随机给积分
    #         case model_galxe.Gamification.POINTS | model_galxe.Gamification.POINTS_MYSTERY_BOX:
    #             logger.info(f'_claim_campaign_rewards Claiming points for campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
    #
    #             # # 如果不等于none
    #             # if claim_data_v1.get('loyaltyPointsTxResp'):
    #             #     claimed_points = claim_data_v1['loyaltyPointsTxResp'].get('TotalClaimedPoints')
    #
    #             # claimed_log = f'{claimed_points} points'
    #
    #             # if reward_type == model_galxe.Gamification.POINTS_MYSTERY_BOX:
    #             # claimed_log += ' from Mystery Box'
    #
    #         # 如果是oat
    #         # 前面已经领取了分数，这里仅仅是领取nft
    #         # notice 任务奖励类型同时有nft和分数的时候，这里算nft
    #         case model_galxe.Gamification.OAT | model_galxe.Gamification.DROP:
    #             logger.info(f'_claim_campaign_rewards Claiming nfts for campaign {campaign["name"]} reward_type({reward_type}) {self.__account.log_info_v2()}')
    #
    #             mintCount = self.get_mintCount(campaign)  # 要去领取的nft的数量
    #             logger.info(f'_claim_campaign_rewards mintCount({mintCount}) {self.__account.log_info_v2()}')
    #             if mintCount > 0:
    #                 # 重新获取claim_data
    #                 claim_data_v2 = self._get_claim_data(campaign=campaign, pointMintAmount=0, mintCount=mintCount)
    #                 logger.info(f'_claim_campaign_rewards 重新获取claim_data. mintCount({mintCount}) {self.__account.log_info_v2()} claim_data_v2({claim_data_v2}) ')
    #
    #                 nft_type = 'NFT' if reward_type == model_galxe.Gamification.DROP else 'OAT'
    #                 logger.info(f'_claim_campaign_rewards nft_type({nft_type}) {self.__account.log_info_v2()}')
    #
    #                 gas_less = campaign['gasType'] == model_galxe.GasType.GAS_LESS
    #                 logger.info(f'_claim_campaign_rewards gas_less({gas_less}) {self.__account.log_info_v2()}')
    #
    #                 was_gasless = False
    #
    #                 if gas_less:
    #                     sufficient = self.__dao_galxe.sufficient_for_gasless_chain_query(
    #                         int(campaign['space']['id']),
    #                         campaign['chain'],
    #                     )
    #                     logger.info(f'_claim_campaign_rewards 项目方是否有足够的钱帮忙免费用sufficient({sufficient}) {self.__account.log_info_v2()}')
    #                     # update 10-11 从https://app.galxe.com/quest/Route-X/GCw6xtkFpV任务看，现在好像不需要判断sufficient，都能让项目方帮忙支付gas领取
    #                     # if not sufficient:
    #                     #     logger.warning(f'Insufficient space balance for gasless claim')
    #                     #     # was_gasless表示曾经是不需要gas的
    #                     #     gas_less, was_gasless = False, True
    #
    #                 if not gas_less:
    #                     self._claim_gas_reward_v2(campaign, claim_data_v2, was_gasless)
    #
    #                 # mintFuncInfo字段是none
    #                 # claimed_nfts = len(claim_data_v2['mintFuncInfo']['verifyIDs'])
    #                 # claimed_log = f"claimed_nfts={claimed_nfts} nft_type={nft_type}"
    #
    #             else:
    #
    #                 logger.warning(f'_claim_campaign_rewards mintCount({mintCount}) is 0, 就不需要领取了')
    #                 # claimed_log = 'No NFTs to claim'
    #
    #         case model_galxe.Gamification.BOUNTY:
    #             logger.info(f' Claiming bounty for campaign {campaign["name"]}')
    #
    #             # claimed_log = '[Participated in Bounty]'
    #
    #         # 是dc角色
    #         case model_galxe.Gamification.DISCORD_ROLE:
    #             logger.info(f' Claiming discord role for campaign {campaign["name"]}')
    #
    #             # claimed_log = '[Discord Role]'
    #
    #         # 直接给币
    #         case model_galxe.Gamification.TOKEN:
    #             logger.info(f' Claiming token reward for campaign {campaign["name"]}')
    #
    #             # if campaign.get('distributionType') == 'RAFFLE':
    #             #     claimed_log = '[Participated in Raffle]'
    #             # else:
    #             #     raise Exception('Unexpected distribution type for token reward')
    #
    #         case unexpected:
    #             raise Exception(f'{unexpected} reward type is not supported for claim yet')
    #
    #     # result = ('Points', claimed_points) if claimed_points > 0 else None
    #     # result = (nft_type, claimed_nfts) if claimed_nfts > 0 else result
    #
    #     # logger.success(f'领取成功 Campaign({campaign["name"]}) claimed claimed_log({claimed_log}) result({result})')
    #
    #     # 返回值没有意义
    #     # return result
    #     return

    def _claim_campaign_rewards_v2_point(self, campaign: dict, pointMintAmount: int):
        logger.info(f'start')

        if pointMintAmount == 0:
            logger.warning(f' reward_type is POINTS, 但是pointMintAmount是0。 不算异常，但是有点其奇怪')
            is_claim_campaign_success = False
            return is_claim_campaign_success

        prepareParticipate_resp = self._get_claim_data(campaign, pointMintAmount, mintCount=0)
        logger.info(f'prepareParticipate_resp({prepareParticipate_resp})')

        loyaltyPointsTxResp = prepareParticipate_resp['loyaltyPointsTxResp']

        loyaltyPointDistributionStation = loyaltyPointsTxResp['loyaltyPointDistributionStation']
        logger.info(f'loyaltyPointDistributionStation({loyaltyPointDistributionStation})')

        signature = loyaltyPointsTxResp['signature']
        logger.info(f'signature({signature})')

        loyaltyPointContract = loyaltyPointsTxResp['loyaltyPointContract']
        logger.info(f'loyaltyPointContract({loyaltyPointContract})')

        if len(loyaltyPointDistributionStation) == 0 and len(signature) == 0 and len(loyaltyPointContract) == 0:
            logger.warning(f'不需要g链tx，直接结束')
            return


        VerifyIDs = loyaltyPointsTxResp['VerifyIDs']
        VerifyID = VerifyIDs[0]
        logger.info(f'VerifyIDs({VerifyIDs}) VerifyID({VerifyID})')


        Points = loyaltyPointsTxResp['Points']
        Point = Points[0]
        logger.info(f'Points({Points}) Points({Points})')

        nonce = loyaltyPointsTxResp['nonce']
        logger.info(f'nonce({nonce})')



        #  切换g链
        self.__account.switch_chain(rpc_config.GChainConfig)

        # 领取奖励：先生成tx
        tx_hash = self.__account.galxe_claim_point_on_g_chain(
            point_contract=loyaltyPointContract,
            verifyID=VerifyID,
            point_amount=Point,
            signature=signature,
        )

        # 真的领取奖励：需要把刚才的tx发给银河
        self.__dao_galxe.participatePoint(
            address_evm_prefix_and_eip55=self.address_evm_prefix_and_eip55(),
            campaign_id=campaign['id'],
            chain='GRAVITY_ALPHA',  # 直接写死
            nonce=nonce,
            tx_hash=tx_hash,
            verifyIDs=VerifyIDs)

        logger.info(f'end')

    def _claim_campaign_rewards_v2_OAT(self, campaign: dict, pointMintAmount: int):
        """
        # notice 任务奖励类型同时有nft和分数的时候，先领取分数，再领取nft，是两个步骤

        :param campaign:
        :param pointMintAmount:
        :return:
        """
        logger.info(f'start')

        self._claim_campaign_rewards_v2_point(campaign, pointMintAmount)

        mintCount = self.get_mintCount(campaign)  # 要去领取的nft的数量
        logger.info(f' mintCount({mintCount}) {self.__account.log_info_v2()}')

        if mintCount > 0:
            # 重新获取claim_data
            claim_data_v2 = self._get_claim_data(campaign=campaign, pointMintAmount=0, mintCount=mintCount)
            logger.info(f' 重新获取claim_data. mintCount({mintCount}) {self.__account.log_info_v2()} claim_data_v2({claim_data_v2}) ')

            gas_less = campaign['gasType'] == model_galxe.GasType.GAS_LESS
            logger.info(f' gas_less({gas_less}) {self.__account.log_info_v2()}')

            if not gas_less:
                self._claim_gas_reward_v2(campaign, claim_data_v2)
            else:
                logger.info(f'项目方支付gas了，那么我就什么都不需要做了')
        else:
            logger.warning(f' mintCount({mintCount}) is 0, 就不需要领取了')

        logger.info(f'end')

    # v2和原版的区别就是，删除了一些注释，并对不同的类型对了不同的处理
    def _claim_campaign_rewards_v2(self, campaign: dict, pointMintAmount: int):
        """
        积分类型的话，就是先_get_claim_data领取积分 ，再判断要不要tx，但是只是g链
        oat类型的，也是先_get_claim_data领取积分，再判断要不要tx，但是要看链
        其他类型的话pointMintAmount，肯定是

        :param campaign:
        :param pointMintAmount:要去领取的分数
        :return:
        """
        logger.info(f' start. campaign_name({campaign["name"]}) pointMintAmount({pointMintAmount}) {self.__account.log_info_v2()}')

        reward_type = campaign['gamification']['type']  # 奖励类型
        logger.info(f' start reward_type({reward_type}) {self.__account.log_info_v2()}')

        match reward_type:
            # 积分类型，or，积分神秘盒子类型（积分神秘盒子本质就是随机给积分）
            case model_galxe.Gamification.POINTS | model_galxe.Gamification.POINTS_MYSTERY_BOX:

                logger.info(f' Claiming points for campaign_name({campaign["name"]}) {self.__account.log_info_v2()}')
                self._claim_campaign_rewards_v2_point(campaign, pointMintAmount)

            # 本质是NFT
            case model_galxe.Gamification.OAT | model_galxe.Gamification.DROP:

                logger.info(f' Claiming nfts for campaign {campaign["name"]} reward_type({reward_type}) {self.__account.log_info_v2()}')
                self._claim_campaign_rewards_v2_OAT(campaign, pointMintAmount)

            case model_galxe.Gamification.BOUNTY | model_galxe.Gamification.DISCORD_ROLE | model_galxe.Gamification.TOKEN:
                logger.info(f' 当前奖励类型只打印日志 reward_type({reward_type}) {campaign["name"]}')

            case unexpected:
                raise Exception(f'{unexpected} reward type is not supported for claim yet')

        return

    def _get_claim_data(self, campaign: dict, pointMintAmount: int, mintCount: int = 0):
        logger.warning(f' start 去调prepare_participate campaign_name({campaign["name"]}) pointMintAmount({pointMintAmount}) {self.__account.log_info_v2()}')

        chain = campaign['chain']

        if chain == 'APTOS':
            raise Exception(f' Aptos claim rewards is not supported')

        cur_service_referral_code = service_referral_code.ServiceReferralCode()
        referral_code = cur_service_referral_code.get_referral_code(campaign['id'])
        if len(referral_code) == 0:
            logger.info(f' referral_code is empty')
        else:
            logger.info(f' referral_code={referral_code}')

        # update 9-5 经常Failed to verify recaptcha，我尝试次数从5次改为8次
        retries = 8  # 最大重试次数。多重试几次
        for attempt in range(retries):
            try:
                captcha = self.__get_captcha()

                # 这一步已经是领取奖励了
                # 如果是不需要gas，那么这一步就算是领取完成了
                return self.__dao_galxe.prepare_participate(
                    self.address_evm_prefix_and_lower(),
                    campaign['id'],
                    captcha,
                    chain,
                    pointMintAmount,
                    referral_code=referral_code,
                    mintCount=mintCount
                )
            except Exception as e:
                if 'Failed to record billing' in str(e) or \
                        'Failed to verify recaptcha token' in str(e) or \
                        'Exceeded request limit, please try again later' in str(e):
                    logger.warning(f"_get_claim_data 需要重试的错误是 1验证码识别 2银河记录失败. attempt({attempt}) exp({e})")
                    attempt += 1
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, 'prepare_participate重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f" 最大重试次数已达，仍未能成功连接。{e}")
                        raise
                else:
                    logger.error(f"_get_claim_data 请求失败: {e}")
                    raise

    # 考虑批量的场景
    def _claim_gas_reward_v2(self, campaign, claim_data, was_gasless=False):
        logger.info(f' start. claim_data({claim_data}) {self.__account.log_info_v2()}')

        space_station = campaign['spaceStation']
        logger.info(f' start campaign_name({campaign["name"]}) space_station({space_station}) {self.__account.log_info_v2()}')

        # 什么合约，什么链，都要获取到
        space_station_address, space_chain = space_station['address'], space_station['chain']

        # 如果true，那么使用任务的链，而不是space的链
        if was_gasless:
            space_chain = campaign['chain']
            logger.info(f' was_gasless space_chain({space_chain}) {self.__account.log_info_v2()}')

        # 收到配置里面处理
        # CHAIN_NAME_MAPPING = {'MATIC': 'Polygon'}
        # 马蹄链的名字有个改写
        # capitalize是首字母大写的python内置函数
        # chain = CHAIN_NAME_MAPPING.get(space_chain, space_chain.capitalize())

        #  切换account使用的链
        cur_chain_config = self.__get_chain_config_by_name(chain_name=space_chain)
        self.__account.switch_chain(cur_chain_config)
        logger.info(f' space_chain({space_chain}) switch_chain({cur_chain_config}) {self.__account.log_info_v2()}')

        number_id = campaign['numberID']
        logger.info(f' number_id({number_id}) {self.__account.log_info_v2()}')

        signature = claim_data['signature']
        logger.info(f' signature({signature}) {self.__account.log_info_v2()}')

        nonce = claim_data['nonce']  # notice 不用于生成tx，而是作为于下一步和银河交互的接口参数
        logger.info(f' nonce({nonce}) {self.__account.log_info_v2()}')

        nft_core_address = claim_data['mintFuncInfo']['nftCoreAddress']
        logger.info(f' nft_core_address({nft_core_address}) {self.__account.log_info_v2()}')

        verifyIDs = claim_data['mintFuncInfo']['verifyIDs']
        logger.info(f' verifyIDs({verifyIDs}) {self.__account.log_info_v2()}')

        powahs = claim_data['mintFuncInfo']['powahs']
        logger.info(f' powahs({powahs}) {self.__account.log_info_v2()}')

        # 领取奖励，发生tx
        # 在指定合约，制定链上领取奖励
        tx_hash = self.__account.galxe_claim_v2(
            space_station_address=space_station_address,
            number_id=number_id,
            signature=signature,
            nft_core_address=nft_core_address,
            verifyIDs=verifyIDs,
            powahs=powahs
        )

        # 真的领取奖励
        # 需要把刚才的tx发给银河
        self.__dao_galxe.participate(
            address_evm_prefix_and_eip55=self.address_evm_prefix_and_eip55(),
            campaign_id=campaign['id'],
            chain=space_chain,
            nonce=nonce,
            tx_hash=tx_hash,
            verifyIDs=verifyIDs)

        logger.success(f'end. Claimed gas reward for campaign {campaign["name"]} cur_chain_config={cur_chain_config} tx_hash={tx_hash} {self.__account.log_info_v2()}')

    # def complete_and_claim_campaign_with_retry(self, campaign_id: str):
    #     retries = 3  # 最大重试次数
    #     for attempt in range(retries):
    #         try:
    #             return self.complete_and_claim_campaign(campaign_id)  # 成功后退出循环
    #         except Exception as e:
    #             if '又是all类型又当前子任务又失败' in str(e):
    #                 logger.warning(f"complete_and_claim_campaign_with_retry 去做重试的第({attempt + 1})次，e({e})")
    #                 if attempt < retries - 1:
    #                     helper_sleep.calculate_backoff_time_and_sleep(attempt, 'complete_and_claim_campaign_with_retry 重试中')  # 计算等待时间并等待
    #                 else:
    #                     logger.error(f"complete_and_claim_campaign_with_retry 最大重试次数已达，仍不成功。e({e})")
    #                     raise
    #             else:
    #                 logger.error(f"complete_and_claim_campaign_with_retry 失败,e({e})")
    #                 # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
    #                 raise  # 其他请求异常，不重试

    # def complete_and_claim_campaign_can_not_allow(self, campaign_id: str) -> bool:
    #     """
    #     或许项目方还没同步数据，不allow也行，不算报错
    #     :param campaign_id:
    #     :return:
    #     """
    #     try:
    #         self.complete_and_claim_campaign(campaign_id)
    #         return True  # 成功后退出循环
    #     except Exception as e:
    #         logger.warning(f"complete_and_claim_campaign_can_not_allow 失败,e({e})")
    #         if '又是all类型又当前子任务又失败' in str(e):
    #             return False
    #         else:
    #             logger.error(f"complete_and_claim_campaign_with_retry 失败,e({e})")
    #             # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
    #             raise  # 其他请求异常，不重试

    def complete_and_claim_campaign(self, campaign_id: str) -> (bool, bool, bool):
        """
        :return:  ret = (already_claimed, is_complete_campaign_success, is_claim_success) python 不能提前定义返回值
        """

        logger.info(f' start. campaign_id({campaign_id}) {self.__account.log_info_v2()}')
        already_claimed, is_complete_campaign_success, is_claim_success = False, False, False

        already_claimed = self.already_claimed_campaign(campaign_id)
        logger.info(f' already_claimed({already_claimed}) campaign_id({campaign_id}) {self.__account.log_info_v2()}')

        if already_claimed:
            logger.info(f'已经领取')
            return already_claimed, False, False

        is_complete_campaign_success = self.complete_campaign(campaign_id)
        # 如果任务成功完成（也验证完成）
        if is_complete_campaign_success:
            # 2s对于关注space可能不够
            # 5s可能部分分数没更新
            helper_sleep.wait_a_bit(20, "complete_and_claim_campaign 完成和领取之间等待")
            is_claim_success = self.claim_campaign(campaign_id)
            if is_claim_success:
                logger.success(f' end. campaign_id({campaign_id}) {self.__account.log_info_v2()}')

        logger.warning(f' already_claimed({already_claimed}) is_complete_campaign_success({is_complete_campaign_success}) is_claim_success({is_claim_success})')
        return already_claimed, is_complete_campaign_success, is_claim_success

    """
                  ╔═══════════════════════════════════════════════════════════════════════╗
                  ║ 以下是 movement aptos相关的                                              ║
                  ╚═══════════════════════════════════════════════════════════════════════╝
    """

    async def galxe_echelon_7_day_check(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCPQGtkBS3",
        ]
        galxe_event = "echelon_7_day_check_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        base_new_event = 'echelon_one_day_check'
        did_online_aptos = False
        did_online_galxe = False

        did_online_aptos = await cur_ServiceAccountAptos.echelon_today_check(base_new_event)
        logger.info(f' echelon_today_check did_online_aptos({did_online_aptos})')
        if did_online_aptos:
            has_signed_for_7days = cur_ServiceAccountAptos.echelon_has_signed_for_7days(base_new_event)

            if has_signed_for_7days:
                helper_sleep.wait_a_bit(time_gap, "galxe_echelon_7_day_check 链上和银河之间等待")

                # 第三步，验证银河
                all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_meridian_7_day_check(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GC28GtkSqd",
        ]
        galxe_event = "meridian_7_day_check_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        base_new_event = 'meridian_dex_one_day_check'
        did_online_aptos = False
        did_online_galxe = False
        did_online_aptos = await cur_ServiceAccountAptos.meridian_dex_today_check(base_new_event)
        logger.info(f' meridian_dex_today_check did_online_aptos({did_online_aptos})')
        if did_online_aptos:
            has_signed_for_7days = cur_ServiceAccountAptos.meridian_dex_is_check_7days(base_new_event)

            if has_signed_for_7days:
                helper_sleep.wait_a_bit(time_gap, "galxe_meridian_7_day_check 链上和银河之间等待")

                # 第三步，验证银河
                all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_echelon(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCjk8txqAA",  # Borrow 3 unique assets on Echelon
            "GC2AGtkWkW",  # Borrow any asset on Echelon
            "GCanGtkrK7",  # Supply any asset on Echelon
        ]
        # random.shuffle(cur_campaign_id_list)  # 有顺序依赖
        online_event = "galxe_echelon_online"
        galxe_event = "echelon_cur_campaign_id_"
        time_gap = 10 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f'galxe_echelon 银河都完成了')
            return True, False

        did_online_aptos = False
        did_online_galxe = False

        # 第二步，做链上
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.echelon()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True

            helper_sleep.wait_a_bit(time_gap, "galxe_echelon 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_mosaic_dex(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GC4Qetvzju",
            "GC4Petvh3W",
            "GCwJetvdcw",
            "GC4KetvdKq",
        ]
        # random.shuffle(cur_campaign_id_list)  # 有顺序依赖
        online_event = "galxe_Mosaic_dex_online"
        galxe_event = "mosaic_dex_cur_campaign_id_"
        time_gap = 5 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.Mosaic_dex()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_mosaic_dex 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    # async def galxe_route_x_dex(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
    #     logger.info(f' start. {self.__account.log_info_v2()}')
    #
    #     # 第零步，初始化配置
    #     cur_campaign_id_list = [
    #         "GCprxtk6kL",  # 10-24截止时间
    #     ]
    #     random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
    #     online_event = "galxe_route_x_dex_online"
    #     galxe_event = "route_x_dex_cur_campaign_id_"
    #     time_gap = 5 * 60
    #
    #     # 第一步，验证当前状态
    #     all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
    #     if all_done:
    #         logger.info(f' 银河都完成了')
    #         return True, False
    #
    #     # 第二步，做链上
    #     did_online_aptos = False
    #     did_online_galxe = False
    #     if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
    #         await  cur_ServiceAccountAptos.route_x_dex()
    #         self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
    #         did_online_aptos = True
    #         helper_sleep.wait_a_bit(time_gap, "galxe_route_x_dex 链上和银河之间等待")
    #
    #     # 第三步，验证银河
    #     all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)
    #
    #     logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
    #
    #     return all_done, did_online_aptos or did_online_galxe

    async def galxe_razor_dex(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCAZttvuys",
            "GC94ttv9vW",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "galxe_razor_dex_online_v2"
        galxe_event = "razor_dex_cur_campaign_id_"
        time_gap = 10 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.razor_dex()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_razor_dex 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_razor_dex_LP(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCFAttvPoC",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "galxe_razor_dex_LP_online_v2"
        galxe_event = "razor_dex_cur_campaign_id_"
        time_gap = 10 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.razor_dex_10_LP_move_usdc()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_razor_dex_LP 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_meridian_dex(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GC9FGtk7Pp",
            "GC2hGtkWe1",
            "GCvTutxVA4",
            "GCG3utxsYe",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "galxe_meridian_dex_online"
        galxe_event = "meridian_dex_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.meridian_dex()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_meridian_dex 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def galxe_seekers_alliance(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GC1JCtkRV6",
            "GCpbCtkicS",
            "GC65CtkS2X",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "galxe_seekers_alliance_online"
        galxe_event = "seekers_alliance_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.seekers_alliance()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_seekers_alliance 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe
        # notice 没有办法做一个总的记录，因为步骤太多了，也因为子步骤都有记录了也行吧 update 必须要做整体记录，因为函数入口先判断银河是不是做完了

    async def galxe_hypervative_dex(self, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCCEutxFrC",
            "GC3MutxHFs",
            "GCJVutxHkR",
        ]
        # random.shuffle(cur_campaign_id_list)  # 有顺序依赖
        online_event = "galxe_hypervative_dex_online"
        galxe_event = "hypervative_dex_cur_campaign_id_"
        time_gap = 10 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_aptos = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            await  cur_ServiceAccountAptos.hypervative_dex_30_swap()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_aptos = True
            helper_sleep.wait_a_bit(time_gap, "galxe_hypervative_dex 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_aptos({did_online_aptos}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_aptos or did_online_galxe

    async def xenobunny_mint(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCXoQtx8ng",
        ]
        # random.shuffle(cur_campaign_id_list)  # 有顺序依赖
        online_event = "xenobunny_mint_online"
        galxe_event = "xenobunny_mint_cur_campaign_id_"
        time_gap = 10

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            self.__account.movement_dapp_xenobunny_mint()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "online_event 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe

    async def avitus(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        online_event_faucet = "avitus_online_faucet"
        online_event_approve = "avitus_online_approve"
        time_gap = 10

        # 第二步，做链上
        did_online = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_faucet):
            self.__account.movement_dapp_avitus_faucet()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_faucet)
            did_online = True
            helper_sleep.wait_a_bit(time_gap, "online_event_faucet 之间等待")

        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_approve):
            self.__account.movement_dapp_avitus_approve_usdc()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_approve)
            did_online = True
            helper_sleep.wait_a_bit(time_gap, "online_event_approve 之间等待")

        logger.warning(f'end. did_online({did_online}) {self.__account.log_info_v2()}')
        return True, did_online

    # ut了确认可以验证银河
    async def zoth(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCGoktKR8M",
        ]
        # random.shuffle(cur_campaign_id_list)  # 有顺序依赖
        online_event = "zoth_online"
        galxe_event = "zoth_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            self.__account.movement_dapp_zoth()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "zoth 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe

    async def rndm(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        cur_campaign_id_list = [
            "GCyZftK3jb",  #只有一个任务
        ]
        online_event_approve = "rndm_online"
        galxe_event = "rndm_cur_campaign_id_"
        time_gap = 20

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False


        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_approve):
            self.__account.movement_dapp_rndm()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_approve)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "rndm 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)


        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe

    async def gasyard_deposit(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCDHotKEYW", # 只做存钱的银河
        ]
        online_event = "gasyard_online"
        galxe_event = "gasyard_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            self.__account.movement_dapp_gasyard_deposit_move()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "online_event 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe

    async def layerbank(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCKrYtxrfK",
        ]
        online_event_available_as_collateral = "layerbank_online_available_as_collateral"
        online_event_deposit_move            = "layerbank_online_deposit_move"
        online_event_borrow_move             = "layerbank_online_borrow_move"
        galxe_event = "layerbank_cur_campaign_id_"
        time_gap = 10

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_available_as_collateral):
            self.__account.movement_dapp_layerbank_available_as_collateral()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_available_as_collateral)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "online_event_available_as_collateral 等待")
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_deposit_move):
            self.__account.movement_dapp_layerbank_deposit_move()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_deposit_move)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "online_event_deposit_move 等待")
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event_borrow_move):
            self.__account.movement_dapp_layerbank_borrow_move()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event_borrow_move)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "online_event_borrow_move 等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe


    async def fluswap_faucet(self) -> (bool, bool):
        logger.info(f' start. {self.__account.log_info_v2()}')

        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCPX8tKfBC",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "fluswap_faucet_online"
        galxe_event = "fluswap_faucet_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            self.__account.fluswap_5_faucet()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "fluswap_faucet 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe


    async def fluswap_swap(self) -> (bool, bool):

        logger.info(f' start. {self.__account.log_info_v2()}')


        all_done, did_online = await  self.fluswap_faucet()
        if did_online:
            helper_sleep.sleep_wrap(20,'领水和操作之间时间间隔')



        # 第零步，初始化配置
        cur_campaign_id_list = [
            "GCab8tKmwa",
        ]
        random.shuffle(cur_campaign_id_list)  # 没有顺序依赖
        online_event = "fluswap_swap_online"
        galxe_event = "fluswap_swap_cur_campaign_id_"
        time_gap = 1 * 60

        # 第一步，验证当前状态
        all_done = self.already_claimed_by_campaign_ids(cur_campaign_id_list)
        if all_done:
            logger.info(f' 银河都完成了')
            return True, False

        # 第二步，做链上
        did_online_evm = False
        did_online_galxe = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=online_event):
            self.__account.fluswap_approve_and_5_swap()
            self.record.append_event(account_name=self.__account.account_name, new_event=online_event)
            did_online_evm = True
            helper_sleep.wait_a_bit(time_gap, "fluswap_swap 链上和银河之间等待")

        # 第三步，验证银河
        all_done, did_online_galxe = self.galxe_aptos_do_campaign_list_and_record(galxe_event, cur_campaign_id_list)

        logger.warning(f'end. all_done({all_done}) did_online_evm({did_online_evm}) did_online_galxe({did_online_galxe}) {self.__account.log_info_v2()}')
        return all_done, did_online_evm or did_online_galxe





    def galxe_aptos_do_campaign_list_and_record(self, base_event, cur_campaign_id_list) -> (bool, bool):
        all_done = True
        did_online = False

        for campaign_id in cur_campaign_id_list:

            cur_event = base_event + campaign_id
            logger.info(f' cur_event({cur_event})')

            if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=cur_event):

                (already_claimed, is_complete_campaign_success, is_claim_success) = self.complete_and_claim_campaign(campaign_id)

                if already_claimed or is_claim_success:
                    logger.info(f' 已经领取和领取成功都需要记录db')
                    self.record.append_event(account_name=self.__account.account_name, new_event=cur_event)
                else:
                    logger.warning(f' 没成功就告诉上层没成功')
                    all_done = False

                if is_claim_success:
                    helper_sleep.wait_a_bit(10, "galxe_aptos_do_campaign_list_and_record for循环任务之间等待")
                    did_online = True

        logger.warning(f' end. all_done({all_done}) {self.__account.log_info_v2()}')
        return all_done, did_online

    async def galxe_aptos_dispatcher(self, task_event, cur_ServiceAccountAptos: service_account_aptos.ServiceAccountAptos):
        logger.info(f' start. task_event({task_event})')
        did_online = False
        if not self.record.event_exists(account_name=self.__account.account_name, event_to_check=task_event):
            did_online = True

            all_done = False
            match task_event:
                case 'echelon':
                    all_done, did_online = await  self.galxe_echelon(cur_ServiceAccountAptos)
                case 'mosaic_dex':
                    all_done, did_online = await  self.galxe_mosaic_dex(cur_ServiceAccountAptos)
                # case 'route_x_dex':
                #     all_done, did_online = await  self.galxe_route_x_dex(cur_ServiceAccountAptos)
                case 'razor_dex':
                    all_done, did_online = await  self.galxe_razor_dex(cur_ServiceAccountAptos)
                case 'razor_dex_LP':
                    all_done, did_online = await  self.galxe_razor_dex_LP(cur_ServiceAccountAptos)
                case 'meridian_dex':
                    all_done, did_online = await  self.galxe_meridian_dex(cur_ServiceAccountAptos)
                case 'seekers_alliance':
                    all_done, did_online = await  self.galxe_seekers_alliance(cur_ServiceAccountAptos)
                case 'hypervative_dex':
                    all_done, did_online = await  self.galxe_hypervative_dex(cur_ServiceAccountAptos)

                case 'galxe_echelon_7_day_check':
                    all_done, did_online = await  self.galxe_echelon_7_day_check(cur_ServiceAccountAptos)
                case 'galxe_meridian_7_day_check':
                    all_done, did_online = await  self.galxe_meridian_7_day_check(cur_ServiceAccountAptos)

                # case 'xenobunny_mint': #过期了
                #     all_done, did_online = await  self.xenobunny_mint()
                case 'avitus': # 不能全部脚本
                    all_done, did_online = await  self.avitus()
                case 'zoth':
                    all_done, did_online = await  self.zoth()
                case 'rndm': # 不能全部脚本
                    all_done, did_online = await  self.rndm()
                case 'gasyard_deposit':
                    all_done, did_online = await  self.gasyard_deposit()
                case 'layerbank':
                    all_done, did_online = await  self.layerbank()

                case 'tx_25_times':
                    all_done, did_online = await  cur_ServiceAccountAptos.tx_25_times()


                case 'fluswap_faucet':
                    all_done, did_online = await  self.fluswap_faucet()
                case 'fluswap_swap':
                    all_done, did_online = await  self.fluswap_swap()

                case unexpected:
                        raise Exception(f'unexpected {unexpected} is not supported yet')

            logger.info(f' all_done({all_done}) did_online({did_online})')
            if all_done:
                self.record.append_event(account_name=self.__account.account_name, new_event=task_event)

        logger.info(f' end. did_online({did_online})')
        return did_online


def ut_aptos():
    helper_logger.init_logger()
    account_name = "F08"

    # 从db读一个元素出来 new account实例
    password = 'Android123!'
    cur_ServiceAccountEVMStorage = service_account_evm_storage.ServiceAccountEVMStorage()
    cur_account_storage = cur_ServiceAccountEVMStorage.get_account_by_name_after_decode(account_name, password)

    logger.info(f"one_account_info={cur_account_storage.name}")

    account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()

    cur_account_evm = service_account_evm.Account(account_name=cur_account_storage.name,
                                                  address=cur_account_storage.address,
                                                  private_key=cur_account_storage.private_key,
                                                  cur_header=account_header_map[cur_account_storage.name]
                                                  )
    cur_ServiceGalxe = ServiceGalxe(cur_account_evm)

    cur_ServiceAccountAptosStorage = service_account_aptos_storage.ServiceAccountAptosStorage()
    cur_account_aptos_storage = cur_ServiceAccountAptosStorage.get_account_by_name_after_decode(account_name, password)

    cur_ServiceAccountAptos = service_account_aptos.ServiceAccountAptos(account_name=cur_account_aptos_storage.name,
                                                                        private_key=cur_account_aptos_storage.private_key,
                                                                        chain_config=rpc_config.MovementAptosTestNetChainConfig, )

    asyncio.run(cur_ServiceGalxe.galxe_route_x_dex(cur_ServiceAccountAptos))


if __name__ == '__main__':
    ut_aptos()
