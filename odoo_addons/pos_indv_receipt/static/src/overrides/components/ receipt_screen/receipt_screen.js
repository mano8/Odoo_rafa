/** @odoo-module **/

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useTrackedAsync } from "@point_of_sale/app/utils/hooks";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ProductSelectionPopup } from "@pos_indv_receipt/app/product_selection_popup/product_selection_popup";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


/**
 * Patch for the ReceiptScreen to add functionality for printing individual receipts for prepayed products.
 * This allows printing individual receipts for each product in an order,
 * which is useful for scenarios where products are pre-paid and need to be printed separately.
 * @typedef {import("@point_of_sale/app/screens/receipt_screen/receipt_screen").ReceiptScreen} ReceiptScreen
 * @see {@link https://github.com/odoo/odoo/blob/de4634f54f7414f0d732ca3ac0f35fe138fbf674/addons/point_of_sale/static/src/app/screens/receipt_screen/receipt_screen.js}
 */
patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.dialog = useService("dialog");

        this.labels = {
            print_individual_receipt: _t("Print Individual Receipts")
        };

        this.doOpenProductSelectionPopup = useTrackedAsync(() => this._onClickPrintProductTickets());
        // This function is used to print the full receipt for the order, including all prepaid products
        this.doPrintFullPrepaidReceipt = useTrackedAsync(({
            basic = false,
            order_lines = null,
            printFullClientReceipt = true,
            printCachierReceipt = true
        }) => this.pos.printFullPrepaidReceipt({ 
            basic: basic,
            order_lines: order_lines,
            printFullClientReceipt: printFullClientReceipt,
            printCachierReceipt: printCachierReceipt
        }));
        // This function is used to print individual receipts for each product in the order
        this.doPrintIndividualPrepaidReceipt = useTrackedAsync(({
            basic = false,
            order_line = null
        }) => this.pos.printIndividualPrepaidReceipt({ 
            basic: basic,
            order_line: order_line
        }));
    },

    async _onClickPrintProductTickets() {
        const order = this.currentOrder;
        // ensure order is not empty
        if (!order || order.get_orderlines().length === 0) {
            await this.dialog.add(AlertDialog, {
                title: _t("Empty Order"),
                body: _t("There are no products in this order to print tickets for."),
            });
            return;
        }

        try {
            const result = await makeAwaitable(this.dialog, ProductSelectionPopup, {
                order: order,
                formatCurrency: this.env.utils.formatCurrency
            });

            // Check if the user cancelled the dialog or no products were selected
            // Print full ticket is not triggered if no products are selected.
            if (!result || !result.selectedOrderLines || result.selectedOrderLines.length === 0) {
                await this.dialog.add(AlertDialog, {
                    title: _t("No Selection"),
                    body: _t("No products were selected for printing."),
                });
                return;
            }

            // Print individual tickets for selected products
            // If printFullClientReceipt is true, print the full receipt first
            await this._printIndividualProductTickets(
                result.selectedOrderLines,
                result.printFullClientReceipt,
                result.printCachierReceipt,
                result.individualDetailledReceipt
            );
        } catch (err) {
            console.error("pos_indv_receipt: Error in product selection popup: ", err);
            await this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t("An error occurred while selecting products. Please try again."),
            });
        }
    },

    async _printIndividualProductTickets(
        selectedOrderLines,
        printFullClientReceipt = true,
        printCachierReceipt = true,
        individualDetailledReceipt = false
    ) {
        console.debug(
            "_printIndividualProductTickets called with order:", this.pos.order,
            " - selectedOrderLines: ", selectedOrderLines,
            " - printFullClientReceipt: ", printFullClientReceipt
        );
        // Ensure selectedOrderLines is an array
        if (!Array.isArray(selectedOrderLines) || selectedOrderLines.length === 0) {
            console.warn("No order lines selected for printing individual tickets.");
            await this.dialog.add(AlertDialog, {
                title: _t("No Selection"),
                body: _t("No products were selected for printing."),
            });
            return;
        }
        // Print full receipt for client if requested
        if (printFullClientReceipt === true) {
            console.debug("Printing full receipt for customer.");
            await this.doPrintFullPrepaidReceipt.call({
                basic: false,
                order_lines: selectedOrderLines,
                printFullClientReceipt: printFullClientReceipt,
                printCachierReceipt: false
            });
            const result = ['success', 'error'].includes(this.doPrintFullPrepaidReceipt.status) && this.doPrintFullPrepaidReceipt.result
            console.debug(
                "Printing Full ticket for customer, result: ", result
            );
        }
        // Print full receipt for cachier if requested
        if (printCachierReceipt === true) {
            console.debug("Printing full receipt for cachier.");
            await this.doPrintFullPrepaidReceipt.call({
                basic: true,
                order_lines: selectedOrderLines,
                printCachierReceipt: printCachierReceipt,
                printFullClientReceipt: false
            });
            const result = ['success', 'error'].includes(this.doPrintFullPrepaidReceipt.status) && this.doPrintFullPrepaidReceipt.result
            console.debug(
                "Printing Full ticket for cachier, result: ", result
            );
        }
        // Print individual tickets for each selected order line
        for (const line of selectedOrderLines) {
            const quantity = line.prepayed_quantity || 0;
            if( quantity <= 0) {
                console.warn(
                    "Skipping printing for line with non-positive quantity:", line,
                    " - quantity: ", quantity,
                );
                continue; // Skip lines with non-positive quantity
            }
            for (let i = 0; i < quantity; i++) {
                await this.doPrintIndividualPrepaidReceipt.call({
                    basic: !individualDetailledReceipt,
                    order_line: line
                });
                const result = ['success', 'error'].includes(this.doPrintIndividualPrepaidReceipt.status) && this.doPrintIndividualPrepaidReceipt.result
                console.debug(
                    "Printing individual line iteration:", i + 1, "of", quantity,
                    " - result: " , result
                );
            }
        }
        return true;
    }
});