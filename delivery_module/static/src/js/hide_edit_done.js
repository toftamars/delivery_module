odoo.define('delivery_module.hide_edit_done', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const patch = require('web.utils').patch;

    patch(FormController.prototype, 'delivery_module_hide_edit_button_done', {
        updateButtons() {
            this._super.apply(this, arguments);
            try {
                if (this.model && this.modelName === 'delivery.document' && this.renderer && this.renderer.state && this.renderer.state.data) {
                    const state = this.renderer.state.data.state;
                    if (state === 'done' && this.$buttons) {
                        const $edit = this.$buttons.find('button.o_form_button_edit');
                        $edit && $edit.hide();
                    }
                }
            } catch (e) {
                // ignore
            }
        },
    });
});
