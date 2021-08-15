$('#submit').addClass('form_button')
$('label[for=username]').addClass('form_label')
$('label[for=email]').addClass('form_label')
$('label[for=password]').addClass('form_label')
$('label[for=password2]').addClass('form_label')
$('label[for=password2]').addClass('form_label')
$('#email').addClass('form_input')

$('#email').focus(function () {
    foc(this, $('label[for=email]'))
}).blur(function () {
    blu(this, $('label[for=email]'))
})

$('#password').addClass('form_input')
$('#password').focus(function () {
    foc(this, $('label[for=password]'))
}).blur(function () {
    blu(this, $('label[for=password]'))
})

$('#username').addClass('form_input')
$('#username').focus(function () {
    foc('username', $('label[for=username]'))
}).blur(function () {
    blu(this, $('label[for=username]'))
})

$('#password2').addClass('form_input')
$('#password2').focus(function () {
    foc(this, $('label[for=password2]'))
}).blur(function () {
    blu(this, $('label[for=password2]'))
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