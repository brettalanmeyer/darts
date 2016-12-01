ALTER TABLE `players`
	ADD COLUMN `enabled` TINYINT NULL DEFAULT NULL AFTER `name`;

UPDATE `players` SET `enabled` = 1;
