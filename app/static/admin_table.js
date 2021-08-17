let limit = 10
sort.sort_up = false
sort.current_parameter = 'project_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

document.addEventListener('click', function (event) {
    if (event.target.id === 'team') {
        if ($('#team').attr('data-order') === '0' ||
            $('#team').attr('data-order') === '1')
            $('#team').attr('data-order', -1)
        else
            $('#team').attr('data-order', 0)
    }

    if (event.target.id === 'region') {
        if ($('#region').attr('data-order') === '0' ||
            $('#region').attr('data-order') === '1')
            $('#region').attr('data-order', -1)
        else
            $('#region').attr('data-order', 0)
    }

    if (event.target.tagName === 'LI') {
        if (event.target.getAttribute('type_sort') === 'team')
            $('#team').attr('data-order', 1)
        if (event.target.getAttribute('type_sort') === 'region')
            $('#region').attr('data-order', 1)
    }

    if ($('#teams').attr('value') === 'Все команды' &&
        event.target.id !== 'team')
        $('#team').attr('data-order', 0)

    if ($('#regions').attr('value') === '–' &&
        event.target.id !== 'region')
        $('#region').attr('data-order', 0)

    let x = event.target.tagName
    console.log(x)
    $('.dropdown_2').focusout(function (event) {
        if (x !== 'TH' && x !== 'INPUT' && x !== 'LABEL' && x !== 'LI') {
            $(this).removeClass('active');
            $(this).find('.dropdown-menu').slideUp(300);
        }
    });
})

$('.dropdown_2').click(function (event) {
    if (event.target.id !== 'min_age' && event.target.id !== 'max_age' &&
        event.target.id !== 'min_age_value' && event.target.id !== 'max_age_value') {
        console.log(123)
        $(this).attr('tabindex', 1).focus();
        $(this).toggleClass('active');
        $(this).find('.dropdown-menu').slideToggle(300);
    }
});


$('.dropdown_2 .dropdown-menu li').click(function (event) {
    if (event.target.id !== 'min_age' && event.target.id !== 'max_age' &&
        event.target.id !== 'min_age_value' && event.target.id !== 'max_age_value') {
        $(this).parents('.dropdown_2').find('span').text($(this).text());
        $(this).parents('.dropdown_2').find('input').attr('value', $(this).attr('id'))
    }
});
/*End Dropdown Menu*/

$('.dropdown-menu li').click(function (event) {
    if (event.target.id !== 'min_age' && event.target.id !== 'max_age' &&
        event.target.id !== 'min_age_value' && event.target.id !== 'max_age_value') {
        let input = '<strong>' + $(this).parents('.dropdown_2').find('input').val() + '</strong>',
            msg = '<span class="msg">Hidden input value: ';
        $('.msg').html(msg + input + '</span>');
}
});



function draw_table(response, project_number) {

    document.getElementById('tbody').innerHTML = ''
    let users = JSON.parse(response['users'])
    let quantity = users.length

    if (limit > quantity) {
        if (quantity < 10)
            limit = 10
        else
            limit = quantity
        $('body').append(
            `<div class="message warning"><h4>
                В таблице присутствуют все участники</h4></div>`)
        setTimeout( ()=> {
            $('.message').css({transition: 'all 0.3s ease', opacity: 0})}, 2000)
        setTimeout( ()=> {
            $('.message').css({display: 'none'})}, 2300)
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
            $(`#number_str${i}`).append(`<td id="birthday${i}">${Math.floor((new Date() - new Date(users[i]['birthday']))
            / (24 * 3600 * 365.25 * 1000))}</td>`)
        if (users[i]['team'] === 'None')
            $(`#number_str${i}`).append(`<td id="team${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="team${i}">${users[i]['team']}</td>`)

        if (users[i]['region'] === 'None')
            $(`#number_str${i}`).append(`<td id="region${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="region${i}">${users[i]['region']}</td>`)


        for(let j = 0; j < 10; j++) {
            if (users[i][`sum_grade_${j}`]) {
                if (users[i][`sum_grade_${j}`] == 0 || isNaN(users[i][`sum_grade_${j}`]) ||
                    users[i][`sum_grade_${j}`] === 'None')
                    $(`#number_str${i}`).append(`<td id="sum_grade_${j}${i}">–</td>`)
                else
                    $(`#number_str${i}`).append(`<td id="sum_grade_${j}${i}">${Math.ceil(users[i][`sum_grade_${j}`] * 100) / 100}</td>`)
            }
        }

        if (users[i]['sum_grade_all'] == 0 || isNaN(users[i][`sum_grade_all`]) ||
            users[i]['sum_grade_all'] === 'None')
            $(`#number_str${i}`).append(`<td id="sum_grade_all${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="sum_grade_all${i}">${Math.ceil(users[i]['sum_grade_all'] * 100) / 100}</td>`)
    }
}

function age_sort(project_number) {
    //if (min_age > max_age) {
    //    let t = min_age
    //    min_age = max_age
    //    max_age = t
    //}

    if ($('#age_sort').html() === 'По возрастанию')
        setTimeout( ()=> { $('#age_sort').html('По убыванию') }, 300)
    else
        setTimeout( ()=> { $('#age_sort').html('По возрастанию') }, 300)

    sort('birthday', project_number)
}

function show_more(new_field, project_number) {

    limit += new_field

    $.post('/show_more_users', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        project_number: project_number,
        team: $('#teams').attr('value'),
        region: $('#regions').attr('value'),
        min_age: arguments[2] || '',
        max_age: arguments[3] || ''
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
        team: $('#teams').attr('value'),
        region: $('#regions').attr('value'),
    }).done(
        function (response) {

            let users = JSON.parse(response['users'])
            let quantity = users.length

            for (let i = 0; i < quantity; i++) {

                $(`#number_str${i}`).attr('onclick',
                    `location.href='/user_grades_table/${project_number}/${users[i]["id"]}'`)

                $(`#id${i}`).html(users[i]['id'] ? users[i]['project_id'] : '–');
                $(`#username${i}`).html(users[i]['username'] ? users[i]['username'] : '–')

                $(`#birthday${i}`).html(users[i]['birthday'] !== 'None' ?
                    Math.floor((new Date() - new Date(users[i]['birthday'])) / (24 * 3600 * 365.25 * 1000)) :
                    '–')

                $(`#team${i}`).html(users[i]['team'] !== 'None' ? users[i]['team'] : '–')
                $(`#region${i}`).html(users[i]['region'] !== 'None' ? users[i]['region'] : '–')

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
