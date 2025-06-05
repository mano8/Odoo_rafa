import { OrderWidget  } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { Component, useEffect, useRef } from "@odoo/owl";
import { CenteredIcon } from "@point_of_sale/app/generic_components/centered_icon/centered_icon";
import { _t } from "@web/core/l10n/translation";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { formatMonetary } from "@web/views/fields/formatters";
import { patch } from "@web/core/utils/patch";

patch(OrderWidget .prototype, {
    setup() {
        super.setup(...arguments);
        console.log("OrderWidget props :", this.props)
        console.log("OrderWidget this :", this)
        //individualReceipt
        
    },

});