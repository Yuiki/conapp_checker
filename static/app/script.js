waitingDialog.show('ツイートを分析しています...');
$.ajax({
    type: 'GET',
    url: '../check',
    dataType: 'json',
    success: function (response) {
        var table = document.getElementById('table');
        for (var key in response) {
            var rows = table.insertRow(-1);
            var tdKey = rows.insertCell(-1);
            var tdValue = rows.insertCell(-1);
            tdKey.innerHTML = key;
            tdValue.innerHTML = response[key];
            waitingDialog.hide()
        }
        return response;
    },
    error: function (response) {
        return response;
    }
});