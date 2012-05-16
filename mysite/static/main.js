datepicker_options = {
    showButtonPanel: true,
    showOn: "both",
    buttonImage: "/images/calendar.gif",
    buttonImageOnly: true
};
timepicker_options = datepicker_options;

$(function(){

    $('.start_date').datepicker(datepicker_options);
    $('.end_date').datepicker(datepicker_options);
    $('.start_time').timepicker(timepicker_options);
    $('.end_time').timepicker(timepicker_options);

    $('.submit').click(function(){
        data = $('#event-info-form').serializeArray();
        timezone = jstz.determine_timezone();
        timezone_name = timezone.name();

        // to help debug: print timezone info
        console.log('your timezone:');
        console.log(timezone);
        console.log('your timezone name:');
        console.log(timezone_name);

        data.push({'name':'timezone', 'value': timezone_name});
        console.log(data);
        data = JSON.stringify(data);
        console.log(data);
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '/ajax_add_event',
            data: {'data_as_json': data},
            success: function(data){
                console.log(data);
                url = data['our_url'];
                $('#result').show();
                $('#result').empty();
                box = $('<textarea></textarea>')
                box.append(url);
                $('#result').append(box);
            },
            error: function(e){
                console.log(e);
                alert('aw, crud. an error.' + e);
            },
        });
        return false;
    });
    if (is_event_add_page) {
        set_current_datetime_as_defaults();
    }

});

function set_current_datetime_as_defaults(){
    // grab the current time/date and set it as the defaults
    now = new Date();
    in_one_hour = new Date(now.getTime() + (1000*60*60));
    time = now.getHours() + ':' + now.getMinutes();
    time_in_one_hour = in_one_hour.getHours() + ':' + in_one_hour.getMinutes();
    date = (now.getMonth() + 1) + '/' + now.getDate() + '/' + now.getFullYear();
    date_in_one_hour = (in_one_hour.getMonth() + 1) + '/' + in_one_hour.getDate() + '/' + in_one_hour.getFullYear();

    $('.start_date').val(date);
    $('.end_date').val(date_in_one_hour);
    $('.start_time').val(time);
    $('.end_time').val(time_in_one_hour);
}

