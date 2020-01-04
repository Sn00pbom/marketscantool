var table;
var timerFunc = updateTable;
const dataPath = "data.json";

function initTable() {
    table = new Tabulator("#value-table", {
        layout: "fitColumns",
        // autoResize: true,
        placeholder: "No Data",
        height: 800,
        selectable: true,
        autoColumns: true,
        // columns: [
        //     {title:"Name", field:"name", sorter:"string", width:200},
        //     {title:"Progress", field:"progress", sorter:"number", formatter:"progress"},
        //     {title:"Gender", field:"gender", sorter:"string"},
        //     {title:"Rating", field:"rating", formatter:"star", align:"center", width:100},
        //     {title:"Favourite Color", field:"col", sorter:"string"},
        //     {title:"Date Of Birth", field:"dob", sorter:"date", align:"center"},
        //     {title:"Driver", field:"car", align:"center", formatter:"tickCross", sorter:"boolean"},
        // ],
    });

    try {
        table.setData(dataPath);
    } catch (e) {
        console.log(e);
    }
}

function updateTable() {
    try {
        table.replaceData()
    } catch (e) {
        window.clearInterval(timerFunc);
        console.log("Warning: data.json load error!");
    }
}

function copyToClipboard(text) {
  var $temp = $("<textarea>");
  $("body").append($temp);
  // $temp.val($(element).text()).select();
  $temp.val(text).select();
  document.execCommand("copy");
  $temp.remove();
  alert("Copied to Clipboard!")
}

function selectedToString() {
    var selectedData = table.getSelectedData();
    var s = "";
    var i;
    for (i = 0; i < selectedData.length; i++) {
        s += selectedData[i].Symbol + "\n";
    }
    return s;
}

function selectedToClipboard() {
    var selectedString = selectedToString();
    copyToClipboard(selectedString);
}

function doTimer() {
    var seconds = parseInt($("#interval-select :selected").val());
    window.clearInterval(timerFunc);
    updateTable();
    timerFunc = window.setInterval(updateTable, 1000 * seconds * 60);
}

