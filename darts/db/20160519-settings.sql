
CREATE TABLE `settings` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`startDate` DATETIME NULL DEFAULT NULL,
	`endDate` DATETIME NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

INSERT INTO `darts_development`.`settings` (`id`) VALUES (1);
