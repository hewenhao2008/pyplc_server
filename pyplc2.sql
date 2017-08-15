-- MySQL dump 10.13  Distrib 5.7.18, for osx10.11 (x86_64)
--
-- Host: localhost    Database: pyplc
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interface_log`
--

DROP TABLE IF EXISTS `interface_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interface_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) DEFAULT NULL,
  `host_url` varchar(32) DEFAULT NULL,
  `method` varchar(8) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `param` text,
  `old_data` text,
  `new_data_id` int(11) DEFAULT NULL,
  `endpoint` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interface_log`
--

LOCK TABLES `interface_log` WRITE;
/*!40000 ALTER TABLE `interface_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `interface_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `station_id` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `note` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `station_id` (`station_id`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`station_id`) REFERENCES `yjstationinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs`
--

LOCK TABLES `logs` WRITE;
/*!40000 ALTER TABLE `logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parameter`
--

DROP TABLE IF EXISTS `parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parameter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable_id` int(11) DEFAULT NULL,
  `param_name` varchar(32) DEFAULT NULL,
  `unit` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `variable_id` (`variable_id`),
  CONSTRAINT `parameter_ibfk_1` FOREIGN KEY (`variable_id`) REFERENCES `yjvariableinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter`
--

LOCK TABLES `parameter` WRITE;
/*!40000 ALTER TABLE `parameter` DISABLE KEYS */;
/*!40000 ALTER TABLE `parameter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `query_group`
--

DROP TABLE IF EXISTS `query_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `query_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `query_group`
--

