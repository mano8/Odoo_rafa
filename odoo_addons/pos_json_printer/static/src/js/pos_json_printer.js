/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

// ─── hw_proxy helpers ─────────────────────────────────────────────────────────

function _hwUrl(config) {
    return (
        (config.hw_proxy_json_url || "").replace(/\/$/, "") ||
        `${window.location.protocol}//${window.location.hostname}:9001`
    );
}

async function _postJson(url, body) {
    try {
        const resp = await fetch(`${url}/hw_proxy/print_receipt_json`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
            signal: AbortSignal.timeout(10000),
        });
        if (!resp.ok) {
            console.error("[pos_json_printer] hw_proxy error:", resp.status);
            return false;
        }
        return true;
    } catch (err) {
        console.error("[pos_json_printer] fetch error:", err);
        return false;
    }
}

// ─── DOM → receipt lines ──────────────────────────────────────────────────────
//
// Scans the rendered OWL receipt DOM and converts it to a flat array of typed
// line objects (text / row / div).  CSS class → ESC/POS attribute mapping:
//   fw-bold / fw-bolder / fw-semibold  → b: true
//   fs-1 (Bootstrap largest)           → s: 2  (double size)
//   text-center / pos-receipt-*align / pos-receipt-contact → c: "center"
//   text-uppercase                     → text.toUpperCase()
//   pos-receipt-right-align / ms-auto  → right column of a "row" line
//   justify-content-between + flex-grow-1 → product-name/price row pattern

const _BOLD = new Set(["fw-bold", "fw-bolder", "fw-semibold"]);
const _CENTER = new Set([
    "text-center",
    "pos-receipt-center-align",
    "pos-receipt-contact",
]);
// Tags treated as block-level for hasBlock detection
const _SKIP_TAG = new Set(["IMG", "SCRIPT", "STYLE", "BR", "IFRAME"]);
const _BLOCK_TAG = new Set([
    "DIV", "P", "H1", "H2", "H3", "H4", "UL", "OL", "LI", "PRE",
]);

function _isHidden(el) {
    return el.style && (
        el.style.visibility === "hidden" || el.style.display === "none"
    );
}

function _skip(el) {
    if (_SKIP_TAG.has(el.tagName)) return true;
    if (el.tagName === "I") return true; // Font Awesome icons
    if (_isHidden(el)) return true;
    return false;
}

/**
 * Collect ESC/POS formatting attributes by walking ancestors up to root.
 * Also queries descendants for fs-1 (e.g. tracking-number span inside a div).
 */
function _style(el, root) {
    let bold = false, big = false, center = false, upper = false;
    for (let n = el; n && n !== root; n = n.parentElement) {
        const cls = n.classList;
        if (!bold && [...cls].some((c) => _BOLD.has(c))) bold = true;
        if (!big && cls.contains("fs-1")) big = true;
        if (!center && [...cls].some((c) => _CENTER.has(c))) center = true;
        if (!upper && cls.contains("text-uppercase")) upper = true;
    }
    if (!big && el.querySelector && el.querySelector(".fs-1")) big = true;
    return { bold, s: big ? 2 : 1, center, upper };
}

function _isDivider(text) {
    return text.length >= 3 && /^[-=]+$/.test(text);
}

function _hasRightChild(el) {
    return [...el.children].some(
        (c) => c.classList.contains("pos-receipt-right-align") || c.classList.contains("ms-auto")
    );
}

function _isFlexRow(el) {
    const cls = el.classList;
    return (
        (cls.contains("d-flex") && cls.contains("justify-content-between")) ||
        _hasRightChild(el)
    );
}

/**
 * Extract left/right text pair from a flex-row element.
 * Prefers explicit .pos-receipt-right-align / .ms-auto over justify-content-between.
 */
