let limit = 15

sort.sort_up = false
sort.current_parameter = 'expert_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

edit_grade.old_value = Array()
edit_data.old_value = Array()


document.addEventListener('click', function (event) {

    if (event.target.tagName !== 'INPUT' && event.target.id !== 'data_table' &&
        event.target.id !== 'edit_data' && $('#edit_data').html() === 'Сохранить изменения') {

        $('#photo').slideUp(300)
        setTimeout( () => { $('#photo').remove() }, 300)

        $('#data_table tr').each(function (index, element) {
            let td = $(this).children('td').children('span')
            if (index !== 2 && index !== 0) {

                td.html(`${edit_data.old_value[index - 1]}`)
                $('#edit_data').html('Редактировать данные')
            }
            else if (index === 2) {
                let date = edit_data.old_value[index - 1].split('.')
                td.html(Math.floor((new Date() - new Date(date[2], date[1], date[0]))
                    / (24 * 3600 * 365.25 * 1000)))
            }
        })
    }
})


function edit_data(user_id, user_birthday) {
    if ($('#edit_data').html() !== 'Сохранить изменения') {

        let width = $("#edit_data").outerWidth()
        $('#edit_data').html('Сохранить изменения').css({width: width}).css('text-align', 'center')
        edit_data.old_value = Array()

        $('#edit_data').after('<div id="photo_btn" class="input__wrapper">' +
            '                        <input name="photo" type="file" id="photo" class="input input__file">' +
            '                        <label for="photo" class="input__file-button_2">' +
            '                            <span class="input__file-button-text_2">Изменить Фото Профиля</span>' +
            '                        </label>' +
            '                    </div>')
        $('#photo_btn').slideUp(0).slideDown(300)
        $('#photo').attr('file', '1').on('change', function () {
            $('#photo').attr('file', $('#photo').attr('file') * -1)
        })

        $('#data_table tr').each(function (index, element) {
            let td = $(this).children('td').children('span')

            if (index !== 2 && index !== 0) {
                let value = td.html()
                edit_data.old_value.push(value)
                td.html(`<input id="d${index}" onchange="
                                    document.getElementById(this.id).setAttribute('value', this.value)" 
                                    class="form" type="text" value="${value}">`)
            }
            else if (index === 2) {
                edit_data.old_value.push(user_birthday)
                td.html(`<input id="d${index}" onchange="
                                    document.getElementById(this.id).setAttribute('value', this.value)" 
                                    class="form" type="text" value="${user_birthday}">`)
            }
        })
    }
    else {
        let data = Array()
        $('#edit_data').html('Редактировать данные')

        $('#data_table tr').each(function (index, element) {
            let td = $(this).children('td').children('span').children('input').val()
            if (index !== 2 && index !== 0) {
                data.push(td)
            }
            else if (index === 2) {
                data.push(td.replace(/[.]/g,'-').split("-").reverse().join("-"))
            }

        })

        $.post('/save_user_data', {
            data: JSON.stringify(data),
            user_id: user_id
        }).done(function (response) {
            $('#data_table tr').each(function (index, element) {
                let td = $(this).children('td').children('span')
                if (index !== 2 && index !== 0) {
                    td.html(`${td.children('input').val()}`)
                }
                else if (index === 2) {
                    let date = data[1].split('-')
                    td.html(Math.floor((new Date() -
                            new Date(date[0], date[1], date[2]))
                        / (24 * 3600 * 365.25 * 1000)))

                }
            })
        }).fail(function () {
            alert("Error AJAX request")
            $('#data_table tr').each(function (index, element) {
                if (index !== 2 && index !== 0) {
                    let td = $(this).children('td').children('span')
                    td.html(`${edit_data.old_value[index - 1]}`)
                    $('#edit_data').html('Редактировать данные')
                }
            })

            $('body').append(
                `<div class="message success"><h4>Изменения сохранены</h4></div>`)
            setTimeout( ()=> {
                $('.message').css({transition: 'all 0.3s ease', opacity: 0})}, 2000)
            setTimeout( ()=> {
                $('.message').css({display: 'none'})}, 2300)
        })
        console.log($('#photo').attr('file'))
        if ($('#photo').attr('file') === '-1')
            $('#submit').trigger('click')

        $('#photo_btn').slideUp(300)
        setTimeout( () => { $('#photo_btn').remove() }, 300)

    }
}



function delete_user(id, project_id) {
    if (confirm(`Удадить пользователя с ID ${project_id}?`))
        $.post('/delete_user', {
            role: 'user',
            id: id
        }).done(function (response) {
            alert('Пользователь удалён')
        }).fail(function () {
            alert('Error AJAX request')
        })
}


function show_more(new_field, user_id) {

    limit += new_field

    $.post('/show_more_grades_for_user', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        user_id: user_id
    }).done(function (response) {

        $("#tbody").html('')
        let grades = JSON.parse(response['grades'])
        let quantity = grades.length

        if (limit > quantity) {
            quantity < 15 ? limit = 15 : limit = quantity
            $('body').append(
                `<div class="message warning"><h4>
                В таблице присутствуют все оценки участника</h4></div>`)
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

            if (grades[i]['expert_id'] === 'None')
                $(`#number_str${i}`).append(`<td id="expert_id${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="expert_id${i}">${grades[i]['expert_id']}</td>`)

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

function sort(parameter, user_id) {

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

    $.post('/sort_grades_table_for_user', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
        user_id: user_id
    }).done(
        function (response) {
            let grades = JSON.parse(response['grades'])
            let quantity = grades.length
            limit = quantity

            for (let i = 0; i < quantity; i++) {
                $(`#expert_id${i}`).html(grades[i]['expert_id'] ? grades[i]['expert_id'] : '–');
                $(`#date${i}`).html(grades[i]['date'] ? grades[i]['date'] : '–')

                for (let j = 0; j < 15; j++)
                    if ($(`#parameter_${j}${i}`))
                        $(`#parameter_${j}${i}`).html(grades[i][`parameter_${j}`] !== '0' ?
                            grades[i][`parameter_${j}`] : '–')

                $(`#comment${i}`).html(grades[i][`comment`] ? grades[i][`comment`] : '–')

            }

        }).fail(function () {
        alert("Error AJAX request")
    })
}