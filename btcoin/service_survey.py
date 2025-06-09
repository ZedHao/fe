import os
import random
from pathlib import Path

import helper_random

from loguru import logger
import model_survey
import dao_survey
import service_account_header


# 调研类型的任务
# 每次必须new新的对象，来获取答案
# 绝对不能一直使用一个对象
# 在init的时候做好随机，而不是在get的时候随机
class ServiceSurvey:

    def __init__(self, proxy: str, header: dict):
        self.__dao=dao_survey.DaoSurvey(proxy,header)

        # 需要上传图片的答案的固定替换符号
        self.__const_need_upload='need_upload_picture'

        self.credential_id_to_answers = dict()

        # 例子
        self.credential_id_to_answers["id"] = "可能是推特链接"

        # https://app.galxe.com/quest/HenrySocial/GCuBTtkfDT
        self.credential_id_to_answers["436949601572880384"] = helper_random.generate_random_string()

        # HenrySocial/GCrkTtk8cN
        self.credential_id_to_answers["436564171962724352"] = helper_random.generate_random_string()

        twitter_links = ["https://twitter.com/qingqinglove520/status/1830512528356671710",
                         "https://twitter.com/xiaoyubtc/status/1821898205950570931",
                         "https://twitter.com/xiaoyubtc/status/1821034863950193143",
                         "https://twitter.com/xiaoyubtc/status/1820734013671407825",
                         "https://twitter.com/xiaoyubtc/status/1820022753229201418",
                         "https://twitter.com/maik2hello/status/1828652528109564359",
                         "https://twitter.com/airdrop_nanhan/status/1787667511829520419",
                         ]

        evm_addresses = model_survey.evm_addresses

        # https://app.galxe.com/quest/RazorDao/GCX43tkmoZ
        self.credential_id_to_answers["440484675253788672"] = random.choice(twitter_links)

        # https://app.galxe.com/quest/Route-X/GCpkxtkfqQ
        self.credential_id_to_answers["436503156893978624"] = random.choice(twitter_links)
        self.credential_id_to_answers["436503345398583296"] = random.choice(twitter_links)

        # https://app.galxe.com/quest/HenrySocial/GCXKRtksuT
        self.credential_id_to_answers["436941373304745984"] = random.choice(twitter_links)
        # https://app.galxe.com/quest/HenrySocial/GCNQRtkaUG
        self.credential_id_to_answers["436942121535143936"] = random.choice(twitter_links)
        # https://app.galxe.com/quest/HenrySocial/GCu3Ttkm3G
        # 需要2个元素，一个推特链接，一个地址
        self.credential_id_to_answers["436566514146070528"] = [
            random.choice(twitter_links), random.choice(evm_addresses)]

        # https://app.galxe.com/quest/Nexio/GCRPftkqEU
        # 2个元素都是推特链接
        self.credential_id_to_answers["434469096831098880"] = [
            random.choice(twitter_links), random.choice(twitter_links)]

        # https://app.galxe.com/quest/StableJack/GCXvTtv55a
        self.credential_id_to_answers["440832455780392960"] = random.choice(twitter_links)
        # https://app.galxe.com/quest/StableJack/GCY6TtvBDF
        self.credential_id_to_answers["440836457943306240"] = random.choice(twitter_links)

        # https://app.galxe.com/quest/BRKT/GCxawtvMfR
        self.credential_id_to_answers["440769397158600704"] = self.__const_need_upload
        # https://app.galxe.com/quest/BRKT/GCct4tvupM
        self.credential_id_to_answers["440771307492163584"] = self.__const_need_upload

        # https://app.galxe.com/quest/StableJack/GCdnhtvvKP
        self.credential_id_to_answers["440847229150834688"] = random.choice(twitter_links)
        # https://app.galxe.com/quest/StableJack/GCk5htvzYD
        self.credential_id_to_answers["440847950294376448"] = random.choice(twitter_links)

        # https://app.galxe.com/quest/InfiniteSeas/GCDo5tkfrF
        self.credential_id_to_answers["442172634940092416"] = self.__const_need_upload

        # https://app.galxe.com/quest/Movement/GCtmhtkiLb
        self.credential_id_to_answers["439818195247886336"] = self.__const_need_upload
        # https://app.galxe.com/quest/Movement/GCTLhtk5U7
        self.credential_id_to_answers["436567482669539328"] = self.__const_need_upload
        # GCw7htkRK5
        self.credential_id_to_answers["436567879249321984"] = self.__const_need_upload
        # GCyS5tkbCD
        self.credential_id_to_answers["442226031445721088"] = self.__const_need_upload

        # GCdiXtvLKG
        self.credential_id_to_answers["443459115453288448"] = self.__const_need_upload


        # GC25Dtvara
        self.credential_id_to_answers["444865304888176640"] = random.choice(twitter_links)

        # GChv4txmHF
        self.credential_id_to_answers["448752076374278144"] = [random.choice(twitter_links),self.__const_need_upload   ]


        # GCZpRtxaXp
        self.credential_id_to_answers["454162329722966016"] = helper_random.generate_username()
        # GCsfKtxVRa
        self.credential_id_to_answers["450362998473691136"] = self.__const_need_upload
        # GCUo4tv8qM
        self.credential_id_to_answers["440777053764071424"] = random.choice(twitter_links)
        # GCCf4tvDT4
        self.credential_id_to_answers["440775940239323136"] = self.__const_need_upload
        # GCw14tvm6K
        self.credential_id_to_answers["440778111584399360"] = random.choice(twitter_links)
        # GC4F4tvpwA
        self.credential_id_to_answers["440777873259761664"] = random.choice(twitter_links)
        #GCawTtkkpx
        self.credential_id_to_answers["436553226746073088"] = self.__const_need_upload
        #GCPeTtkv5j
        self.credential_id_to_answers["436560463573102592"] = random.choice(twitter_links)
        #GCs2Ttkz6D
        self.credential_id_to_answers["436560939806924800"] = random.choice(twitter_links)
        #GCP9TtkkC8
        self.credential_id_to_answers["436562878078742528"] = random.choice(twitter_links)
        #GCPpTtkxvP
        self.credential_id_to_answers["436563236180029440"] = random.choice(twitter_links)
        #GC4f2tgdrJ
        self.credential_id_to_answers["434441744281522176"] = [self.__const_need_upload,random.choice(twitter_links)   ]
        #GCfvFtgDHX
        self.credential_id_to_answers["434436950447931392"] = [random.choice(twitter_links),random.choice(twitter_links)]
        #GCXAwtvQmT
        self.credential_id_to_answers["440741330344357888"] = [self.__const_need_upload,random.choice(twitter_links),random.choice(twitter_links)]
        #GCN8wtvNUb
        self.credential_id_to_answers["440740335488888832"] = [self.__const_need_upload,random.choice(twitter_links)]
        #GCeY6tk4PJ
        self.credential_id_to_answers["437765783947341824"] = [random.choice(twitter_links),self.__const_need_upload]
        #GCu4ftk9r6
        self.credential_id_to_answers["434448811847323648"] = [self.__const_need_upload,random.choice(twitter_links)]
        #GC442tggmz
        self.credential_id_to_answers["434450961944068096"] =[ random.choice(twitter_links),random.choice(twitter_links)]
        #GCw52tgkjS
        self.credential_id_to_answers["434436950447931392"] = [random.choice(twitter_links),random.choice(twitter_links)]
        #GCTh2tghP8
        self.credential_id_to_answers["434440198810509312"] =[self.__const_need_upload, random.choice(twitter_links)]
        #GCnTFtv95D
        self.credential_id_to_answers["446716923913224192"] = random.choice(twitter_links)
        #GC7jMtkhB2
        self.credential_id_to_answers["437565933335130112"] = [  helper_random.generate_username(),random.choice(twitter_links)]
        #GC54MtkdMx
        self.credential_id_to_answers["437581679784124416"] = [  helper_random.generate_username(),helper_random.generate_username(),self.__const_need_upload ]
        #GCt4ptvH3y
        self.credential_id_to_answers["436490370524647424"] = random.choice(twitter_links)
        #GC48ptvrPE
        self.credential_id_to_answers["441863912531431424"] = random.choice(twitter_links)
        #GCFK1tvxfk
        self.credential_id_to_answers["436490909509550080"] = random.choice(twitter_links)
        #GCQzvtK7pS
        self.credential_id_to_answers["461062856209723392"] = [random.choice(twitter_links),random.choice(evm_addresses)]
        #GCoFxtKUfu
        self.credential_id_to_answers["461078164379136000"] = [random.choice(evm_addresses),random.choice(twitter_links)]
        # GCqA1tvU84
        self.credential_id_to_answers["440867993036083200"] = random.choice(twitter_links)
        #GCkzUtvnEa
        self.credential_id_to_answers["440804673323155456"] = [random.choice(twitter_links),random.choice(evm_addresses)]


        # 11-15
        # https://app.galxe.com/quest/Route-X/GCpCxtkfei
        self.credential_id_to_answers["433892158970327040"] = random.choice(twitter_links)
        # https://app.galxe.com/quest/Xebra/GCt4ptvH3y
        self.credential_id_to_answers["436490370524647424"] = random.choice(twitter_links)
        #  https://app.galxe.com/quest/Xebra/GC48ptvrPE
        self.credential_id_to_answers["441863912531431424"] = random.choice(twitter_links)
        # GCFK1tvxfk
        self.credential_id_to_answers["436490909509550080"] = random.choice(twitter_links)
        # GCvKxtKgP7
        self.credential_id_to_answers["461082704235008000"] = [random.choice(evm_addresses) ,random.choice(twitter_links)   ]
        #
        self.credential_id_to_answers[""] = random.choice(twitter_links)
        #
        self.credential_id_to_answers[""] = random.choice(twitter_links)
        #
        self.credential_id_to_answers[""] = random.choice(twitter_links)




    def get_all_file_paths(self,directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.abspath(os.path.join(root, file)))
        return file_paths



    def choice_picture_and_upload(self , survey_credential_id ):
        files = self.get_all_file_paths('/Users/dongqi/000--空投计划/001--社交网站引流计划')  # 替换为你的文件夹路径
        cur_file =  random.choice(files)
        ret_url= self.__dao.upload_picture_with_retry(cur_file,survey_credential_id)
        return ret_url



    def get_credential_answers(self, credential_id) -> list:
        logger.info(f"get_credential_answers start. credential_id={credential_id}")

        if credential_id not in self.credential_id_to_answers:
            # 必须要有答案，不然直接报错
            raise Exception(f"get_credential_answers Invalid credential_id({credential_id}) type({type(credential_id)})")
        else:
            answer = self.credential_id_to_answers[credential_id]
            if isinstance(answer,list):
                for i in range(len(answer)):
                    if answer[i] == self.__const_need_upload:
                        answer[i] = self.choice_picture_and_upload(credential_id)

            else:
                if  answer  == self.__const_need_upload:
                    answer = self.choice_picture_and_upload(credential_id)



            logger.info(f'get_credential_answers end. answer({answer})')
            return answer


if __name__ == '__main__':

    header = service_account_header.RealisticHeaderGenerator().generate_header()




    cur_service = ServiceSurvey(proxy="http://127.0.0.1:7890",header=header)
    credential_id = "443459115453288448"
    answers = cur_service.get_credential_answers(credential_id)
    logger.info(f"answers={answers}")
    # for answer in answers:
    #     logger.info(f"answer={answer} type({type(answer)})")
