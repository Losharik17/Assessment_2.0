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


// делает кнопку отправки неактивной
// чтобы предотвротить многократное выставление оценок
document.getElementById('submit').addEventListener("click", function (event) {
    setTimeout(()=> { $('#submit').attr('disabled','disabled')}, 1)
})
