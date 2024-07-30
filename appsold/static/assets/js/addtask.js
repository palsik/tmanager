
    $(document).ready(function () {
        $('#department').change(function () {
            var department = $(this).val();
            $.ajax({
                type: 'GET',
                url: '/get_personnel/',
                data: { 'department': department },
                success: function (response) {
                    $('#personnel').empty();
                    $('#personnel').append('<option value="">Select Personnel</option>');
                    $.each(response.personnel, function (index, personnel) {
                        $('#personnel').append('<option value="' + personnel.id + '">' + personnel.name + '</option>');
                    });
                },
                error: function (error) {
                    console.log(error);
                }
            });
        });

        $('#taskForm').submit(function (e) {
            e.preventDefault();
            var formData = $(this).serialize();
            $.ajax({
                type: 'POST',
                url: '/create_task/',
                data: formData,
                success: function (response) {
                    // Handle success response
                    console.log(response);
                },
                error: function (error) {
                    console.log(error);
                }
            });
        });
    });

