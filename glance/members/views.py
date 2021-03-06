# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum

from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import (SubLevelSerialSerializer,
                          MemberOrdersSerializer,
                          AllMemberOrdersSerializer,
                          AssginMemberSerializer,
                          )
from .models import Serial, Member, Order, MonthlyData
from commons.exceptions import APIError
from .forms import UserForm, SerialForm

logger = logging.getLogger(__name__)


# def _paginate_response(data, request):
#     paginator = PageNumberPagination()
#     result_page = paginator.paginate_queryset(data, request)
#     return paginator.get_paginated_response(result_page)


# class CustomPagination(PageNumberPagination):
#     def get_paginated_response(self, data):
#         return Response({
#             'links': {
#                 'next': self.get_next_link(),
#                 'previous': self.get_previous_link()
#             },
#             'count': self.page.paginator.count,
#             'results': data
#         })


# class SerialListView(APIView):
#     """返回所有序列会员"""
#     def get(self, request, format=None):
#         # Returns a JSON response with a listing of serial objects
#         serials = Serial.objects.all()
#         paginator = PageNumberPagination()
#         result_page = paginator.paginate_queryset(serials, request)
#         serializer = SerialSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serializer.data)


def register(request):
    """会员注册"""
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        serial_form = SerialForm(data=request.POST)

        if user_form.is_valid() and serial_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            serial = serial_form.save(commit=False)
            serial.user = user
            serial.save()
            registered = True

        else:
            print user_form, serial_form.errors

    else:
        user_form = UserForm()
        serial_form = SerialForm()

    return render(request,
                  'register.html',
                  {'user_form': user_form,
                   'serial_form': serial_form,
                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                # redirect to the serial
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Glance account is disabled.")
        else:
            login_info = "Invalid login details supplied. Please try again."
            return render(request, 'login.html', {'login_info': login_info})
    else:
        return render(request, 'login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def _format_serials(serials):
    """将符查找到合条件的serials转换为{"level": 1,"serials": 0101}的形式"""
    details = []
    from collections import defaultdict
    d = defaultdict(list)
    for v, k in [(s.serial, s.level) for s in serials]:
        d[k].append(v)
    for v, k in d.items():
        print v, k
        details.append({"level": v,
                        "serials": k})
    return {'results': details}


@api_view(['GET'])
@login_required
def sub_level_serials(request):
    """根据当前serial获取该seial的下级serial, sort in level"""
    logger.info('[sub_level_serials] Received data : %s' %
                request.query_params)
    serializer = SubLevelSerialSerializer(data=request.query_params)
    if serializer.is_valid():
        logger.info('[sub_level_serials] Received data is valid.')
        serial = Serial.objects.get(serial=serializer.validated_data['serial'])
        results = _format_serials(serial.get_subserial(include=False))
        return Response(results)
    raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)


@api_view(['GET'])
@login_required
def get_member_orders(request):
    """根据当前serial，获取直系用户订单"""
    logger.info('[get_member_orders] Received data : %s' %
                request.query_params)
    serializer = MemberOrdersSerializer(data=request.query_params)
    if serializer.is_valid():
        logger.info('[get_member_orders] Received data is valid.')
        start_date = serializer.validated_data['start_date']
        # end_date 需要+1来确保取到end_date当日的数据
        end_date = serializer.validated_data['end_date'] + timedelta(1)
        details = []
        # 取到该序列会员所关联的优宜巧购用户
        members = Member.objects.filter(
            serial=serializer.validated_data['serial']
        )
        for member in members:
            orders = Order.objects.filter(
                buyer_id=member.uid,
                finished_time__range=(start_date, end_date)
            ).order_by('finished_time')
            for order in orders:
                details.append({'order_number': order.order_number,
                                'buyer_name': order.buyer_name,
                                'total': order.total,
                                'order_time': order.order_time,
                                'finished_time': order.finished_time})
        return Response({'results': details})  # 数据能够呈现，之后需要根据前端要求，进行修改
    raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)


@api_view(['GET'])
@login_required
def get_monthly_data(request):
    """
    根据当前serial,获取直系用户月度订单,此接口不能通过日期来查看
    目前取近6个月的数据，用AllMemberOrdersSerializer
    TODO: 按日期查询
    """
    logger.info('[get_monthly_data] Received data : %s' %
                request.query_params)
    serializer = AllMemberOrdersSerializer(data=request.query_params)
    if serializer.is_valid():
        logger.info('[get_monthly_data] Received data is valid.')
        details = []
        # 取到该序列会员所关联的优宜巧购用户的buyer_id
        members = Member.objects.filter(
            serial=serializer.validated_data['serial']
        )
        buyer_ids = [member.uid for member in members]
        # 序列会员的推荐巧购用户多有月度订单汇总数据
        monthly_data = MonthlyData.objects.filter(buyer_id__in=buyer_ids)

        def _gen_past_six_months(given_date=None):
            if given_date is None:
                return [date.today() + relativedelta(
                    months=-i) for i in range(1, 7)]
            else:
                return [given_date + relativedelta(
                    months=-i) for i in range(1, 7)]
        # FIX ME: REMOVE date(2017, 3, 1)
        for month in _gen_past_six_months(date(2017, 3, 1)):
            data = monthly_data.filter(month=month.strftime("%Y-%m"))
            details.append(
                {"month": month.strftime("%Y-%m"),
                 "total": data.aggregate(Sum("total"))["total__sum"],
                 "amount": data.aggregate(Sum("amount"))["amount__sum"],
                 "num_of_buyers": len(data)
                 })
        return Response({'results': details})
    raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)


