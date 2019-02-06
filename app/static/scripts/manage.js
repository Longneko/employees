// const ERR_GENERAL_ID is defined in the template
// const FORM_DELETE_ID is defined in the template
// const MODAL_DELETE_ID is defined in the template
// const API_URL_FLASH is defined in the template
// const EMPLOYEE_URL is defined in the template

function show_modal_delete(employee_id, replacement_id=null) {
    var data = {'id': employee_id}

    clear_errors(get_form_fields(FORM_DELETE_ID));
    form_set_defaults(FORM_DELETE_ID);

    if ( replacement_id ) {
        data['replacement_id'] = replacement_id;
    }
    form_populate(FORM_DELETE_ID, data);
}


$(document).ready(function(){
    $('#form-delete').submit(function(e) {
        var form = $(this);
        var url = form.attr('action');
        var form_fields = get_form_fields(form.attr('id'));
        
        clear_errors(form_fields);

        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            // success: function(data) {
            //     $.ajax({
            //         type: 'POST',
            //         url: API_URL_FLASH,
            //         data: {msg: 'Employee deleted successfully!', category: 'success'},
            //         complete: function() { location.reload(); $(document).scrollTop(0); },
            //     });
            // },
            success: function() {
                employee_table.runSearch();
                $('#' + MODAL_DELETE_ID).modal('hide');
            },
            error: function(data, textStatus, jqXHR) {
                var errors =  data['responseJSON']['errors'];
                if ( !errors ) {
                    errors = {ERR_GENERAL_ID: [ERR_GENERAL_MSG]};
                }
                show_errors(errors, err_general_id=ERR_GENERAL_ID);                
            }
        });

        e.preventDefault();
    });


    // Vue components:

    // Vue fitlers:
    Vue.filter('capitalize', function (value) {
        if (!value) return ''
        value = value.toString()
        return value.charAt(0).toUpperCase() + value.slice(1)
    })
    Vue.filter('replace', function (str, old, replacement) {
        return str.replace(new RegExp(old, 'g'), replacement)
    })

    // Employee table grid component
    Vue.component('grid-sortable', {
      template: '#grid-sortable-template',
      props: {
        data: Array,
        columns: Array,
      },
      data: function () {
        var sortOrders = {}
        this.columns.forEach(function (key) {
          sortOrders[key] = 1
        })
        return {
          sortKey: '',
          sortOrders: sortOrders
        }
      },
      computed: {
        sortedData: function () {
          var sortKey = this.sortKey
          var order = this.sortOrders[sortKey] || 1
          var data = this.data
          if (sortKey) {
            data = data.slice().sort(function (a, b) {
              a = a[sortKey]
              b = b[sortKey]
              return (a === b ? 0 : a > b ? 1 : -1) * order
            })
          }
          return data
        }
      },
      methods: {
        sortBy: function (key) {
          this.sortKey = key
          this.sortOrders[key] = this.sortOrders[key] * -1
        }
      }
    })

    // Employee table vue app
    var employee_table = new Vue({
      el: '#employee_table',
      data: {
        searchQuery: {},
        gridColumns: [{
          name:'id',
          searchable: true
        }, {
          name:'full_name',
          searchable: true
        }, {
          name:'position',
          searchable: true
        }, {
          name:'salary',
          searchable: true
        }, {
          name:'hire_date',
          searchable: true
        }, {
          name: 'supervisor',
          searchable: false
        }],
        gridData: []
      },
      methods: {
        runSearch() {
          var that = this;
          var request = {};
          for ( key of Object.keys(this.searchQuery) ) {
            request['_' + key] = that.searchQuery[key];
          }
          $.getJSON({
            url: EMPLOYEE_URL,
            data: request,
            success: function(dataJSON) {
              that.gridData = dataJSON;
            }
          });
        },
      },
      computed: {
        searchFields: function() {
          return this.gridColumns.filter(x => x['searchable']).map(x => x['name'])
        }
      }
    })

});
