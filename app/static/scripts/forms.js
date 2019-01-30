const ERR_GENERAL_MSG = 'Something went wrong, please try again later.';
const CSRF_TOKEN_NAME = 'csrf_token';

// Set form element to default state based on its type and data-default if provided
function field_set_default(element) {
    var type;
    switch($(element).prop('nodeName')) {
        case 'SELECT':
            type = 'select';
            break
        case 'TEXTAREA':
            type = 'textarea';
            break
        case 'IMG':
            type = 'img';
            break
        case 'INPUT':
            type = $(element).attr('type');
            break
        default:
            return false;
    }

    var default_val;
    try {
        default_val = $(element).data('default');
    } catch (err) {
        default_val = '';
    }

    if ( ['select', 'textarea', 'text', 'number', 'email', 'url', 'file'].includes(type) ) {
        $(element).val(default_val);
    }
    if ( type == 'checkbox' ) {
        $(element).prop('checked', Boolean(default_val));
    }
    if ( type == 'img' ) {
        if ( default_val ) {
            $(element).prop('src', default_val);
        }
    }
}



// Return input decendants of the specified form and elements with 'form' atrribute poinitng to it
function get_form_fields(form_id) {
    return $('#' + form_id + ' input, input[form=' + form_id + ']');
}

// Sets all of the form's input fields to their defaults, except for those in the exclusion lists 
// and CSRF token(s)
function form_set_defaults(form_id, exclude=[], exclude_ids=[]) {
    var fields = get_form_fields(form_id);
    exclude_ids.push('csrf_token')
    for ( var field of fields ) {
        var id = $(field).attr('id');
        var name = $(field).attr('name');
        if ( !exclude.includes(field) && !exclude_ids.includes(id) && !name.includes(CSRF_TOKEN_NAME) ) {
            field_set_default(field);
        }
    }
}

// populates form fields based on the 'data' object where key value pairs contain name and value
// atributes of the fields respectively
function form_populate(form_id, data) {
    var form_fields = get_form_fields(form_id);
    for ( var key in data ) {
        $(form_fields).filter('[name=' + key + ']').val(data[key]);
    }
}

// Shows form validation errors and errors caused by exceptions.
// errors obj is a dict, where key is respective field_id and value is a list of error strings
// all errors bound to hidden or unfound fields will display a single general error
function show_errors(errors, err_general_id=null, err_general_msg=ERR_GENERAL_MSG) {
    for ( var field_id in errors ) {
        var err_node = $('.errors[for=' + field_id + ']');
        if ( err_node.length ) {
            for ( var err_text of errors[field_id] ) {
                $(err_node).append('<span>[' + err_text +']</span>');
            }
        } else if ( err_general_id ) {
            // Show general error message for errors on hidden fields
            err_node = $('.errors[for=' + err_general_id + ']');
            $(err_node).html('<span>[' + err_general_msg +']</span>');
        }
    }
}

function clear_errors(fields) {
    for ( var field of fields ) {
        var err_node = $('.errors[for=' + $(field).attr('id') + ']');
        if ( err_node ) {
            $(err_node).html('');
        }
    }
}
