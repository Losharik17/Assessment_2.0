$("#start").inputmask({
    clearMaskOnLostFocus : false,
    mask: "D.M.Y",
    placeholder: "дд.мм.гг",
    definitions: {
        "Y": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp = new RegExp("[0-9][0-9]");
                return valExp.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-9]", cardinality: 1 },
                { validator: "[0-9][0-9]", cardinality: 2 },
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

$("#end").inputmask({
    clearMaskOnLostFocus : false,
    mask: "D.M.Y",
    placeholder: "дд.мм.гг",
    definitions: {
        "Y": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp = new RegExp("[0-9][0-9]");
                return valExp.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                { validator: "[0-9]", cardinality: 1 },
                { validator: "[0-9][0-9]", cardinality: 2 },
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


$('label[for=start]').css({
    top: '-18px',
    'font-size': '14px',
})

$('label[for=end]').css({
    top: '-18px',
    'font-size': '14px',
})

$('label[for=name]').css({
    top: '-18px',
    'font-size': '14px',
})


$('#start').focus(function () {
    $(this).css({
        'border-bottom': '1px solid #1a73a8'
    })
}).blur(function () {
    $(this).css({
        'border-bottom': '1px solid #cccccc'
    })
})

$('#end').focus(function () {
    $(this).css({
        'border-bottom': '1px solid #1a73a8'
    })
}).blur(function () {
    $(this).css({
        'border-bottom': '1px solid #cccccc'
    })
})

$('#name').focus(function () {
    $(this).css({
        'border-bottom': '1px solid #1a73a8'
    })
}).blur(function () {
    $(this).css({
        'border-bottom': '1px solid #cccccc'
    })
})

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


function delete_project(number) {

    if (confirm('Вы уверены?') && confirm('Все данные о проекте будут удалены.'))
        $.post('/delete_project', {
            number: number,
        }).done(function (response) {
            ('body').append(
                `<div class="message success"><h4>Проект удалён</h4></div>`)
            setTimeout( ()=> {
                $('.message').css({transition: 'all 0.3s ease', opacity: 0})}, 2000)
            setTimeout( ()=> {
                $('.message').css({display: 'none'})}, 2300)
        }).fail(function () {
            alert('Error AJAX request')
        })


}