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
    else if (is_event_edit_page) {
        //convert_datetimes_to_local();
    }

});

function datetime_as_date_and_time_strs(datetime){
    time = datetime.getHours() + ':' + datetime.getMinutes();
    date = (datetime.getMonth() + 1) + '/' + datetime.getDate() + '/' + datetime.getFullYear();
    return {'time': time, 'date': date};
}

function set_current_datetime_as_defaults(){
    // grab the current time/date and set it as the defaults
    now = new Date();
    in_one_hour = new Date(now.getTime() + (1000*60*60));

    update_fields_with_datetimes(now, in_one_hour);
}

function update_fields_with_datetimes(start_datetime, end_datetime){
    start_datetime_str = datetime_as_date_and_time_strs(start_datetime);
    end_datetime_str = datetime_as_date_and_time_strs(end_datetime);

    $('.start_date').val(start_datetime_str['date']);
    $('.start_time').val(start_datetime_str['time']);
    $('.end_date').val(end_datetime_str['date']);
    $('.end_time').val(end_datetime_str['time']);
}

function get_tz_utc_offset_secs(){
    return new Date().getTimezoneOffset() * 60000;
}

function convert_datetimes_to_local(){
    start_datetime_str = $('.start_date').val() + ' ' + $('.start_time').val();
    end_datetime_str = $('.end_date').val() + ' ' + $('.end_time').val();

    start_datetime = new Date(start_datetime_str);
    end_datetime = new Date(end_datetime_str);

    tz_utc_offset_secs = get_tz_utc_offset_secs();
    start_datetime = new Date(start_datetime.getTime() + tz_utc_offset_secs);
    end_datetime = new Date(end_datetime.getTime() + tz_utc_offset_secs);

    update_fields_with_datetimes(start_datetime, end_datetime);
}