@api_view(['POST'])
@login_required
def assgin_member(request):
    """
    顶级序列会员可把自己的巧购用户分配个sub序列会员.
    """
    logger.info('[assgin_member] Received data : %s' %
                request.data)
    serializer = AssginMemberSerializer(data=request.data)
    if serializer.is_valid():
        logger.info('[assgin_member] Received data is valid.')
        member = Member.objects.get(mobile=serializer.validated_data['mobile'])
        member.serial = serializer.validated_data['to_serial']
        member.save()
        return Response({'results': "success"})
    #  FIX ME: 需要调整返回接口结构内容
    return Response({'results': str(serializer.errors)})


# ########################drop later#########################
@api_view(['GET'])
@login_required
def get_all_member_orders(request):
    """根据当前serial,获取直系用户所有订单,此接口不能通过日期来查看"""
    logger.info('[get_all_member_orders] Received data : %s' %
                request.query_params)
    serializer = AllMemberOrdersSerializer(data=request.query_params)
    if serializer.is_valid():
        logger.info('[get_all_member_orders] Received data is valid.')
        details = []
        # 取到该序列会员所关联的优宜巧购用户
        members = Member.objects.filter(
            serial=serializer.validated_data['serial']
        )
        for member in members:
            orders = Order.objects.filter(
                buyer_id=member.uid
            ).order_by('finished_time')
            for order in orders:
                details.append({'order_number': order.order_number,
                                'buyer_name': order.buyer_name,
                                'total': order.total,
                                'order_time': order.order_time,
                                'finished_time': order.finished_time})
        import operator
        details.sort(key=operator.itemgetter('finished_time'))
        details.reverse()
        return Response({'results': details})  # 数据能够呈现，之后需要根据前端要求，进行修改
    raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)


def _format_serials_without_level(serials):
    """将符查找到合条件的sub serials"""
    details = []
    for s, n in [(s.serial, s.name) for s in serials]:
        details.append({"serial": s, "name": n})
    return {'results': details}


@api_view(['GET'])
@login_required
def sub_serials(request):
    """根据当前serial获取该seial的下级serial"""
    logger.info('[sub_serials] Received data : %s' %
                request.query_params)
    serializer = SubLevelSerialSerializer(data=request.query_params)
    if serializer.is_valid():
        logger.info('[sub_serials] Received data is valid.')
        serial = Serial.objects.get(serial=serializer.validated_data['serial'])
        serials = serial.get_subserial(include=False)
        results = _format_serials_without_level(serials)
        return Response(results)
    raise APIError(APIError.INVALID_REQUEST_DATA, detail=serializer.errors)
# ########################drop later#########################
