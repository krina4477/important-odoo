odoo.define('cr_medical_base.models', function (require){
    "use strict";

    var models = require('point_of_sale.models');

    models.load_models({
        model: 'pharmacy.prescription',
        fields: ['opd_id','ref_opd_id','indication_id', 'medicine_id','dose','total_tablets','medicine_days'],
        loaded: function (self, medicine_id) {
          self.medicine_id =medicine_id;
        }
 });
});