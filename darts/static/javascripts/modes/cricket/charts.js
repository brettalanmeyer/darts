var googleChartLoaded = false;

function charts(response){

	if(!googleChartLoaded){
		google.charts.load("current", { "packages": [ "corechart" ]});
		googleChartLoaded = true;
	}

	var container = $(".match-graphs-container");
	var div = $("<div />").addClass("graph");

	var data = [[
		"Round", "Marks", "Average"
	]];

	var playerId;
	var playerName;
	var game;
	var gameData;

	var avg;
	var avgCounter;
	var totalPoints;

	google.charts.setOnLoadCallback(doIt);

	function doIt(){

		for(var i = 0; i < response.length; i++){

			var row = response[i];

			if(playerId != row.playerId){
				playerId = row.playerId;
				playerName = row.name;
			}

			if(game != row.game){
				game = row.game;
				gameData = [].concat(data);
				avg = 0;
				avgCounter = 0;
				totalPoints = 0;

			}

			if(row.points == "0"){
				row.total = 0;
			}

			totalPoints += row.total;
			avgCounter++;

			gameData.push([
				row.round,
				row.total,
				totalPoints / avgCounter
			]);

			if(i >= response.length - 1 || game != response[i + 1].game){

				var vMax = 0;
				var hMax = 0;

				for(var j = 0; j < gameData.length; j++){
					var mark = gameData[j];
					if(mark[0] > hMax){
						hMax = mark[0];
					}
					if(mark[1] > vMax){
						vMax = mark[1];
					}
				}

				vMax++;

				var vTicks = [];
				for(var k = 0; k <= vMax; k++){
					vTicks.push(k);
				}

				var hTicks = [];
				for(var k = 1; k <= hMax; k++){
					hTicks.push(k);
				}

				var thisDiv = div.clone();
				container.append(thisDiv);
				drawChart(game, playerName, gameData, thisDiv[0], vTicks, hTicks);

			}

		}

	}

	function drawChart(game, playerName, gameData, div, vTicks, hTicks) {

		var dataTable = google.visualization.arrayToDataTable(gameData);

		// Set chart options
		var options = {
			title: playerName + "'s marks per round - Game " + game,
			vAxis: {
				title: "marks",
				ticks: vTicks
			},
			hAxis: {
				title: "rounds",
				ticks: hTicks,
				gridlines: {
					count: 0,
					color: "transparent"
				}
			},
			seriesType: "bars",
			series: {
				1: {
					type: "line"
				}
			}
		};

		// Instantiate and draw our chart, passing in some options.
		var chart = new google.visualization.ComboChart(div);

		$("[data-tab=match-graphs]").on("click", function(){
			chart.draw(dataTable, options);
		});
	}

}


// https://developers.google.com/chart/interactive/docs/gallery/barchart#examples

/*

SELECT `playerId`, `game`, `round`, GROUP_CONCAT(value) as `points`, count(*) as `total`
FROM marks
WHERE `matchId` = 722
GROUP BY `playerId`, `game`, `round`
ORDER BY `playerId`, `game`, `round`

*/


