$(document).ready(function() {
    checkCookiesEnabled();
    $('select').selectpicker({ virtualScroll: false });
    $('[data-toggle="tooltip"]').tooltip({
        trigger : 'hover'
    })  
    
});
