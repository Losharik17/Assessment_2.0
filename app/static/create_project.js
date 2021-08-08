function activate_buttons(index) {
    // делает кнопки + и - активными

    $(`#minus${index}`).click(function () {
        let value = Math.round(($(`#weight${index}`).attr('value') - 0.1) * 10) / 10

        if (value > 0)
            $(`#weight${index}`).attr('value', value)
    })

    $(`#plus${index}`).click(function () {

        let value = Math.round((+$(`#weight${index}`).attr('value') + 0.1) * 10) / 10

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
    console.log($(`#parameter${number}`))
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
    $(`#button_add`).before(`<div id="parameter${number + 1}"><label 
                                for="name${number + 1}"></label>
                                <input id="name${number + 1}" name="name${number + 1}"
                                size="16" type="text" value="" class="form_input" 
                                placeholder="Критерий ${number + 2}"/>
                                <span id="minus${number + 1}">-</span>
                                <input type="number" id="weight${number + 1}" 
                                value="1.0" step="0.1" max="2.0" min="0.1" />
                                <span id="plus${number + 1}">+</span></div>`)

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