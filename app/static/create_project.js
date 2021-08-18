function activate_buttons(index) {
    // делает кнопки + и - активными

    $(`#minus${index}`).click(function () {
        let value = (Math.round(($(`#weight${index}`).attr('value') - 0.1) * 10) / 10)
            .toFixed(1)

        if (value > 0)
            $(`#weight${index}`).attr('value', value)
    })

    $(`#plus${index}`).click(function () {

        let value = (Math.round((+$(`#weight${index}`).attr('value') + 0.1) * 10) / 10)
            .toFixed(1)

        if (value <= 2)
            $(`#weight${index}`).attr('value', value)
    })
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

    $(`#parameter${number}`).remove()

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

$('[id^="name"]').each(function (index, element) {

    $(element).focus(function () {

        $(element).addClass('placeholder_activate')

    })
})

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
