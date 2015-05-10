-- MySQL dump 10.13  Distrib 5.5.35, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: history2
-- ------------------------------------------------------
-- Server version	5.5.35-0ubuntu0.12.04.2

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
-- Table structure for table `templateDayk`
--

DROP TABLE IF EXISTS `templateDayk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `templateDayk` (
  `Time` date NOT NULL,
  `Open` float NOT NULL DEFAULT '0',
  `Highest` float NOT NULL DEFAULT '0',
  `Lowest` float NOT NULL DEFAULT '0',
  `Close` float NOT NULL DEFAULT '0',
  `Avg` float DEFAULT '0',
  `SellVol` int(11) DEFAULT '0',
  `BuyVol` int(11) DEFAULT '0',
  `Tr` float DEFAULT NULL,
  `Atr` float DEFAULT NULL,
  PRIMARY KEY (`Time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `templateDayk`
--

LOCK TABLES `templateDayk` WRITE;
/*!40000 ALTER TABLE `templateDayk` DISABLE KEYS */;
/*!40000 ALTER TABLE `templateDayk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `templateMink`
--

DROP TABLE IF EXISTS `templateMink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `templateMink` (
  `Time` datetime NOT NULL,
  `Open` float NOT NULL DEFAULT '0',
  `Highest` float NOT NULL DEFAULT '0',
  `Lowest` float NOT NULL DEFAULT '0',
  `Close` float NOT NULL DEFAULT '0',
  `Avg` float DEFAULT '0',
  `SellVol` int(11) DEFAULT '0',
  `BuyVol` int(11) DEFAULT '0',
  `Tr` float DEFAULT NULL,
  `Atr` float DEFAULT NULL,
  PRIMARY KEY (`Time`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `templateMink`
--

LOCK TABLES `templateMink` WRITE;
/*!40000 ALTER TABLE `templateMink` DISABLE KEYS */;
/*!40000 ALTER TABLE `templateMink` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-05-10 13:06:50
