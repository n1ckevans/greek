from django.urls import include, re_path
from . import views
from .views import CheckoutView

urlpatterns = [
    re_path(r'^$', views.splash),
    re_path(r'^home$', views.home),
    re_path(r'^about$', views.about),
    re_path(r'^catering$', views.catering),
    re_path(r'^signin$', views.signin),
    re_path(r'^signup$', views.signup),
    re_path(r'^register$', views.register),
    re_path(r'^login_post$', views.login_post),
    re_path(r'^signout$', views.signout),
    re_path(r'^items$', views.all_items),
    re_path(r'^items/show/(?P<product_id>[0-9]+)$', views.show_item),
    re_path(r'^products/search$', views.item_search),
    re_path(r'^products/search/(?P<sortby>[a-z\\-]+)$', views.product_sortby),
    # re_path(r'^category/(?P<category>[a-z]+)$', views.show_category),
    re_path(r'^cart$', views.view_cart),
    re_path(r'^add_to_cart$', views.add_to_cart),
    re_path(r'^cart/update/(?P<orderitem_id>[0-9]+)$', views.update_cart),
    re_path(r'^cart/delete/(?P<orderitem_id>[0-9]+)$', views.delete_cart),
    re_path(r'^checkout$', CheckoutView.as_view(), name='checkout'),
    re_path(r'^check_promo$', views.check_promo),
    re_path(r'^checkout/shipping_info$', views.shipping_info),
    re_path(r'^checkout/payment_options$', views.payment_options),
    re_path(r'^checkout/complete$', views.payment_complete),
    re_path(r'^payment-done$', views.payment_done, name='payment_done'),
    re_path(r'^payment-cancelled$', views.payment_cancelled, name='payment_cancelled'),
    re_path(r'^charge$', views.charge),
    re_path(r'^account$', views.account),
    re_path(r'^account/orders/(?P<order_id>[0-9]+)$', views.order),
]
