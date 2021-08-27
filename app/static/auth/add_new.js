$('#submit').addClass('form_button')

$('#email').focus(function () {
    foc(this, $('label[for=email]'))
}).blur(function () {
    blu(this, $('label[for=email]'))
})

$('#birthday').focus(function () {
    foc(this, $('label[for=birthday]'))
}).blur(function () {
    blu(this, $('label[for=birthday]'))
})

$('#username').focus(function () {
    foc(this, $('label[for=username]'))
}).blur(function () {
    blu(this, $('label[for=username]'))
})


$('#team').focus(function () {
    foc(this, $('label[for=team]'))
}).blur(function () {
    blu(this, $('label[for=team]'))
})

$('#region').focus(function () {
    foc(this, $('label[for=region]'))
}).blur(function () {
    blu(this, $('label[for=region]'))
})



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