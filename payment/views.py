from django.shortcuts import render
import razorpay
from payment.constants import *
from test1.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY

client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))


def pay(request):
    order_amount = request.GET.get(AMOUNT)
    order_amount=int(order_amount)*100
    order_currency = "INR"
    payment_order = client.order.create(
        dict(amount=order_amount, currency=order_currency, payment_capture=1)
    )
    payment_order_id = payment_order["id"]
    context = {
        AMOUNT: order_amount,
        "api_key": RAZORPAY_API_KEY,
        "order_id": payment_order_id,
    }
    return render(request, "inventory/pay.html", context)
