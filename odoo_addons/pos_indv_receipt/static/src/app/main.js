/** @odoo-module **/

// This file can be a central point for loading JS files in a specific order
// or for any initial setup if required by the module.
// However, with OWL components often registering themselves (as ProductSelectionPopup does),
// and patches being applied when their files are loaded, this file might be minimal or unnecessary.

console.log("pos_indv_receipt main.js loaded.");

// Example: If you had other components or utilities to explicitly register or initialize:
// import { MyOtherComponent } from "./components/my_other_component";
// import { MyUtility } from "./utils/my_utility";
// Registries.Component.add(MyOtherComponent);
// MyUtility.initialize();