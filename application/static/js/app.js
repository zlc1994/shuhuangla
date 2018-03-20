function imgError(image) {
    image.onerror = "";
    image.src = "https://st.zlc1994.com/shuhuangla/cover/no_cover.png";
    return true;
}

document.addEventListener('DOMContentLoaded', function () {

    // Get all "navbar-burger" elements
    var $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Check if there are any navbar burgers
    if ($navbarBurgers.length > 0) {

        // Add a click event on each of them
        $navbarBurgers.forEach(function ($el) {
            $el.addEventListener('click', function () {

                // Get the target from the "data-target" attribute
                var target = $el.dataset.target;
                var $target = document.getElementById(target);

                // Toggle the class on both the "navbar-burger" and the "navbar-menu"
                $el.classList.toggle('is-active');
                $target.classList.toggle('is-active');

            });
        });
    }

});

$( function() {
    $( "#q" ).autocomplete({
        classes: {
            "ui-autocomplete": "menu-list"
        },
        source: "/autocomplete",
        minLength: 2,
        select: function(event, ui) {
            $("#q").val(ui.item.value);
            $("#queryForm").submit();

            return false;
        }
    })
        .autocomplete( "instance" )._renderItem = function( ul, item ) {
        return $( "<li>" )
            .append( item.value)
            .appendTo( ul );
    };
} );