import os
import sys


current_file_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
current_dir = os.path.dirname(current_file_path)  # 获取当前文件所在的目录
parent_dir = os.path.dirname(current_dir)  # 获取当前目录的父目录
sys.path.insert(0, current_dir)
sys.path.insert(1, parent_dir)

###############################################################################################


import helper_logger
import service_account_header
import service_email_account

import service_account_evm_storage
import service_galxe

import service_account_evm

from loguru import logger

import encode_decode



@logger.catch
def main(cur_account_name,galxe_code:str):
    cur_password = 'Android123!'

    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()
    all_account_email_map = service_email_account.ServiceEmailAccount().get_all_account_email_map()


    cur_account = all_accounts_evm_map[cur_account_name]

    cur_header = all_account_header_map[cur_account_name]
    assert cur_header is not None

    cur_account = service_account_evm.Account(account_name=cur_account.name,
                                              private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                              cur_header=cur_header,
                                              )

    cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)

    galxe_id = cur_ServiceGalxe.get_galxe_id()
    galxe_has_email = cur_ServiceGalxe.has_email()
    logger.warning(f"cur_account_name={cur_account_name} galxe_id={galxe_id} galxe_has_email={galxe_has_email}  ")

    if not galxe_has_email:
        logger.info(f'没绑定邮箱的就去绑定邮箱')
        cur_account_email = all_account_email_map[cur_account_name]
        assert cur_account_email is not None

        cur_account.email_address = cur_account_email.email_address
        cur_account.email_password = cur_account_email.email_password

        cur_ServiceGalxe.confirm_email(galxe_code)

        logger.success('绑定email成功')
    else:
        logger.info(f'已经绑定了邮箱的就什么都不需要做')


if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])
    main(cur_account_name='GIT85', galxe_code="182027")