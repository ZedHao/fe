import helper_get_password
import helper_json
import helper_logger

import service_account_evm
import service_account_evm_storage
import service_account_header
import service_account_twitter


import encode_decode
import service_galxe
from loguru import logger



def ut_check_twitter():
    helper_logger.init_logger()
    account_name = "F02"

    # 从db读一个元素出来 new account实例
    # password = helper_get_password.get_password()
    password ='Android123!'
    cur_ServiceAccountEVMStorage = service_account_evm_storage.ServiceAccountEVMStorage()
    cur_account = cur_ServiceAccountEVMStorage.get_account_by_name_after_decode(account_name, password)

    account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()



    logger.info(f"one_account_info={cur_account.name}")

    cur_account = service_account_evm.Account(account_name=cur_account.name,
                                  address=cur_account.address,
                                  private_key=cur_account.private_key,
                                  cur_header=account_header_map[cur_account.name]
                                  )

    cur_ServiceGalxe = service_galxe.ServiceGalxe(cur_account)

    """
          ╔═══════════════════════════════════════════════════════════════════════╗
          ║ 以下 任务id                                                   ║
          ╚═══════════════════════════════════════════════════════════════════════╝
    """
    campaign_id = 'GCLqPtKH7H'
    credential_id='468424340078080000'
    cur_ServiceGalxe.ut_check_twitter_result(campaign_id,credential_id)





if __name__ == '__main__':
    ut_check_twitter()