LOCK TABLES `query_group` WRITE;
/*!40000 ALTER TABLE `query_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `query_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `description` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles_users`
--

DROP TABLE IF EXISTS `roles_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles_users` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `roles_users_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `roles_users_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles_users`
--

LOCK TABLES `roles_users` WRITE;
/*!40000 ALTER TABLE `roles_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `email` varchar(32) DEFAULT NULL,
  `pw_hash` varchar(128) DEFAULT NULL,
  `login_count` int(11) DEFAULT NULL,
  `last_login_ip` varchar(64) DEFAULT NULL,
  `last_login_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `values`
--

DROP TABLE IF EXISTS `values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable_id` int(11) DEFAULT NULL,
  `value` varchar(128) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `variable_id` (`variable_id`),
  CONSTRAINT `values_ibfk_1` FOREIGN KEY (`variable_id`) REFERENCES `yjvariableinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `values`
--

LOCK TABLES `values` WRITE;
/*!40000 ALTER TABLE `values` DISABLE KEYS */;
/*!40000 ALTER TABLE `values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `var_alarm_info`
--

DROP TABLE IF EXISTS `var_alarm_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `var_alarm_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable_id` int(11) DEFAULT NULL,
  `alarm_type` int(11) DEFAULT NULL,
  `note` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `variable_id` (`variable_id`),
  CONSTRAINT `var_alarm_info_ibfk_1` FOREIGN KEY (`variable_id`) REFERENCES `yjvariableinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `var_alarm_info`
--

LOCK TABLES `var_alarm_info` WRITE;
/*!40000 ALTER TABLE `var_alarm_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `var_alarm_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `var_alarm_log`
--

DROP TABLE IF EXISTS `var_alarm_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `var_alarm_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alarm_id` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `confirm` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alarm_id` (`alarm_id`),
  CONSTRAINT `var_alarm_log_ibfk_1` FOREIGN KEY (`alarm_id`) REFERENCES `var_alarm_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `var_alarm_log`
--

LOCK TABLES `var_alarm_log` WRITE;
/*!40000 ALTER TABLE `var_alarm_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `var_alarm_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `variables_queries`
--

DROP TABLE IF EXISTS `variables_queries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `variables_queries` (
  `query_id` int(11) NOT NULL,
  `variable_id` int(11) NOT NULL,
  PRIMARY KEY (`query_id`,`variable_id`),
  KEY `variable_id` (`variable_id`),
  CONSTRAINT `variables_queries_ibfk_1` FOREIGN KEY (`query_id`) REFERENCES `query_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `variables_queries_ibfk_2` FOREIGN KEY (`variable_id`) REFERENCES `yjvariableinfo` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `variables_queries`
--

LOCK TABLES `variables_queries` WRITE;
/*!40000 ALTER TABLE `variables_queries` DISABLE KEYS */;
/*!40000 ALTER TABLE `variables_queries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yjgroupinfo`
--

DROP TABLE IF EXISTS `yjgroupinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yjgroupinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(20) DEFAULT NULL,
  `note` varchar(100) DEFAULT NULL,
  `upload` tinyint(1) DEFAULT NULL,
  `upload_cycle` int(11) DEFAULT NULL,
  `ten_id` varchar(255) DEFAULT NULL,
  `item_id` varchar(20) DEFAULT NULL,
  `plc_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `plc_id` (`plc_id`),
  CONSTRAINT `yjgroupinfo_ibfk_1` FOREIGN KEY (`plc_id`) REFERENCES `yjplcinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yjgroupinfo`
--

LOCK TABLES `yjgroupinfo` WRITE;
/*!40000 ALTER TABLE `yjgroupinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `yjgroupinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yjplcinfo`
--

DROP TABLE IF EXISTS `yjplcinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yjplcinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `plc_name` varchar(30) DEFAULT NULL,
  `note` varchar(200) DEFAULT NULL,
  `ip` varchar(30) DEFAULT NULL,
  `mpi` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `plc_type` varchar(20) DEFAULT NULL,
  `ten_id` varchar(255) DEFAULT NULL,
  `item_id` varchar(20) DEFAULT NULL,
  `rack` int(11) DEFAULT NULL,
  `slot` int(11) DEFAULT NULL,
  `tcp_port` int(11) DEFAULT NULL,
  `station_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `station_id` (`station_id`),
  CONSTRAINT `yjplcinfo_ibfk_1` FOREIGN KEY (`station_id`) REFERENCES `yjstationinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yjplcinfo`
--

LOCK TABLES `yjplcinfo` WRITE;
/*!40000 ALTER TABLE `yjplcinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `yjplcinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yjstationinfo`
--

DROP TABLE IF EXISTS `yjstationinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yjstationinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `station_name` varchar(30) DEFAULT NULL,
  `mac` varchar(20) DEFAULT NULL,
  `ip` varchar(20) DEFAULT NULL,
  `note` varchar(200) DEFAULT NULL,
  `id_num` varchar(200) DEFAULT NULL,
  `plc_count` int(11) DEFAULT NULL,
  `ten_id` varchar(255) DEFAULT NULL,
  `item_id` varchar(20) DEFAULT NULL,
  `con_time` int(11) DEFAULT NULL,
  `modification` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yjstationinfo`
--

LOCK TABLES `yjstationinfo` WRITE;
/*!40000 ALTER TABLE `yjstationinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `yjstationinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `yjvariableinfo`
--

DROP TABLE IF EXISTS `yjvariableinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `yjvariableinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable_name` varchar(20) DEFAULT NULL,
  `db_num` int(11) DEFAULT NULL,
  `address` float DEFAULT NULL,
  `data_type` varchar(10) DEFAULT NULL,
  `rw_type` int(11) DEFAULT NULL,
  `upload` int(11) DEFAULT NULL,
  `acquisition_cycle` int(11) DEFAULT NULL,
  `server_record_cycle` int(11) DEFAULT NULL,
  `note` varchar(50) DEFAULT NULL,
  `ten_id` varchar(200) DEFAULT NULL,
  `item_id` varchar(20) DEFAULT NULL,
  `write_value` int(11) DEFAULT NULL,
  `area` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `yjvariableinfo_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `yjgroupinfo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `yjvariableinfo`
--

LOCK TABLES `yjvariableinfo` WRITE;
/*!40000 ALTER TABLE `yjvariableinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `yjvariableinfo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-08-15 16:04:19
