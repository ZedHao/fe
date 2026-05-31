import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from dao import mock_data


def _ok(data, message='请求成功'):
    return JsonResponse({'code': 200, 'message': message, 'data': data}, safe=False)


def _err(msg, status=400):
    return JsonResponse({'code': status, 'message': msg, 'data': None}, status=status)


@require_http_methods(['GET'])
def premium(request):
    return _ok(mock_data.get_premium_data())


@require_http_methods(['GET'])
def fund_history(request, code):
    return JsonResponse(mock_data.get_fund_history(code), safe=False)


@require_http_methods(['GET'])
def fund_limit(request, code):
    return JsonResponse(mock_data.get_fund_limit(code), safe=False)


@require_http_methods(['GET'])
def health(request):
    return JsonResponse(mock_data.health(), safe=False)


@require_http_methods(['GET'])
def custom_funds(request):
    return JsonResponse(mock_data.get_custom_funds(), safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def add_fund(request):
    body = json.loads(request.body or '{}')
    code = body.get('code', '').strip()
    if not code:
        return _err('缺少 code')
    result = mock_data.add_custom_fund(code, body.get('name'))
    if result.get('error'):
        return _err(result['error'])
    return JsonResponse(result, safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def remove_fund(request):
    body = json.loads(request.body or '{}')
    code = body.get('code', '').strip()
    if not code:
        return _err('缺少 code')
    return JsonResponse(mock_data.remove_fund(code), safe=False)


@require_http_methods(['GET'])
def perks(request):
    return JsonResponse(mock_data.get_perks(
        request.GET.get('filter', 'all'),
        request.GET.get('search', ''),
    ), safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def perks_update(request):
    body = json.loads(request.body or '{}')
    perks = body.get('perks', [])
    return JsonResponse(mock_data.update_perks(perks), safe=False)


@require_http_methods(['GET'])
def futures_basis(request):
    return JsonResponse(mock_data.get_futures_basis(), safe=False)


@require_http_methods(['GET'])
def futures_detail(request, symbol):
    return JsonResponse(mock_data.get_futures_detail(symbol), safe=False)


@require_http_methods(['GET'])
def house_prices(request):
    city = request.GET.get('city', 'suzhou')
    return JsonResponse(mock_data.get_house_prices(city), safe=False)


@require_http_methods(['GET'])
def calendar(request):
    return JsonResponse(mock_data.get_calendar(), safe=False)


@require_http_methods(['GET'])
def blacklist(request):
    return JsonResponse(mock_data.get_blacklist(), safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def blacklist_add(request):
    body = json.loads(request.body or '{}')
    code = body.get('code', '').strip()
    if not code:
        return _err('缺少 code')
    result = mock_data.add_blacklist(code, body.get('name', ''), body.get('reason', ''))
    if result.get('error'):
        return _err(result['error'])
    return JsonResponse(result, safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def blacklist_remove(request):
    body = json.loads(request.body or '{}')
    code = body.get('code', '').strip()
    if not code:
        return _err('缺少 code')
    return JsonResponse(mock_data.remove_blacklist(code), safe=False)


@require_http_methods(['GET'])
def stock_risk(request, code):
    return JsonResponse(mock_data.get_stock_risk(code), safe=False)
