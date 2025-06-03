import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

console.log("pos_indv_receipt: PosStore.js patch is being loaded."); // Debug log

/**
 * Patch for the PosStore to add functionality for printing individual receipts for prepayed products.
 * This allows printing individual receipts for each product in an order,
 * which is useful for scenarios where products are pre-paid and need to be printed separately.
 * @typedef {import("@point_of_sale/app/store/pos_store").PosStore} PosStore
 * @see {@link https://github.com/odoo/odoo/blob/a43ef8e15f4e0ee28bdb1975a8a359d3373e8d2c/addons/point_of_sale/static/src/app/store/pos_store.js}
 */
patch(PosStore.prototype, {
    /**
     * Postore setup is asynchronous, so we need to ensure that the setup is completed before using the store.
     * Need to "return super.setup(...arguments)"to ensure the original setup logic is executed. 
     */
    setup() {
        return super.setup(...arguments);
    },

    /**
     * 
     * @param {*} order 
     * @param {*} order_line 
     * @returns 
     */
    orderExportForPrintingIndividualReceipt({
        order,
        order_line = null
    }) {
        const headerData = this.getReceiptHeaderData(order);
        const baseUrl = this.session._base_url;
        return order.export_for_printing_individual_prepaid_products(
            baseUrl,
            headerData,
            order_line
        );
    },

    /**
     * 
     * @param {*} param0 
     * @returns 
     */
    async printIndividualPrepaidReceipt({
        basic = false,
        order = this.get_order(),
        order_line = null,
        printBillActionTriggered = false,
    } = {}) {
        const result = await this.printer.print(
            OrderReceipt,
            {
                data: this.orderExportForPrintingIndividualReceipt({
                    order: order,
                    order_line: order_line
                }),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: basic,
            },
            { webPrintFallback: true }
        );
        if (!printBillActionTriggered) {
            order.nb_print += 1;
            if (typeof order.id === "number" && result) {
                await this.data.write("pos.order", [order.id], { nb_print: order.nb_print });
            }
        }
        return true;
    },

    /**
     * 
     * @param {*} order 
     * @param {*} order_line 
     * @returns 
     */
    orderExportForPrintingFullPrepaidReceipt({
        order,
        order_lines = null,
        printCachierReceipt = false,
        printFullClientReceipt = false
    }) {
        const headerData = this.getReceiptHeaderData(order);
        const baseUrl = this.session._base_url;
        return order.export_for_printing_full_prepaid_products(
            baseUrl,
            headerData,
            order_lines,
            printCachierReceipt,
            printFullClientReceipt
        );
    },
    /**
     * 
     * @param {*} param0 
     * @returns 
     */
    async printFullPrepaidReceipt({
        basic = false,
        order = this.get_order(),
        order_lines = null,
        printCachierReceipt = false,
        printFullClientReceipt = false,
        printBillActionTriggered = false,
    } = {}) {
        const result = await this.printer.print(
            OrderReceipt,
            {
                data: this.orderExportForPrintingFullPrepaidReceipt({
                    order: order,
                    order_lines: order_lines,
                    printCachierReceipt: printCachierReceipt,
                    printFullClientReceipt: printFullClientReceipt
                }),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: basic,
            },
            { webPrintFallback: true }
        );
        if (!printBillActionTriggered) {
            order.nb_print += 1;
            if (typeof order.id === "number" && result) {
                await this.data.write("pos.order", [order.id], { nb_print: order.nb_print });
            }
        }
        return true;
    }
});