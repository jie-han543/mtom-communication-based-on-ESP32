# 创建数据库
create database mtom
# 使用数据库
use mtom
# 创建表
CREATE TABLE IF NOT EXISTS `temp` (
	`time` DATETIME NOT NULL,
	`temp` FLOAT NOT NULL
	)DEFAULT CHARSET=utf8;
# 插入数据
INSERT INTO `temp` (`time`, `temp`)
	VALUES (CURRENT_TIMESTAMP(), 25.8);
# 读取时间按升序排列时从第0行起20行的数据表
select * from `temp` ORDER BY `time` ASC LIMIT 0, 20;