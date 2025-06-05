import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { parseUTCString, qrCodeSrc } from "@point_of_sale/utils";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { formatDate, formatDateTime } from "@web/core/l10n/dates";
import { floatIsZero } from "@web/core/utils/numbers";
import { omit } from "@web/core/utils/objects";
const { DateTime } = luxon;

/**
 * Patch for the PosOrder to add functionality for printing individual receipts for prepayed products.
 * This allows printing individual receipts for each product in an order,
 * which is useful for scenarios where products are pre-paid and need to be printed separately.
 * @typedef {import("@point_of_sale/app/models/pos_order").PosOrder} PosOrder
 * @see {@link https://github.com/odoo/odoo/blob/2ffd7fba6107b84f9608d3e8b27d3f70f3bcbc8d/addons/point_of_sale/static/src/app/models/pos_order.js}
 */
patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
    },

    get_prepaid_labels(){
        return{
            label_prepaid_quantity: _t("Prepaid Quantity"),
            label_prepaid_uid: _t("Prepaid ID"),
            label_prepaid_products: _t("This order contains prepaid products."),
            label_prepaid_products_print: _t("Each prepaid product will be printed separately."),
            label_prepaid_products_note: _t("Do not lose your tickets; to claim the products, you need to exchange them at the bar."),
            label_prepaid_product_list_head: _t("List of Prepaid Products:"),
            label_prepaid_product_available: _t("The product above has been prepaid."),
            label_change_prepaid_product: _t("Please exchange this ticket for your product at the bar.")
        }
    },
    export_for_printing_full_prepaid_products(
        baseUrl,
        headerData,
        lines,
        printCachierReceipt = false,
        printFullClientReceipt = false
    ) {
        const print_data = this.export_for_printing(
            baseUrl,
            {
                ...headerData,
                printIndividualDetalledReceipt: printIndividualDetalledReceipt,
                printFullClientReceipt: printFullClientReceipt,
                printCachierReceipt: printCachierReceipt,
                label_customer_recept: _t("Customer Receipt"),
                label_cashier_recept: _t("Cashier Receipt"),
            },
        )
        
        const order_lines = this.getSortedOrderlines()
            .map((l) => omit(l.getDisplayData(), "internalNote"));
        const prepaid_items = lines
                .map((l) => omit(l, "internalNote"));
        console.log("export_for_printing_full_prepaid_products: prepaid_items", prepaid_items, " - order lines", order_lines);
        return {
            ...print_data,
            orderlines: order_lines,
            // Additional data for individual receipt printing
            ...this.get_prepaid_labels(),
            individualReceipt: false,
            printCachierReceipt: printCachierReceipt,
            printFullClientReceipt: printFullClientReceipt,
            prepaid_items: prepaid_items,
            
        };
    },
    export_for_printing_individual_prepaid_products(
        baseUrl,
        headerData,
        line
    ) {
        const print_data = this.export_for_printing(
            baseUrl,
            {
                ...headerData,
                individualReceipt: true,
                prepaid_uuid: line && line.prepaid_uuid ? line.prepaid_uuid : null,
                label_prepaid_title: _t("Prepaid Product"),
            },
        )
        
        const order_lines = this.getSortedOrderlines()
                .filter((l) => line ? l.id === line.id : false)
                .map((l) => omit(l.getDisplayData(), "internalNote"))
                .map((l) => {
                    return {
                        ...l,
                        qty: "1,00"
                    }
                });
        console.log("Order lines: ", order_lines)
        return {
            ...print_data,
            orderlines: order_lines,
            // Additional data for individual receipt printing
            ...this.get_prepaid_labels(),
            individualReceipt: true,
            printFullClientReceipt: false,
            printCachierReceipt: false,
            prepaid_items: null,
            
        };
    },

    /**
     * This method is no more used only for dev process.
     * @param {*} baseUrl 
     * @param {*} headerData 
     * @param {*} line 
     * @param {*} printFullClientReceipt 
     * @returns 
     */
    export_for_printing_prepaid_products(
        baseUrl,
        headerData,
        line,
        printFullClientReceipt = false
    ) {
        const paymentlines = this.payment_ids
            .filter((p) => !p.is_change)
            .map((p) => p.export_for_printing());

        const taxTotals = this.taxTotals;

        const order_rounding = taxTotals.order_rounding;
        const order_change = this.get_change();

        const base_lines = this.getSortedOrderlines();
        let order_lines = [];
        let prepaid_items = null;
        if (printFullClientReceipt === true) {
            order_lines = base_lines
                .map((l) => omit(l.getDisplayData(), "internalNote"))
            prepaid_items = base_lines
                .filter((l) => line ? l.id === line.id : false)
                .map((l) => omit(l.getDisplayData(), "internalNote"))
        }
        else{
            order_lines = base_lines
                .filter((l) => line ? l.id === line.id : false)
                .map((l) => omit(l.getDisplayData(), "internalNote"))
                .map((l) => parseInt(l.qty) > 1 ? { ...l, qty: "1,00" } : l)
        }
        return {
            orderlines: order_lines,
            taxTotals: taxTotals,
            label_total: _t("TOTAL"),
            label_rounding: _t("Rounding"),
            label_change: _t("CHANGE"),
            label_discounts: _t("Discounts"),
            show_rounding: !floatIsZero(order_rounding, this.currency.decimal_places),
            order_rounding: order_rounding,
            show_change: !floatIsZero(order_change, this.currency.decimal_places),
            order_change: order_change,
            paymentlines,
            amount_total: this.get_total_with_tax(),
            total_without_tax: this.get_total_without_tax(),
            amount_tax: this.get_total_tax(),
            total_paid: this.get_total_paid(),
            total_discount: this.get_total_discount(),
            tax_details: this.get_tax_details(),
            change: this.amount_return,
            name: this.pos_reference,
            generalNote: this.general_note || "",
            invoice_id: null, //TODO
            cashier: this.getCashierName(),
            date: formatDateTime(parseUTCString(this.date_order)),
            pos_qr_code:
                this.company.point_of_sale_use_ticket_qr_code &&
                this.finalized &&
                qrCodeSrc(`${baseUrl}/pos/ticket/`),
            ticket_code: this.ticket_code,
            base_url: baseUrl,
            footer: this.config.receipt_footer,
            // FIXME: isn't there a better way to handle this date?
            shippingDate: this.shipping_date && formatDate(DateTime.fromSQL(this.shipping_date)),
            headerData: {
                ...headerData,
                trackingNumber: this.tracking_number,
            },
            screenName: "ReceiptScreen",
            // Additional data for individual receipt printing
            individualReceipt: !printFullClientReceipt,
            printFullClientReceipt: printFullClientReceipt,
            prepaid_items: prepaid_items,
            label_prepaid_products: _t("This order contains prepaid products."),
            label_prepaid_products_print: _t("Each prepaid product will be printed separately."),
            label_prepaid_products_note: _t("Do not lose your tickets; to claim the products, you need to exchange them at the bar."),
            label_prepaid_product_list_head: _t("List of Prepaid Products:"),
            label_prepaid_product_available: _t("The product above has been prepaid."),
            label_change_prepaid_product: _t("Please exchange this ticket for your product at the bar.")
        };
    }

});