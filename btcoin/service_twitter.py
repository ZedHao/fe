import json
from datetime import datetime

from loguru import logger

import helper_json
import helper_logger
import helper_session
import helper_sleep
import helper_url

import model_twitter
import random

import service_account_record_v2

"""
还是得干同步，异步时报错太复杂，自己都不好处理
"""


# 没做dao层，只能是先这么干了，直接抄的
class ServiceTwitter:

    def __init__(self, twitter_auth_token: str = None, proxy: str = None, header: dict = None,account_name:str=None):

        if not twitter_auth_token:
            raise Exception('Empty twitter auth token')

        if not proxy:
            raise Exception('Empty proxy')
        self.proxy = proxy

        self.my_user_id = None
        self.my_username = None

        self.__session = helper_session.new_session(proxy, header)

        # 更新了推特特有的header
        self.__session.headers.update(_get_headers_only_for_twitter())

        if 'Accept-Encoding' in self.__session.headers:
            del self.__session.headers['Accept-Encoding']
            logger.info(f"ServiceTwitter init 删除Accept-Encoding")
        if 'Connection' in self.__session.headers:
            del self.__session.headers['Connection']
            logger.info(f"ServiceTwitter init 删除Connection")
        if 'x-client-uuid' in self.__session.headers:
            del self.__session.headers['x-client-uuid']
            logger.warning(f'！！好像现在推特已经不需要x-client-uuid参数了')


        logger.info(f"ServiceTwitter init 打印最终版本的headers({self.__session.headers}))")

        self.__session.cookies.update({
            'auth_token': twitter_auth_token,
            'ct0': '',
        })

        self.__start()


        self._account_name= account_name
        self._record=service_account_record_v2.ServiceAccountRecordV2()

    # 一开始就要获取ct0，这个是必须的
    # update 9-7 算私有函数，新建推特对象的时候，就会调用这个函数
    def __start(self):
        ct0 = self._get_ct0()
        if not ct0:
            raise Exception('ServiceTwitter start Empty ct0')

        logger.info(f'ServiceTwitter start 获取ct0: {ct0}')

        self.__session.cookies.update({'ct0': ct0})
        self.__session.headers.update({'x-csrf-token': ct0})

        self.my_username = self.get_my_profile_info()
        logger.warning(f'ServiceTwitter start 获取用户名: {self.my_username}')

        self.my_user_id = self.get_user_id(self.my_username)
        logger.warning(f'ServiceTwitter start 获取推特用户ID: {self.my_user_id}')

    # 重新更新cookie
    def set_cookies(self, resp_cookies):
        # 循环解析所有的cookie，然后设置当当前的cookie
        self.__session.cookies.update({name: value.value for name, value in resp_cookies.items()})

    # 怎么获取，程序刚开始的时候
    def _get_ct0(self):
        logger.info(f'_get_ct0 start')

        cur_url = 'https://api.x.com/1.1/account/settings.json'
        resp = self.__session.get(cur_url)
        logger.info(f'_get_ct0 status_code({resp.status_code})')
        logger.info(f'_get_ct0 text({resp.text})')  # 这里返回err也没关系，这里只是拿cookie不需要返回值
        logger.info(f'_get_ct0 cookies({resp.cookies})')

        # resp_json= resp.json()
        # if 'errors' in resp_json and

        new_csrf = resp.cookies.get("ct0")
        return new_csrf

    def get_my_profile_info(self):
        url = 'https://api.x.com/1.1/account/settings.json'
        params = {
            'include_mention_filter': 'true',
            'include_nsfw_user_flag': 'true',
            'include_nsfw_admin_flag': 'true',
            'include_ranked_timeline': 'true',
            'include_alt_text_compose': 'true',
            'ext': 'ssoConnections',
            'include_country_code': 'true',
            'include_ext_dm_nsfw_media_filter': 'true',
            'include_ext_sharing_audiospaces_listening_data_with_followers': 'true',
        }
        resp = self.__session.get(url, params=params)
        self.set_cookies(resp.cookies)

        resp_json = resp.json()
        logger.info(f'get_my_profile_info resp_json({resp_json})')

        if 'errors' in resp_json and len(resp_json['errors']) > 0:
            exp = Exception(f'Get my profile info 获取我的推特信息失败 {str(resp_json)}')
            logger.error(exp)

            if 'this account is temporarily locked' in str(resp_json):
                raise Exception('账户被临时锁定了，去做验证码，不需要重新获取token')

            raise exp

        """
        get_my_profile_info resp_json({'errors': [{'code': 326, 'message': 'To protect our users from spam and other malicious activity, this account is temporarily locked. Please log in to https://twitter.com to unlock your account.', 'sub_error_code': 0, 'bounce_location': 'https://twitter.com/account/access'}]})
        临时锁定，需要去网页上登录做验证
        就解决了
        说明还是代码不够像真人
        """

        # 返回推特名字，不是账户名字，是用户名字
        ret = resp_json['screen_name'].lower()
        logger.info(f'获取我的推特name ret({ret})')
        return ret

    def get_user_id(self, username):
        logger.info(f'get_user_id start. username({username})')

        url = 'https://x.com/i/api/graphql/9zwVLJ48lmVUk8u_Gh9DmA/ProfileSpotlightsQuery'
        # 能兼容@的情况
        if username[0] == '@':
            username = username[1:]
        username = username.lower()
        params = {
            'variables': to_json({'screen_name': username})
        }
        resp = self.__session.get(url, params=params)
        self.set_cookies(resp.cookies)

        resp_json = resp.json()
        logger.info(f'get_user_id resp_json({resp_json})')

        # 返回int数据类型的用户id
        ret = int(resp_json['data']['user_result_by_screen_name']['result']['rest_id'])
        logger.info(f'获取用户id ret({ret})')
        return ret

    # 关注
    def follow(self, username) -> None:
        logger.warning(f'follow start. 要关注这个人username({username})')

        user_id = self.get_user_id(username)
        url = 'https://x.com/i/api/1.1/friendships/create.json'
        params = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_has_nft_avatar': '1',
            'include_ext_is_blue_verified': '1',
            'include_ext_verified_type': '1',
            'include_ext_profile_image_shape': '1',
            'skip_status': '1',
            'user_id': user_id,
        }
        # 关注别人的时候，不能真的改变header，只能是在这个请求里面加上
        # 自己解析请求看了看，还真是表单，不是json，牛逼了
        # 其他的都是json形式只有这个是表单形式
        self.__session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
        self.__session.headers.update({'x-client-transaction-id': model_twitter.generate_random_x_client_transaction_id()})  # 加入随机的x-client-transaction-id参数
        for key, value in self.__session.headers.items():
            logger.info(f"follow 查看headers每个元素 key({key}) value({value})")
        for key, value in self.__session.cookies.items():
            logger.info(f"follow 查看cookies每个元素 key({key}) value({value})")

        # notice post的params是表单的参数
        resp = self.__session.post(url, params=params)
        self.set_cookies(resp.cookies)

        resp_json = resp.json()
        logger.info(f'follow resp_json({(resp_json)})')

        if 'errors' in resp_json and \
                len(resp_json['errors']) > 0 and \
                'message' in resp_json['errors'][0] and \
                len(resp_json['errors'][0]['message']) > 0:
            exp=Exception(f'follow resp_json({resp_json})')
            logger.error(exp)
            raise exp


        self._record.append_event(self._account_name, 'follow'+datetime.now().strftime("_%Y-%m-%d_%H:%M:%S"))
        logger.success(f'关注成功 username({username})')


    # 给发推加入重试机制
    def post_tweet_wrapper(self, text) -> str:

        retries = 3
        for attempt in range(retries):
            try:
                return self.__post_tweet(text)
            except Exception as e:
                logger.error(f'e({str(e)})')

                if 'This request looks like it might be automated' in str(e):
                    logger.warning(f'post_tweet_wrapper 推特说我像机器人，我重试一下 attempt({attempt}) e({e})')
                    if attempt < retries - 1:
                        helper_sleep.wait_a_bit(30*attempt, f'推特')
                        continue

                elif 'You have reached your daily limit for sending Tweets and messages' in str(e):
                    logger.warning(f'post_tweet_wrapper 推特说达到上限 attempt({attempt}) e({e})')
                    if attempt < retries - 1:
                        helper_sleep.wait_a_bit(30*attempt, f'post_tweet_wrapper attempt({attempt}) ')
                        continue

                exp = Exception(f'post_tweet_wrapper attempt({attempt}) error({str(e)})')
                logger.error(exp)
                raise exp

    # 发推需要这么多参数吗？？？？我草这么复杂吗
    def __post_tweet(self, text) -> str:
        logger.warning(f' start. 发推的文案是({text})')

        action = "CreateTweet"
        query_id = "oB-5XsHNAbjvARJEc8CZFw"  # 观察到不一样的值 TODO
        # 字典的键可以不使用引号
        _json = dict(
            variables=dict(
                tweet_text=text,
                media=dict(
                    media_entities=[],
                    possibly_sensitive=False
                ),
                semantic_annotation_ids=[],
                dark_request=False
            ),
            features=dict(
                communities_web_enable_tweet_community_results_fetch=True,
                c9s_tweet_anatomy_moderator_badge_enabled=True,
                tweetypie_unmention_optimization_enabled=True,
                responsive_web_edit_tweet_api_enabled=True,
                graphql_is_translatable_rweb_tweet_is_translatable_enabled=True,
                view_counts_everywhere_api_enabled=True,
                longform_notetweets_consumption_enabled=True,
                responsive_web_twitter_article_tweet_consumption_enabled=True,
                tweet_awards_web_tipping_enabled=False,
                creator_subscriptions_quote_tweet_preview_enabled=False,
                longform_notetweets_rich_text_read_enabled=True,
                longform_notetweets_inline_media_enabled=True,
                articles_preview_enabled=True,
                rweb_video_timestamps_enabled=True,
                rweb_tipjar_consumption_enabled=True,
                responsive_web_graphql_exclude_directive_enabled=True,
                verified_phone_label_enabled=False,
                freedom_of_speech_not_reach_fetch_enabled=True,
                standardized_nudges_misinfo=True,
                tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled=True,
                responsive_web_graphql_skip_user_profile_image_extensions_enabled=False,
                responsive_web_graphql_timeline_navigation_enabled=True,
                responsive_web_enhance_cards_enabled=False,
            ),
            queryId=query_id,
        )

        url = f'https://x.com/i/api/graphql/{query_id}/{action}'

        self.__session.headers.update({'content-type': 'application/json'})
        self.__session.headers.update({'x-client-transaction-id': model_twitter.generate_random_x_client_transaction_id()})  # 加入随机的x-client-transaction-id参数
        tmp_dict={}
        for key, value in self.__session.headers.items():
            logger.info(f" 查看headers每个元素 key({key}) value({value})")
            tmp_dict[key] = value
        for key, value in tmp_dict.items():
            logger.info(f" 查看headers每个元素 v2 tmp_dict key({key}) value({value})")

        for key, value in self.__session.cookies.items():
            logger.info(f" 查看cookies每个元素 key({key}) value({value})")

        resp = self.__session.post(url, json=_json)
        self.set_cookies(resp.cookies)
        resp_json = resp.json()
        logger.info(f' resp_json({(helper_json.build_json_one_line(resp_json))})')

        """
        不可能啊，我新买的token，还没发几条消息啊，不是表示我被封号了
        草了，网页能发推。
        又行了，神奇，经验就是重试，
        resp_json({'errors': [{'message': 'Authorization: You have reached your daily limit for sending Tweets and messages. Please try again later. (344)', 'locations': [{'line': 18, 'column': 3}], 'path': ['create_tweet'], 'extensions': {'name': 'AuthorizationError', 'source': 'Client', 'code': 344, 'kind': 'Permissions', 'tracing': {'trace_id': '5180713cdf5b3117'}}, 'code': 344, 'kind': 'Permissions', 'name': 'AuthorizationError', 'source': 'Client', 'tracing': {'trace_id': '5180713cdf5b3117'}}], 'data': {}})
        """

        if 'errors' in resp_json and len(resp_json['errors']) > 0:
            exp = Exception(f'Post tweet error: {str(resp_json)}')
            logger.error(f'发推失败 resp_json({str(resp_json)})')
            raise exp

        def _handler(resp):
            _result = resp['data']['create_tweet']['tweet_results']['result']
            _username = _result['core']['user_results']['result']['legacy']['screen_name']
            _tweet_id = _result['rest_id']
            _url = f'https://x.com/{_username}/status/{_tweet_id}'
            return _url

        ret = _handler(resp_json)

        self._record.append_event(self._account_name, 'post_tweet'+datetime.now().strftime("_%Y-%m-%d_%H:%M:%S"))
        logger.success(f'发推成功，返回url ret({ret})')
        return ret

    # 这里必须克服蜜罐，真的推特成功，不然外部的2cap反复去做的话，就浪费太多钱了
    def retweet_with_retry(self, referenceLink) -> None:
        retries = 7
        for attempt in range(retries):
            resp_json = self.__retweet(referenceLink)
            if 'errors' in resp_json and len(resp_json['errors']) > 0 and 'message' in resp_json['errors'][0]:

                message = resp_json['errors'][0]['message']

                if 'You have already retweeted this Tweet' in message:
                    logger.success(f'retweet_with_retry 已经转推过了，才算成功 attempt({attempt}) referenceLink({referenceLink}) message({message})')
                    return
                elif 'Could not authenticate you' in message:
                    exp = Exception(f'retweet_with_retry 推特报错未认证需要去重新登录，失败 attempt({attempt}) referenceLink({referenceLink}) message({message})')
                    logger.error(exp)
                    raise exp
                else:
                    logger.warning(f"retweet_with_retry 有除了已经转推的其他报错，要重试 attempt({attempt}) message({message})")
                    helper_sleep.calculate_backoff_time_and_sleep(attempt, f'retweet 重试中 attempt({attempt})', base_delay=60)
            else:
                logger.warning(f'retweet_with_retry 没有提示已经转推，要重试 attempt({attempt}) ')
                # update 9-21 60s肯定不够，加到90s
                helper_sleep.calculate_backoff_time_and_sleep(attempt, f'retweet_with_retry 重试中 ({attempt})', base_delay=90)

    def __retweet(self, referenceLink) -> dict:
        tweet_id = helper_url.get_query_param(referenceLink, 'tweet_id')

        logger.info(f'__retweet start. referenceLink({referenceLink}) tweet_id({tweet_id})')

        self.__session.headers.update({'content-type': 'application/json'})
        self.__session.headers.update({'x-client-transaction-id': model_twitter.generate_random_x_client_transaction_id()})  # 加入随机的x-client-transaction-id参数
        self.__session.headers.update({'referer': referenceLink})
        for key, value in self.__session.headers.items():
            logger.info(f"__retweet 查看headers每个元素 ({key}):({value})")
        for key, value in self.__session.cookies.items():
            logger.info(f"__retweet 查看cookies每个元素 ({key}):({value})")

        action = 'CreateRetweet'
        query_id = 'ojPdsZsimiJrUGLR1sjUtA'  # TODO 这个固定的是什么？？？？抓包接口也是这样的
        url = f'https://x.com/i/api/graphql/{query_id}/{action}'
        _json = {
            'variables': {
                'tweet_id': tweet_id,
                'dark_request': False
            },
            'queryId': query_id
        }

        logger.info(f'__retweet 转推请求的json post数据({_json})')

        resp = self.__session.post(url, json=_json)
        self.set_cookies(resp.cookies)  # 更新cookie

        resp_json = resp.json()
        logger.warning(f'__retweet 转推的接口返回({resp_json}) tweet_id({tweet_id})')


        self._record.append_event(self._account_name, 'retweet'+datetime.now().strftime("_%Y-%m-%d_%H:%M:%S"))
        return resp_json

    def like(self, tweet_id) -> None:
        """
        点赞已经私有，所有任务都不需要真的做
        """
        pass
        # logger.info(f'like start tweet_id({tweet_id})')
        # action = 'FavoriteTweet'
        # query_id = 'lI07N6Otwv1PhnEgXILM7A'
        # url = f'https://x.com/i/api/graphql/{query_id}/{action}'
        # _json = {
        #     'variables': {
        #         'tweet_id': tweet_id,
        #         'dark_request': False
        #     },
        #     'queryId': query_id
        # }
        #
        # self.__session.headers.update({'content-type': 'application/json'})
        # resp = self.__session.post(url, json=_json)
        # self.set_cookies(resp.cookies)
        # resp_json = resp.json()
        # logger.info(f'like resp_json({resp_json})')
        #
        # if 'errors' in resp_json and len(resp_json['errors']) > 0:
        #     for error in resp_json['errors']:
        #         if 'message' in error and 'has already favorited tweet' in error['message']:
        #             logger.warning(f'已经点赞过了，也算成功 tweet_id({tweet_id})')
        #             return
        #
        # if resp_json['data']['favorite_tweet'] == 'Done':
        #     logger.success(f'点赞成功 tweet_id({tweet_id})')
        # else:
        #     raise Exception(f'Like失败 resp_json({str(resp_json)})')

    # 找我自己的发的推特
    def find_posted_tweet(self, text_condition_func, count=5) -> str:
        action = "UserTweets"
        query_id = "V1ze5q3ijDS1VeLwLY0m7g"
        params = {
            'variables': to_json({
                "userId": self.my_user_id,
                "count": count,
                "includePromotedContent": False,
                "withQuickPromoteEligibilityTweetFields": False,
                "withVoice": False,
                "withV2Timeline": True,
            }),
            'features': to_json({
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False,
            }),
        }

        url = f'https://x.com/i/api/graphql/{query_id}/{action}'

        self.__session.headers.update({'content-type': 'application/json'})
        # 加入随机的x-client-transaction-id参数
        self.__session.headers.update({'x-client-transaction-id': model_twitter.generate_random_x_client_transaction_id()})
        # 打印 headers 的每个元素
        for key, value in self.__session.headers.items():
            logger.info(f"find_posted_tweet 查看headers每个元素 ({key}):({value})")
        for key, value in self.__session.cookies.items():
            logger.info(f"find_posted_tweet 查看cookies每个元素 ({key}):({value})")

        resp = self.__session.get(url, params=params)
        self.set_cookies(resp.cookies)
        resp_json = resp.json()
        logger.info(f'find_posted_tweet resp_json({helper_json.build_json_one_line(resp_json)})')

        def _handler(resp):
            instructions = resp['data']['user']['result']['timeline_v2']['timeline']['instructions']
            entries = None
            for instruction in instructions:
                if instruction['type'] == 'TimelineAddEntries':
                    entries = instruction['entries']
                    break
            if entries is None:
                return None
            for entry in entries:
                tweet_text = entry['content']['itemContent']['tweet_results']['result']
                tweet_text = tweet_text['legacy']['full_text']
                if text_condition_func and not text_condition_func(tweet_text):
                    continue
                tweet_id = entry['entryId']
                if tweet_id.startswith('tweet-'):
                    tweet_id = tweet_id[6:]
                _url = f'https://x.com/{self.my_username}/status/{tweet_id}'
                return _url
            return None

        ret = _handler(resp_json)
        logger.success(f'找到推特 ret({ret})')
        return ret


