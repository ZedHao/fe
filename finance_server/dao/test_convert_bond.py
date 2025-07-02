from unittest import TestCase
from dao.convert_bond import search_cover_bond_data
import pdb

class Test(TestCase):
    def test_get_df_cover_bond_data(self):
        res = search_cover_bond_data('飞沃科技',301232)
        pdb.set_trace()
        self.fail()