function _extractRow(el) {
    const rightEl = el.querySelector(".pos-receipt-right-align, .ms-auto");
    if (rightEl) {
        const right = rightEl.textContent.trim();
        const leftParts = [];
        for (const n of el.childNodes) {
            if (n.nodeType === Node.TEXT_NODE) {
                const t = n.textContent.trim();
                if (t) leftParts.push(t);
            } else if (
                n.nodeType === Node.ELEMENT_NODE &&
                !n.contains(rightEl) &&
                !_isHidden(n)
            ) {
                const t = n.textContent.trim();
                if (t) leftParts.push(t);
            }
        }
        return { left: leftParts.join(" "), right };
    }
    // justify-content-between: flex-grow-1 child is left, its next sibling is right
    const vis = [...el.children].filter(
        (c) => !_skip(c) && !_isHidden(c) && c.textContent.trim()
    );
    if (vis.length < 2) return null;
    const gIdx = vis.findIndex((c) => c.classList.contains("flex-grow-1"));
    if (gIdx >= 0 && gIdx + 1 < vis.length) {
        return {
            left: vis[gIdx].textContent.trim(),
            right: vis[gIdx + 1].textContent.trim(),
        };
    }
    return {
        left: vis[0].textContent.trim(),
        right: vis[vis.length - 1].textContent.trim(),
    };
}

function _walk(el, root, out) {
    if (_skip(el)) return;

    const hasBlock = [...el.children].some(
        (c) => _BLOCK_TAG.has(c.tagName) && !_skip(c)
    );

    if (!hasBlock) {
        // ── Atomic element ───────────────────────────────────────────
        const raw = el.textContent;
        const text = raw.trim().replace(/\s+/g, " ");
        if (!text) return;

        if (_isDivider(text)) {
            out.push({ t: "div", dv: text[0] });
            return;
        }
        if (_isFlexRow(el)) {
            const row = _extractRow(el);
            if (row && (row.left || row.right)) {
                const { bold, s } = _style(el, root);
                const line = { t: "row" };
                if (row.left) line.l = row.left;
                if (row.right) line.r = row.right;
                if (bold) line.b = true;
                if (s > 1) line.s = s;
                out.push(line);
                return;
            }
        }
        // Pre-formatted text: preserve newlines (white-space:pre-line, PRE tags)
        const { bold, s, center, upper } = _style(el, root);
        if (
            el.tagName === "PRE" ||
            (el.style && el.style.whiteSpace === "pre-line")
        ) {
            for (const ln of raw.split("\n")) {
                const t = ln.trim();
                if (!t) continue;
                const line = { t: "text", v: upper ? t.toUpperCase() : t };
                if (center) line.c = "center";
                if (bold) line.b = true;
                if (s > 1) line.s = s;
                out.push(line);
            }
            return;
        }
        const line = { t: "text", v: upper ? text.toUpperCase() : text };
        if (center) line.c = "center";
        if (bold) line.b = true;
        if (s > 1) line.s = s;
        out.push(line);
        return;
    }

    // ── Container with block children ────────────────────────────────
    // Check for flex-row pattern before recursing (e.g. d-flex with DIV children)
    if (_isFlexRow(el)) {
        const row = _extractRow(el);
        if (row && (row.left || row.right)) {
            const { bold, s } = _style(el, root);
            const line = { t: "row" };
            if (row.left) line.l = row.left;
            if (row.right) line.r = row.right;
            if (bold) line.b = true;
            if (s > 1) line.s = s;
            out.push(line);
            return;
        }
    }
    for (const child of el.children) {
        _walk(child, root, out);
    }
}

function _domToLines(rootEl) {
    // Remove Odoo branding line ("Powered by Odoo" and any i18n equivalent):
    // it lives in a <p> directly inside .pos-receipt-order-data.
    for (const p of rootEl.querySelectorAll(".pos-receipt-order-data > p")) {
        p.remove();
    }

    const out = [];
    for (const child of rootEl.children) {
        // The bottom order-data block (order number + date): always Small,
        // with 1 blank line separating it from the payments section above.
        if (
            child.classList &&
            child.classList.contains("pos-receipt-order-data") &&
            child.querySelector("#order-date")
        ) {
            out.push({ t: "text", v: "" });
            const section = [];
            for (const gc of child.children) {
                _walk(gc, child, section);
            }
            for (const line of section) {
                line.pin = true;
            }
            out.push(...section);
            continue;
        }
        _walk(child, rootEl, out);
    }
    return out;
}

// ─── render OWL component → scan DOM → POST ──────────────────────────────────

/**
 * Renders ``OrderReceipt`` with the given props, walks the resulting DOM,
 * converts it to a flat lines array, and POSTs it to hw_proxy.
 *
 * Because the actual Odoo receipt component is rendered (with all OWL patches
 * applied by every installed addon), the JSON payload automatically reflects
 * the receipt preview — including pos_indv_receipt banners, localization
 * modules, and any other patched receipt content.
 */
