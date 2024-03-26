SELECT census.SECTOR, cp.*, census.multipolygon
FROM `UCaglary`.`community profiles compiled` AS cp
LEFT JOIN `UCaglary`.`census 2019 data` AS census ON census.Name = UPPER(cp.`Community Name`)
limit 202;
