
class ServiceReferralCode:

    def __init__(self):
        self.campaign_id_to_referral_code = {
            "campaign_id":"campaign_id_to_referral_code",
        }


        """
        Cysic项目
        """
        self.campaign_id_to_referral_code["GCTt4tkQiy"]="GRFr2JXjOum4m_StZt8NaOaiTgr-4BAVMIUbHQgC6cJ7Cs=" #Chapter Two: The Path of Pioneers: Stage 1
        self.campaign_id_to_referral_code["GCiWUtvt6S"]="GRFr2Jqr4qm_0qNn5t8NaOaiS1fKFb9IRvTTQnh94ywH7c=" #Chapter Two: The Path of Pioneers: Stage 2



        # https://app.galxe.com/quest/Vana/GCMintxk3n
        # F01的推荐
        self.campaign_id_to_referral_code["GCMintxk3n"]="GRFr2JOkbGm8VWIoptLbLKx3DCGRTDOGHyuYMJ09bBrssWk"



    def get_referral_code(self, campaign_id)->str:
        # 没有时返回空字符串就行，不要报错
        return self.campaign_id_to_referral_code.get(campaign_id, "")
