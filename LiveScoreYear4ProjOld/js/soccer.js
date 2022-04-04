var $$ = function (id) { return document.getElementById(id); };
var rootURL = "http://localhost/LiveScoreYear4Proj/public/standings";
var rootURL2 = "http://localhost/LiveScoreYear4Proj/public/players";
var rowId = 0;

const table = {
	id : 0,
	position : 0,
	team : "",
	played : 0,
	win : 0,
	draw : 0,
	loss : 0,
	gfor : 0,
	gagainst : 0,
	gdiff : 0,
	points : 0
}

const players = {
	id : 0,
	player : "",
	position : "",
	played : 0,
	goals : 0
}

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
		
		var team;
		
		for(var x = 0; x < 20; x++)
		{
			team = response.response[0].league.standings[0][x];
			table.id = team.team.id;
			table.position = team.rank;
			table.team = team.team.name;
			table.played = team.all.played;
			table.win = team.all.win;
			table.draw = team.all.draw;
			table.loss = team.all.lose;
			table.gfor = team.all.goals.for;
			table.gagainst = team.all.goals.against;
			table.gdiff = team.goalsDiff;
			table.points = team.points;
			console.log(table);
	
			console.log('updateFilm');
			$.ajax({
				type: 'PUT',
				contentType: 'application/json',
				url: rootURL + '/' + table.id,
				dataType: "json",
				data: formToJSON(table),
				success: function(data, textStatus, jqXHR){
					findAll();
				},
				error: function(jqXHR, textStatus, errorThrown){
					alert('updateFilm error: ' + textStatus);
				}
			});
		}
	})
	.catch(err => {
		console.error(err);
	});

}



function playerRequest() {
	fetch("https://api-football-v1.p.rapidapi.com/v3/players/topscorers?league=39&season=2021", {
	"method": "GET",
	"headers": {
		"x-rapidapi-host": "api-football-v1.p.rapidapi.com",
		"x-rapidapi-key": "c1a198c06amsha00190a5e978e9ep1494dbjsn139488ca1b93"
		}
	})
	.then(response => response.json())
	.then(response => {
		
		var team;
		
		for(var x = 0; x < 20; x++)
		{
			team = response.response[x];
			console.log(team);
			players.id = team.player.id;
			players.player = team.player.name;
			players.position = team.statistics[0].games.position;
			players.played = team.statistics[0].games.appearences;
			players.goals = team.statistics[0].goals.total;
			console.log(players);
	
			console.log('updateFilm');
			$.ajax({
				type: 'PUT',
				contentType: 'application/json',
				url: rootURL2 + '/' + players.id,
				dataType: "json",
				data: formToJSONPlayers(players),
				success: function(data, textStatus, jqXHR){
					findAll();
				},
				error: function(jqXHR, textStatus, errorThrown){
					alert('updateFilm error: ' + textStatus);
				}
			});
		}
	})
	.catch(err => {
		console.error(err);
	});

}


function formToJSON(table) {
	return JSON.stringify({
		"id": table.id == "" ? null : table.id,
		"position": table.position, 
		"name": table.team, 
		"played": table.played,
		"win": table.win,
		"draw": table.draw,
		"loss": table.loss,
		"gfor": table.gfor,
		"gagainst": table.gagainst,
		"gdiff": table.gdiff,
		"points": table.points
		});
}


function formToJSONPlayers(players) {
	return JSON.stringify({
		"id": players.id == "" ? null : table.id,
		"player": players.player, 
		"position": players.position, 
		"played": players.played,
		"goals": players.goals
		});
}



function findAll() {
	console.log('findAll');
	$.ajax({
		type: 'GET',
		url: rootURL,
		dataType: "json", 
		success: renderList,
        error: function() {
          alert('Error occurs!');
       }
	});
}

function renderList(data) {
	console.log('render');
	var list = data == null ? [] : (data instanceof Array ? data : [data]);
}

function refresh(){
	var reload = $('#prem').DataTable();
	reload.ajax.reload();
	var reload = $('#tScorers').DataTable();
	reload.ajax.reload();
	console.log("refresh");
}

window.onload = function(){
	tableRequest();
	playerRequest();
	//findAll();
	//liveRequest();
	//$$("live").onclick = liveRequest;
	//$$("fixtures").onclick = fixturesRequest;
	//$$("results").onclick = resultsRequest;
	//$$("stats").onclick = statsRequest;
}