$(document).ready(function($) {
    $("#workbook").on("change", function() {
        if($("#workbook")[0].files.length > 10) {
            $("#workbook").val('')
            alert("You can select only 10 files");
        }
    });
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
})

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function upload() {
    var form = new FormData()
    $.each($('#workbook')[0].files, function(i, file) {
        form.append('files[]', file);
    });
    $("#form-btn").attr("disabled", true)
    connectSocket()
    $.ajax({
        type:'POST',
        url: '/',
        processData : false,
        contentType : false,
        data: form,
        success: function (response) {
            $("#form-btn").attr("disabled", false)
            ws4redis.close()
        },
        statusCode: {
            500: function(xhr, textStatus) {
                $("#form-btn").attr("disabled", false)
                ws4redis.close()
                return alert("Something went wrong.")
            },
            400: function(xhr, textStatus) {
                var error = JSON.parse(xhr.responseText)
                $("#form-btn").attr("disabled", false)
                ws4redis.close()
                return $('#error').html("Error:" + error.error_message)
            },
        }
    });
    return false
}

function connectSocket() {
    ws4redis = WS4Redis({
        uri: WEBSOCKET_URI + 'processing?subscribe-broadcast',
        connecting: on_connecting,
            connected: on_connected,
            receive_message: updateProcess,
            disconnected: on_disconnected,
            heartbeat_msg: WS4REDIS_HEARTBEAT
    });
}

function on_connecting() {
    console.log('Websocket is connecting...')
}

function on_connected() {
    console.log('connected')
}

function on_disconnected(evt) {
    console.log('Websocket was disconnected: ' + JSON.stringify(evt))
}

function updateProcess(msg) {
    var data = JSON.parse(msg)
    console.log(data)
    if (data.error) {
        $('#error').html("Error:<br>" + data.error_message)
    }
    $("#total_rows").html('<a>Total Rows : ' + data.total_rows + '</a>')
    $("#rows_processed").html('<a>Rows Processed: ' + data.rows_processed + '</a>')
    $("#rows_ignored").html('<a>Rows Ignored: ' + data.rows_ignored + '</a>')
    $("#jd_created").html('<a>Job Description Created: ' + data.jd_created + '</a>')
}