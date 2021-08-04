$('#submit').addClass('form_button')
$('#comment').addClass('comment')
$('#comment').attr('placeholder', 'Комментарий к оценке')

// отмена оценки при втором клике
$(":input").on("click", function (e) {
    e.preventDefault();

    setTimeout(
        () => $(this).prop("checked", !this.checked).trigger("change")
    );
});

// скрытие нулевых полей
$(`[value='0']`).each(function (index, element) {
    $(element).css('display', 'none')
})

$(`[for^='parameter']`).each(function (index, element) {
    if ($(element).html() === '')
        $(element).css('display', 'none')
})
