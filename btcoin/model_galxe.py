from enum import StrEnum


class Recurring(StrEnum):
    DAILY = 'DAILY'
    ONCE = 'ONCE'


class Credential(StrEnum):
    TWITTER = 'TWITTER'
    EMAIL = 'EMAIL'
    EVM_ADDRESS = 'EVM_ADDRESS'
    GALXE_ID = 'GALXE_ID'
    DISCORD = 'DISCORD'
    TELEGRAM = 'TELEGRAM'  # 电报
    APTOS_ADDRESS = 'APTOS_ADDRESS'  # atpos地址


class CredSource(StrEnum):
    TWITTER_FOLLOW = 'TWITTER_FOLLOW'
    TWITTER_RT = 'TWITTER_RT'
    TWITTER_LIKE = 'TWITTER_LIKE'
    TWITTER_QUOTE = 'TWITTER_QUOTE'
    TWITTER_BULLISH = 'TWITTER_BULLISH' # 就是发推的任务，但是指定了#标签


    VISIT_LINK = 'VISIT_LINK'
    QUIZ = 'QUIZ'
    SURVEY = 'SURVEY'
    SPACE_USERS = 'SPACE_USERS'
    WATCH_YOUTUBE = 'WATCH_YOUTUBE'
    CSV = 'CSV'
    CAMPAIGN_REFERRAL = "CAMPAIGN_REFERRAL"  # 推荐
    # 我自己扩展一个银河分数
    # 可能不需要扩展
    # GALXE_WEB3_SCORE= "GALXE_WEB3_SCORE"
    # GITCOIN_PASSPORT= "GITCOIN_PASSPORT"
    # SUBGRAPH= "SUBGRAPH" #可能是银河护照，可能是nomis的评分


class ConditionRelation(StrEnum):
    ALL = 'ALL'
    ANY = 'ANY'


class Gamification(StrEnum):
    POINTS = 'Points'
    OAT = 'Oat'
    POINTS_MYSTERY_BOX = 'PointsMysteryBox'
    DROP = 'Drop'
    BOUNTY = 'Bounty'
    DISCORD_ROLE = 'DiscordRole'# 是dc角色
    TOKEN = 'Token' #直接给币


class GasType(StrEnum):
    GAS_LESS = 'Gasless'
    GAS = 'Gas'
