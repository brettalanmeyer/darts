
ALTER TABLE `settings`
	CHANGE COLUMN `startDate` `startDate` DATE NULL DEFAULT NULL AFTER `id`,
	CHANGE COLUMN `endDate` `endDate` DATE NULL DEFAULT NULL AFTER `startDate`;
