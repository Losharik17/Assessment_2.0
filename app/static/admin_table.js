let limit = 10
sort.sort_up = false
sort.current_parameter = 'project_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

$('.dropdown_2 .dropdown-menu').css({'top': $('#team').outerHeight() - 15})
$('.dropdown_2 .dropdown-menu').each(function (index, element) {
    $(element).css({'min-width': $(this).parent().outerWidth()})
})

function dataorder(parameter, event) {
    if (event.target.id === parameter) {
        if ($(`#${parameter}`).attr('data-order') === '0' ||
            $(`#${parameter}`).attr('data-order') === '1')
            $(`#${parameter}`).attr('data-order', -1)
        else
            $(`#${parameter}`).attr('data-order', 0)
    }

    if (event.target.tagName === 'LI')
        if (event.target.getAttribute('type_sort') === parameter)
            $(`#${parameter}`).attr('data-order', 1)
}

document.addEventListener('click', function (event) {

    dataorder('team', event)
    dataorder('region', event)
    dataorder('birthday', event)

    if ($('#teams').attr('value') === 'Все команды' &&
        event.target.id !== 'team')
        $('#team').attr('data-order', 0)

    if ($('#regions').attr('value') === '–' &&
        event.target.id !== 'region')
        $('#region').attr('data-order', 0)

    if ($('#birthdays').attr('value') === '–' &&
        event.target.id !== 'birthday')
        $('#birthday').attr('data-order', 0)
})

$('html').click(function (event) {
    // очень хрупкая и тупая конструкция, но она работает
    if (!$('#birthday').hasClass('active') && event.target.tagName === 'TH' &&
        event.target.id === 'birthday') {
        $('#birthday').attr('tabindex', 1).focus();
        $('#birthday').addClass('active');
        $('#birthday').find('.dropdown-menu').slideDown(300);
    }
    else if (event.target.tagName !== 'INPUT' || event.target.id === 'submit_sort_age'
        || ($('#birthday').hasClass('active') && (event.target.tagName === 'TH' ||
            event.target.tagName === 'LI' || event.target.tagName === 'LABEL'))) {
        $('#birthday').removeClass('active');
        $('#birthday').find('.dropdown-menu').slideUp(300);
    }
});

$('#team').click(function () {
    $(this).attr('tabindex', 1).focus();
    $(this).toggleClass('active');
    $(this).find('.dropdown-menu').slideToggle(300);
});

$('#team').focusout(function (event) {
    $(this).removeClass('active');
    $(this).find('.dropdown-menu').slideUp(300);
});

$('#region').click(function () {
    $(this).attr('tabindex', 1).focus();
    $(this).toggleClass('active');
    $(this).find('.dropdown-menu').slideToggle(300);
});

$('#region').focusout(function () {
    $(this).removeClass('active');
    $(this).find('.dropdown-menu').slideUp(300);
});

$('.dropdown_2 .dropdown-menu li').click(function (event) {
    $(this).parents('.dropdown_2').find('span').text($(this).text());
    $(this).parents('.dropdown_2').find('input').attr('value', $(this).attr('id'))
});
/*End Dropdown Menu*/

$('.dropdown-menu li').click(function (event) {
    let input = '<strong>' + $(this).parents('.dropdown_2').find('input').val() + '</strong>',
        msg = '<span class="msg">Hidden input value: ';
    $('.msg').html(msg + input + '</span>');
});
/*Width of Dropdown*/
$('.dropdown_2 .dropdown-menu').each(function (index, element) {
    $(element).css({'min-width': $(this).parent().outerWidth()})
})



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
            ` onclick="location.href='/user_grades_table_for_admin/${project_number}/${users[i]['id']}'"></tr>`)

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

function age_sort(project_number, type=0) {
    let min_age = $('#min_age_value').val() || 0,
        max_age = $('#max_age_value').val() || 200
    if (+min_age > +max_age) {
        $('#min_age_value').val(max_age)
        $('#max_age_value').val(min_age)
    }

    if ($('#age_sort').html() === 'По возрастанию')
        setTimeout( ()=> { $('#age_sort').html('По убыванию') }, 300)
    else
        setTimeout( ()=> { $('#age_sort').html('По возрастанию') }, 300)

    if (type)
        sort('birthday', project_number)
    else
        show_more(0, project_number)
}

function age_sort_delete(project_number) {
    $('#min_age_value').val(null)
    $('#max_age_value').val(null)
    setTimeout( ()=> {$('#birthday').attr('data-order', 0) }, 10)

    sort('project_id', project_number)
    show_more(0 , project_number)
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
        min_age: $('#min_age_value').val() || 0,
        max_age: $('#max_age_value').val() || 200
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
        min_age: $('#min_age_value').val() || 0,
        max_age: $('#max_age_value').val() || 200
    }).done(
        function (response) {

            let users = JSON.parse(response['users'])
            let quantity = users.length

            for (let i = 0; i < quantity; i++) {

                $(`#number_str${i}`).attr('onclick',
                    `location.href='/user_grades_table_for_admin/${project_number}/${users[i]["id"]}'`)

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
