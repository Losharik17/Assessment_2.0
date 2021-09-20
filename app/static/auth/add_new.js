$('#submit').addClass('form_button')

$('#email').focus(function () {
    foc(this, $('label[for=email]'))
}).blur(function () {
    blu(this, $('label[for=email]'))
})

$('#birthday').focus(function () {
    $(this).css({
        'border-bottom': '1px solid #1a73a8'
    })
}).blur(function () {
    $(this).css({
        'border-bottom': '1px solid #cccccc'
    })
})

$('label[for=birthday]').css({
    top: '-18px',
    'font-size': '12px',
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

$("#birthday").inputmask({
    clearMaskOnLostFocus : false,
    mask: "D.M.Y",
    placeholder: "дд.мм.гггг",
    definitions: {
        "Y": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp = new RegExp("1[9][0-9][0-9]|2[0][0-9][0-9]");
                return valExp.test(chrs);
            },
            cardinality: 4,
            prevalidator: [
                { validator: "[12]", cardinality: 1 },
                { validator: "(1|2)[09]", cardinality: 2 },
                { validator: "(1|2)(0|9)[0-9]", cardinality: 3 },
                { validator: "(1|2)(0|9)[0-9][0-9]", cardinality: 4 },
            ]
        },
        "M": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp2 = new RegExp("0[1-9]|1[0-2]");
                return valExp2.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[01]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "1[1-2]", cardinality: 2 },
            ]
        },
        "D": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp3 = new RegExp("0[1-9]|[12][0-9]|3[01]");
                return valExp3.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-3]", cardinality: 1 },
                { validator: "0[1-9]", cardinality: 2 },
                { validator: "(1|2)[0-9]", cardinality: 2 },
                { validator: "3[0-1]", cardinality: 2 },
            ]
        },
    }
});

let inputs = document.querySelectorAll('.input__file');
Array.prototype.forEach.call(inputs, function (input) {
    let label = input.nextElementSibling,
        labelVal = label.querySelector('.input__file_button_text_2').innerText;

    input.addEventListener('change', function (e) {
        let countFiles = '';
        if (this.files && this.files.length >= 1)
            countFiles = this.files.length;

        if (countFiles)
            label.querySelector('.input__file_button_text_2').innerText = 'Выбрано файлов: ' + countFiles;
        else
            label.querySelector('.input__file_button_text_2').innerText = labelVal;
    });
});

