$('#submit').addClass('form_button')
$('#comment').addClass('comment')
$('#comment').attr('placeholder', 'Комментарий к оценке')

// отмена оценки при втором клике
$(":input[id^='parameter']").on("click", function (e) {
    e.preventDefault();

    setTimeout(
        () => $(this).prop("checked", !this.checked).trigger("change")
    );
});

// скрытие нулевых полей
$(`[value='0']`).each(function (index, element) {
    $(element).parent().css({display: 'none'});
})

$('#birthday').append(Math.floor((new Date() - new Date(`{{ user.birthday }}`))
    / (24 * 3600 * 365.25 * 1000)))


document.getElementById('submit').addEventListener("click", function (event) {
    $('#submit').attr('disabled','disabled')
    setTimeout(()=> {    $('#submit').attr('disabled','enabled')}, 5000)
})
