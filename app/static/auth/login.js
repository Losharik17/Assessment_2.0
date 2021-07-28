$('#submit').addClass('form_button')
$('label[for=email]').addClass('form_label')
$('label[for=password]').addClass('form_label')
$('#email').addClass('form_input').attr('placeholder', " ")
$('#email').focus(function () {
    input('email', $('label[for=email]'))
})
$('#password').addClass('form_input').attr('placeholder', " ")
$('#password').focus(function () {
    input('password', $('label[for=password]'))
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