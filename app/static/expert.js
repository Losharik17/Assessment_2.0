$('#submit').addClass('form_button')
$('label[for=user_id]').addClass('form_label')
$('#user_id').addClass('form_input').attr('placeholder', " ")
$('#user_id').focus(function () {
    input('user_id', $('label[for=user_id]'))
})

function input(el, label) {
    $('#' + el).css({
        'border-bottom': '1px solid #1a73a8'
    })
    label.css({
        top: '-18px',
        'font-size': '12px',
        'color': '#999999'
    })
}