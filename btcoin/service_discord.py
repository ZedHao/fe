import dao_discord


class ServiceDiscord:

    def __init__(self, proxy: str, header: dict = None):
        self.__dao_discord = dao_discord.DaoDiscord(proxy, header)

    # 从买的token，转为一个用于银河验证的token
    def get_galxe_verify_token(self, address_evm_prefix_and_lower, state, discord_token):



        return self.__dao_discord.get_galxe_verify_token(
            address_evm_prefix_and_lower=address_evm_prefix_and_lower,
            state=state,
            discord_token=discord_token,
        )
