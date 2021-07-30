let limit = 5
sort.sort_up = false
sort.current_parameter = 'id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

function show_more(new_field) {

    limit += new_field

    $.post('/show_more_users', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up
    }).done(function(response) {

        document.getElementById('tbody').innerHTML = ''
        let users = JSON.parse(response['users'])
        let quantity = users.length

        for (let i = 0; i < quantity; i++) {

            $("#tbody").append(`<tr id="number_str${i}"` +
                ` onclick="location.href='/user_grades_table/${users[i]['id']}'"></tr>`)

            if (users[i]['id'] === 'None')
                $(`#number_str${i}`).append(`<td id="id${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="id${i}">${users[i]['id']}</td>`)

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


            //$("#tbody").append('</tr>')

        }
    }).fail(function () {
        alert('Error AJAX request')
    })

}


function sort(parameter) {

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
        lim: limit
    }).done(
        function (response) {

            let users = JSON.parse(response['users'])
            let quantity = users.length

            for (let i = 0; i < quantity; i++) {
                $(`#id${i}`).html(users[i]['id'] ? users[i]['id'] : '–');
                $(`#username${i}`).html(users[i]['username'] ? users[i]['username'] : '–')
                $(`#birthday${i}`).html(users[i]['birthday'] !== 'None' ? users[i]['birthday'] : '–')
                $(`#team${i}`).html(users[i]['team'] !== 'None' ? users[i]['team'] : '–')

                for (let j = 0; j < 10; j++)
                    if (users[i][`sum_grade_${j}`] != 0 && isNaN(users[i][`sum_grade_${j}`]) &&
                        users[i][`sum_grade_${j}`] !== 'None')
                        $(`#sum_grade_${j}${i}`).html(Math.floor(users[i][`sum_grade_${j}`] * 100) / 100)
                    else
                        $(`#sum_grade_${j}${i}`).html('–')
                console.log(users[i][`sum_grade_all`] != 0 && isNaN(users[i][`sum_grade_all`]))
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



$(function () {
    let timer = null;
    let xhr = null;
    $('.user_popup').hover(
        function(event) {
            // mouse in event handler
            let elem = $(event.currentTarget);
            timer = setTimeout(function() {
                timer = null;
                xhr = $.post('/user_popup', {
                    user_id: 3,
                }).done(
                    function(data) {
                        xhr = null;
                        $('#number_str0').popover({title:'Title',content:'Content'});
                        console.log(123);
                    }
                );
            }, 1000);
        },
        function(event) {
            // mouse out event handler
            let elem = $(event.currentTarget);
            if (timer) {
                clearTimeout(timer);
                timer = null;
            }
            else if (xhr) {
                xhr.abort();
                xhr = null;
            }
            else {
                elem.popover('destroy');
            }
        }
    );
});