def to_json(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


# 都是固定的一个就很假，我十几个号，都是一个头就不行啊
# 可能需要一个号对应一个头
def _get_headers_only_for_twitter() -> dict:
    # USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    # SEC_CH_UA = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
    # SEC_CH_UA_PLATFORM = '"macOS"'

    return {
        'accept': '*/*',
        'priority': 'u=1, i',  # update 9-20 加了字段
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',  # update 9-20 除了英语加了其他
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',

        'origin': 'https://x.com',
        'referer': 'https://x.com/',  # TODO 如果是转推的话，那么可以用当前的链接，更真实

        # x-twitter-client-language、x-twitter-active-user 和 x-twitter-auth-type 这几个 HTTP 请求头字段
        # 是 Twitter 在某些请求中使用的私有自定义头部字段，通常与 Twitter 客户端应用的 API 调用相关。
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en',
        'x-csrf-token': '',

        # 每个请求手动定义
        # 'content-type': 'application/json',

        # notice 以下这些参数我已经固定在header里面了
        # 'user-agent': USER_AGENT,
        # 'x-client-uuid': random.choice(model_twitter.x_client_uuid_list),
        # 'sec-ch-ua': SEC_CH_UA,
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': SEC_CH_UA_PLATFORM,
        # 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors',
        # 'sec-fetch-site': 'same-origin',

    }


import service_account_header


def main():
    header = service_account_header.RealisticHeaderGenerator().generate_header()

    # AshleyMaug18073:ptc67QIVZDfLYrc:mtkirros@rambler.ru:ifWiys1kr:auth_token=f31d4a12ffc64a9841c4fd18d4a7303c7fcf6065:2024.08.11

    twitter_auth_token = 'f31d4a12ffc64a9841c4fd18d4a7303c7fcf6065'
    proxy = 'http://127.0.0.1:7890'

    service_twitter = ServiceTwitter(twitter_auth_token, proxy, header)

    # service_twitter.post_tweet('hiiiii')

    # service_twitter.follow("@qingqinglove520")
    #
    # service_twitter.find_posted_tweet(None, 5)


# 解决无法转推 1817610094768480605 的问题
# 草了，单独测试的时候转推成功了
def ut_retweet():
    header = service_account_header.RealisticHeaderGenerator().generate_header()

    # AshleyMaug18073:ptc67QIVZDfLYrc:mtkirros@rambler.ru:ifWiys1kr:auth_token=f31d4a12ffc64a9841c4fd18d4a7303c7fcf6065:2024.08.11

    twitter_auth_token = '9f26f4998f5dc93b1fa60c51324b5af672a7e2c9'
    proxy = 'http://127.0.0.1:7890'

    cur_service_twitter = ServiceTwitter(twitter_auth_token, proxy, header)


if __name__ == "__main__":
    helper_logger.init_logger()
    ut_retweet()
