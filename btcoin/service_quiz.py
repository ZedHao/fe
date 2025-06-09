from loguru import logger


class ServiceQuiz:

    def __init__(self):
        self.credential_id_to_answers = dict()

        # 例子
        self.credential_id_to_answers["id"] = ["A", "B", "C", "D"]

        """
              ╔═══════════════════════════════════════════════════════════════════════╗
              ║ 以下是Autonomys Network相关的                                                     ║
              ╚═══════════════════════════════════════════════════════════════════════╝
        """
        self.credential_id_to_answers["447832620886233088"] = ["PINT"]
        self.credential_id_to_answers["450012076350472192"] = ["A", "rNFTs", "D", "Auto ID"]

        """
          ╔═══════════════════════════════════════════════════════════════════════╗
          ║ 以下是movement相关的                                                     ║
          ╚═══════════════════════════════════════════════════════════════════════╝
        """
        # GCBiQtgo1C Quiz: What is Movement
        self.credential_id_to_answers["427182193014497280"] = ["MOVE", "C", "decentralized shared sequencer", "A", "B"]
        # GCBiQtgo1C Quiz: Meet The Team
        self.credential_id_to_answers["427223917673852928"] = ["A", "Vanderbilt", "B", "San Francisco"]
        # GCBiQtgo1C Quiz: Tech, Partners, and More
        self.credential_id_to_answers["427236061542879232"] = ["Fractal", "Celestia", "razor", "D", "A"]
        # GCBiQtgo1C Quiz: Guilds, Gorillas, and Gud Vibes
        self.credential_id_to_answers["427261543617413120"] = ["gmove", "Pathfinders", "Creators", "Scholars", "Explorers", "Masons", "C", "Moveus"]

        # https://app.galxe.com/quest/BRKT/GCCj4tvjEA  done
        self.credential_id_to_answers["440774855441260544"] = ["C", "D", "A"]

        # https://app.galxe.com/quest/RIZE/GCb8ntkq1n  --done
        self.credential_id_to_answers["440443280161968128"] = ["B", "A", "C"]

        # https://app.galxe.com/quest/HenrySocial/GCjeFtgTTJ 还不知道答案
        self.credential_id_to_answers["441621364789489664"] = ["D", "infrastructure commerce", "C", "A", "D"]
        self.credential_id_to_answers["441625252758339584"] = ["B", "B", "C", "A", "A"]

        # https://app.galxe.com/quest/SeekersAlliance/GCJdJtk1rB
        self.credential_id_to_answers["440106272403050496"] = ["C", "A", "D", "E", "B"]
        # https://app.galxe.com/quest/SeekersAlliance/GC38JtkfjK
        self.credential_id_to_answers["440110896145059840"] = ["A", "D", "A", "D", "E"]

        # https://app.galxe.com/quest/RazorDao/GCX43tkmoZ
        self.credential_id_to_answers["439582556942270464"] = ["B", "C", "A", "C", "B"]
        self.credential_id_to_answers["440638077657067520"] = ["C", "B", "A", "A"]

        # https://app.galxe.com/quest/Route-X/GCpkxtkfqQ
        self.credential_id_to_answers["433653260763623424"] = ["C", "C"]
        self.credential_id_to_answers["434238894603567104"] = ["A", "B"]

        # https://app.galxe.com/quest/Movewiffrens/GC2Z7tk3TG
        self.credential_id_to_answers["433161609918021632"] = ["B", "D", "A", "B", "D"]
        self.credential_id_to_answers["433161611855802368"] = ["B", "C", "B", "A", "C", "B", "C", "B", "C", "C"]

        # https://app.galxe.com/quest/EnsoFi/GCkrPtvmmg
        self.credential_id_to_answers["446232554761117696"] = ["C", "D", "C"]
        # https://app.galxe.com/quest/EnsoFi/GCxxPtvVNU
        self.credential_id_to_answers["446237105530617856"] = ["A", "C", "A"]

        # https://app.galxe.com/quest/Mosaic/GCepQtvzwy
        self.credential_id_to_answers["443681676208398336"] = ["B", "A", "C", "D"]

        # https://app.galxe.com/quest/OmniBTC/GChqAtvCy4
        self.credential_id_to_answers["435631737129680896"] = ["C", "C", "B"]
        # https://app.galxe.com/quest/OmniBTC/GCE6Atvowr
        self.credential_id_to_answers["435636294358503424"] = ["E", "A", "B"]

        # https://app.galxe.com/quest/WarpGate/GC2zetviKg
        self.credential_id_to_answers["443678270261583872"] = ["B", "D", "B", "C"]
        # https://app.galxe.com/quest/WarpGate/GC2HutvqoY
        self.credential_id_to_answers["445855513691906048"] = ["B", "B"]
        # https://app.galxe.com/quest/WarpGate/GCacBtvtmE
        self.credential_id_to_answers["445861813796487168"] = ["C", "C"]

        # https://app.galxe.com/quest/DegenHive/GC9d9tky1N
        self.credential_id_to_answers["438637682764021760"] = ["E", "E", "A", "A", "A", "D", "D", "B", "B", "B", "E"]

        # https://app.galxe.com/quest/LunchApp/GCacqtkico
        self.credential_id_to_answers["439349717386665984"] = ["C", "A", "C", "B"]

        # https://app.galxe.com/quest/XenoBunny/GCYjrtxLKE
        self.credential_id_to_answers["454343702660362240"] = ["B", "B", "D", "B", "C", "A", "D", "A"]

        # https://app.galxe.com/quest/satay/GCDN2tkLow
        self.credential_id_to_answers["438963288508780544"] = ["A", "Blocks Strategist Vault", "Movement", "C", "blocks", "vaults", "blocks", "B"]
        # self.credential_id_to_answers["438963288508780544"] = ["A", "Blocks Strategist Vault", "Movement",  "C", "blocks", "vaults", "vaultcoin","blocks","B"]

        # GC3q7tvyLe
        self.credential_id_to_answers["444342236356849664"] = ["blocks"]

        """
              ╔═══════════════════════════════════════════════════════════════════════╗
              ║ 以下是 xion 相关的                                                     ║
              ╚═══════════════════════════════════════════════════════════════════════╝
        """
        # https://app.galxe.com/quest/burnt/GCxLutxvCN
        self.credential_id_to_answers["458138876029009920"] = ["B", "D", "A", "A"]
        # GCLqPtKH7H
        self.credential_id_to_answers["468396748386082816"] = ["A", "B", "C"]

        """
              ╔═══════════════════════════════════════════════════════════════════════╗
              ║ 以下是 puffer 相关的                                                     ║
              ╚═══════════════════════════════════════════════════════════════════════╝
        """
        # https://app.galxe.com/quest/pufferfinance/GCcVntxZAi
        self.credential_id_to_answers["458314899316142080"] = ["B", "C", "B", "D"]

        """
              ╔═══════════════════════════════════════════════════════════════════════╗
              ║ 以下是 冒险岛MapleStoryUniverse 相关的                                                     ║
              ╚═══════════════════════════════════════════════════════════════════════╝
        """
        # https://app.galxe.com/quest/MapleStoryUniverse/GCJGhtVkin  DCABA
        self.credential_id_to_answers["472315850792165376"] = ["D"]
        self.credential_id_to_answers["472316024880893952"] = ["C"]
        self.credential_id_to_answers["472316172067422208"] = ["A"]
        self.credential_id_to_answers["472316440058281984"] = ["B"]
        self.credential_id_to_answers["472316566541721600"] = ["A"]

        # https://app.galxe.com/quest/Vana/GCMintxk3n  aacbc
        self.credential_id_to_answers["458251787066023936"] = ["A", "A", "C", "B", "C"]

        # https://app.galxe.com/quest/LagrangeLabs/GCvBgtVAeu
        self.credential_id_to_answers["473468243659472896"] = ["C", "B"]

        # https://app.galxe.com/quest/SpaceandTimeDB/GCxwBtKJXi A、F、C、B、A
        self.credential_id_to_answers["472104962118160384"] = ["A", "F", "C", "B", "A"]

        # https://app.galxe.com/quest/Cysic/GCnwUtVMZN  BBBAC-BA
        self.credential_id_to_answers["471995292590313472"] = ["B", "B", "B", "A", "C", "B", "A"]

        # https://app.galxe.com/quest/CORN/GCTcbtKxoc
        # 1BCAC 2ABDC 3BCDC 4BBAD 5BCCA 6BCAD 7CBCB   8BBAB 9BAAD 10BBAD 11BCAD
        self.credential_id_to_answers["467696052812705792"] = ["B", "C", "A", "C"] #1
        self.credential_id_to_answers["468392267581784064"] = ["A", "B", "D", "C"] #2
        self.credential_id_to_answers["468393769138454528"] = ["B", "C", "D", "C"] #3
        self.credential_id_to_answers["468395721444368384"] = ["B", "B", "A", "D"] #4
        self.credential_id_to_answers["468397657967042560"] = ["B", "C", "C", "A"] #5
        self.credential_id_to_answers["468399428412149760"] = ["B", "C", "A", "D"] #6
        self.credential_id_to_answers["468401147812585472"] = ["C", "B", "C", "B"] #7
        self.credential_id_to_answers["468405262038888448"] = ["B", "B", "A", "B"] #8
        self.credential_id_to_answers["468406334434369536"] = ["B", "A", "A", "D"] #9
        self.credential_id_to_answers["468407557417971712"] = ["B", "B", "A", "D"] #10
        self.credential_id_to_answers["468408779239669760"] = ["B", "C", "A", "D"] #11


        # https://app.galxe.com/quest/Fluswap/GC2EhtKbmK
        self.credential_id_to_answers["459490845180047360"] = ["A", "A", "A"]

        # https://app.galxe.com/quest/curvance/GCvEYtKNPH
        self.credential_id_to_answers["463311129163182080"] = ["B", "A", "B"]



    def get_credential_answers(self, credential_id) -> list:
        logger.info(f"get_credential_answers start credential_id={credential_id} type({type(credential_id)})")

        if credential_id not in self.credential_id_to_answers:
            # 必须要有答案，不然直接报错
            raise Exception(f"get_credential_answers Invalid credential_id({credential_id}) type({type(credential_id)})")
        else:
            answers = self.credential_id_to_answers[credential_id]
            # 替换大写字母为数字
            for i in range(len(answers)):
                if len(answers[i]) == 1 and 'A' <= answers[i] <= 'Z':
                    answers[i] = str(ord(answers[i]) - ord('A'))
            return answers


if __name__ == '__main__':
    cur_service = ServiceQuiz()
    credential_id = "427182193014497280"
    answers = cur_service.get_credential_answers(credential_id)
    logger.info(f"answers={answers}")
    for answer in answers:
        logger.info(f"answer={answer} type({type(answer)})")
