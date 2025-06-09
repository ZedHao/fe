import os
import sys



current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)
# if current_dir not in sys.path:
# sys.path.insert(0, current_dir)
# if parent_dir not in sys.path:
# sys.path.insert(0, parent_dir)


###############################################################################################
import model_galxe_kyc_list
import helper_random

import helper_get_password
import helper_logger
import helper_sleep
import service_account_header

import service_account_record_v2
import service_account_evm_storage
import service_galxe

from loguru import logger

import encode_decode

import random

import service_account_evm

# 使用 logger.catch 捕获异常并记录
# 它可以捕获未处理的异常并自动记录到日志文件中。即使程序终止，异常信息也会被记录下来。
@logger.catch
def main(todo_account_and_campaign):

    cur_service_account_record_v2 = service_account_record_v2.ServiceAccountRecordV2()
    if cur_service_account_record_v2.is_exist_for_all_account_all_event([account for account, _ in todo_account_and_campaign],
                                                                     todo_account_and_campaign[0][1]):
        logger.warning(f"main 所有账号的所有任务都已经完成了，不需要再做了")
        return

    # all_account_twitter_map = service_account_twitter.ServiceAccountTwitter().get_all_account_twitter_map()
    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()

    success_account_count = 0
    # cur_password = helper_get_password.get_password()
    cur_password = "Android123!"

    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(todo_account_and_campaign):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!     开始一个账号     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        logger.warning(f"main start account_idx({account_idx}) cur_account_name({cur_account_name})")

        for campaign_list_idx, cur_campaign_str in enumerate(quiz_campaign_list):
            logger.warning(f"############################################################")
            logger.warning(f"#############    开始一个任务       ##########################")
            logger.warning(f"############################################################")

            const_new_event = cur_campaign_str
            campaign_id = cur_campaign_str.split("/")[1]
            logger.warning(f"main start campaign_list_idx({campaign_list_idx}) cur_campaign_str({cur_campaign_str}) campaign_id({campaign_id})")

            if cur_service_account_record_v2.event_exists(cur_account_name, const_new_event):
                logger.warning(f"main 已经完成过了 cur_account_name({cur_account_name}) campaign_id({campaign_id})")
                continue

            cur_account = all_accounts_evm_map[cur_account_name]
            logger.info(f"main account_idx({account_idx}) one_account_info={cur_account.name} campaign_id({campaign_id})")

            # if cur_account_name in all_account_twitter_map:
            #     twitter_auth_token = all_account_twitter_map[cur_account_name].auth_token
            # else:
            #     raise Exception(f"main 没有找到对应的twitter账号 cur_account_name({cur_account_name}) campaign_id({campaign_id})")

            if cur_account_name in all_account_header_map:
                cur_header = all_account_header_map[cur_account_name]
            else:
                raise Exception(f"main 没有找到对应的header cur_account_name({cur_account_name}) campaign_id({campaign_id})")

            cur_account = service_account_evm.Account(account_name=cur_account.name,
                                          private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                          # twitter_auth_token=twitter_auth_token,
                                          cur_header=cur_header
                                          )
            logger.info(f"main account_idx({account_idx}) new一个号 one_account_info={cur_account.log_info()} campaign_id({campaign_id})")

            cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)

            cur_ServiceGalxe.complete_and_claim_campaign(campaign_id)

            cur_service_account_record_v2.append_event(account_name=cur_account_name, new_event=const_new_event)
            logger.success(f"main account_idx({account_idx})  {cur_account.log_info()}这个号成功完成了campaign_id({campaign_id})这个任务")
            success_account_count = success_account_count + 1

            helper_sleep.wait_a_bit(10, "每个任务之间等待一下")


            if success_account_count % 6 == 0:
                helper_sleep.wait_a_bit(3 * 60, "每6个任务之间，多等等")


if __name__ == '__main__':
    # 获取当前文件的名称（不包含扩展名）
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    galxe_kyc_list = [
    "PY01",
    "PY02",
    "PY03",
    "F01",
    "F02",
    "F03",
    "F04",
    "F05",
    "F06",
    "F07",
    "F08",
    "F09",
    "F10",
    "ZHU01",
    "ZHU02",
    "ZHU03",
    "ZHU04",
    "ZHU05",
    "ZHU06",
    "ZHU07",
    "ZHU08",
    "ZHU09",
    "ZHU10",
    "ZHU11",
    "ZHU12",
    "ZHU13",
    "ZHU14",
    "ZHU15",
    "ZHU16",
    "ZHU17",
    "ZHU18",
    "ZHU19",
    "ZHU20",
    "ZHU21",
    "ZHU22",
]

    # 随机打乱顺序，防止女巫，因为现在都是上链的
    # 每次循环都要打乱一次
    # 只能打乱账号，不能打乱任务，因为任务都是有前置依赖的
    # 做推特任务就不要打乱了
    random.shuffle(galxe_kyc_list)

    quiz_campaign_list = [
        "Movement/GCZkTtx9hF/1009", #notice 一定指定日期，任务在北京时间早上8点刷新. 报错请求超出限制，可能是做了但是没记录吗
    ]

    # 是一个数组，每个元素都是一个元组，元组的第一个元素是账号名，第二个元素是任务list
    # 都是随机的
    todo_account_and_campaign = []
    for cur_account_name in galxe_kyc_list:
        todo_account_and_campaign.append(
            (cur_account_name, helper_random.group_and_shuffle_campaigns(quiz_campaign_list))
        )

    for account_idx, (cur_account_name, quiz_campaign_list) in enumerate(todo_account_and_campaign):
        logger.warning(f"前置检查任务配置 account_idx({account_idx}) cur_account_name({cur_account_name}) quiz_campaign_list={quiz_campaign_list}")

    main(todo_account_and_campaign)
