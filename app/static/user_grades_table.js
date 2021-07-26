let limit = 5
sort.sort_up = false
sort.current_parameter = 'expert_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

delete_buttons()

function delete_buttons() {
    document.addEventListener('click', function (event) {

        for (let i = 0; i < limit; i++) {
            if (event.target.tagName !== 'TD' && event.target.id.substring(0, event.target.id.length - 1) !== 'edit' &&
                event.target.id.substring(0, event.target.id.length - 1) !== `delete`) {
                console.log(event.target.id.substring(0, event.target.id.length - 1), event.target.tagName)

                $('#buttons' + buttons.previous_str).fadeTo(300)
                setTimeout(() => {$('#buttons' + buttons.previous_str).css("display", "none")})
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
            }
            $('#buttons' + i).fadeTo(0)
            $('#buttons' + i).css({
                display: 'flex', position: "absolute", width: "content-width",
                background: "red", height: $('#number_str' + i).height()
            }).offset({
                left: $('#number_str' + i).offset().left + $('#tbody').width(),
                top: $('#number_str' + i).offset().top
            }).fadeTo(300, 1)
            buttons.previous_str = i

            console.log($('#tbody').width)
        })
    }
}

function edit_grade(id, number_str) {

    if ($("#" + id).html() !== 'Сохранить') {
        $("#" + id).html('Сохранить')
    } else {
        $("#" + id).html('Редактировать')

        let grades = Array()
        for (let i = 0; i < 5; i++)
            grades[i] = i
        $.post('/save_grade', {

            val: `${grades[0]}`,
            date: '2021-07-23 14:53:23.540060',
            expert_id: 1

        }).done(function (response) {


        }).fail(function () {
            alert("Error AJAX request")
        })
    }
}


function delete_grade(number_str) {

}

function show_more(new_field, user_id) {

    limit += new_field

    $.post('/show_more_grades', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        user_id: user_id
    }).done(function (response) {

        document.getElementById('tbody').innerHTML = ''
        let grades = JSON.parse(response['grades'])
        let quantity = grades.length
        limit = quantity
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

            $(`#number_str${i}`).append(`<div id="buttons${i}" class="buttons">` +
                `<span id="edit${i}" onClick="edit_grade(this.id, ${i})">` +
                `Редактировать` + `</span>` +
                `<span id="delete${i}" onClick="delete_grade(this.id, ${i})">` +
                `Удалить оценку` + `</span>` + `</div>`)
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

    $.post('/sort_grades_table', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
        user_id: 1
    }).done(
        function (response) {
            let grades = JSON.parse(response['grades'])
            let quantity = grades.length

            for (let i = 0; i < quantity; i++) {
                $(`#expert_id${i}`).html(grades[i]['expert_id'] ? grades[i]['expert_id'] : '–');
                $(`#date${i}`).html(grades[i]['date'] ? grades[i]['date'] : '–')

                for (let j = 0; j < 15; j++)
                    if ($(`#parameter_${j}${i}`))
                        $(`#parameter_${j}${i}`).html(grades[i][`parameter_${j}`] !== '0' ? grades[i][`parameter_${j}`] : '–')
            }

        }).fail(function () {
        alert("Error AJAX request")
    })
}