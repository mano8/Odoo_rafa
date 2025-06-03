/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import {uuidv4} from "@point_of_sale/utils";

export class ProductSelectionPopup extends Component {
    static template = "pos_indv_receipt.ProductSelectionPopup";
    static components = { Dialog };
    static props = {
        getPayload: Function,
        formatCurrency: Function,
        order: { type: Object, optional: true },
        close: Function,
    };
    
    static defaultProps = {
        order: null,
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.orderlines = this.props.order?.get_orderlines() || [];
        
        this.labels = {
            confirm: _t("Print Individual Receipts"),
            print_options_title: _t("Options"),
            cancel: _t("Cancel"),
            title: _t("Select Products for Individual Receipt Printing"),
            description: _t("Select all products that need to be printed separately."),
            note: _t("For each selected product, depending on the quantity defined, a ticket will be printed for each unit of the same product."),
            no_items_found: _t("No items found in the order."),
            select_all: _t("Select All"),
            deselect_all: _t("Deselect All"),
            print_cachier_receipt: _t("Print Full Cashier Receipt"),
            print_full_client_receipt: _t("Print Full Customer Receipt"),
            print_individual_detalled_receipt: _t("Print Detailed Individual Receipts"),
            quantity: _t("Quantity"),
            unit_price: _t("Unit Price"),
        };

        this.state = useState({
            selectedLines: this._getInitialSelectedLines(),
            printCachierReceipt: false,
            printFullClientReceipt: false,
            individualDetailledReceipt: true
            
        });

        // hasAnySelected as getter property
        Object.defineProperty(this, "hasAnySelected", {
            get: () => this.getSelectedOrderlines().length > 0,
        });

        console.log("ProductSelectionPopup initialized with lines:", this.orderlines);
    }

    _getLineId(line) {
        return line.uuid || null;
    }

    _getInitialSelectedLines() {
        // Use reduce to build the selectedLines object immutably
        return this.orderlines.reduce((selected, line) => {
            const lineId = this._getLineId(line);
            if (lineId !== null) {
                selected[lineId] = {
                    selected: true,
                    quantity: line.get_quantity(),
                    prepaid_uuid: uuidv4()
                };
            }
            return selected;
        }, {});
    }

    get formatCurrency() {
        return this.pos.format_currency; 
    }

    togglePrintCachierReceipt() {
        this.state.printCachierReceipt = this.state.printCachierReceipt ? false : true;
    }

    togglePrintFullClientReceipt() {
        this.state.printFullClientReceipt = this.state.printFullClientReceipt ? false : true;
    }

    toggleIndividualDetailledReceipt() {
        this.state.individualDetailledReceipt = this.state.individualDetailledReceipt ? false : true;
    }

    toggleLine(lineId) {
        this.state.selectedLines[lineId].selected = !this.state.selectedLines[lineId].selected;
        this.resetQuantity(lineId);
    }

    getSelectedOrderlines() {
        return this.orderlines
            .filter(line => {
                const lineId = this._getLineId(line);
                return lineId && this.state.selectedLines[lineId].selected;
            })
            .map(line => {
                const lineId = this._getLineId(line);
                return {
                    ...line,
                    prepayed_quantity: this.state.selectedLines[lineId].quantity,
                    prepaid_uuid: this.state.selectedLines[lineId].prepaid_uuid,
                };
            });
    }

    getSelectedOrderline(lineId) {
        const order_line = this.orderlines.filter(line => {
            const baseId = this._getLineId(line);
            return baseId && baseId === lineId;
        });
        return order_line.length > 0 ? order_line[0] : null;
    }

    resetQuantity(lineId) {
        const order_line = this.getSelectedOrderline(lineId);
        if (this.state.selectedLines[lineId].selected) {
            this.state.selectedLines[lineId].quantity = order_line.get_quantity();
        } else {
            this.state.selectedLines[lineId].quantity = 0;
        }
    }

    updateQuantity(line, quantity) {
            const lineId = this._getLineId(line);
            const order_line = this.getSelectedOrderline(lineId);
            if (lineId !== null && order_line !== null) {
                const qty = parseInt(quantity);
                if (isNaN(qty) || qty < 0) {
                    console.warn(`Invalid quantity: ${quantity} for line ${lineId}.`);
                }
                else if( qty === 0) {
                    console.warn(`Quantity is zero for line ${lineId}. Deselecting line.`);
                    this.state.selectedLines[lineId].selected = false;
                    this.state.selectedLines[lineId].quantity = qty;
                }
                else if( qty > order_line.get_quantity()) {
                    console.warn(`Quantity ${qty} exceeds available quantity for line ${lineId}. Setting to available quantity.`);
                    this.state.selectedLines[lineId].quantity = order_line.get_quantity();
                }
                else{
                    this.state.selectedLines[lineId].quantity = qty;
                }
                
            }
    }

    get hasAnySelected() {
        // Use some for clarity
        return Object.values(this.state.selectedLines).filter(line => line.selected).length <= 1;
    }

    isAllSelected() {
        return this.orderlines.every(line => {
            const lineId = this._getLineId(line);
            return lineId && this.state.selectedLines[lineId].selected;
        });
    }

    selectAll() {
        for (const line of this.orderlines) {
            const lineId = this._getLineId(line);
            if (lineId) {
                this.state.selectedLines[lineId].selected = true;
                this.resetQuantity(lineId);
            }
        }
    }

    deselectAll() {
        for (const line of this.orderlines) {
            const lineId = this._getLineId(line);
            if (lineId) {
                this.state.selectedLines[lineId].selected = false;
                this.resetQuantity(lineId);
            }
        }
    }

    toggleAll() {
        if (this.isAllSelected()) {
            this.deselectAll();
        } else {
            this.selectAll();
        }
    }

    cancel() {
        this.props.close();
    }

    confirm() {
        const selected = this.getSelectedOrderlines();
        this.props.getPayload({
            selectedOrderLines: selected,
            printCachierReceipt: this.state.printCachierReceipt,
            printFullClientReceipt: this.state.printFullClientReceipt,
            individualDetailledReceipt: this.state.individualDetailledReceipt,
            
        });
        this.props.close();
    }
}