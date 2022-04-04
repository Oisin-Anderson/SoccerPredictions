"use strict";

var counter = 0;

var $ = function(id) { return document.getElementById(id); };

var displayCurrentTime = function() {
   
    let d = new Date();

    let hours = d.getHours();
    let minutes = d.getMinutes();
    let seconds = d.getSeconds();
    var ampm = "";

    if(hours < 12){
        ampm = "am";
    }
    else if(hours == 12)
    {
        ampm = "pm";
    }
    else if(hours == 24)
    {
        hours = hours-12;
        ampm = "am";
    }
    else
    {
        hours -= 12;
        ampm = "pm";
    }
    

    $("time").innerHTML = hours+"-"+padSingleDigit(minutes)+"-"+padSingleDigit(seconds)+" "+ampm;


};

var padSingleDigit = function(num) {
    return (num < 10) ? "0" + num : num;
};

window.onload = function() {
    timer = setInterval(displayCurrentTime, 1000);

    
};