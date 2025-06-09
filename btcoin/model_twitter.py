import random
import string
import uuid

"""
观察按这些字符串的规律，再另外随机生成10个的字符串
84OwnyqRhSKXH5j84dX/8FS93UY90PYUIvflndMu/JWJnxSi1h6iXb6FKUoOnc3eVCYmbvHyazToVPtf0o9R4WIUOSIM8A
95hV4G6Zr2TEb0hcqZZ/6yVJcGEsQp1RXtz1tu+2PR8mtAwBDd0joYbImqLRHU2UhZFxavXGUnqwq93/mwkEMjEUidLW9A
UD/yR8k+CMNjyO/7DjHYTILu18aL5Tr2+XtSEUgRmriBE6umqnqEBiFvPQV2uuozIrzVzVK9Vla335Q8S6KcD0LC/c2UUw
9ZpX4mybrWbGbUpeq5R96SdLcmMuQJ9TXN73tO20Px0ktg4DD98ho4TKmKDTH0+Wh5dwaPfeV4VJs9ObGrKfz9/hcV2i9g

"""


def generate_random_x_client_transaction_id():
    length = 64
    characters = string.ascii_letters + string.digits + "/+"
    return ''.join(random.choice(characters) for _ in range(length))




"""
观察按这些字符串的规律，再另外随机生成5个的字符串，再给出python的编程方式
aee76ee9-29ac-4465-ac51-edf966581a14
610352a3-c156-466c-a34b-69356c8cda92
71d31f5d-2a23-47e0-b062-87b294a5fe75
"""


def generate_random_x_client_uuid():
    return str(uuid.uuid4())


# notice 太扯淡了，我连长度都没搞对，一定是36位
# x_client_uuid_list = []


