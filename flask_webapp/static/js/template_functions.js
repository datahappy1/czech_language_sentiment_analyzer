function show_details() {
    if(document.getElementById('span_with_details').style.display=='none') {
        document.getElementById('span_with_details').style.display='block';
        document.getElementById('link_show_details').style.display='none';
    }
    return false;
}

function clear_textarea_and_alert() {
    document.getElementById('Input_Text').value = "";
    if (document.getElementById('error_message')) {
        document.getElementById('error_message').style.display='none';
    }
    if (document.getElementById('result_overall_sentiment')) {
        document.getElementById('result_overall_sentiment').style.display='none';
    }
    return false;
}
