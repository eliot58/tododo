let modal = $("#open__modal");
let sendModal = $("#send__modal")
let btnModalHide = $("#next__modal");
let closeModal = $("#close__modal")
let profileModal = $(".popup-profile-page")

$(document).ready(function () {
    $('#accordeon .acc__head').on('click', f_acc);
});
function f_acc() {
    $('#accordeon .acc__body').not($(this).next()).slideUp(400);
    $(this).next().slideToggle(200);
}
$(".tab_item").not(":first").hide();
$(".wrapper .tab").click(function () {
    $(".wrapper .tab").removeClass("active").eq($(this).index()).addClass("active");
    $(".tab_item").hide().eq($(this).index()).fadeIn()
}).eq(0).addClass("active");


$(".process__table-btn").click(function () {
    modal.show(300)
})
btnModalHide.click(function () {
    modal.hide(300)
    sendModal.show(300)
})
closeModal.click(function () {
    sendModal.hide(300)
})
