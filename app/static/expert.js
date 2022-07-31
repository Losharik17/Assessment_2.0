$('#submit').addClass('form_button')
$('label[for=user_id]').addClass('form_label')
$('#user_id').addClass('form_input').attr('placeholder', " ").attr('autocomplete', 'off')
$('#user_id').focus(function () {
    foc(this, $('label[for=user_id]'))
}).blur(function () {
    blu(this, $('label[for=user_id]'))
})


function foc(el, label) {
    $(el).css({
        'border-bottom': '1px solid #1a73a8'
    })
    label.css({
        top: '-18px',
        'font-size': '12px',
        'color': '#999999'
    })
}

function blu(el, label) {
    $(el).css({
        'border-bottom': '1px solid #e0e0e0'
    })
    if ($(el).val() === '')
        label.css({
            top: 0,
            color: '#9e9e9e',
            'font-size': '16px'
        })
}