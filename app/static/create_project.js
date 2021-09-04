function activate_buttons(index) {
    // делает кнопки + и - активными

    $(`#minus${index}`).click(function () {
        $(this).css("opacity", "0.5")
        setTimeout(() => { $(this).css("opacity", "1") }, 125)
        let value = (Math.round(($(`#weight${index}`).attr('value') - 0.1) * 10) / 10)
            .toFixed(1)

        if (value > 0)
            $(`#weight${index}`).attr('value', value)
    })

    $(`#plus${index}`).click(function () {
        $(this).css("opacity", "0.5")
        setTimeout(() => { $(this).css("opacity", "1") }, 125)
        let value = (Math.round((+$(`#weight${index}`).attr('value') + 0.1) * 10) / 10)
            .toFixed(1)

        if (value <= 2)
            $(`#weight${index}`).attr('value', value)
    })


    $("[id^='weight']").css({cursor: 'default'})

}


activate_buttons(0)

$('#button_add').click(function () {
    addField(0)
})

$('#button_delete').click(function () {
    deleteField(0)
})

function deleteField(number) {
    if (number === 0)
        return alert('Извините. У вас должен быть хотя бы один критерий')

    $('#quantity').val(+$('#quantity').val() - 1)
    $(`#parameter${number}`).slideUp(250)
    setTimeout(() => { $(`#parameter${number}`).remove() }, 250)

    $('#button_delete').unbind()
    $('#button_delete').click(function () {
        deleteField(number - 1)
    })

    $('#button_add').unbind()
    $('#button_add').click(function () {
        addField(number - 1)
    })
}

function addField(number) {
    if (number === 9)
        return alert('Извините. Вы не можете создать более 10 критериев')

    $('#quantity').val(+$('#quantity').val() + 1)
    $(`#button_add`).before(`<div id="parameter${number + 1}">
                                 <div class="block_4">
                                     <label for="name${number + 1}"></label>
                                     <input id="name${number + 1}" name="name${number + 1}"
                                     size="16" type="text" value="" class="input_text_2" 
                                     placeholder="Критерий ${number + 2}"/>
                                     <div class="block_5">
                                     <input type="button" id="minus${number + 1}" 
                                     class="button" value="-">
                                     <input type="number" id="weight${number + 1}" 
                                     value="1.0" step="0.1" max="2.0" min="0.1" class="crit"/>
                                     <input type="button"  id="plus${number + 1}" class="button" 
                                     value="+">
                                     </div>
                                 </div>
                             </div>`)
    $(`#parameter${number + 1}`).slideUp(0)
    $(`#parameter${number + 1}`).slideDown(250)

    activate_buttons(number + 1)
    $('#button_add').unbind()
    $('#button_add').click(function () {
        addField(number + 1)
    })
    $('#button_delete').unbind()
    $('#button_delete').click(function () {
        deleteField(number + 1)
    })
}

let inputs = document.querySelectorAll('.input__file');
Array.prototype.forEach.call(inputs, function (input) {
    let label = input.nextElementSibling,
        labelVal = label.querySelector('.input__file-button-text').innerText;

    input.addEventListener('change', function (e) {
        let countFiles = '';
        if (this.files && this.files.length >= 1)
            countFiles = this.files.length;

        if (countFiles)
            label.querySelector('.input__file-button-text').innerText = 'Выбрано файлов: ' + countFiles;
        else
            label.querySelector('.input__file-button-text').innerText = labelVal;
    });
});

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
    clearMaskOnLostFocus: false,
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
                {validator: "[0-9]", cardinality: 1},
                {validator: "[0-9][0-9]", cardinality: 2},
            ]
        },
        "M": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp2 = new RegExp("0[1-9]|1[0-2]");
                return valExp2.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                {validator: "[01]", cardinality: 1},
                {validator: "0[1-9]", cardinality: 2},
                {validator: "1[1-2]", cardinality: 2},
            ]
        },
        "D": {
            validator: function (chrs, buffer, pos, strict, opts) {
                let valExp3 = new RegExp("0[1-9]|[12][0-9]|3[01]");
                return valExp3.test(chrs);
            },
            cardinality: 2,
            prevalidator: [
                {validator: "[0-3]", cardinality: 1},
                {validator: "0[1-9]", cardinality: 2},
                {validator: "(1|2)[0-9]", cardinality: 2},
                {validator: "3[0-1]", cardinality: 2},
            ]
        },
    }
})


$('label[for=start]').css({
    top: '-18px',
    'font-size': '14px',
})

$('label[for=end]').css({
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

function waiting() {
    $('body').append('<div class="preloader">' +
        '<div class="preloader-text">' +
        '<h4>Создание проекта может занять несколько минут</h4>' +
        '</div>' +
        '<div class="preloader-5"></div>' +
        '</div>')
}