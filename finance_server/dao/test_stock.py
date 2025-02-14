from unittest import TestCase

from dao import  stock
class Test(TestCase):
    def test_get_bao_stock_data(self):
        ret = stock.get_bao_stock_data("比亚迪","2025-02-04","2025-02-10")
        print(ret)
        self.fail()