async function _printByDomScan(store, props) {
    const el = await store.printer.renderer.toHtml(OrderReceipt, props);
    if (!el) return false;
    const lines = _domToLines(el);
    if (!lines.length) return false;
    return await _postJson(_hwUrl(store.config), {
        lines,
        char_size: store.config.receipt_char_size || 1,
        cut: true,
        open_cashdrawer: false,
    });
}

// ─── PosStore patches ─────────────────────────────────────────────────────────

patch(PosStore.prototype, {
    /**
     * Intercept standard receipt printing.
     * Renders the real OWL receipt component, scans its DOM, and sends the
     * extracted lines as JSON.  Falls back to the standard PNG path on any
     * error so the user never loses a receipt.
     */
    async printReceipt(options = {}) {
        const order = options.order || this.get_order();
        if (this.config.use_json_printer && order) {
            const ok = await _printByDomScan(this, {
                data: this.orderExportForPrinting(order),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: options.basic || false,
            });
            if (ok) {
                order.nb_print = (order.nb_print || 0) + 1;
                if (typeof order.id === "number") {
                    await this.data.write("pos.order", [order.id], {
                        nb_print: order.nb_print,
                    });
                }
                return true;
            }
            console.warn("[pos_json_printer] DOM scan failed, falling back");
        }
        return await super.printReceipt(options);
    },
});

// ─── pos_indv_receipt integration ─────────────────────────────────────────────
// Only applied when pos_indv_receipt is installed (checked at load time).
// pos_indv_receipt loads first (alphabetical order in the asset bundle), so
// printIndividualPrepaidReceipt / printFullPrepaidReceipt already exist on the
// prototype by the time this module runs.

if (typeof PosStore.prototype.printIndividualPrepaidReceipt === "function") {
    patch(PosStore.prototype, {
        /**
         * One ticket per product unit.  The rendered DOM contains only the
         * selected product line — different content from the full receipt.
         */
        async printIndividualPrepaidReceipt({
            basic = false,
            order = this.get_order(),
            order_line = null,
            printBillActionTriggered = false,
        } = {}) {
            if (this.config.use_json_printer) {
                const ok = await _printByDomScan(this, {
                    data: this.orderExportForPrintingIndividualReceipt({
                        order,
                        order_line,
                    }),
                    formatCurrency: this.env.utils.formatCurrency,
                    basic_receipt: basic,
                });
                if (ok) {
                    if (!printBillActionTriggered) {
                        order.nb_print += 1;
                        if (typeof order.id === "number") {
                            await this.data.write("pos.order", [order.id], {
                                nb_print: order.nb_print,
                            });
                        }
                    }
                    return true;
                }
                console.warn(
                    "[pos_json_printer] Individual DOM scan failed, falling back"
                );
            }
            return await super.printIndividualPrepaidReceipt({
                basic,
                order,
                order_line,
                printBillActionTriggered,
            });
        },

        /**
         * Full prepaid receipt (customer or cashier copy).
         * pos_indv_receipt injects a "CUSTOMER RECEIPT" / "CASHIER RECEIPT"
         * banner into the DOM via receipt_header.xml xpath patches; the DOM
         * scan picks this up automatically without any special handling here.
         */
        async printFullPrepaidReceipt({
            basic = false,
            order = this.get_order(),
            order_lines = null,
            printCachierReceipt = false,
            printFullClientReceipt = false,
            printBillActionTriggered = false,
        } = {}) {
            if (this.config.use_json_printer) {
                const ok = await _printByDomScan(this, {
                    data: this.orderExportForPrintingFullPrepaidReceipt({
                        order,
                        order_lines,
                        printCachierReceipt,
                        printFullClientReceipt,
                    }),
                    formatCurrency: this.env.utils.formatCurrency,
                    basic_receipt: basic,
                });
                if (ok) {
                    if (!printBillActionTriggered) {
                        order.nb_print += 1;
                        if (typeof order.id === "number") {
                            await this.data.write("pos.order", [order.id], {
                                nb_print: order.nb_print,
                            });
                        }
                    }
                    return true;
                }
                console.warn(
                    "[pos_json_printer] Full prepaid DOM scan failed, falling back"
                );
            }
            return await super.printFullPrepaidReceipt({
                basic,
                order,
                order_lines,
                printCachierReceipt,
                printFullClientReceipt,
                printBillActionTriggered,
            });
        },
    });
}
