$('#submit').addClass('form_button')
$('label[for=username]').addClass('form_label')
$('label[for=email]').addClass('form_label')
$('label[for=password]').addClass('form_label')
$('label[for=password2]').addClass('form_label')
$('label[for=password2]').addClass('form_label')
$('#email').addClass('form_input')

$('#email').focus(function () {
    input('email', $('label[for=email]'))
})

$('#password').addClass('form_input')
$('#password').focus(function () {
    input('password', $('label[for=password]'))
})

$('#username').addClass('form_input')
$('#username').focus(function () {
    input('username', $('label[for=username]'))
})

$('#password2').addClass('form_input')
$('#password2').focus(function () {
    input('password2', $('label[for=password2]'))
})

function not_focus (el, label) {
    $('#' + el).css({
        'border-bottom': '1px solid #e0e0e0'
    })
    label.css({
        top: '0px',
        'font-size': '16px',
        'color': '#9e9e9e'
    })
}


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