# -*- coding: utf-8 -*-
import logging
import time
import calendar
from datetime import timedelta, date, datetime

from django.db import connections, transaction
from django.db.models import Sum

from models import Member, Order, MonthlyData


logger = logging.getLogger(__name__)

TODAY = date.today()
YESTERDAY = TODAY - timedelta(1)

# 获取前一天注册的新用户
NEW_MEMEBERS_SQL = ("""
SELECT
    user_id,user_name,email,phone_mob,reg_time
FROM
    ecmall.ecm_member
WHERE
    reg_time >= UNIX_TIMESTAMP('%s')
        AND reg_time < UNIX_TIMESTAMP('%s');
""" % (YESTERDAY, TODAY))

# 获取前一天完成的订单
NEW_FINISHED_ORDERS_SQL = ("""
SELECT
    order_sn,buyer_id,buyer_name,goods_amount,add_time,finished_time
FROM
    ecmall.ecm_order
WHERE
    status = 40
        AND finished_time >= UNIX_TIMESTAMP('%s')
        AND finished_time < UNIX_TIMESTAMP('%s');
""" % (YESTERDAY, TODAY))


def timestamp_converter(timestamp):
    """将时间戳转换成datetime"""
    time_str = time.strftime("%b %d %Y %I:%M%p", time.localtime(timestamp))
    dt_obj = datetime.strptime(time_str, '%b %d %Y %I:%M%p')
    return dt_obj


def get_data_from_external(sql):
    """获取外部数据库的数据"""
    cursor = connections['external'].cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


@transaction.atomic
def auto_create_new_members():
    """每日创建前一天新注册的用户"""
    logger.info("Fetching %s's new MEMBERs from external database on %s." %
                (YESTERDAY, TODAY))
    rows = get_data_from_external(NEW_MEMEBERS_SQL)
    if rows:
        for row in rows:
            Member.objects.create(name=row[1],
                                  email=row[2],
                                  mobile=row[3],
                                  uid=str(row[0]),
                                  reg_time=timestamp_converter(row[4]))
        logger.info("%s new MEMBERs on %s. Done!" % (len(rows), TODAY))
    else:
        logger.info("No new MEMBERs.")


@transaction.atomic
def auto_create_new_orders():
    """每日创建前一天新完成的订单"""
    logger.info("Fetching %s's new ORDERs from external database on %s." %
                (YESTERDAY, TODAY))
    rows = get_data_from_external(NEW_FINISHED_ORDERS_SQL)
    if rows:
        for row in rows:
            Order.objects.create(order_number=str(row[0]),
                                 buyer_id=str(row[1]),
                                 buyer_name=row[2],
                                 total=row[3],
                                 order_time=timestamp_converter(row[4]),
                                 finished_time=timestamp_converter(row[5]))
        logger.info("%s new ORDERs on %s. Done!" % (len(rows), TODAY))
    else:
        logger.info("No new ORDERs.")


@transaction.atomic
def auto_generate_monthly_data():
    """
    每月1号创建前一月度巧购用户的订单汇总
    每月1号凌晨执行
    """
    if TODAY.day == 1:
        logger.info("Generating %s's MONTHLY_DATA on %s." %
                    (YESTERDAY.strftime("%Y-%m"), TODAY))
        last_month_orders = Order.objects.filter(
            finished_time__year=YESTERDAY.year,
            finished_time__month=YESTERDAY.month)

        for d in last_month_orders.values('buyer_id').distinct():
            orders = last_month_orders.filter(
                buyer_id=d['buyer_id'])
            MonthlyData.objects.create(month=YESTERDAY.strftime("%Y-%m"),
                                       buyer_id=d['buyer_id'],
                                       buyer_name=orders[0].buyer_name,
                                       total=orders.aggregate(
                                           Sum('total'))["total__sum"],
                                       amount=len(orders))
        logger.info(" %s's monthly_datas on %s Done!." %
                    (YESTERDAY.strftime("%Y-%m"), TODAY))
