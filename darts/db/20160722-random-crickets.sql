
ALTER TABLE `modes` ADD COLUMN `orderNum` INT(11) NULL DEFAULT NULL AFTER `alias`;

INSERT INTO `modes` (`name`, `mode`, `alias`, `orderNum`, `enabled`)
VALUES ('Random Crickets', 'random-crickets', 'cricket', 1, 1);


UPDATE `modes`
SET `orderNum` = 1
WHERE `mode` = 'cricket';

UPDATE `modes`
SET `orderNum` = 2
WHERE `mode` = 'random-crickets';

UPDATE `modes`
SET `orderNum` = 3
WHERE `mode` = 'around-the-world';

UPDATE `modes`
SET `orderNum` = 4
WHERE `mode` = '301';

UPDATE `modes`
SET `orderNum` = 5
WHERE `mode` = '501';

UPDATE `modes`
SET `orderNum` = 6
WHERE `mode` = '701';

UPDATE `modes`
SET `orderNum` = 7
WHERE `mode` = '901';


ALTER TABLE `matches` ADD COLUMN `data` VARCHAR(255) NULL DEFAULT NULL AFTER `complete`;
