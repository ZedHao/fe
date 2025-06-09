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

import random


@logger.catch
def main():
    """
    完成邮箱的账号
"PY01",
"PY02",
"PY03",
"PY04",
"PY05",

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
"F11",
"F12",
"F13",
"F14",
"F15",
"F16",
"F17",
"F18",
"F19",
"F20",

"SCR01",
"SCR02",
"SCR03",
"SCR04",
"SCR05",
"SCR06",
"SCR07",
"SCR08",
"SCR09",
"SCR10",
"SCR11",
"SCR12",
"SCR13",
"SCR14",
"SCR15",
"SCR16",
"SCR17",
"SCR18",
"SCR19",
"SCR20",


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
"ZHU23",
"ZHU24",
"ZHU25",
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


"GIT01",
"GIT02",
"GIT03",
"GIT04",
"GIT05",
"GIT06",
"GIT07",
"GIT08",
"GIT09",
"GIT10",
'GIT11',
'GIT12',
'GIT13',
'GIT14',
'GIT15',
'GIT16',
'GIT17', # skwwhjbd@santalmail.com 被识别为不好的邮箱
'GIT18',
'GIT19',#done
'GIT20',#done
'GIT21',#done
'GIT22',#done
'GIT23',
'GIT24',
'GIT25',
'GIT26',
'GIT27',
'GIT28',
'GIT29',
'GIT30',
'GIT31',
'GIT32',
'GIT34',
'GIT35',
'GIT36',
'GIT37',
'GIT38',
'GIT39',
'GIT40',
'GIT41',
'GIT42',
'GIT43',
'GIT44',
'GIT45',
'GIT46',
'GIT47',
'GIT48',
'GIT49',
'GIT50',
'GIT51',
'GIT52',
'GIT53',
'GIT54',
'GIT55',
'GIT56',
'GIT57',
'GIT58',
'GIT59',
'GIT60',
'GIT61',
'GIT62',
'GIT63',
'GIT64',

        'GIT65',
        'GIT66',
        'GIT67',
        'GIT68',
        'GIT69',
        'GIT70',
        'GIT71',
  'GIT72',
        'GIT73',
        'GIT74',
        'GIT75',
        'GIT76',
        'GIT77',
        'GIT78',
        'GIT79',
        'GIT80',
        'GIT81',
        'GIT82',
        'GIT83',
          'GIT84',
        'GIT85',
        'GIT86',
        'GIT87',
        'GIT88',
        'GIT89',
        'GIT90',
         'GIT91',
        'GIT92',
        'GIT93',
        'GIT94',
        'GIT95',
        'GIT96',
        'GIT97',
        'GIT98',
        'GIT99',

"""
    galxe_kyc_list = [


    ]
    random.shuffle(galxe_kyc_list)

    # cur_password = helper_get_password.get_password()
    cur_password = 'Android123!'

    all_accounts_evm_map = service_account_evm_storage.ServiceAccountEVMStorage().get_all_accounts_evm_map()
    all_account_header_map = service_account_header.ServiceAccountHeader().get_all_accounts_map()
    all_account_email_map = service_email_account.ServiceEmailAccount().get_all_account_email_map()

    for account_idx, cur_account_name in enumerate(galxe_kyc_list):

        cur_account = all_accounts_evm_map[cur_account_name]

        if cur_account_name in all_account_header_map:
            cur_header = all_account_header_map[cur_account_name]
        else:
            raise Exception(f"main 没有找到对应的header cur_account_name({cur_account_name}) )")

        cur_account = service_account_evm.Account(account_name=cur_account.name,
                                                  private_key=encode_decode.decode(cur_password, cur_account.private_key),
                                                  cur_header=cur_header,
                                                  # email_address=cur_header.email_address,
                                                  # email_password=cur_header.email_password,
                                                  )

        cur_ServiceGalxe = service_galxe.get_service_instance(cur_account)

        galxe_id = cur_ServiceGalxe.get_galxe_id()
        galxe_has_email = cur_ServiceGalxe.has_email()
        galxe_twitterUserName = cur_ServiceGalxe.get_twitterUserName()
        galxe_discordUserID = cur_ServiceGalxe.get_discordUserID()
        logger.warning(f"cur_account_name={cur_account_name} galxe_id={galxe_id} galxe_has_email={galxe_has_email} galxe_twitterUserName={galxe_twitterUserName} galxe_discordUserID={galxe_discordUserID} ")

        if not galxe_has_email:
            logger.info(f'没绑定邮箱的就去绑定邮箱')
            if cur_account_name in all_account_email_map:
                cur_account_email = all_account_email_map[cur_account_name]
            else:
                raise Exception(f" 没有找到对应的email cur_account_name({cur_account_name}) )")

            cur_account.email_address = cur_account_email.email_address
            cur_account.email_password = cur_account_email.email_password

            cur_ServiceGalxe.link_email()

            logger.success('绑定email成功')
        else:
            logger.info(f'已经绑定了邮箱的就什么都不需要做')


if __name__ == '__main__':
    helper_logger.init_logger(os.path.splitext(os.path.basename(__file__))[0])

    main()
