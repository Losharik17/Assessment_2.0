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
    foc(this, $('label[for=username]'))
}).blur(function () {
    blu(this, $('label[for=username]'))
})

$('#birthday').addClass('form_input')
$('#birthday').focus(function () {
    foc(this, $('label[for=birthday]'))
}).blur(function () {
    blu(this, $('label[for=birthday]'))
})

$('#team').addClass('form_input')
$('#team').focus(function () {
    foc(this, $('label[for=team]'))
}).blur(function () {
    blu(this, $('label[for=team]'))
})

$('#region').addClass('form_input')
$('#region').focus(function () {
    foc(this, $('label[for=region]'))
}).blur(function () {
    blu(this, $('label[for=region]'))
})

$('#weight').addClass('form_input')
$('#weight').focus(function () {
    foc(this, $('label[for=weight]'))
}).blur(function () {
    blu(this, $('label[for=weight]'))
})

$('#organization').addClass('form_input')
$('#organization').focus(function () {
    foc(this, $('label[for=organization]'))
}).blur(function () {
    blu(this, $('label[for=organization]'))
})


$('#password2').addClass('form_input')
$('#password2').focus(function () {
    foc(this, $('label[for=password2]'))
}).blur(function () {
    blu(this, $('label[for=password2]'))
})

$('#phone_number').focus(function () {
    $(this).css({
        'border-bottom': '1px solid #1a73a8'
    })
}).blur(function () {
    $(this).css({
        'border-bottom': '1px solid #cccccc'
    })
})

$('label[for=phone_number]').css({
    top: '-18px',
    'font-size': '12px',
})

$('#phone_number').inputmask("+7 (999) 999-9999",
    {clearMaskOnLostFocus : false});

function foc(el, label) {
    $(el).css({
        'border-bottom': '1px solid #1a73a8'
    })
    label.css({
        top: '-18px',
        'font-size': '12px',
    })
}

function blu(el, label) {
    $(el).css({
        'border-bottom': '1px solid #cccccc'
    })
    if ($(el).val() === '')
        label.css({
            top: 0,
            'font-size': '16px'
        })
}