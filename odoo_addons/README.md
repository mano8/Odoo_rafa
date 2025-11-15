# 🧩 Odoo Add-ons

This directory contains optional or custom modules that extend the functionality of the **Odoo 18.0** instance provided by the [Odoo Local POS Stack](../README.md).

---

## 🧾 POS Individual Receipt (`pos_indv_receipt`)

### Overview

**POS Indv Receipt** enhances Odoo’s Point of Sale by allowing users to **print one ticket per unit** directly from the receipt screen.

This feature is ideal for **bars, events, and venues** where individual items (e.g. drinks, food portions, or entry tokens) must be issued as separate vouchers or receipts.

---

### ✨ Key Features

* 🖨️ Adds a **“Print Product Tickets”** button to the POS receipt screen.
* 🧾 Opens a popup to **select products** from the current order.
* 🔁 Prints **one ticket per quantity unit** for each selected product.
* 🧱 Reuses the **standard POS receipt header and footer** for consistent branding.
* 🪄 Works seamlessly with Odoo’s default POS printing mechanism.

---

### ⚙️ Installation

1. Ensure this folder is mounted inside your Odoo container (for example):

    ```bash
    ./odoo_addons/pos_indv_receipt/
    ```

2. Restart Odoo:

   ```bash
   docker compose restart fiesta_odoo
   ```

3. Log in to Odoo → **Apps** → Update Apps List → Search for **POS Individual Receipt** → Install.
4. Once installed, open the **Point of Sale** app → complete an order → click **“Print Product Tickets”** on the receipt screen.

---

### 🧰 Updating the Module

Odoo in this stack automatically updates `pos_indv_receipt` at startup (`-u pos_indv_receipt`).
To force a manual update inside a running container:

```bash
docker exec -it fiesta_odoo odoo -u pos_indv_receipt -d odoo
```

---

### 💾 Export / Package as ZIP

You can easily package the module for backup or deployment elsewhere:

```bash
cd /opt/Odoo_rafa/odoo_addons/
zip -r /opt/Odoo_rafa/pos_indv_receipt_v18.0.1.zip pos_indv_receipt
```

This creates a distributable file:

```bash
/opt/Odoo_rafa/pos_indv_receipt_v18.0.1.zip
```

> 💡 Use semantic versioning (e.g. `v18.0.1`) when tagging releases for clarity.

---

### 🧱 File Structure

```bash
pos_indv_receipt/
├── __manifest__.py         # Module metadata
├── models/                 # Python models (if any)
├── static/
│   ├── src/js/             # Frontend logic (POS screen actions)
│   └── xml/                # XML templates for UI
├── views/                  # Receipt view / popup definitions
└── README.md               # Module description (this file)
```

---

### 🧑‍💻 Developer Notes

* Compatible with **Odoo 18.0+**.
* Built and maintained by **Eli Serra**.
* Designed to integrate seamlessly with **Odoo Local POS Stack**.
* Tested with **ESC/POS** printers through the `hw_proxy` integration.

---

### 📜 License

Licensed under the **Apache License 2.0**.
See the main repository’s [LICENSE](../LICENSE) file for details.
