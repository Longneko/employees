// const ERR_GENERAL_ID is defined in the template
// const FORM_DELETE_ID is defined in the template
// const API_URL_FLASH is defined in the template

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
            success: function(data) {
                $.ajax({
                    type: 'POST',
                    url: API_URL_FLASH,
                    data: {msg: 'Employee deleted successfully!', category: 'success'},
                    complete: function() { location.reload(); $(document).scrollTop(0); },
                });
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
});
