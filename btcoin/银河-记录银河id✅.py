import os
import sys

import service_email_account

current_file_path = os.path.abspath(__file__) # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path) # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir) # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)



###############################################################################################

import helper_random

import helper_get_password
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
import service_account_galxe_storage
import random


# 使用 logger.catch 捕获异常并记录
# 它可以捕获未处理的异常并自动记录到日志文件中。即使程序终止，异常信息也会被记录下来。
@logger.catch
def main():
    """
    完成邮箱的账号
            # "PY01",
        # "PY02",
        # "PY03",
        "PY04",
        "PY05",

        # "F01",
        # "F02",
        # "F03",
        # "F04",
        # "F05",
        # "F06",
        # "F07",
        # "F08",
        # "F09",
        # "F10",
        # "F11",
        # "F12",
        # "F13",
        # "F14",
        # "F15",
        # "F16",
        # "F17",
        # "F18",
        # "F19",
        # "F20",

        # "SCR01",
        # "SCR02",
        # "SCR03",
        # "SCR04",
        # "SCR05",

        # "ZHU01",
        # "ZHU02",
        # "ZHU03",
        # "ZHU04",
        # "ZHU05",
        # "ZHU06",
        # "ZHU07",
        # "ZHU08",
        # "ZHU09",
        # "ZHU10",
        # "ZHU11",
        # "ZHU12",
        # "ZHU13",
        # "ZHU14",
        # "ZHU15",
        # "ZHU16",
        # "ZHU17",
        # "ZHU18",
        # "ZHU19",
        # "ZHU20",
        # "ZHU21",
        # "ZHU22",
        # "ZHU23",
        # "ZHU24",
        # "ZHU25",


        "ZHU26",
        "ZHU27",
        "ZHU28",
        "ZHU29",
        "ZHU30",

        "ZHU31",
        "ZHU32",
        "ZHU33",
        "ZHU34",
        "ZHU35",
        "ZHU36",
        "ZHU37",
        "ZHU38",
        "ZHU39",
        "ZHU40",
        "ZHU41",
        "ZHU42",
        "ZHU43",
        "ZHU44",
        "ZHU45",
        "ZHU46",
        "ZHU47",
        "ZHU48",
        "ZHU49",
        "ZHU50",

    """
    galxe_kyc_list = [


    ]
    random.shuffle(galxe_kyc_list)



    # cur_password = helper_get_password.get_password()
    cur_password = 'Android123!'




    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()
    cur_ServiceAccountGalxeStorage = service_account_galxe_storage.ServiceAccountGalxeStorage()


    for account_idx, cur_account_name in enumerate(galxe_kyc_list):




        cur_account = all_accounts_evm_map[cur_account_name]


        cur_header = all_account_header_map[cur_account_name]
        assert cur_header is not None



        cur_account = service_account_evm.Account(account_name=cur_account.name,
                                      private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                      cur_header=cur_header,
                                      )

        cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)


        galxe_id = cur_ServiceGalxe.get_galxe_id()
        logger.warning(f"获取到了银河id cur_account_name={cur_account_name} galxe_id={galxe_id} ")
        cur_ServiceAccountGalxeStorage.update_account(cur_account_name,**{'galxe_id':galxe_id } )
        logger.success(f"写入db成功 cur_account_name={cur_account_name} galxe_id={galxe_id} ")







if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    main()
