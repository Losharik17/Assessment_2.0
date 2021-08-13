let limit = 5
sort.sort_up = false
sort.current_parameter = 'project_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

function draw_table(response, project_number) {

    document.getElementById('tbody').innerHTML = ''
    let users = JSON.parse(response['users'])
    let quantity = users.length

    if (limit > quantity) {
        limit = quantity
        $('body').append(
            `<div class="message warning"><h4>
                В таблице присутствуют все участники</h4></div>`)
        $('#show_more').css('display', 'none')
        $('#show_all').css('display', 'none')
    }
    else {
        $('#show_more').css('display', 'inline-block')
        $('#show_all').css('display', 'inline-block')
    }

    for (let i = 0; i < quantity; i++) {

        $("#tbody").append(`<tr id="number_str${i}"` +
            ` onclick="location.href='/user_grades_table/${project_number}/${users[i]['id']}'"></tr>`)

        if (users[i]['id'] === 'None')
            $(`#number_str${i}`).append(`<td id="id${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="id${i}">${users[i]['project_id']}</td>`)

        if (users[i]['username'] === 'None')
            $(`#number_str${i}`).append(`<td id="username${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="username${i}">${users[i]['username']}</td>`)

        if (users[i]['birthday'] === 'None')
            $(`#number_str${i}`).append(`<td id="birthday${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="birthday${i}">${users[i]['birthday']}</td>`)

        if (users[i]['team'] === 'None')
            $(`#number_str${i}`).append(`<td id="team${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="team${i}">${users[i]['team']}</td>`)

        for(let j = 0; j < 10; j++) {
            if (users[i][`sum_grade_${j}`]) {
                if (users[i][`sum_grade_${j}`] == 0 || isNaN(users[i][`sum_grade_${j}`]) ||
                    users[i][`sum_grade_${j}`] === 'None')
                    $(`#number_str${i}`).append(`<td id="sum_grade_${j}${i}">–</td>`)
                else
                    $(`#number_str${i}`).append(`<td id="sum_grade_${j}${i}">${Math.floor(users[i][`sum_grade_${j}`] * 100) / 100}</td>`)
            }
        }

        if (users[i]['sum_grade_all'] == 0 || isNaN(users[i][`sum_grade_all`]) ||
            users[i]['sum_grade_all'] === 'None')
            $(`#number_str${i}`).append(`<td id="sum_grade_all${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="sum_grade_all${i}">${Math.floor(users[i]['sum_grade_all'] * 100) / 100}</td>`)
    }
}

function show_more(new_field, project_number) {

    limit += new_field


    $.post('/show_more_users', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        project_number: project_number,
        team: $('#teams').val()
    }).done(function(response) {

        draw_table(response, project_number)

    }).fail(function () {
        alert('Error AJAX request')
    })

}

function sort(parameter, project_number) {

    if (sort.current_parameter === parameter) {
        sort.sort_up = !sort.sort_up
        $("#" + sort.current_parameter).attr("data-order") > 0 ?
            $("#" + sort.current_parameter).attr("data-order", "-1") :
            $("#" + sort.current_parameter).attr("data-order", "1")
    }
    else {
        sort.previous_parameter = sort.current_parameter
        sort.current_parameter = parameter
        sort.sort_up = true
        $("#" + sort.previous_parameter).attr("data-order", "0")
        $("#" + sort.current_parameter).attr("data-order") > 0 ?
            $("#" + sort.current_parameter).attr("data-order", "1") :
            $("#" + sort.current_parameter).attr("data-order", "-1")
    }

    $.post('/sort_users_table', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
        project_number: project_number,
        team: $('#teams').val()
    }).done(
        function (response) {

            let users = JSON.parse(response['users'])
            let quantity = users.length

            for (let i = 0; i < quantity; i++) {

                $(`#number_str${i}`).attr('onclick',
                    `location.href='/user_grades_table/${project_number}/${users[i]["id"]}'`)

                $(`#id${i}`).html(users[i]['id'] ? users[i]['project_id'] : '–');
                $(`#username${i}`).html(users[i]['username'] ? users[i]['username'] : '–')
                $(`#birthday${i}`).html(users[i]['birthday'] !== 'None' ? users[i]['birthday'] : '–')
                $(`#team${i}`).html(users[i]['team'] !== 'None' ? users[i]['team'] : '–')

                for (let j = 0; j < 10; j++)
                    if (users[i][`sum_grade_${j}`] != 0 && !isNaN(users[i][`sum_grade_${j}`]) &&
                        users[i][`sum_grade_${j}`] !== 'None')
                        $(`#sum_grade_${j}${i}`).html(Math.floor(users[i][`sum_grade_${j}`] * 100) / 100)
                    else
                        $(`#sum_grade_${j}${i}`).html('–')

                if (users[i][`sum_grade_all`] != 0 && !isNaN(users[i][`sum_grade_all`]) &&
                    users[i]['sum_grade_all'] !== 'None')
                    $(`#sum_grade_all${i}`).html(Math.floor(users[i]['sum_grade_all'] * 100) / 100)
                else
                    $(`#sum_grade_all${i}`).html('–')
            }
        }).fail(function () {
        alert("Error AJAX request")
    })
}
