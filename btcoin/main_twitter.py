import argparse
import os
import sys
current_file_path = os.path.abspath(__file__) # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path) # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir) # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)



###############################################################################################

import helper_random

import helper_logger
import helper_sleep
import service_account_header

import service_account_record_v2
import service_account_twitter
import service_account_evm_storage
import service_galxe

import service_account_evm

from loguru import logger

import encode_decode

import model_twitter

# 使用 logger.catch 捕获异常并记录
# 它可以捕获未处理的异常并自动记录到日志文件中。即使程序终止，异常信息也会被记录下来。
@logger.catch
def main(todo_account_and_campaign: list[tuple[str, list[str]]]):




    cur_service_account_record_v2 = service_account_record_v2.ServiceAccountRecordV2()
    if cur_service_account_record_v2.is_exist_for_all_account_all_event([account for account, _ in todo_account_and_campaign],
                                                                     todo_account_and_campaign[0][1]):
        logger.warning(f"main 所有账号的所有任务都已经完成了，不需要再做了")
        return


    all_account_twitter_map = service_account_twitter.ServiceAccountTwitter().get_all_account_twitter_map()
    all_accounts_evm_map = service_account_evm_storage.get_all_accounts_evm_map()
    all_account_header_map = service_account_header.get_all_accounts_map()






    success_account_count = 0
    # cur_password = helper_get_password.get_password()
    cur_password = 'Android123!'
    for account_idx, (cur_account_name,campaign_list) in enumerate(todo_account_and_campaign):
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!     开始一个账号     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        logger.warning(f"main start account_idx({account_idx}) cur_account_name({cur_account_name})")

        for campaign_list_idx, cur_campaign_str in enumerate(campaign_list):
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

            twitter_auth_token = all_account_twitter_map[cur_account_name].auth_token
            assert  len(twitter_auth_token)!=0

            cur_header = all_account_header_map[cur_account_name]
            assert  cur_header is  not None
            assert  len(cur_header)!=0


            cur_account = service_account_evm.Account(account_name=cur_account.name,
                                          private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                          twitter_auth_token=twitter_auth_token,
                                          cur_header=cur_header
                                          )
            logger.info(f"main account_idx({account_idx}) new一个号 one_account_info={cur_account.log_info()} campaign_id({campaign_id})")

            cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)
            logger.info(f"main cur_ServiceGalxe.twitter={cur_ServiceGalxe.twitter}")
            logger.info(f"main cur_ServiceGalxe.captcha={cur_ServiceGalxe.captcha}")

            try:
                cur_ServiceGalxe.complete_and_claim_campaign(campaign_id)
            except Exception as e:
                # 仅仅记录日志，不要处理
                logger.critical(f"{cur_account.log_account_name()} 完成campaign_id({campaign_id})这个任务失败 e({e})")
                raise

            cur_service_account_record_v2.append_event(account_name=cur_account_name, new_event=const_new_event)
            logger.success(f"main account_idx({account_idx})  {cur_account.log_info()}这个号成功完成了campaign_id({campaign_id})这个任务")
            success_account_count = success_account_count + 1


            # notice 每个推特任务之间需要等待更长的时间
            helper_sleep.wait_a_bit(60, "每个推特任务之间需要等待更长的时间")

            if success_account_count % 6 == 0:
                helper_sleep.wait_a_bit(3 * 60, "每6个任务之间，多等等")




