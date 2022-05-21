$(document).ready(function my() {
    $('#multi-check').multiselect({
        onChange: function (option, checked) {
            // Get selected options.
            var selectedOptions = $('#multi-check option:selected');

            if (selectedOptions.length >= 3) {
                // Disable all other checkboxes.
                var nonSelectedOptions = $('#multi-check option').filter(function () {
                    return !$(this).is(':selected');
                });

                nonSelectedOptions.each(function () {
                    var input = $('input[value="' + $(this).val() + '"]');
                    input.prop('disabled', true);
                    input.parent('.multiselect-option').addClass('disabled');
                });
            }
            else {
                // Enable all checkboxes.
                $('#multi-check option').each(function () {
                    var input = $('input[value="' + $(this).val() + '"]');
                    input.prop('disabled', false);
                    input.parent('.multiselect-option').addClass('disabled');
                });
            }
        },
        templates: {
            button: '<button type="button" class="multiselect dropdown-toggle my-multi-select" data-bs-toggle="dropdown" aria-expanded="false"><span class="multiselect-selected-text"></span></button>'
        },
    });
});