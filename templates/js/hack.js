var els = document.querySelectorAll('.eur');

els.forEach(function(el) {
    console.log(el.classList.innerHTML);
    el.classList.innerHTML="1000";
});