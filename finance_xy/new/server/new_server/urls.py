from django.contrib import admin
from django.urls import path

from service import etf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/premium', etf.premium),
    path('api/fund-history/<str:code>', etf.fund_history),
    path('api/fund-limit/<str:code>', etf.fund_limit),
    path('api/health', etf.health),
    path('api/custom-funds', etf.custom_funds),
    path('api/add-fund', etf.add_fund),
    path('api/remove-fund', etf.remove_fund),
    path('api/perks', etf.perks),
    path('api/perks/update', etf.perks_update),
    path('api/futures-basis', etf.futures_basis),
    path('api/futures-detail/<str:symbol>', etf.futures_detail),
    path('api/house-prices', etf.house_prices),
    path('api/calendar', etf.calendar),
    path('api/blacklist', etf.blacklist),
    path('api/blacklist/add', etf.blacklist_add),
    path('api/blacklist/remove', etf.blacklist_remove),
    path('api/stock-risk/<str:code>', etf.stock_risk),
]
