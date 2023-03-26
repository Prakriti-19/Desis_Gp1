from django.shortcuts import render
import razorpay
from payment.constants import *
from test1.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY

client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))


def pay(request):
    """
    Creates a payment order using the Razorpay API client and renders the
    payment page

    :param request:
        the HTTP request object

    :return:
        the rendered payment page
    """
    order_amount = request.GET.get(AMOUNT)
    order_amount = int(order_amount) * PAISE
    order_currency = CURRENCY
    payment_order = client.order.create(
        dict(amount=order_amount, currency=order_currency, payment_capture=1)
    )
    payment_order_id = payment_order[ID]
    context = {
        AMOUNT: order_amount,
        API_KEY: RAZORPAY_API_KEY,
        ORDER_ID: payment_order_id,
    }
    return render(request, "inventory/pay.html", context)
