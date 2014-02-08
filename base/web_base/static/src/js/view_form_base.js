openerp.web_base = function(openerp) {
var QWeb = openerp.web.qweb,
      _t =  openerp.web._t,
     _lt = openerp.web._lt;
     
openerp.web.form.Field = openerp.web.form.Field.extend({

    is_dirty: function() {
      // DECODIO KGB START Save readony required dirty  
      //return this.dirty && !this.readonly;
        return this.dirty && ( !this.readonly || (this.required && this.readonly));
    }
});


openerp.web.FormView = openerp.web.FormView.extend({
    do_save: function(success, prepend_on_create) {
        var self = this;
        return this.mutating_mutex.exec(function() { return self.is_initialized.pipe(function() {
            try {
            var form_invalid = false,
                values = {},
                first_invalid_field = null;
            for (var f in self.fields) {
                f = self.fields[f];
                if (!f.is_valid()) {
                    form_invalid = true;
                    if (!first_invalid_field) {
                        first_invalid_field = f;
                    }
                } else if (f.name !== 'id' && !f.readonly && (!self.datarecord.id || f.is_dirty())) {
                    // Special case 'id' field, do not save this field
                    // on 'create' : save all non readonly fields
                    // on 'edit' : save non readonly modified fields
                    values[f.name] = f.get_value();
                // DECODIO KGB START Save readony required dirty    
                } else if (f.name !== 'id' && f.readonly && f.required && f.is_dirty())  { 
                    values[f.name] = f.get_value();
                // DECODIO KGB END Save readony required dirty    
                }
                f.update_dom(true);
            }
            if (form_invalid) {
                first_invalid_field.focus();
                self.on_invalid();
                return $.Deferred().reject();
            } else {
                var save_deferral;
                if (!self.datarecord.id) {
                    //console.log("FormView(", self, ") : About to create", values);
                    save_deferral = self.dataset.create(values).pipe(function(r) {
                        return self.on_created(r, undefined, prepend_on_create);
                    }, null);
                } else if (_.isEmpty(values) && ! self.force_dirty) {
                    //console.log("FormView(", self, ") : Nothing to save");
                    save_deferral = $.Deferred().resolve({}).promise();
                } else {
                    self.force_dirty = false;
                    //console.log("FormView(", self, ") : About to save", values);
                    save_deferral = self.dataset.write(self.datarecord.id, values, {}).pipe(function(r) {
                        return self.on_saved(r);
                    }, null);
                }
                return save_deferral.then(success);
            }
            } catch (e) {
                console.error(e);
                return $.Deferred().reject();
            }
        });});
    },
    
});

openerp.web.form.Widget = openerp.web.form.Widget.extend({

    process_modifiers: function() {
        var compute_domain = openerp.web.form.compute_domain;
        /** DECODIO START KGB allow parent.field in attribs */
        // trying to find (guesswork) parent fields values
        var parent_fields; 
        var i=0;
        tmp_parent = this.view.widget_parent;
        while (i<10)  {
            if (tmp_parent && tmp_parent.model){
                if (tmp_parent.model !== this.view.model) {
                    parent_fields = tmp_parent.fields;
                    break;
                }
            }
            if (tmp_parent.widget_parent){
                tmp_parent = tmp_parent.widget_parent;
            } else {
                parent_fields = false;
                break;
            }
            i++;
        }
        for (var a in this.modifiers) {
          //this[a] = compute_domain(this.modifiers[a], this.view.fields); 
            this[a] = compute_domain(this.modifiers[a], this.view.fields, parent_fields);
        }
    }
});


/** DECODIO KGB allow parent.field in attribs */
openerp.web.form.compute_domain = function(expr, fields, parent_fields) {
    var stack = [];
    for (var i = expr.length - 1; i >= 0; i--) {
        var ex = expr[i];
        if (ex.length == 1) {
            var top = stack.pop();
            switch (ex) {
                case '|':
                    stack.push(stack.pop() || top);
                    continue;
                case '&':
                    stack.push(stack.pop() && top);
                    continue;
                case '!':
                    stack.push(!top);
                    continue;
                default:
                    throw new Error(_.str.sprintf(
                        _t("Unknown operator %s in domain %s"),
                        ex, JSON.stringify(expr)));
            }
        }

        var field = fields[ex[0]];
        /** DECODIO START KGB allow parent.field in attribs */
        var parent_field;
        var splitted;
        if (parent_fields && !field ) {
            splitted = ex[0].split('.');
            if (splitted.length > 1 && splitted[0] === "parent") {
                parent_field = parent_fields[splitted[1]]; 
            }
        }
        if ((!field) && (!parent_field)) {
            throw new Error(_.str.sprintf(
                _t("Unknown field %s in domain %s"),
                ex[0], JSON.stringify(expr)));
        }
        if (field) {
            var field_value = field.get_value ? fields[ex[0]].get_value() : fields[ex[0]].value;
        }
        if (parent_field) {
            var field_value = parent_field.get_value ? parent_fields[splitted[1]].get_value() : parent_fields[splitted[1]].value;
        }        
        /** DECODIO END KGB allow parent.field in attribs */
        var op = ex[1];
        var val = ex[2];

        switch (op.toLowerCase()) {
            case '=':
            case '==':
                stack.push(field_value == val);
                break;
            case '!=':
            case '<>':
                stack.push(field_value != val);
                break;
            case '<':
                stack.push(field_value < val);
                break;
            case '>':
                stack.push(field_value > val);
                break;
            case '<=':
                stack.push(field_value <= val);
                break;
            case '>=':
                stack.push(field_value >= val);
                break;
            case 'in':
                if (!_.isArray(val)) val = [val];
                stack.push(_(val).contains(field_value));
                break;
            case 'not in':
                if (!_.isArray(val)) val = [val];
                stack.push(!_(val).contains(field_value));
                break;
            default:
                console.warn(
                    _t("Unsupported operator %s in domain %s"),
                    op, JSON.stringify(expr));
        }
    }
    return _.all(stack, _.identity);
};
};