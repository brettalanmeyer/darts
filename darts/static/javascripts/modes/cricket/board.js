$(function(){

	var matchId = $("input[name=matchId]").val();
	var baseUrl = "/matches/" + matchId + "/modes/cricket";

	var statsModal = $(".modal-stats");
	var statsContainer = $(".match-stats-container");
	var nextRoundModal = $(".modal-next-round");
	var displayNextRoundWhenStatsAreDone = false;

	$(".btn-stats-show").on("click", stats);
	$(".btn-stats-done").on("click", function(){
		statsModal.hide();
		if(displayNextRoundWhenStatsAreDone){
			nextRoundModal.show();
		}
	});


	$(".score").first().addClass("target turn").find(".button-label").html("Turn");
	$(".score").last().addClass("target home").find(".button-label").html("Home");

	indicateClosedPoints();
	var complete = $("input[name=complete]").val() == "1";
	if(complete){
		$(".home").find(".button-label").addClass("complete");
		$(".turn").find(".button-label").html("Stats").addClass("complete");
		$(".home").on("click", function(){
			window.location = "/";
		});
		$(".turn").on("click", stats);
		return;
	}

	var spectatorInterval;
	if(window.location.search == "?spectator"){
		spectatorInterval = setInterval(spectate, 2500);
		return false;
	}

	function spectate(data){

		$.get("/matches/" + matchId + "/modes/cricket/spectator/", function(data){

			for(var i in data.teams){
				var team = data.teams[i];

				for(points in team.marks){
					$(".target.awarded[data-points=" + points + "][data-teamid=" + team.id + "]").attr("data-hits", team.marks[points]);
				}

				for(var j in team.players){
					var player = team.players[j];

					var mpr = $(".player[data-playerid=" + player.id + "]").find(".marks-per-round");
					mpr.find(".val.all").html(player.mpr);
					if(data.game >= 1) mpr.find(".val.r1").html(player.mpr1);
					if(data.game >= 2) mpr.find(".val.r2").html(player.mpr2);
					if(data.game >= 3) mpr.find(".val.r3").html(player.mpr3);
				}

				$(".score[data-teamid=" + team.id + "]").find(".current-round-points").html(team.marks.points);
			}

			$(".player").removeClass("active");
			$(".player-row").removeClass("highlight");
			$(".player[data-playerid=" + data.turn + "]").addClass("active").parents(".player-row").addClass("highlight");

			indicateClosedPoints();

			if(data.complete){
				clearTimeout(spectatorInterval);
			}
		});

	}


	var team1Id = $(".score").first().data("teamid");
	var team2Id = $(".score").last().data("teamid");


	var homeModal = $(".modal-home");
	var games = parseInt($("input[name=games]").val());
	var game = parseInt($("input[name=game]").val());
	var numPlayers = parseInt($("input[name=players]").val());
	var round = parseInt($("input[name=round]").val());
	var createdAt = new Date($("input[name=createdAt]").val());
	var markStyleId = $("input[name=markStyleId]");
	var markStyleIds = $("input[name=markStyleIds]").val().replace(/\[|\]|\s/g, "").split(",");
	var markStyleIdIndex = 0;

	var turnTimeout;
	var turnDelay = 5000;
	var valueOfMark;

	highlightTeam();

	$(".home").on("click", function(){
		homeModal.show();
	});
	$(".home-yes").on("click", function(){
		window.location = "/";
	});
	$(".home-no").on("click", function(){
		homeModal.hide();
	});

	$(".undo").on("click", undo);

	$(".turn").on("click", function(){
		nextTurn();
		clearTimeout(turnTimeout);
	});

	$(".miss").on("click", function(){
		var teamId =  $(".player.active").data("teamid");
		var playerId = $(".player.active").data("playerid");
		$.post(baseUrl + "/teams/" + teamId + "/players/" + playerId + "/matches/" + game + "/rounds/" + round + "/marks/0/").done(function(response){
			updateMarksPerRound(response);
			nextTurn();
		});
	});

	$(".awarded").on("click", function(){

		var source = $(this);
		var hits = parseInt(source.attr("data-hits"));
		var point = source.data("points");
		var teamId = source.data("teamid");
		var playerId = $(".player.active").data("playerid");

		if($(".player.active[data-teamid=" + teamId + "]").length == 0){
			return;
		}

		var points = 0;
		var closed = $(".awarded[data-points=" + point + "]:not([data-teamid=" + teamId + "])").attr("data-hits") >= 3;

		if( hits < 3 || !closed ){
			source.attr("data-hits", hits + 1);
			$.post(baseUrl + "/teams/" + teamId + "/players/" + playerId + "/matches/" + game + "/rounds/" + round + "/marks/" + point + "/", updateMarksPerRound);

			if(point != valueOfMark){
				valueOfMark = point;
			}

			scoreMarksForPoints(source, point);
		}

		if( hits >= 3 && !closed ){
			points += source.data("points");
		}

		if(!closed){
			var current = $('.score[data-teamid="' + teamId + '"]');
			current.data("score", current.data("score") + points);
			current.find(".current-round-points").html(current.data("score"));
		}

		indicateClosedPoints();
		determineWinner();

		clearTimeout(turnTimeout);
		turnTimeout = setTimeout(nextTurn, turnDelay);

	});

	function isClosed(teamId){
		var closed = true;
		$(".awarded[data-teamid=" + teamId + "]").each(function(){
			if($(this).attr("data-hits") < 3){
				closed = false;
			}
		});
		return closed;
	}

	function getScore(teamId){
		return parseInt($(".score[data-teamid=" + teamId + "]").data("score"));
	}

	function highlightTeam(){
		$(".player-row, .awarded").removeClass("highlight");
		var teamId =  $(".player.active").data("teamid");
		$(".player-row[data-teamid=" + teamId + "]").addClass("highlight");
		$(".awarded[data-teamid=" + teamId + "]").addClass("highlight");

	}

	function getActivePlayer(){
		return parseInt($(".players").find(".active").data("playerid"));
	}

	function nextTurn(){

		var players = $(".player");

		var position = 0;
		for( var i = 0; i < players.length; i++){
			var player = $(players[i]);
			if(player.hasClass("active")){
				position = i;
				break;
			}
		}

		players.removeClass("active");

		if(players.length == 4){

			var index = 0;
			switch(position){
				case 0:
					index = 2;
					break;
				case 1:
					index = 3;
					break;
				case 2:
					index = 1;
					break;
				case 3:
					index = 0;
					break;
			}

		} else {
			var index = position == 0 ? 1 : 0;
		}

		if(index == 0){
			round++;
		}

		var playerId = $(players[index]).addClass("active").data("playerid");
		$.post(baseUrl + "/players/" + playerId + "/turn/");
		highlightTeam();
		numberOfMarks = 0;

		clearMarksForPoints();

	}

	function result(winner, loser){
		$.post(baseUrl + "/game/" + game + "/game-over/", {
			winner: winner,
			winnerScore: getScore(winner),
			loser: loser,
			loserScore: getScore(loser)
		});
	}

	function stats(){
		nextRoundModal.hide();

		var playerContainerTemplate = $("<div />").addClass("stat-player");
		var pointContainerTemplate = $("<div />").addClass("point-player");

		$.get(baseUrl + "/stats").done(function(data){
			var players = data.players;
			var games = data.games;

			statsContainer.empty().addClass("games-" + games);

			for(var i = 0; i < players.length; i++){
				var playerContainer = playerContainerTemplate.clone();
				var player = players[i];

				playerContainer.append('<span class="name">' + player.name + "</span>");

				var pointContainer = pointContainerTemplate.clone();
				pointContainer.append("Total:<br />");
				for(var points in player.total){
					pointContainer.append('<span class="stat-point-label">' + points + ":</span>");
					pointContainer.append('<span class="stat-point-value">' + player.total[points] + "</span><br />");
				}
				playerContainer.append(pointContainer);

				for(var game in player.games){
					var pointContainer = pointContainerTemplate.clone();
					pointContainer.append("Game " + game + "<br />");

					for(var points in player.games[game]){
						pointContainer.append('<span class="stat-point-label ' + (points != "Miss" && player.games[game][points] > 3 ? 'pointed' : '') + '">' + points + ":</span>");
						pointContainer.append('<span class="stat-point-value ' + (points != "Miss" && player.games[game][points] > 3 ? 'pointed' : '') + '">' + player.games[game][points] + "</span><br />");
					}
					playerContainer.append(pointContainer);
				}

				statsContainer.append(playerContainer);
			}

			statsModal.show();

			charts(data.graph);

		});
	}

	function nextRound(num, winnerId, loserId){
		nextRoundModal.show();

		if($("input[name=result][data-winner=" + winnerId + "]").length >= Math.floor(games / 2)){
			nextRoundModal.find("h1").html("Team " + num + "<br />Wins The Game!");
			nextRoundModal.find("button").removeClass("hidden").first().html("Done");
			$.post(baseUrl + "/match-over/");
			displayNextRoundWhenStatsAreDone = true;
		} else {
			nextRoundModal.find("h1").html("Team " + num + "<br />Wins Round " + game + "!");
		}

	}

	function determineWinner(){

		var team1Closed = isClosed(team1Id);
		var team2Closed = isClosed(team2Id);
		var team1Score = getScore(team1Id);
		var team2Score = getScore(team2Id);

		var team1Wins = team1Closed && team1Score >= team2Score;
		var team2Wins = team2Closed && team2Score >= team1Score;

		if(team1Wins) {
			result(team1Id, team2Id);
			nextRound(1, team1Id, team2Id);
		} else if(team2Wins){
			result(team2Id, team1Id);
			nextRound(2, team2Id, team1Id);
		}

	}

	function undo(){
		clearTimeout(turnTimeout);

		return $.post(baseUrl + "/undo/", function(response){
			if(response.valid){

				if(response.redirect){
					window.location = baseUrl + "/play/";
					return;
				}

				$(".player").removeClass("active");
				$(".player[data-playerid=" + response.playerId + "]").addClass("active");
				highlightTeam();

				var awarded = $(".awarded[data-teamid=" + response.teamId + "][data-points=" + response.value + "]");
				var hits = parseInt(awarded.attr("data-hits")) - 1;
				awarded.attr("data-hits", hits);

				if(hits >= 3){
					var current = $(".score[data-teamid=" + response.teamId + "]");
					current.data("score", current.data("score") - response.value);
					current.find(".current-round-points").html(current.data("score"));
				}
				indicateClosedPoints();

				removeMarksForPoints(awarded, response.value);
			}
		});
	}

	function updateMarksPerRound(data){
		var mprs = $(".player[data-playerid=" + data.playerId + "]").find(".marks-per-round");
		mprs.find(".value .all").html(data.mpr);
		mprs.find(".value .r1").html(game >= 1 ? data.mpr1 : "-");
		mprs.find(".value .r2").html(game >= 2 ? data.mpr2 : "-");
		mprs.find(".value .r3").html(game >= 3 ? data.mpr3 : "-");
		mprs.find(".value .r4").html(game >= 4 ? data.mpr4 : "-");
		mprs.find(".value .r5").html(game >= 5 ? data.mpr5 : "-");
	}

	function indicateClosedPoints(){
		$(".points").each(function(){
			var source = $(this).removeClass("closed");
			var team1 = source.find(".awarded").first();
			var team2 = source.find(".awarded ").last();
			if(team1.attr("data-hits") >= 3 && team2.attr("data-hits") >= 3){
				source.addClass("closed");
			}
		});
	}

	$(".time-label").last().remove();
	var timeLabel = $(".time-label");

	calculateTime();
	setInterval(calculateTime, 1000);

	function calculateTime(){
		var total = Math.floor((new Date() - createdAt) / 1000);
		var hours = Math.floor(total / 60 / 60);
		var minutes = Math.floor(total / 60) % 60;
		var seconds = total % 60;
		var time = ((hours < 10) ? ("0" + hours) : hours) + ":" + ((minutes < 10) ? ("0" + minutes) : minutes) + ":" + ((seconds < 10) ? ("0" + seconds) : seconds);
		timeLabel.html(time);
	}

	$(".point-value").eq(3).on("click", function(){
		var id = markStyleIds[markStyleIdIndex];
		$(".awarded").removeClass("mark-style-" + markStyleId.val()).addClass("mark-style-" + id);
		markStyleId.attr("value", id);
		markStyleIdIndex++;
		if(markStyleIdIndex >= markStyleIds.length){
			markStyleIdIndex = 0;
		}
	});


	var numberOfMarks = {};

	function scoreMarksForPoints(source, point){
		if(!(point in numberOfMarks)){
			numberOfMarks[point] = 0;
		}

		numberOfMarks[point]++;

		source.find(".mark-counter").html(numberOfMarks[point]);
	}

	function clearMarksForPoints(){
		numberOfMarks = {};
		$(".mark-counter").empty();
	}

	function removeMarksForPoints(source, point){
		if(!(point in numberOfMarks)){
			return;
		}

		numberOfMarks[point]--;

		source.find(".mark-counter").html(numberOfMarks[point]);

		if(numberOfMarks[point] == 0){
			source.find(".mark-counter").empty();
		}
	}

});
