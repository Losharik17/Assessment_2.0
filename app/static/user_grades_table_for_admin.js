let limit = 10

sort.sort_up = false
sort.current_parameter = 'expert_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

edit_grade.old_value = Array()
edit_data.old_value = Array()


function edit_data(user_id, user_birthday) {
    if ($('#edit_data').html() !== 'Сохранить изменения') {
        let width = $("#edit_data").outerWidth()
        $('#edit_data').html('Сохранить изменения').css({width: width})
        edit_data.old_value = Array()
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
        })

    }
}

const but = document.querySelectorAll(".btn");
but.forEach((button) => {
    button.onclick = function(e){
        let x = e.clientX - e.target.offsetLeft;
        let y = e.clientY - e.target.offsetTop;
        let ripple = document.createElement("span");
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        this.appendChild(ripple);
        setTimeout(function(){
            ripple.remove();
        }, 600);
    }
});


function delete_buttons(user_id) {
    document.addEventListener('click', function (event) {

        for (let i = 0; i < limit; i++) {

            if (event.target.tagName !== 'TD' &&
                event.target.id.substring(0, event.target.id.length - 1) !== 'edit' &&
                event.target.id.substring(0, event.target.id.length - 1) !== `delete` &&
                event.target.tagName !== 'INPUT') {

                $('#buttons' + buttons.previous_str).fadeOut(300)
                setTimeout(() => {$('#buttons' + buttons.previous_str).css("display", "none")}, 300)
                setTimeout(() => {$("#edit" + i + " :input").attr('value', 'Редактировать')}, 300)
                for (let k = 0; k < 10; k++) {
                    if (document.getElementById(`parameter_${k}${buttons.previous_str}`) &&
                        edit_grade.old_value.length !== 0)
                        $(`#parameter_${k}${buttons.previous_str}`).html(edit_grade.old_value[k])
                    if (k === 10) edit_grade.old_value = Array()
                }
            }
        }
    })
}

function buttons(quantity) {
    buttons.previous_str = ''

    for (let i = 0; i < quantity; i++) {
        document.getElementById('number_str' + i).addEventListener('click', function () {

            if (buttons.previous_str !== '' && buttons.previous_str != i) {
                $('#buttons' + buttons.previous_str).fadeTo(300, 0.0)
                if ($("#edit" + buttons.previous_str + " :input").attr('value') === 'Сохранить') {
                    let x = buttons.previous_str
                    $('#buttons' + x).fadeOut(300)
                    setTimeout(() => {$('#buttons' + x).css("display", "none")}, 300)
                    setTimeout(() => {$("#edit" + x + " :input").attr('value', 'Редактировать')}, 300)
                    for (let k = 0; k < 10; k++) {
                        if (document.getElementById(`parameter_${k}${x}`) &&
                            edit_grade.old_value.length !== 0)
                            $(`#parameter_${k}${x}`).html(edit_grade.old_value[k])
                        if (k === 10) edit_grade.old_value = Array()
                    }
                }
            }
            $('#buttons' + i).fadeTo(0)
            $('#buttons' + i).css({
                display: 'inline-block', position: "absolute", width: "auto",
                'max-height': $('#number_str' + i).height()
            }).offset({
                left: $('#number_str' + i).offset().left + $('#tbody').width(),
                top: $('#number_str' + i).offset().top
            }).fadeTo(300, 1)
            buttons.previous_str = i
        })
    }
}

function edit_grade(grade_id, user_id, number_str) {
    console.log(grade_id)
    if ($("#edit" + number_str + " :input").attr('value') !== 'Сохранить') {
        let width = $("#edit" + number_str + " :input").innerWidth()
        edit_grade.old_value = Array()
        $("#edit" + number_str + " :input").attr('value', 'Сохранить').css({width: width})

        for (let i = 0; i < 10; i++) {
            if (document.getElementById(`parameter_${i}${number_str}`)) {

                let td = $(`#parameter_${i}${number_str}`)
                let value = td.html()
                edit_grade.old_value.push(value)
                td.html(`<input id="p${i}" onchange="
                                document.getElementById(this.id).setAttribute('value', this.value)" 
                                class="input" type="number" value="${value}" min="-1" max="3" 
                                step="1">`)
            }
        }
    } else {
        let grades = Array(), save = true

        for (let i = 0; i < 10; i++) {
            if (document.getElementById(`parameter_${i}${number_str}`)) {
                let element_value = $(`#parameter_${i}${number_str}` + " :input").attr('value')
                if ( element_value === '' || element_value === '-' || element_value === '–' || element_value === '—' || element_value === '0') {
                    grades.push(0)
                } else {
                    if (-1 <= element_value && element_value <= 3) {
                        grades.push(element_value)
                    } else {
                        save = false
                        grades = Array()
                        alert('Значения должны быть в пределах от -1 до 3')
                        break
                    }
                }
            }
        }

        if (save) {
            $('#buttons' + buttons.previous_str).fadeOut(300)
            setTimeout(() => {$('#buttons' + buttons.previous_str).css("display", "none")}, 300)
            setTimeout(() => {$("#edit" + number_str + " :input").attr('value', 'Редактировать')}, 300)
            $.post('/save_grade', {
                grades: JSON.stringify(grades),
                grade_id: grade_id
            }).done(function (response) {
                show_more(0, user_id)
            }).fail(function () {
                alert("Error AJAX request")
            })
        }
    }
}

function delete_grade(grade_id, user_id, number_str) {

    if (confirm('Удалить оценку?'))
        $.post('/delete_grade', {
            id: grade_id,
            user_id: user_id,
            lim: limit
        }).done(function (response) {

            document.getElementById(`buttons${number_str}`).style.transition = '0.3s';
            document.getElementById(`buttons${number_str}`).style.opacity = '0';
            setTimeout(() => {
                document.getElementById(`buttons${number_str}`).style.display = 'none'
            }, 300)

            show_more(0, user_id)

        }).fail(function () {
            alert("Error AJAX request")
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
            limit = quantity
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

            $("#tbody").append(`<tr id="number_str${i}"></tr>`)

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
            $(`#number_str${i}`).append(`<div id="buttons${i}" class="buttons">` +
                `<span id="edit${i}" onclick="edit_grade(${grades[i].id}, ${grades[i].user_id}, ${i})">` +
                `<input id="e${i}" type="button" value="Редактировать" class="btn"></span>` +
                `<span id="delete${i}" onclick="delete_grade(${grades[i].id}, ${grades[i].user_id}, ${i})">` +
                `<input id="d${i}" type="button" value="Удалить" class="btn_delete"></span></div>`)
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

                $(`#buttons${i}`).html(`<span id="edit${i}" onclick="edit_grade(${grades[i].id}, ${grades[i].user_id}, ${i})">` +
                    `<input id="e${i}" type="button" value="Редактировать" class="btn"></span>` +
                    `<span id="delete${i}" onclick="delete_grade(${grades[i].id}, ${grades[i].user_id}, ${i})">` +
                    `<input id="d${i}" type="button" value="Удалить" class="btn_delete"></span>`)
            }

        }).fail(function () {
        alert("Error AJAX request")
    })
}