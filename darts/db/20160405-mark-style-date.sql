ALTER TABLE `mark_styles`
	ADD COLUMN `createdAt` DATETIME NULL DEFAULT NULL AFTER `approved`;

ALTER TABLE `mark_styles`
	ADD COLUMN `name` VARCHAR(255) NULL DEFAULT NULL AFTER `id`;