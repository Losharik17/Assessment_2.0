let limit = 5

sort.sort_up = false
sort.current_parameter = 'registration_date'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")


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
                event.target.id.substring(0, event.target.id.length - 1) !== 'admin' &&
                event.target.id.substring(0, event.target.id.length - 1) !== 'viewer' &&
                event.target.id.substring(0, event.target.id.length - 1) !== `delete` &&
                event.target.tagName !== 'INPUT') {

                $('#buttons' + buttons.previous_str).fadeOut(300)
                setTimeout(() => {$('#buttons' + buttons.previous_str)
                    .css("display", "none")}, 300)
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
                let x = buttons.previous_str
                $('#buttons' + x).fadeOut(300)
                setTimeout(() => {$('#buttons' + x).css("display", "none")}, 300)
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

function give_role(id, number_str, role) {

    let x = $(`#username${number_str}`).html()

    if (confirm(`Выдать пользователю ${x} уровень доступа "${role}"?`))
        $.post('/give_role', {
            id: id,
            role: role,
            lim: limit
        }).done(function (response) {

            document.getElementById(`buttons${number_str}`).style.transition = '0.3s';
            document.getElementById(`buttons${number_str}`).style.opacity = '0';
            setTimeout(() => {
                document.getElementById(`buttons${number_str}`).style.display = 'none'
            }, 300)

            show_more(0)

        }).fail(function () {
            alert("Error AJAX request")
        })
}

function show_more(new_field) {

    limit += new_field

    $.post('/show_more_waiting_users', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
    }).done(function (response) {

        $("#tbody").html('')
        let waiting_users = JSON.parse(response['waiting_users'])
        let quantity = waiting_users.length

        if (limit > quantity) {
            limit = quantity
            $('body').append(
                `<div  id="message" class="message warning"><h4>
                В таблице присутствуют все пользователи</h4></div>`)
            setTimeout( ()=> {
                $('#message').css({transition: 'all 0.3s ease', opacity: 0})}, 4000)
            setTimeout( ()=> {
                $('#message').css({display: 'none'})}, 4100)
            $('#show_more').css('display', 'none')
            $('#show_all').css('display', 'none')
        }
        else {
            $('#show_more').css('display', 'inline-block')
            $('#show_all').css('display', 'inline-block')
        }

        for (let i = 0; i < quantity; i++) {

            $("#tbody").append(`<tr id="number_str${i}"></tr>`)

            if (waiting_users[i]['username'] === 'None')
                $(`#number_str${i}`).append(`<td id="username${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="username${i}">${waiting_users[i]['username']}</td>`)

            if (waiting_users[i]['email'] === 'None')
                $(`#number_str${i}`).append(`<td id="email${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="email${i}">${waiting_users[i]['email']}</td>`)

            if (waiting_users[i]['registration_date'] === 'None')
                $(`#number_str${i}`).append(`<td id="registration_date${i}">–</td>`)
            else
                $(`#number_str${i}`).append(`<td id="registration_date${i}">${waiting_users[i]['registration_date']}</td>`)

            $(`#number_str${i}`).append(`<div id="buttons${i}" class="buttons">` +
                `<span id="admin${i}" onclick="give_role(${waiting_users[i]['id']}, ${i},  'Администратор')">` +
                `<input id="a${i}" type="button" value="Администратор" class="btn"></span>` +
                `<span id="viewer${i}" onclick="give_role(${waiting_users[i]['id']}, ${i}, 'Заказчик')">` +
                `<input id="v${i}" type="button" value="Заказчик"" class="btn"></span>` +
                `<span id="delete${i}" onclick="give_role(${waiting_users[i]['id']}, ${i},  'Удалить')">` +
                `<input id="d${i}" type="button" value="Удалить"" class="btn_delete"></span></div>`)
        }
        delete_buttons()
        buttons(limit)
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
    } else {
        sort.previous_parameter = sort.current_parameter
        sort.current_parameter = parameter
        sort.sort_up = true
        $("#" + sort.previous_parameter).attr("data-order", "0")
        $("#" + sort.current_parameter).attr("data-order") > 0 ?
            $("#" + sort.current_parameter).attr("data-order", "1") :
            $("#" + sort.current_parameter).attr("data-order", "-1")
    }

    $.post('/sort_waiting_users', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
    }).done(
        function (response) {
            let waiting_users = JSON.parse(response['waiting_users'])
            let quantity = waiting_users.length
            limit = quantity

            for (let i = 0; i < quantity; i++) {
                $(`#username${i}`).html(waiting_users[i]['username'] ? waiting_users[i]['username'] : '–');
                $(`#email${i}`).html(waiting_users[i]['email'] ? waiting_users[i]['email'] : '–')
                $(`#registration_date${i}`).html(waiting_users[i]['registration_date'] ? waiting_users[i]['registration_date'] : '–')

                $(`#buttons${i}`).html(`<span id="admin${i}" onclick="give_role(${waiting_users[i]['id']},  ${i},  'Администратор')">` +
                    `<input id="a${i}" type="button" value="Администратор" class="btn"></span>` +
                    `<span id="viewer${i}" onclick="give_role(${waiting_users[i]['id']},  ${i},  'Заказчик')">` +
                    `<input id="v${i}" type="button" value="Заказчик" class="btn"></span>` +
                    `<span id="delete${i}" onclick="give_role(${waiting_users[i]['id']}, ${i},  'Удалить')">` +
                    `<input id="d${i}" type="button" value="Удалить" class="btn_delete"></span>`)
            }
            delete_buttons()
            buttons(limit)


        }).fail(function () {
        alert("Error AJAX request")
    })
}