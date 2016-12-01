
CREATE TABLE `games` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`matchId` int(11) DEFAULT NULL,
	`game` int(11) DEFAULT NULL,
	`data` VARCHAR(255)  NULL DEFAULT NULL,
	`start` int(11) DEFAULT NULL,
	`turn` int(11) DEFAULT NULL,
	`round` int(11) DEFAULT NULL,
	`complete` tinyint(1) DEFAULT NULL,
	`winner` int(11) DEFAULT NULL,
	`winnerScore` int(11) DEFAULT NULL,
	`loser` int(11) DEFAULT NULL,
	`loserScore` int(11) DEFAULT NULL,
	`createdAt` datetime DEFAULT NULL,
	`completedAt` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `fk_games_matches` (`matchId`),
	CONSTRAINT `fk_games_matches` FOREIGN KEY (`matchId`) REFERENCES `matches` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	KEY `fk_games_players` (`turn`),
	CONSTRAINT `fk_games_players` FOREIGN KEY (`turn`) REFERENCES `players` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	KEY `fk_games_players_start` (`start`),
	CONSTRAINT `fk_games_players_start` FOREIGN KEY (`start`) REFERENCES `players` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	KEY `fk_games_winner` (`winner`),
	CONSTRAINT `fk_games_winner` FOREIGN KEY (`winner`) REFERENCES `teams` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
	KEY `fk_games_loser` (`loser`),
	CONSTRAINT `fk_games_loser` FOREIGN KEY (`loser`) REFERENCES `teams` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;
