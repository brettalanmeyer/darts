-- --------------------------------------------------------
-- Host:                         10.9.0.160
-- Server version:               5.5.46-0ubuntu0.14.04.2 - (Ubuntu)
-- Server OS:                    debian-linux-gnu
-- HeidiSQL Version:             9.3.0.4984
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Dumping structure for table darts-production.games
CREATE TABLE IF NOT EXISTS `games` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modeId` int(11) DEFAULT NULL,
  `players` int(11) DEFAULT NULL,
  `game` int(11) DEFAULT NULL,
  `round` int(11) DEFAULT NULL,
  `ready` tinyint(4) DEFAULT NULL,
  `turn` int(11) DEFAULT NULL,
  `complete` tinyint(1) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_games_modes` (`modeId`),
  CONSTRAINT `fk_games_modes` FOREIGN KEY (`modeId`) REFERENCES `modes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.marks
CREATE TABLE IF NOT EXISTS `marks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gameId` int(11) DEFAULT NULL,
  `teamId` int(11) DEFAULT NULL,
  `playerId` int(11) DEFAULT NULL,
  `game` int(11) DEFAULT NULL,
  `round` int(11) DEFAULT NULL,
  `twenty` tinyint(4) DEFAULT NULL,
  `nineteen` tinyint(4) DEFAULT NULL,
  `eighteen` tinyint(4) DEFAULT NULL,
  `seventeen` tinyint(4) DEFAULT NULL,
  `sixteen` tinyint(4) DEFAULT NULL,
  `fifteen` tinyint(4) DEFAULT NULL,
  `bullseye` tinyint(4) DEFAULT NULL,
  `value` int(11) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_scores_games` (`gameId`),
  KEY `fk_scores_teams` (`teamId`),
  KEY `fk_scores_players` (`playerId`),
  CONSTRAINT `fk_scores_games` FOREIGN KEY (`gameId`) REFERENCES `games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_scores_players` FOREIGN KEY (`playerId`) REFERENCES `players` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_scores_teams` FOREIGN KEY (`teamId`) REFERENCES `teams` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.modes
CREATE TABLE IF NOT EXISTS `modes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `mode` varchar(255) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.players
CREATE TABLE IF NOT EXISTS `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.results
CREATE TABLE IF NOT EXISTS `results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gameId` int(11) DEFAULT NULL,
  `teamId` int(11) DEFAULT NULL,
  `game` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `win` tinyint(1) DEFAULT NULL,
  `loss` tinyint(1) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_results_games` (`gameId`),
  KEY `fk_results_teams` (`teamId`),
  CONSTRAINT `fk_results_games` FOREIGN KEY (`gameId`) REFERENCES `games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_results_teams` FOREIGN KEY (`teamId`) REFERENCES `teams` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.teams
CREATE TABLE IF NOT EXISTS `teams` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gameId` int(11) DEFAULT NULL,
  `win` tinyint(1) DEFAULT NULL,
  `loss` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_teams_games` (`gameId`),
  CONSTRAINT `fk_teams_games` FOREIGN KEY (`gameId`) REFERENCES `games` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.


-- Dumping structure for table darts-production.teams_players
CREATE TABLE IF NOT EXISTS `teams_players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teamId` int(11) DEFAULT NULL,
  `playerId` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_teams_players_players` (`teamId`),
  KEY `fk_teams_players_teams` (`playerId`),
  CONSTRAINT `fk_teams_players_players` FOREIGN KEY (`playerId`) REFERENCES `players` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_teams_players_teams` FOREIGN KEY (`teamId`) REFERENCES `teams` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
