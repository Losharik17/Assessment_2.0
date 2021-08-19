let limit = 10
sort.sort_up = false
sort.current_parameter = 'project_id'
sort.previous_parameter = ''
$("#" + sort.current_parameter).attr("data-order", "1")

function draw_table(response, project_number) {

    document.getElementById('tbody').innerHTML = ''
    let experts = JSON.parse(response['experts'])
    let quantity = experts.length

    if (limit > quantity) {
        if (quantity < 10)
            limit = 10
        else
            limit = quantity
        $('body').append(
            `<div class="message warning"><h4>
                В таблице присутствуют все участники</h4></div>`)
        setTimeout(() => {
            $('.message').css({transition: 'all 0.3s ease', opacity: 0})
        }, 2000)
        setTimeout(() => {
            $('.message').css({display: 'none'})
        }, 2300)
        $('#show_more').css('display', 'none')
        $('#show_all').css('display', 'none')
    } else {
        $('#show_more').css('display', 'inline-block')
        $('#show_all').css('display', 'inline-block')
    }

    for (let i = 0; i < quantity; i++) {

        $("#tbody").append(`<tr id="number_str${i}"` +
            ` onclick="location.href='/expert_table/${project_number}/${experts[i]['id']}'"></tr>`)

        if (experts[i]['project_id'] === 'None')
            $(`#number_str${i}`).append(`<td id="project_id${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="project_id${i}">${experts[i]['project_id']}</td>`)

        if (experts[i]['username'] === 'None')
            $(`#number_str${i}`).append(`<td id="username${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="username${i}">${experts[i]['username']}</td>`)

        if (experts[i]['weight'] === 'None')
            $(`#number_str${i}`).append(`<td id="weight${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="weight${i}">${experts[i]['weight']}</td>`)

        if (experts[i]['quantity'] === 'None')
            $(`#number_str${i}`).append(`<td id="quantity${i}">–</td>`)
        else
            $(`#number_str${i}`).append(`<td id="quantity${i}">${experts[i]['quantity']}</td>`)
    }
}

function show_more(new_field, project_number) {

    limit += new_field

    $.post('/show_more_experts', {
        lim: limit,
        parameter: sort.current_parameter,
        sort_up: sort.sort_up,
        project_number: project_number,
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


    $.post('/sort_experts_table', {
        parameter: parameter,
        sort_up: sort.sort_up,
        lim: limit,
        project_number: project_number
    }).done(
        function (response) {
            console.log(123)
            let experts = JSON.parse(response['experts'])
            let quantity = experts.length

            for (let i = 0; i < quantity; i++) {

                $(`#number_str${i}`).attr('onclick',
                    `location.href='/expert_table/${project_number}/${experts[i]["id"]}'`)

                $(`#project_id${i}`).html(experts[i]['project_id'] ? experts[i]['project_id'] : '–');
                $(`#username${i}`).html(experts[i]['username'] ? experts[i]['username'] : '–')
                $(`#weight${i}`).html(experts[i]['weight'] !== 'None' ? experts[i]['weight'] : '–')
                $(`#quantity${i}`).html(experts[i]['quantity'] !== 'None' ? experts[i]['quantity'] : '–')
            }

        }).fail(function () {
        alert("Error AJAX request")
    })
}
