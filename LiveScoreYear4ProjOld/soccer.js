var $ = function (id) { return document.getElementById(id); };

var teams = [];
var goalfor = [];
var goalaga = [];
var goaldif = [];
var points = [];

function tableRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/standings?season=2021&league=39", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		//console.log(response);
		var team = response;
		console.log(team)
		//var name = team.response[0].team.name;
		//var country = team.response[0].team.country;
		
		console.log(team.response[0].league.name + " Season " + team.response[0].league.season);
		$("disheader").innerHTML = "<h1>League Table</h1>"
		$("display").innerHTML = "<tr><th>Position</th><th>Team</th><th>GF</th><th>GA</th><th>GD</th><th>Points</th></tr>"
		for(var x = 0; x < 20; x++)
		{
			teams[x] = team.response[0].league.standings[0][x].team.name;
			goalfor[x] = team.response[0].league.standings[0][x].all.goals.for;
			goalaga[x] = team.response[0].league.standings[0][x].all.goals.against;
			goaldif[x] = team.response[0].league.standings[0][x].goalsDiff;
			points[x] = team.response[0].league.standings[0][x].points;
			//console.log(team.response[0].league.standings[0][x].team.name + ": " + team.response[0].league.standings[0][x].points + ", form: " + team.response[0].league.standings[0][x].form);
			var pos = x + 1;
			console.log(teams[x])
			$("display").innerHTML += "<tr><th>"+pos+"</th><th>"+teams[x]+"</th><th>"+goalfor[x]+"</th><th>"+goalaga[x]+"</th><th>"+goaldif[x]+"</th><th>"+points[x]+"</th></tr>"
		}
	})
	.catch(err => {
		console.error(err);
	});

}

function liveRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all&league=39", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		var team = response;
		console.log(team.response[0])
		console.log(team.response[0].teams.home.name)

		homet = team.response[0].teams.home.name;
		homes = team.response[0].goals.home;
		awayt = team.response[0].teams.away.name;
		aways = team.response[0].goals.away;
		
		$("disheader").innerHTML = "<h1>Live Matches</h1>"
		$("display").innerHTML = "<tr><th>Home</th><th></th><th>Away</th></tr>"
		$("display").innerHTML += "<tr><th>"+homet+"</th><th></th><th>"+awayt+"</th></tr>"
		$("display").innerHTML += "<tr><th>"+homes+"</th><th></th><th>"+aways+"</th></tr>"
	})
	.catch(err => {
		$("disheader").innerHTML = "<h1>No live matches on right now</h1>"
		$("display").innerHTML = ""
		console.error(err);
	});

}

function fixturesRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&next=10", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		var team = response;
		console.log(team.response[0])
		console.log(team.response[0].teams.home.name)
		$("disheader").innerHTML = "<h1>Next Weeks Fixtures</h1>"
		$("display").innerHTML = "<tr><th>Home</th><th></th><th>Away</th></tr>"

		for(var x=0; x < 10; x++){
			home = team.response[x].teams.home.name;
			away = team.response[x].teams.away.name;
			
			$("display").innerHTML += "<tr><th>"+home+"</th><th>VS</th><th>"+away+"</th></tr>"
		}
	})
	.catch(err => {
		console.error(err);
	});

}

function resultsRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&last=10", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		var team = response;
		console.log(team)
		console.log(team.response[0].teams.home.name)
		$("disheader").innerHTML = "<h1>Last Weeks Fixtures</h1>"
		$("display").innerHTML = "<tr><th>Home</th><th></th><th></th><th>Away</th></tr>"

		for(var x=0; x < 10; x++){
			homet = team.response[x].teams.home.name;
			awayt = team.response[x].teams.away.name;
			homes = team.response[x].goals.home;
			aways = team.response[x].goals.away;
			
			$("display").innerHTML += "<tr><th>"+homet+"</th><th>"+homes+"</th><th>"+aways+"</th><th>"+awayt+"</th></tr>"
		}
	})
	.catch(err => {
		console.error(err);
	});

}

function statsRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/players/topscorers?league=39&season=2021", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		var team = response;
		console.log(team.response[0])
		console.log(team.response[0].player.name)
		$("disheader").innerHTML = "<h1>Top Scorers</h1>"
		$("display").innerHTML = "<tr><th>Player</th><th>Goals</th><th>Games</th><th>Goals/Game</th></tr>"

		for(var x=0; x < 20; x++){
			player = team.response[x].player.name;
			goals = team.response[x].statistics[0].goals.total;
			games = team.response[x].statistics[0].games.appearences;
			ratio = goals / games;
			ratio = Math.round(ratio * 100) / 100;
			
			$("display").innerHTML += "<tr><th>"+player+"</th><th>"+goals+"</th><th>"+games+"</th><th>"+ratio+"</th></tr>"
		}
	})
	.catch(err => {
		console.error(err);
	});

}

function  processEntries() {
	console.log("hello");
}

window.onload = function(){
	liveRequest();
	$("live").onclick = liveRequest;
	$("table").onclick = tableRequest;
	$("fixtures").onclick = fixturesRequest;
	$("results").onclick = resultsRequest;
	$("stats").onclick = statsRequest;
}