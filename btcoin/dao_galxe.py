from typing import Dict, Any

import helper_json


from loguru import logger


import helper_session
import helper_sleep


# dao层怎么处理resp返回报错？是返回false，还是exp？
# 直接的写法就是直接exp中断程序就完事了，不给service做这一步了
class DaoGalxe:
    # Optional[X] 实际上是 Union[X, None] 的简写。
    def __init__(self, proxy: str, header: dict = None):

        self.__session = helper_session.new_session(proxy=proxy, header=header)
        # 银河只有一个url
        self.__galxe_url = 'https://graphigo.prd.galaxy.eco/query'

    def __post_wrapper_with_retry(self, json_payload_body: Dict[str, Any]) -> Dict[str, Any]:
        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                return self.__post_wrapper(json_payload_body)
            except Exception as e:
                if 'Expecting value' in str(e) or \
                        'Connection reset by peer' in str(e):
                    logger.warning(f"__post_wrapper_with_retry 去做重试的第({attempt + 1})次，e({e})")
                    if attempt < retries - 1:
                        helper_sleep.calculate_backoff_time_and_sleep(attempt, '__post_wrapper_with_retry 重试中')  # 计算等待时间并等待
                    else:
                        logger.error(f"__post_wrapper_with_retry 最大重试次数已达，仍不成功。e({e})")
                        raise
                else:
                    logger.error(f"__post_wrapper_with_retry 失败,e({e})")
                    # 简洁性：如果我们使用 raise e，会重新创建一个异常对象，导致原始异常的堆栈跟踪丢失。因此，直接使用 raise 更加适合在捕获异常后再次抛出。
                    raise  # 其他请求异常，不重试



    # 我再封装一层post，都是同一个url，都是json post形式
    def __post_wrapper(self, json_payload_body: Dict[str, Any]) -> Dict[str, Any]:
        response = self.__session.post(url=self.__galxe_url, json=json_payload_body).json()
        return response

    # 检查这个地址的银河账户是否存在，决定后面要不要创建账户
    def check_galxe_id_exist(self, address):
        payload = {
            "operationName": "GalxeIDExist",  # 这么判断是否存在id
            "variables": {
                "schema": f"EVM:{address}"
            },
            "query": "query GalxeIDExist($schema: String!) {\n  galxeIdExist(schema: $schema)\n}\n"
        }

        resp = self.__post_wrapper_with_retry(payload)

        logger.info(f"check_galxe_id_exist resp: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"check_galxe_id_exist err resp: {resp}")
            logger.error(exp)
            raise exp

        if resp['data']['galxeIdExist']:
            return True
        return False

    # # 登录银河
    # def sign_in_v1(self, address, text, signature):
    #     """
    #     登录银河
    #     :param address:
    #     :param signature:
    #     :return:
    #     """
    #
    #     data = {
    #         "operationName": "SignIn",
    #         "variables": {
    #             "input": {
    #                 "address": address,
    #                 "message": text,
    #                 # 之前的这个写法是tm很有问题啊，这里还有逻辑，不应该的
    #                 "signature": signature.hex(),
    #                 "addressType": "EVM"
    #             }
    #         },
    #         "query": "mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n"
    #     }
    #
    #     response = self.__session.post(url=self.__galxe_url, json=data).json()
    #     logger.info(f"Sign in response: {response}")
    #
    #     # 登录的核心就是在header里面设置Authorization字段，这就算登录了
    #     self.__session.headers.update(
    #         {
    #             'Authorization': response['data']['signin']
    #         }
    #     )
    #
    #     return True

    # 登录银河
    def sign_in_v2(self, address_EIP55, text, signature):

        data = {
            "operationName": "SignIn",
            "variables": {
                "input": {
                    "address": address_EIP55,
                    "message": text,
                    "signature": signature,
                    "addressType": "EVM"
                }
            },
            "query": "mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n"
        }

        # resp = self.__session.post(url=self.__galxe_url, json=data).json()
        resp = self.__post_wrapper_with_retry(json_payload_body=data)
        logger.info(f"Sign in resp: {resp}")

        """
        Sign in response: {'errors': [{'message': 'message could not be parsed', 'path': ['signin'], 'extensions': {'code': 'Unknown'}}], 'data': {'signin': ''}}
        """

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"sign_in_v2 err resp: {resp}")
            logger.error(exp)
            raise exp

        # 登录的核心就是在header里面设置Authorization字段，这就算登录了
        self.__session.headers.update(
            {
                'Authorization': resp['data']['signin']
            }
        )

        return True

    # # 获取任务的凭证ID。
    # def get_cred_id(self , address):
    #     payload = {
    #         "operationName": "CampaignDetailAll",
    #         "variables": {
    #             "address": address,
    #             "id": "GCTN3ttM4T",
    #             "withAddress": True
    #         },
    #         "query": "query CampaignDetailAll($id: ID!, $address: String!, $withAddress: Boolean!) {\n  campaign(id: $id) {\n    ...CampaignForSiblingSlide\n    coHostSpaces {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    bannerUrl\n    ...CampaignDetailFrag\n    userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n      list {\n        status\n        premintTo\n        __typename\n      }\n      __typename\n    }\n    space {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    isBookmarked(address: $address) @include(if: $withAddress)\n    inWatchList\n    claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n    parentCampaign {\n      id\n      isSequencial\n      thumbnail\n      __typename\n    }\n    isSequencial\n    numNFTMinted\n    childrenCampaigns {\n      ...ChildrenCampaignsForCampaignDetailAll\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignDetailFrag on Campaign {\n  id\n  ...CampaignMedia\n  ...CampaignForgePage\n  ...CampaignForCampaignParticipantsBox\n  name\n  numberID\n  type\n  inWatchList\n  cap\n  info\n  useCred\n  smartbalancePreCheck(mintCount: 1)\n  smartbalanceDeposited\n  formula\n  status\n  seoImage\n  creator\n  tags\n  thumbnail\n  gasType\n  isPrivate\n  createdAt\n  requirementInfo\n  description\n  enableWhitelist\n  chain\n  startTime\n  endTime\n  requireEmail\n  requireUsername\n  blacklistCountryCodes\n  whitelistRegions\n  rewardType\n  distributionType\n  rewardName\n  claimEndTime\n  loyaltyPoints\n  tokenRewardContract {\n    id\n    address\n    chain\n    __typename\n  }\n  tokenReward {\n    userTokenAmount\n    tokenAddress\n    depositedTokenAmount\n    tokenRewardId\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  spaceStation {\n    id\n    address\n    chain\n    __typename\n  }\n  ...WhitelistInfoFrag\n  ...WhitelistSubgraphFrag\n  gamification {\n    ...GamificationDetailFrag\n    __typename\n  }\n  creds {\n    id\n    name\n    type\n    credType\n    credSource\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    syncStatus\n    credContractNFTHolder {\n      timestamp\n      __typename\n    }\n    chain\n    eligible(address: $address, campaignId: $id)\n    subgraph {\n      endpoint\n      query\n      expression\n      __typename\n    }\n    dimensionConfig\n    value {\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  credentialGroups(address: $address) {\n    ...CredentialGroupForAddress\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildId\n      guildName\n      roleId\n      roleName\n      inviteLink\n      __typename\n    }\n    premint {\n      startTime\n      endTime\n      chain\n      price\n      totalSupply\n      contractAddress\n      banner\n      __typename\n    }\n    loyaltyPoints {\n      points\n      __typename\n    }\n    loyaltyPointsMysteryBox {\n      points\n      weight\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    bountyWinnersCount\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    referralConfig {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  referralCode(address: $address)\n  recurringType\n  latestRecurringTime\n  nftTemplates {\n    id\n    image\n    treasureBack\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  rewardName\n  type\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupForAddress on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForAddressWithoutMetadata\n    __typename\n  }\n  conditionRelation\n  conditions {\n    expression\n    eligible\n    ...CredentialGroupConditionForVerifyButton\n    __typename\n  }\n  rewards {\n    expression\n    eligible\n    rewardCount\n    rewardType\n    __typename\n  }\n  rewardAttrVals {\n    attrName\n    attrTitle\n    attrVal\n    __typename\n  }\n  claimedLoyaltyPoints\n  __typename\n}\n\nfragment CredForAddressWithoutMetadata on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  description\n  lastUpdate\n  lastSync\n  syncStatus\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  dimensionConfig\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupConditionForVerifyButton on CredentialGroupCondition {\n  expression\n  eligibleAddress\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    claimedLoyaltyPoints\n    currentPeriodClaimedLoyaltyPoints\n    currentPeriodMaxLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistSubgraphFrag on Campaign {\n  id\n  whitelistSubgraph {\n    query\n    endpoint\n    expression\n    variable\n    __typename\n  }\n  __typename\n}\n\nfragment GamificationDetailFrag on Gamification {\n  id\n  type\n  nfts {\n    nft {\n      id\n      animationURL\n      category\n      powah\n      image\n      name\n      treasureBack\n      nftCore {\n        ...NftCoreInfoFrag\n        __typename\n      }\n      traits {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  airdrop {\n    name\n    contractAddress\n    token {\n      address\n      icon\n      symbol\n      __typename\n    }\n    merkleTreeUrl\n    addressInfo(address: $address) {\n      index\n      amount {\n        amount\n        ether\n        __typename\n      }\n      proofs\n      __typename\n    }\n    __typename\n  }\n  forgeConfig {\n    minNFTCount\n    maxNFTCount\n    requiredNFTs {\n      nft {\n        category\n        powah\n        image\n        name\n        nftCore {\n          capable\n          contractAddress\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NftCoreInfoFrag on NFTCore {\n  id\n  capable\n  chain\n  contractAddress\n  name\n  symbol\n  dao {\n    id\n    name\n    logo\n    alias\n    __typename\n  }\n  __typename\n}\n\nfragment ExpressionEntity on ExprEntity {\n  cred {\n    id\n    name\n    type\n    credType\n    credSource\n    dimensionConfig\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    chain\n    eligible(address: $address)\n    metadata {\n      visitLink {\n        link\n        __typename\n      }\n      twitter {\n        isAuthentic\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  attrFormula\n  eligible\n  eligibleAddress\n  __typename\n}\n\nfragment ExpressionReward on ExprReward {\n  arithmetics {\n    ...ExpressionEntity\n    __typename\n  }\n  arithmeticFormula\n  rewardType\n  rewardCount\n  rewardVal\n  __typename\n}\n\nfragment CampaignForgePage on Campaign {\n  id\n  numberID\n  chain\n  spaceStation {\n    address\n    __typename\n  }\n  gamification {\n    forgeConfig {\n      maxNFTCount\n      minNFTCount\n      requiredNFTs {\n        nft {\n          category\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCampaignParticipantsBox on Campaign {\n  ...CampaignForParticipantsDialog\n  id\n  chain\n  space {\n    id\n    isAdmin(address: $address)\n    __typename\n  }\n  participants {\n    participants(first: 10, after: \"-1\", download: false) {\n      list {\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    participantsCount\n    bountyWinners(first: 10, after: \"-1\", download: false) {\n      list {\n        createdTime\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    bountyWinnersCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForParticipantsDialog on Campaign {\n  id\n  name\n  type\n  rewardType\n  chain\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  space {\n    isAdmin(address: $address)\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildName\n      roleName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SpaceDetail on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  status\n  links\n  isVerified\n  discordGuildID\n  followersCount\n  nftCores(input: {first: 1}) {\n    list {\n      id\n      marketLink\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ChildrenCampaignsForCampaignDetailAll on Campaign {\n  space {\n    ...SpaceDetail\n    isAdmin(address: $address) @include(if: $withAddress)\n    isFollowing @include(if: $withAddress)\n    followersCount\n    categories\n    __typename\n  }\n  ...CampaignDetailFrag\n  claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n  userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n    list {\n      status\n      __typename\n    }\n    __typename\n  }\n  parentCampaign {\n    id\n    isSequencial\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForSiblingSlide on Campaign {\n  id\n  space {\n    id\n    alias\n    __typename\n  }\n  parentCampaign {\n    id\n    thumbnail\n    isSequencial\n    childrenCampaigns {\n      id\n      ...CampaignForGetImage\n      ...CampaignForCheckFinish\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCheckFinish on Campaign {\n  claimedLoyaltyPoints(address: $address)\n  whitelistInfo(address: $address) {\n    usedCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForGetImage on Campaign {\n  ...GetImageCommon\n  nftTemplates {\n    image\n    __typename\n  }\n  __typename\n}\n\nfragment GetImageCommon on Campaign {\n  ...CampaignForTokenObject\n  id\n  type\n  thumbnail\n  __typename\n}\n\nfragment CampaignForTokenObject on Campaign {\n  tokenReward {\n    tokenAddress\n    tokenSymbol\n    tokenDecimal\n    tokenLogo\n    __typename\n  }\n  tokenRewardContract {\n    id\n    chain\n    __typename\n  }\n  __typename\n}\n"
    #     }
    #
    #     response =  self.session.post( url=self.base_url, json=payload,  ).json()
    #
    #     return response['data']['campaign']['credentialGroups'][0]['credentials'][0]['id']

    # 随机生成昵称
    # 检查是不是和现在的银河的昵称重复
    def check_nickname_existing(self, nickname):
        payload = {
            "operationName": "IsUsernameExisting",
            "variables": {
                "username": nickname
            },
            "query": "query IsUsernameExisting($username: String!) {\n  usernameExist(username: $username)\n}\n"
        }

        resp = self.__post_wrapper_with_retry(payload)
        logger.info(f"check_nickname_existing resp: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"check_nickname_existing err resp: {resp}")
            logger.error(exp)
            raise exp

        return resp['data']['usernameExist']

    # 创建银河账户
    def dao_create_new_acc(self, nickname, address):
        payload = {
            "operationName": "CreateNewAccount",
            "variables": {
                "input": {
                    "schema": f"EVM:{address}",
                    "socialUsername": "",
                    "username": nickname
                }
            },
            "query": "mutation CreateNewAccount($input: CreateNewAccount!) {\n  createNewAccount(input: $input)\n}\n"
        }

        resp = self.__post_wrapper_with_retry(payload)
        logger.info(f"dao_create_new_acc resp: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"dao_create_new_acc err resp: {resp}")
            logger.error(exp)
            raise exp

        logger.success(f"就算是创建账户成功吧 Create new account response: {resp}")
        return True

    # 获取用户信息
    def get_user_info(self, address):
        payload = {
            "operationName": "BasicUserInfo",
            "variables": {
                "address": address
            },
            # 这是要查询的具体细节
            # 包括是不是有邮箱，有没有绑定社交账号，有没有绑定sol钱包地址等等
            "query": "query BasicUserInfo($address: String!) {\n  addressInfo(address: $address) {\n"
                     "    id\n    username\n    avatar\n    address\n    evmAddressSecondary {\n"
                     "      address\n      __typename\n    }\n    hasEmail\n    solanaAddress\n"
                     "    aptosAddress\n    seiAddress\n    injectiveAddress\n    flowAddress\n"
                     "    starknetAddress\n    bitcoinAddress\n    hasEvmAddress\n"
                     "    hasSolanaAddress\n    hasAptosAddress\n    hasInjectiveAddress\n    hasFlowAddress\n"
                     "    hasStarknetAddress\n    hasBitcoinAddress\n    hasTwitter\n    hasGithub\n"
                     "    hasDiscord\n    hasTelegram\n    displayEmail\n    displayTwitter\n"
                     "    displayGithub\n    displayDiscord\n    displayTelegram\n    displayNamePref\n"
                     "    email\n    twitterUserID\n    twitterUserName\n    githubUserID\n    githubUserName\n"
                     "    discordUserID\n    discordUserName\n    telegramUserID\n    telegramUserName\n"
                     "    enableEmailSubs\n    subscriptions\n    isWhitelisted\n    isInvited\n    isAdmin\n"
                     "    accessToken\n    __typename\n  }\n}\n"
        }

        resp = self.__post_wrapper_with_retry(payload)
        logger.info(f"get_user_info resp: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"get_user_info err resp: {resp}")
            logger.error(exp)
            raise exp

        return resp['data']['addressInfo']

    # 绑定邮箱
    # 会发送验证码
    def dao_send_email(self, address, email_address, captcha):
        payload = {
            "operationName": "SendVerifyCode",
            "variables": {
                "input": {
                    "address": address,
                    "email": email_address,
                    # 我试了试，也可能没有验证码
                    # update 搞错了，一定有验证码，只是页面不显示
                    "captcha": captcha
                }
            },
            "query": "mutation SendVerifyCode($input: SendVerificationEmailInput!) {\n  sendVerificationCode(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n"
        }

        resp = self.__session.post(url=self.__galxe_url, json=payload).json()
        logger.info(f"Send email response: {resp}")
        """
        这是成功
        Send email response: {'data': {'sendVerificationCode': None}}
        
        邮件被标记为垃圾地址，不能发送，这个俄罗斯邮箱不行啊
        Send email response: {'errors': [{'message': 'Failed to send email; msg: You tried to send to recipient(s) that have been marked as inactive. Found inactive addresses: mpahlkdubn@rambler.ru. Inactive recipients are ones that have generated a hard bounce, a spam complaint, or a manual suppression.', 'path': ['sendVerificationCode'], 'extensions': {'args': None, 'code': 'Internal', 'domain': 'EMAIL', 'error': '', 'reason': 'Failed to send email; msg: You tried to send to recipient(s) that have been marked as inactive. Found inactive addresses: mpahlkdubn@rambler.ru. Inactive recipients are ones that have generated a hard bounce, a spam complaint, or a manual suppression.'}}], 'data': {'sendVerificationCode': None}}

        这是验证码无效，挺奇怪的，那就是2captcha的问题了啊？？
        这个错误需要重试！，TODO
        Send email error: [{'message': 'Fail to verify recaptcha', 'path': ['sendVerificationCode'], 'extensions': {'args': None, 'code': 'Internal', 'domain': 'USER', 'error': 'pass_token error', 'reason': 'fail_to_verify_recaptcha'}}]
        
        """

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"dao_send_email err resp: {resp}")
            logger.error(exp)
            raise exp

        return True

    # 确认验证码
    # 原代码是死循环，我感觉不需要死循环吧
    def dao_confirm_email(self, code: str, address: str, email_address: str):
        payload = {
            "operationName": "UpdateEmail",
            "variables": {
                "input": {
                    "address": address,
                    "email": email_address,
                    "verificationCode": code
                }
            },
            "query": "mutation UpdateEmail($input: UpdateEmailInput!) {\n  updateEmail(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n"
        }

        resp = self.__session.post(url=self.__galxe_url, json=payload).json()
        logger.info(f"Confirm email response: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"dao_confirm_email err resp: {resp}")
            logger.error(exp)
            raise exp

        return True

    """
      ╔═══════════════════════════════════════════════════════════════════════╗
      ║ 以下是twitter相关的                                                         ║
      ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def check_twitter_account(self, address, tweet_url):
        json_data = {
            'operationName': 'checkTwitterAccount',
            'query': 'mutation checkTwitterAccount($input: VerifyTwitterAccountInput!) {\n  checkTwitterAccount(input: $input) {\n    address\n    twitterUserID\n    twitterUserName\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'address': address,
                    'tweetURL': tweet_url,
                },
            },
        }
        logger.info(f'json_data({json_data})')
        resp = self.__session.post(self.__galxe_url, json=json_data).json()
        logger.info(f' resp={resp}')
        """
        为什么拿不到user info？？？？没有@银河吗
        查了一下，这个帖子被删除了，可能是被推特官方删了
        像是一个蜜罐，推特resp显示成功，但是实际没成功
        不使用香港ip，改为使用日本ip就好了，就能成功发推了
        可能是香港ip用的人太多了，奈云推荐就是香港ip，所以有问题
        resp={'errors': [{'message': 'Fail to get twitter user info by tweet url', 'path': ['checkTwitterAccount'], 'extensions': {'args': None, 'code': 'Internal', 'domain': 'GRAPHQL', 'error': 'Tweet hastags or mentions are incorrect, hashtags: [], mentions: []', 'reason': 'fail_get_twitter_user_info_by_tweet_url'}}], 'data': {'checkTwitterAccount': None}}
        
        update 10-24 这个问题又出现了，日本ip也不行啊，不知道怎么办了
        """
        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"checkTwitterAccount err resp: {resp}")
            logger.error(exp)
            raise exp

        if resp['data']['checkTwitterAccount']:
            return True

    def verify_twitter_account(self, address, tweet_url):
        json_data = {
            "operationName": "VerifyTwitterAccount",
            "variables": {
                "input": {
                    "address": address,
                    "tweetURL": tweet_url
                }
            },
            "query": "mutation VerifyTwitterAccount($input: VerifyTwitterAccountInput!) {\n  verifyTwitterAccount(input: $input) {\n    address\n    twitterUserID\n    twitterUserName\n    __typename\n  }\n}\n"
        }
        resp = self.__session.post(self.__galxe_url, json=json_data).json()
        logger.info(f'VerifyTwitterAccount resp={resp}')

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"verify_twitter_account err resp: {resp}")
            logger.error(exp)
            raise exp

        """
        resp={'data': {'verifyTwitterAccount': {'address': '', 'twitterUserID': '1807186974979280896', 'twitterUserName': 'KimberlyVa70129', '__typename': 'VerifyTwitterAccountInfo'}}}
        """

        # 原代码这里有个大小写的错误，我fix了
        if resp['data']['verifyTwitterAccount']:
            return True

    # 让银河干了一个什么事，可能是准备好去获取推特信息？
    def twitter_oauth2_status(self):
        """
        从获取获取推特的认证状态？但是有啥用啊？？？好像返回值也什么都不影响
        :return:
        """
        # 推特任务还需要传这个，也没参数，也没返回值
        body = {
            'operationName': 'TwitterOauth2Status',
            'query': 'query TwitterOauth2Status {\n  twitterOauth2Status {\n    oauthRateLimited\n    __typename\n  }\n}\n',
            'variables': {},
        }
        resp_json = self.__post_wrapper_with_retry(body)
        logger.info(f' 这一步的意义是什么 resp={resp_json}')

        if "errors" in resp_json and len(resp_json['errors']) != 0:
            exp = Exception(f"twitter_oauth2_status err resp: {resp_json}")
            logger.error(exp)
            raise exp

    """
      ╔═══════════════════════════════════════════════════════════════════════╗
      ║ 以下是dc相关的                                                         ║
      ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def get_social_auth_url(self, address_evm_prefix_and_lower):

        body = {
            'operationName': 'getSocialAuthUrl',
            'query': 'query getSocialAuthUrl($schema: String!, $type: SocialAccountType!) {\n  getSocialAuthUrl(schema: $schema, type: $type)\n}\n',
            'variables': {
                'schema': address_evm_prefix_and_lower,
                'type': 'DISCORD',
            },
        }
        resp = self.__post_wrapper_with_retry(json_payload_body=body)
        logger.info(f'get_social_auth_url body={helper_json.helper_json(body)} resp={helper_json.helper_json(resp)}')

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"get_social_auth_url err resp: {resp}")
            logger.error(exp)
            raise exp

        ret = resp['data']['getSocialAuthUrl']

        return ret

    def check_discord_account(self, address_evm_prefix_and_lower, state, token):
        body = {
            'operationName': 'checkDiscordAccount',
            'query': 'mutation checkDiscordAccount($input: VerifyDiscordAccountInput!) {\n  checkDiscordAccount(input: $input) {\n    address\n    discordUserID\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'address': address_evm_prefix_and_lower,
                    'state': state,
                    'token': token,
                },
            },
        }
        resp = self.__post_wrapper_with_retry(json_payload_body=body)
        logger.info(f'check_discord_account body={helper_json.helper_json(body)} resp={helper_json.helper_json(resp)}')
        """
        报错token不对，但是我不知道这是怎么计算出来，计算太复杂了，我不知道哪一步有问题
        check_discord_account resp={'errors': [{'message': 'Invalid discord token', 'path': ['checkDiscordAccount'], 'extensions': {'args': None, 'code': 'InvalidArgument', 'domain': 'USER', 'error': 'request discord fail; url: https://discord.com/api/v9/oauth2/token, resp: {"error": "invalid_grant", "error_description": "Invalid \\"redirect_uri\\" in request."}, err: <nil>', 'reason': 'invalid_discord_token'}}], 'data': {'checkDiscordAccount': None}}
        """
        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"check_discord_account err resp: {resp}")
            logger.error(exp)
            raise exp

        # 预期是bool类型
        ret = resp['data']['checkDiscordAccount']
        return ret

    def verify_discord_account(self, address_evm_prefix_and_lower, state, token):
        body = {
            'operationName': 'VerifyDiscord',
            'query': 'mutation VerifyDiscord($input: VerifyDiscordAccountInput!) {\n  verifyDiscordAccount(input: $input) {\n    address\n    discordUserID\n    discordUserName\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'address': address_evm_prefix_and_lower,
                    'state': state,
                    'token': token,
                },
            },
        }
        resp = self.__post_wrapper_with_retry(body)
        logger.info(f'verify_discord_account resp={resp}')

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"verify_discord_account err resp: {resp}")
            logger.error(exp)
            raise exp

        # 预期是bool类型
        ret = resp['data']['verifyDiscordAccount']
        return ret

    """
      ╔═══════════════════════════════════════════════════════════════════════╗
      ║ 以下是任务相关的                                                         ║
      ╚═══════════════════════════════════════════════════════════════════════╝
    """

    # 这玩意还能超时我也是没想到
    def get_campaign_info_with_retry(self, address_lower, campaign_id,log_detail =False):
        retries = 3  # 最大重试次数
        for attempt in range(retries):
            try:
                return self.__get_campaign_info(address_lower, campaign_id,log_detail)
            except Exception as e:# 直接对所有类型的异常进行重试


                logger.warning(f"get_campaign_info_with_retry 重试的第({attempt + 1})次，e({e})")
                if attempt < retries - 1:
                    helper_sleep.calculate_backoff_time_and_sleep(attempt, 'get_campaign_info_with_retry 重试中')  # 计算等待时间并等待
                else:
                    logger.error(f"get_campaign_info_with_retry 最大重试次数已达，仍不成功。e({e})")
                    raise






    # 获取整任务的info
    def __get_campaign_info(self, address_lower, campaign_id,log_detail =False):
        body = {
            'operationName': 'CampaignDetailAll',
            'query': 'query CampaignDetailAll($id: ID!, $address: String!, $withAddress: Boolean!) {\n  campaign(id: $id) {\n    ...CampaignForSiblingSlide\n    coHostSpaces {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    bannerUrl\n    ...CampaignDetailFrag\n    userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n      list {\n        status\n        premintTo\n        __typename\n      }\n      __typename\n    }\n    space {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    isBookmarked(address: $address) @include(if: $withAddress)\n    inWatchList\n    claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n    parentCampaign {\n      id\n      isSequencial\n      thumbnail\n      __typename\n    }\n    isSequencial\n    numNFTMinted\n    childrenCampaigns {\n      ...ChildrenCampaignsForCampaignDetailAll\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignDetailFrag on Campaign {\n  id\n  ...CampaignMedia\n  ...CampaignForgePage\n  ...CampaignForCampaignParticipantsBox\n  name\n  numberID\n  type\n  inWatchList\n  cap\n  info\n  useCred\n  smartbalancePreCheck(mintCount: 1)\n  smartbalanceDeposited\n  formula\n  status\n  seoImage\n  creator\n  tags\n  thumbnail\n  gasType\n  isPrivate\n  createdAt\n  requirementInfo\n  description\n  enableWhitelist\n  chain\n  startTime\n  endTime\n  requireEmail\n  requireUsername\n  blacklistCountryCodes\n  whitelistRegions\n  rewardType\n  distributionType\n  rewardName\n  claimEndTime\n  loyaltyPoints\n  tokenRewardContract {\n    id\n    address\n    chain\n    __typename\n  }\n  tokenReward {\n    userTokenAmount\n    tokenAddress\n    depositedTokenAmount\n    tokenRewardId\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  spaceStation {\n    id\n    address\n    chain\n    __typename\n  }\n  ...WhitelistInfoFrag\n  ...WhitelistSubgraphFrag\n  gamification {\n    ...GamificationDetailFrag\n    __typename\n  }\n  creds {\n    id\n    name\n    type\n    credType\n    credSource\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    syncStatus\n    credContractNFTHolder {\n      timestamp\n      __typename\n    }\n    chain\n    eligible(address: $address, campaignId: $id)\n    subgraph {\n      endpoint\n      query\n      expression\n      __typename\n    }\n    dimensionConfig\n    value {\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  credentialGroups(address: $address) {\n    ...CredentialGroupForAddress\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildId\n      guildName\n      roleId\n      roleName\n      inviteLink\n      __typename\n    }\n    premint {\n      startTime\n      endTime\n      chain\n      price\n      totalSupply\n      contractAddress\n      banner\n      __typename\n    }\n    loyaltyPoints {\n      points\n      __typename\n    }\n    loyaltyPointsMysteryBox {\n      points\n      weight\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    bountyWinnersCount\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    referralConfig {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  referralCode(address: $address)\n  recurringType\n  latestRecurringTime\n  nftTemplates {\n    id\n    image\n    treasureBack\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  rewardName\n  type\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupForAddress on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForAddressWithoutMetadata\n    __typename\n  }\n  conditionRelation\n  conditions {\n    expression\n    eligible\n    ...CredentialGroupConditionForVerifyButton\n    __typename\n  }\n  rewards {\n    expression\n    eligible\n    rewardCount\n    rewardType\n    __typename\n  }\n  rewardAttrVals {\n    attrName\n    attrTitle\n    attrVal\n    __typename\n  }\n  claimedLoyaltyPoints\n  __typename\n}\n\nfragment CredForAddressWithoutMetadata on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  description\n  lastUpdate\n  lastSync\n  syncStatus\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  dimensionConfig\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupConditionForVerifyButton on CredentialGroupCondition {\n  expression\n  eligibleAddress\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    claimedLoyaltyPoints\n    currentPeriodClaimedLoyaltyPoints\n    currentPeriodMaxLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistSubgraphFrag on Campaign {\n  id\n  whitelistSubgraph {\n    query\n    endpoint\n    expression\n    variable\n    __typename\n  }\n  __typename\n}\n\nfragment GamificationDetailFrag on Gamification {\n  id\n  type\n  nfts {\n    nft {\n      id\n      animationURL\n      category\n      powah\n      image\n      name\n      treasureBack\n      nftCore {\n        ...NftCoreInfoFrag\n        __typename\n      }\n      traits {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  airdrop {\n    name\n    contractAddress\n    token {\n      address\n      icon\n      symbol\n      __typename\n    }\n    merkleTreeUrl\n    addressInfo(address: $address) {\n      index\n      amount {\n        amount\n        ether\n        __typename\n      }\n      proofs\n      __typename\n    }\n    __typename\n  }\n  forgeConfig {\n    minNFTCount\n    maxNFTCount\n    requiredNFTs {\n      nft {\n        category\n        powah\n        image\n        name\n        nftCore {\n          capable\n          contractAddress\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NftCoreInfoFrag on NFTCore {\n  id\n  capable\n  chain\n  contractAddress\n  name\n  symbol\n  dao {\n    id\n    name\n    logo\n    alias\n    __typename\n  }\n  __typename\n}\n\nfragment ExpressionEntity on ExprEntity {\n  cred {\n    id\n    name\n    type\n    credType\n    credSource\n    dimensionConfig\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    chain\n    eligible(address: $address)\n    metadata {\n      visitLink {\n        link\n        __typename\n      }\n      twitter {\n        isAuthentic\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  attrFormula\n  eligible\n  eligibleAddress\n  __typename\n}\n\nfragment ExpressionReward on ExprReward {\n  arithmetics {\n    ...ExpressionEntity\n    __typename\n  }\n  arithmeticFormula\n  rewardType\n  rewardCount\n  rewardVal\n  __typename\n}\n\nfragment CampaignForgePage on Campaign {\n  id\n  numberID\n  chain\n  spaceStation {\n    address\n    __typename\n  }\n  gamification {\n    forgeConfig {\n      maxNFTCount\n      minNFTCount\n      requiredNFTs {\n        nft {\n          category\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCampaignParticipantsBox on Campaign {\n  ...CampaignForParticipantsDialog\n  id\n  chain\n  space {\n    id\n    isAdmin(address: $address)\n    __typename\n  }\n  participants {\n    participants(first: 10, after: \"-1\", download: false) {\n      list {\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    participantsCount\n    bountyWinners(first: 10, after: \"-1\", download: false) {\n      list {\n        createdTime\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    bountyWinnersCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForParticipantsDialog on Campaign {\n  id\n  name\n  type\n  rewardType\n  chain\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  space {\n    isAdmin(address: $address)\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildName\n      roleName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SpaceDetail on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  status\n  links\n  isVerified\n  discordGuildID\n  followersCount\n  nftCores(input: {first: 1}) {\n    list {\n      id\n      marketLink\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ChildrenCampaignsForCampaignDetailAll on Campaign {\n  space {\n    ...SpaceDetail\n    isAdmin(address: $address) @include(if: $withAddress)\n    isFollowing @include(if: $withAddress)\n    followersCount\n    categories\n    __typename\n  }\n  ...CampaignDetailFrag\n  claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n  userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n    list {\n      status\n      __typename\n    }\n    __typename\n  }\n  parentCampaign {\n    id\n    isSequencial\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForSiblingSlide on Campaign {\n  id\n  space {\n    id\n    alias\n    __typename\n  }\n  parentCampaign {\n    id\n    thumbnail\n    isSequencial\n    childrenCampaigns {\n      id\n      ...CampaignForGetImage\n      ...CampaignForCheckFinish\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCheckFinish on Campaign {\n  claimedLoyaltyPoints(address: $address)\n  whitelistInfo(address: $address) {\n    usedCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForGetImage on Campaign {\n  ...GetImageCommon\n  nftTemplates {\n    image\n    __typename\n  }\n  __typename\n}\n\nfragment GetImageCommon on Campaign {\n  ...CampaignForTokenObject\n  id\n  type\n  thumbnail\n  __typename\n}\n\nfragment CampaignForTokenObject on Campaign {\n  tokenReward {\n    tokenAddress\n    tokenSymbol\n    tokenDecimal\n    tokenLogo\n    __typename\n  }\n  tokenRewardContract {\n    id\n    chain\n    __typename\n  }\n  __typename\n}\n',
            'variables': {
                'address': address_lower,
                'id': campaign_id,
                'withAddress': True,
            },
        }
        logger.info(f'get_campaign_info body={helper_json.helper_json(body)}')

        resp = self.__post_wrapper_with_retry(body)

        if log_detail:
            logger.info(f'get_campaign_info resp={helper_json.helper_json(resp)}') #详细的log
        else:
            logger.info(f'get_campaign_info resp={resp}')  # 简单的log


        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"get_campaign_info err resp: {resp}")
            logger.error(exp)
            raise exp

        ret = resp['data']['campaign']
        return ret

    # 完成一个子任务
    def add_typed_credential_items(self, address_lower, campaign_id, credential_id, captcha):

        payload = {
            "operationName": "AddTypedCredentialItems",
            "variables": {
                "input": {
                    "campaignId": campaign_id,
                    "captcha": captcha,
                    "credId": credential_id,
                    "items": [
                        address_lower
                    ],
                    "operation": "APPEND"
                }
            },
            "query": "mutation AddTypedCredentialItems($input: MutateTypedCredItemInput!) {\n"
                     "  typedCredentialItems(input: $input) {\n    id\n    __typename\n  }\n}\n"
        }

        resp = self.__post_wrapper_with_retry(json_payload_body=payload)
        logger.info(f"add_typed_credential_items resp: {resp}")

        """
        无法验证是啥意思，这tm还能无法验证
        这种可能需要重试，如果多次遇见就做个重试代码
        resp: {'errors': [{'message': '10000:failed to verify recaptcha token; err: pass_token error', 'path': ['typedCredentialItems'], 'extensions': {'code': 'Unknown'}}], 'data': {'typedCredentialItems': None}}

        """
        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"add_typed_credential_items err resp: {resp}")
            logger.error(exp)
            raise exp

        # 没有其他返回值
        return True


    # def sync_credential_value_with_retry(self, sync_options, is_quiz=False):
    #     max_attempts = 3  # 最大尝试次数
    #     for attempt in range(max_attempts):
    #         try:
    #             return self.sync_credential_value(sync_options , is_quiz)
    #         except Exception as e:
    #             logger.error(f" e.type({type(e).__name__}) e({e})")
    #
    #             if 'upstream request timeout' in str(e):
    #                 logger.warning(f" 已尝试次数attempt({attempt + 1}) e({e})")
    #                 if attempt < max_attempts - 1:
    #                     helper_sleep.calculate_backoff_time_and_sleep(attempt, f'sync_credential_value_with_retry 重试中 attempt({attempt})')  # 计算等待时间并等待
    #                 else:
    #                     logger.error(f" 最大重试次数已达，仍不成功")
    #                     raise
    #             else:  # 其他异常，不重试
    #                 logger.error(f" 失败,e({e})")
    #                 raise


    # sync_options来自上游
    def sync_credential_value(self, sync_options, is_quiz=False):
        body = {
            'operationName': 'SyncCredentialValue',
            'query': 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) {\n  syncCredentialValue(input: $input) {\n    value {\n      address\n      spaceUsers {\n        follow\n        points\n        participations\n        __typename\n      }\n      campaignReferral {\n        count\n        __typename\n      }\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      walletBalance {\n        balance\n        __typename\n      }\n      multiDimension {\n        value\n        __typename\n      }\n      allow\n      survey {\n        answers\n        __typename\n      }\n      quiz {\n        allow\n        correct\n        __typename\n      }\n      __typename\n    }\n    message\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'syncOptions': sync_options
                },
            },
        }

        resp = self.__post_wrapper_with_retry(body)
        logger.info(f'sync_credential_value body={helper_json.helper_json(body)} resp={helper_json.helper_json(resp)}')


        """
            Exception: sync_credential_value err resp: {'errors': [{'message': 'failed to fetch rest value', 
            'path': ['syncCredentialValue'], 'extensions': {'args': None, 'code': 'Internal', 'domain': 'CREDENTIAL', 
            'error': 'The API server used by this credential is busy. Please try later, or seek help from the credential curator.\nError detail: Status code: 502;\nresp: <html>\r\n<head><title>502 Bad Gateway</title></head>\r\n<body>\r\n<center><h1>502 Bad Gateway</h1></center>\r\n<hr><center>nginx/ (Ubuntu)</center>\r\n</body>\r\n</html>\r\n', 'reason': 'failed to fetch rest value'}}], 'data': {'syncCredentialValue': None}}
        """
        # TODO 考虑dao层重试这个异常
        if "errors" in resp and len(resp['errors']) != 0:
            if 'message' in resp['errors'][0] and 'upstream request timeout' in  resp['errors'][0]['message']:
                return False
            else:
                exp = Exception(f"sync_credential_value err resp: {resp}")
                logger.error(exp)
                raise exp

        # 如果答题错误，也算exp，理论上我的答案不可能错误
        value = resp['data']['syncCredentialValue']['value']
        # 如果是答题类型的就再多一层quiz
        if is_quiz:
            value = value['quiz']


        allow = value['allow']

        # 判断是不是成功了
        if allow:
            logger.success(f"sync_credential_value success allow={allow}")
        else:
            # 9-2 update 可能不allow也是合理的，需要service层判断了，dao层直接返回
            logger.warning(f"sync_credential_value disallow allow={allow}")

        return allow




    # 这个人写代码，这是PrepareParticipate准备参与啊，但是另一个人是准备参与和参与都写了
    # 如果不是需要gas 需要tx的任务，这一步PrepareParticipate就算是领取了奖励了
    # v1 更新了query还是不能领取
    # v2 更新pointMintAmount试试
    def prepare_participate(self, address_evm_prefix_and_lower, campaign_id, captcha, chain,  pointMintAmount, referral_code: str = None,mintCount:int = 0):
        """

        :param address_evm_prefix_and_lower:
        :param campaign_id:
        :param captcha:
        :param chain:
        :param pointMintAmount:
        :param referral_code:
        :param mintCount: 表示要打几个nft？但是一般直接0，如果领取分数这个字段0就可以
        :return:
        """
        payload = {
            "operationName": "PrepareParticipate",
            # 'query': 'mutation PrepareParticipate($input: PrepareParticipateInput!) {\n  prepareParticipate(input: $input) {\n    allow\n    disallowReason\n    signature\n    nonce\n    mintFuncInfo {\n      funcName\n      nftCoreAddress\n      verifyIDs\n      powahs\n      cap\n      __typename\n    }\n    extLinkResp {\n      success\n      data\n      error\n      __typename\n    }\n    metaTxResp {\n      metaSig2\n      autoTaskUrl\n      metaSpaceAddr\n      forwarderAddr\n      metaTxHash\n      reqQueueing\n      __typename\n    }\n    solanaTxResp {\n      mint\n      updateAuthority\n      explorerUrl\n      signedTx\n      verifyID\n      __typename\n    }\n    aptosTxResp {\n      signatureExpiredAt\n      tokenName\n      __typename\n    }\n    tokenRewardCampaignTxResp {\n      signatureExpiredAt\n      verifyID\n      __typename\n    }\n    loyaltyPointsTxResp {\n      TotalClaimedPoints\n      __typename\n    }\n    __typename\n  }\n}\n',
            'query':   "mutation PrepareParticipate($input: PrepareParticipateInput!) {\n  prepareParticipate(input: $input) {\n    allow\n    disallowReason\n    signature\n    nonce\n    mintFuncInfo {\n      funcName\n      nftCoreAddress\n      verifyIDs\n      powahs\n      cap\n      __typename\n    }\n    extLinkResp {\n      success\n      data\n      error\n      __typename\n    }\n    metaTxResp {\n      metaSig2\n      autoTaskUrl\n      metaSpaceAddr\n      forwarderAddr\n      metaTxHash\n      reqQueueing\n      __typename\n    }\n    solanaTxResp {\n      mint\n      updateAuthority\n      explorerUrl\n      signedTx\n      verifyID\n      __typename\n    }\n    aptosTxResp {\n      signatureExpiredAt\n      tokenName\n      __typename\n    }\n    spaceStation\n    airdropRewardCampaignTxResp {\n      airdropID\n      verifyID\n      index\n      account\n      amount\n      proof\n      customReward\n      __typename\n    }\n    tokenRewardCampaignTxResp {\n      signatureExpiredAt\n      verifyID\n      encodeAddress\n      weight\n      __typename\n    }\n    loyaltyPointsTxResp {\n      TotalClaimedPoints\n      VerifyIDs\n      loyaltyPointDistributionStation\n      signature\n      disallowReason\n      nonce\n      allow\n      loyaltyPointContract\n      Points\n      reqQueueing\n      __typename\n    }\n    flowTxResp {\n      Name\n      Description\n      Thumbnail\n      __typename\n    }\n    xrplLinks\n    suiTxResp {\n      packageId\n      tableId\n      nftName\n      campaignId\n      verifyID\n      imgUrl\n      signatureExpiredAt\n      __typename\n    }\n    __typename\n  }\n}",
            "variables": {
                "input": {
                    "address": address_evm_prefix_and_lower,  # ok
                    "campaignID": campaign_id,  # ok
                    "captcha": captcha,  # ok
                    "chain": chain,  # GRAVITY_ALPHA 估计没问题
                    # 是不是已经mint的次数？？？
                    "mintCount": mintCount,
                    "signature": "",  # ok
                    # 我自己抓接口，和代码只差这一个地方，可能是允许mint的上限
                    # TODO 后续观察是不是变化
                    # 懂了，这里是要领取的分数。必须精确的填入分数。如果填多了不会实际领取，但是也不报错
                    # 分数会记录到链上
                    # https://gscan.xyz/tx/0x33167c76541b4114a6e18e9ecf772f3d7738f3edd51d4bdaeded113f8edd52b5
                    "pointMintAmount": pointMintAmount
                }
            },

        }

        if referral_code:
            payload['variables']['input']['referralCode'] = referral_code

        logger.info(f"prepare_participate payload: {helper_json.helper_json(payload)}")

        response = self.__post_wrapper_with_retry(payload)
        logger.info(f"prepare_participate response: {helper_json.helper_json(response)}")

        """
        这种算成功啊，我自己看了看
        {
            "data": {
                "prepareParticipate": {
                    "allow": false,
                    "disallowReason": "",
                    "signature": "",
                    "nonce": "",
                    "mintFuncInfo": null,
                    "extLinkResp": null,
                    "metaTxResp": null,
                    "solanaTxResp": null,
                    "aptosTxResp": null,
                    "tokenRewardCampaignTxResp": null,
                    "loyaltyPointsTxResp": {
                        "TotalClaimedPoints": 0,
                        "__typename": "LoyaltyPointsTxResp"
                    },
                    "__typename": "PrepareParticipateCampaignResp"
                }
            }
        }
        """


        """
        # 无法记录账单？？？是啥，重试3次都不行
        resp: {'errors': [{'message': 'Failed to record billing.', 'path': ['prepareParticipate'], 'extensions': {'args': None, 'code': 'InvalidArgument', 'domain': 'BALANCE', 'error': 'failed to deallocate cached statement(s): conn closed', 'reason': 'record_billing_failed'}}], 'data': {'prepareParticipate': None}}
        
        """
        if "errors" in response and len(response['errors']) != 0:
            exp = Exception(f"sync_credential_value err resp: {response}")
            logger.error(exp)
            raise exp

        result = response['data']['prepareParticipate']
        # if not result['allow']:
        #     exp= Exception(f'Not allowed, reason: {result["disallowReason"]}')
        #     logger.error(exp)
        #     raise exp

        # 没有disallowReason就是成功
        if len(result["disallowReason"]) == 0:
            logger.success(f"prepare_participate success result={result}")
            return result
        else:
            exp = Exception(f"sync_credential_value disallowReason result={result}")
            logger.error(exp)
            raise exp

        # if not response['data']['prepareParticipate']['loyaltyPointsTxResp']:
        #     # 已经领取
        #     # 草这，明显不对啊，这里是没领取成功
        #     logger.info(f"Already claimed points on Galxe")
        # elif response['data']['prepareParticipate']['disallowReason'] != "":
        #     # 无法领取
        #     error = response['data']['prepareParticipate']['disallowReason']
        #     raise Exception(f"Can`t claim points on Galxe. Error: {error}")
        #
        # elif int(response['data']['prepareParticipate']['loyaltyPointsTxResp']['TotalClaimedPoints']):
        #     points = int(response['data']['prepareParticipate']['loyaltyPointsTxResp']['TotalClaimedPoints'])
        #     # 领取成功
        #     logger.info(f"Successfully claim {points} points on Galxe")

    # 真正的参与
    def participate(self, address_evm_prefix_and_eip55, campaign_id, chain, nonce, tx_hash, verifyIDs:list):
        """

        :param address_evm_prefix_and_eip55:
        :param campaign_id:
        :param chain:
        :param nonce:
        :param tx_hash:
        :param verifyIDs:  必须是list
        :return:
        """
        body = {
            'operationName': 'Participate',
            'query': 'mutation Participate($input: ParticipateInput!) {\n  participate(input: $input) {\n    participated\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'address': address_evm_prefix_and_eip55,
                    'campaignID': campaign_id,
                    'chain': chain,
                    'nonce': nonce,
                    'signature': '',
                    'tx': tx_hash,
                    'verifyIDs': verifyIDs,
                },
            },
        }
        logger.info(f"participate body({body})")

        resp = self.__post_wrapper_with_retry(body)
        logger.info(f"participate resp({resp})")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"sync_credential_value err resp: {resp}")
            logger.error(exp)
            raise exp

        participated=  resp['data']['participate']['participated']
        if participated:
            logger.success(f"participate success participated={participated}")
        else:
            # 失败就抛出异常
            exp = Exception(f"participate failed participated={participated}")
            logger.error(exp)
            raise exp

    def participatePoint(self, address_evm_prefix_and_eip55, campaign_id, chain, nonce, tx_hash, verifyIDs:list):
        """

        :param address_evm_prefix_and_eip55:
        :param campaign_id:
        :param chain:
        :param nonce:
        :param tx_hash:
        :param verifyIDs:  必须是list
        :return:
        """
        body = {
            'operationName': 'ParticipatePoint',
            'query': 'mutation ParticipatePoint($input: ParticipatePointInput!) {\n  participatePoint(input: $input) {\n    participated\n    failReason\n    __typename\n  }\n}',
            'variables': {
                'input': {
                    'address': address_evm_prefix_and_eip55,
                    'campaignID': campaign_id,
                    'chain': chain,
                    'nonce': nonce,
                    'signature': '',
                    'tx': tx_hash,
                    'verifyIDs': verifyIDs,
                },
            },
        }
        logger.info(f" body({helper_json.helper_json(body)})")

        resp = self.__post_wrapper_with_retry(body)
        logger.info(f" resp({helper_json.helper_json(resp)})")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f" err resp: {resp}")
            logger.error(exp)
            raise exp

        participated=  resp['data']['participatePoint']['participated']
        if participated:
            logger.success(f" success participated={participated}")
        else:
            # 失败就抛出异常
            exp = Exception(f" failed participated={participated}")
            logger.error(exp)
            raise exp


    # 充足的
    def sufficient_for_gasless_chain_query(self, space_id: int, chain: str):
        body = {
            'operationName': 'SufficientForGaslessChainQuery',
            'query': 'query SufficientForGaslessChainQuery($id: Int, $chains: [Chain!]!) {\n  space(id: $id) {\n    id\n    spaceBalance {\n      sufficientForGaslessClaimOnChain(chains: $chains) {\n        sufficient\n        chain\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
            'variables': {
                'chains': [chain],
                'id': space_id,
            },
        }
        logger.info(f"sufficient_for_gasless_chain_query body: {body}")

        resp = self.__post_wrapper_with_retry(body)
        logger.info(f"sufficient_for_gasless_chain_query resp: {resp}")

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"sufficient_for_gasless_chain_query err resp: {resp}")
            logger.error(exp)
            raise exp

        return resp['data']['space']['spaceBalance']['sufficientForGaslessClaimOnChain'][0]['sufficient']

    """
      ╔═══════════════════════════════════════════════════════════════════════╗
      ║ 以下是关注项目方空间的任务的相关的代码                                                         ║
      ╚═══════════════════════════════════════════════════════════════════════╝
    """

    def follow_space(self, space_id):
        body = {
            'operationName': 'followSpace',
            'query': 'mutation followSpace($spaceIds: [Int!]) {\n  followSpace(spaceIds: $spaceIds)\n}\n',
            'variables': {
                'spaceIds': [space_id],
            }
        }
        resp = self.__post_wrapper_with_retry(body)
        logger.info(f'follow_space resp={resp}')

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"follow_space err resp: {resp}")
            logger.error(exp)
            raise exp

        return resp['data']['followSpace'] != 1

    # 这个和SyncCredentialValue不一样
    # 是关注项目方空间的专用的一个类型
    # 其实不需要返回值
    # 带表达式的sync，只有 关注space的项目才会用到
    def sync_evaluate_credential_value(self, eval_expr, sync_options)->None:
        body = {
            'operationName': 'syncEvaluateCredentialValue',
            'query': 'mutation syncEvaluateCredentialValue($input: SyncEvaluateCredentialValueInput!) {\n  syncEvaluateCredentialValue(input: $input) {\n    result\n    value {\n      allow\n      survey {\n        answers\n        __typename\n      }\n      quiz {\n        allow\n        correct\n        __typename\n      }\n      __typename\n    }\n    message\n    __typename\n  }\n}\n',
            'variables': {
                'input': {
                    'evalExpr': eval_expr,
                    'syncOptions': sync_options
                },
            },
        }
        logger.info(f'sync_evaluate_credential_value body({helper_json.helper_json(body)})')

        resp = self.__post_wrapper_with_retry(body)

        logger.info(f'sync_evaluate_credential_value resp({helper_json.helper_json(resp)})')

        if "errors" in resp and len(resp['errors']) != 0:
            exp = Exception(f"sync_evaluate_credential_value err resp: {resp}")
            logger.error(exp)
            raise exp

        # update 9-7 不管返回值，就算是allow is false，其实也能成功的关注上space
        # allow = resp['data']['syncEvaluateCredentialValue']['value']['allow']
        # # 判断是不是成功了
        # if allow:
        #     logger.success(f"sync_evaluate_credential_value success allow is true")
        #     return allow
        # else:
        #     # 这里的失败就直接抛出异常
        #     exp= Exception(f"sync_evaluate_credential_value failed allow is false")
        #     logger.error(exp)
        #     raise exp



        # return not resp['data']['syncEvaluateCredentialValue']



    def close(self):
        """
        关闭会话。
        """
        self.__session.close()


# 示例使用
if __name__ == "__main__":
    pass
