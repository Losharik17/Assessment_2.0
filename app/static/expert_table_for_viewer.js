let limit = 20

sort.sort_up = false
sort.current_parameter = 'user_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

edit_grade.old_value = Array()
edit_data.old_value = Array()

document.addEventListener('click', function (event) {

    if (event.target.tagName !== 'INPUT' && event.target.id !== 'data_table' &&
        event.target.id !== 'edit_data' && $('#edit_data').html() === 'Сохранить изменения') {

        $('#data_table tr').each(function (index, element) {
            if (index !== 3 && index !== 0) {
                let td = $(this).children('td').children('span')
                td.html(`${edit_data.old_value[index - 1]}`)
                $('#edit_data').html('Редактировать данные')
            }
        })
    }
})

function edit_data(expert_id) {
    if ($('#edit_data').html() !== 'Сохранить изменения') {
        let width = $("#edit_data").outerWidth()
        $('#edit_data').html('Сохранить изменения').css({width: width, 'text-align': 'center'});
        edit_data.old_value = Array()

        $('#edit_data').after('<div class="input__wrapper">\n' +
            '                        <input name="logo" type="file" id="input__file" class="input input__file">\n' +
            '                        <label for="input__file" class="input__file-button_2">\n' +
            '                            <span class="input__file-button-text_2">Изменить Фото Профиля</span>\n' +
            '                        </label>\n' +
            '                    </div>')
        $('#photo').slideUp(0).slideDown(300).attr('file', '1')
        $('#photo').on('change', function () {
            $('#photo').attr('file', $('#photo').attr('file') * -1)
        })

        $('#data_table tr').each(function (index, element) {
            if (index !== 3 && index !== 0) {
                let td = $(this).children('td').children('span')
                let value = td.html()
                edit_data.old_value.push(value)
                if (index !== 2)
                    td.html(`<input id="d${index}" onchange="
                                        document.getElementById(this.id).setAttribute('value', this.value)" 
                                        class="form" type="text" value="${value}">`)
                else
                    td.html(`<input id="d${index}" min="0.1" max="2.0" step="0.1" onchange="
                                        document.getElementById(this.id).setAttribute('value', this.value)" 
                                        class="form" type="number" value="${value}">`)
            }
        })
    }
    else {
        let data = Array()
        $('#edit_data').html('Редактировать данные')

        $('#data_table tr').each(function (index, element) {
            if (index !== 3 && index !== 0) {
                let td = $(this).children('td').children('span').children('input').val()
                data.push(td)
            }
        })

        $.post('/save_expert_data', {
            data: JSON.stringify(data),
            expert_id: expert_id
        }).done(function (response) {
            $('#data_table tr').each(function (index, element) {
                if (index !== 3 && index !== 0) {
                    let td = $(this).children('td').children('span')
                    td.html(`${td.children('input').val()}`)
                    $('#edit_data').html('Редактировать данные')
                }
            })

            $('body').append(
                `<div class="message success"><h4>Изменения сохранены</h4></div>`)
            setTimeout( ()=> {
                $('.message').css({transition: 'all 0.3s ease', opacity: 0})}, 2000)
            setTimeout( ()=> {
                $('.message').css({display: 'none'})}, 2300)

        }).fail(function () {
            alert("Error AJAX request")
            $('#data_table tr').each(function (index, element) {
                if (index !== 3 && index !== 0) {
                    let td = $(this).children('td').children('span')
                    td.html(`${edit_data.old_value[index - 1]}`)
                    $('#edit_data').html('Редактировать данные')
                }
            })
        })

        if ($('#photo').attr('file') === '-1')
            $('#submit').trigger('click')

        $('#photo').slideUp(300)
        setTimeout( () => { $('#photo').remove() }, 300)

    }
}

function delete_user(id, project_id) {
    if (confirm(`Удадить пользователя с ID ${project_id}?`))
        $.post('/delete_user', {
            role: 'expert',
            id: id
        }).done(function (response) {
            alert('Пользователь удалён')
        }).fail(function () {
            alert('Error AJAX request')
        })
}


function show_more(new_field, expert_id) {

    limit += new_field

    $.post('/show_more_grades_for_expert', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        expert_id: expert_id
    }).done(function (response) {

        $("#tbody").html('')
        let grades = JSON.parse(response['grades'])
        let quantity = grades.length

        if (limit > quantity) {
            quantity < 15 ? limit = 15 : limit = quantity
            $('body').append(
                `<div class="message warning"><h4>
                В таблице присутствуют все оценки эксперта</h4></div>`)
            setTimeout( ()=> {
                $('.message').css({transition: 'all 0.3s ease', opacity: 0})}, 4000)
            setTimeout( ()=> {
                $('.message').css({display: 'none'})}, 4100)
            $('#show_more').css('display', 'none')
            $('#show_all').css('display', 'none')
        }
        else {
            $('#show_more').css('display', 'inline-block')
            $('#show_all').css('display', 'inline-block')
        }

        for (let i = 0; i < quantity; i++) {

            $("#tbody").append(`<tr class="th_clean" id="number_str${i}"></tr>`)

            if (grades[i]['user_id'] === 'None')
                $(`#number_str${i}`).append(`<td id="user_id${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="user_id${i}">${grades[i]['user_id']}</td>`)

            if (grades[i]['date'] === 'None')
                $(`#number_str${i}`).append(`<td id="date${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="date${i}">${grades[i]['date']}</td>`)

            for (let j = 0; j < 15; j++) {
                if (grades[i][`parameter_${j}`]) {
                    if (grades[i][`parameter_${j}`] === '0')
                        $(`#number_str${i}`).append(`<td id="parameter_${j}${i}">–</td>`)
                    else
                        $(`#number_str${i}`).append(`<td id="parameter_${j}${i}">${grades[i][`parameter_${j}`]}</td>`)
                }
            }
            if (grades[i]['comment'] === 'None' || grades[i]['comment'] === '')
                $(`#number_str${i}`).append(`<td id="comment${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="comment${i}">${grades[i]['comment']}</td>`)
        }
        delete_buttons()
        buttons(limit)
    }).fail(function () {
        alert('Error AJAX request')
    })
}

function sort(parameter, expert_id) {

    if (sort.current_parameter === parameter) {
        sort.sort_up = !sort.sort_up
        $("#" + sort.current_parameter).attr("data-order") > 0 ?
            $("#" + sort.current_parameter).attr("data-order", "-1") :
            $("#" + sort.current_parameter).attr("data-order", "1")
    } else {
        sort.previous_parameter = sort.current_parameter
        sort.current_parameter = parameter
        sort.sort_up = true
        $("#" + sort.previous_parameter).attr("data-order", "0")
        $("#" + sort.current_parameter).attr("data-order") > 0 ?
            $("#" + sort.current_parameter).attr("data-order", "1") :
            $("#" + sort.current_parameter).attr("data-order", "-1")
    }

    $.post('/sort_grades_table_for_expert', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
        expert_id: expert_id
    }).done(
        function (response) {
            let grades = JSON.parse(response['grades'])
            let quantity = grades.length
            limit = quantity

            for (let i = 0; i < quantity; i++) {
                $(`#user_id${i}`).html(grades[i]['user_id'] ? grades[i]['user_id'] : '–');
                $(`#date${i}`).html(grades[i]['date'] ? grades[i]['date'] : '–')

                for (let j = 0; j < 15; j++)
                    if ($(`#parameter_${j}${i}`))
                        $(`#parameter_${j}${i}`).html(grades[i][`parameter_${j}`] !== '0' ?
                            grades[i][`parameter_${j}`] : '–')

                $(`#comment${i}`).html(grades[i][`comment`] ? grades[i][`comment`] : '–')

            }
            delete_buttons()
            buttons(limit)
        }).fail(function () {
        alert("Error AJAX request")
    })
}