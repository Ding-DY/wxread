-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: wxread
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `task_history`
--

DROP TABLE IF EXISTS `task_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_id` int NOT NULL,
  `start_time` timestamp NOT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_message` text COLLATE utf8mb4_unicode_ci,
  `read_minutes` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `config_id` (`config_id`),
  CONSTRAINT `task_history_ibfk_1` FOREIGN KEY (`config_id`) REFERENCES `user_configs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_history`
--

LOCK TABLES `task_history` WRITE;
/*!40000 ALTER TABLE `task_history` DISABLE KEYS */;
INSERT INTO `task_history` VALUES (7,2,'2024-12-25 02:06:05','2024-12-25 02:46:51','stopped',NULL,NULL),(8,2,'2024-12-25 02:06:28','2024-12-25 02:46:51','stopped',NULL,NULL),(9,2,'2024-12-25 02:07:46','2024-12-25 02:07:46','failed','run_read_task() got an unexpected keyword argument \'config_id\'',NULL),(10,2,'2024-12-25 02:09:12','2024-12-25 02:46:51','stopped',NULL,NULL),(11,2,'2024-12-25 02:12:19','2024-12-25 02:46:51','stopped',NULL,NULL),(12,2,'2024-12-25 02:31:10','2024-12-25 02:46:51','stopped',NULL,NULL),(13,2,'2024-12-25 02:40:29','2024-12-25 02:46:51','stopped',NULL,NULL),(14,2,'2024-12-25 02:40:49','2024-12-25 02:46:51','stopped',NULL,NULL),(15,2,'2024-12-25 02:42:10','2024-12-25 02:46:51','stopped',NULL,NULL),(16,2,'2024-12-25 02:43:00','2024-12-25 02:46:51','stopped',NULL,NULL),(17,2,'2024-12-25 02:43:00','2024-12-25 02:46:51','stopped',NULL,NULL),(18,2,'2024-12-25 02:46:10','2024-12-25 02:47:10','success',NULL,60),(19,2,'2024-12-25 02:46:10','2024-12-25 02:46:51','stopped',NULL,NULL),(20,2,'2024-12-25 02:54:25','2024-12-25 03:00:32','stopped',NULL,NULL),(21,2,'2024-12-25 02:56:41','2024-12-25 03:00:32','stopped',NULL,NULL),(22,2,'2024-12-25 03:02:23','2024-12-25 08:50:15','failed','HTTPSConnectionPool(host=\'weread.qq.com\', port=443): Max retries exceeded with url: /web/book/read (Caused by NameResolutionError(\"<urllib3.connection.HTTPSConnection object at 0x000001F988A66F70>: Failed to resolve \'weread.qq.com\' ([Errno 11001] getaddrinfo failed)\"))',NULL),(23,2,'2024-12-25 08:51:02','2024-12-25 15:16:15','failed','HTTPSConnectionPool(host=\'weread.qq.com\', port=443): Max retries exceeded with url: /web/book/read (Caused by NameResolutionError(\"<urllib3.connection.HTTPSConnection object at 0x0000017AE8180FA0>: Failed to resolve \'weread.qq.com\' ([Errno 11001] getaddrinfo failed)\"))',NULL),(24,2,'2024-12-25 08:51:02','2024-12-25 15:16:15','failed','HTTPSConnectionPool(host=\'weread.qq.com\', port=443): Max retries exceeded with url: /web/book/read (Caused by NameResolutionError(\"<urllib3.connection.HTTPSConnection object at 0x0000017AE8180FA0>: Failed to resolve \'weread.qq.com\' ([Errno 11001] getaddrinfo failed)\"))',NULL),(25,2,'2024-12-25 15:45:13','2024-12-25 15:45:13','failed','HTTPSConnectionPool(host=\'weread.qq.com\', port=443): Max retries exceeded with url: /web/book/read (Caused by ProxyError(\'Unable to connect to proxy\', FileNotFoundError(2, \'No such file or directory\')))',NULL),(26,2,'2024-12-25 15:45:13','2024-12-25 15:45:13','failed','HTTPSConnectionPool(host=\'weread.qq.com\', port=443): Max retries exceeded with url: /web/book/read (Caused by ProxyError(\'Unable to connect to proxy\', FileNotFoundError(2, \'No such file or directory\')))',NULL),(27,2,'2024-12-25 15:45:29','2024-12-25 15:47:01','success',NULL,500),(28,2,'2024-12-25 15:45:29','2024-12-25 15:46:38','stopped',NULL,NULL),(29,2,'2024-12-25 15:48:07',NULL,'running',NULL,NULL);
/*!40000 ALTER TABLE `task_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_configs`
--

DROP TABLE IF EXISTS `user_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `headers` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `cookies` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `read_num` int DEFAULT '120',
  `push_method` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pushplus_token` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telegram_bot_token` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telegram_chat_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_running` tinyint(1) DEFAULT '0',
  `last_run` timestamp NULL DEFAULT NULL,
  `schedule_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `schedule_time` time DEFAULT NULL,
  `schedule_days` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_configs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_configs`
--

LOCK TABLES `user_configs` WRITE;
/*!40000 ALTER TABLE `user_configs` DISABLE KEYS */;
INSERT INTO `user_configs` VALUES (2,2,'{\"accept\": \"application/json, text/plain, */*\", \"accept-language\": \"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6\", \"baggage\": \"sentry-environment=production,sentry-release=dev-1730698697208,sentry-public_key=ed67ed71f7804a038e898ba54bd66e44,sentry-trace_id=a6d36fc040b3412b9dbcfb091f734904\", \"content-type\": \"application/json;charset=UTF-8\", \"origin\": \"https://weread.qq.com\", \"priority\": \"u=1, i\", \"referer\": \"https://weread.qq.com/web/reader/ce032b305a9bc1ce0b0dd2a\", \"sec-ch-ua\": \"\\\"Microsoft Edge\\\";v=\\\"131\\\", \\\"Chromium\\\";v=\\\"131\\\", \\\"Not_A Brand\\\";v=\\\"24\\\"\", \"sec-ch-ua-mobile\": \"?0\", \"sec-ch-ua-platform\": \"\\\"Windows\\\"\", \"sec-fetch-dest\": \"empty\", \"sec-fetch-mode\": \"cors\", \"sec-fetch-site\": \"same-origin\", \"sentry-trace\": \"a6d36fc040b3412b9dbcfb091f734904-b74168d8a35bc0d6\", \"user-agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0\"}','{\"pgv_pvid\": \"9613943045\", \"RK\": \"ivVk4jIGXg\", \"ptcz\": \"0f344e527827f4fb17bb59a63dc8b936f7a125a65eae5457555a759077cb123b\", \"_qimei_uuid42\": \"187030839321001a0915ef08c4dd170bf50ab04649\", \"_qimei_fingerprint\": \"7db23f18d9045dfaa58b02a7bb107b59\", \"_qimei_h38\": \"fded35fe0915ef08c4dd170b0200000b318703\", \"_qimei_q36\": \"\", \"_hp2_id.1405110977\": \"%7B%22userId%22%3A%227268511932661891%22%2C%22pageviewId%22%3A%225945508434807284%22%2C%22sessionId%22%3A%225522128187892942%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D\", \"wr_fp\": \"3254396589\", \"wr_gid\": \"262418371\", \"_clck\": \"1s0y0g5|1|frc|0\", \"wr_theme\": \"white\", \"pac_uid\": \"0_pAMT64N7GZeND\", \"wr_vid\": \"914011286\", \"wr_rt\": \"web%40V8EQkia9WyF5yP6W3Pl_AL\", \"wr_localvid\": \"fce32e908367ab496fce66b\", \"wr_name\": \"%E5%AE%87%E6%9E%AB\", \"wr_gender\": \"0\", \"wr_skey\": \"taVPJM2l\", \"wr_pf\": \"undefined\", \"wr_avatar\": \"https%3A%2F%2Fwx.qlogo.cn%2Fmmhead%2F1MLz0YkS76FjgSE3AV4aMSRnFIuHqUTQxaibNNzRzVpADSveAsltH3nkcYtJiaQbgsyewmezFTYsI%2F0\"}',1000,'','','','',1,1,'2024-12-25 15:48:07',NULL,NULL,NULL,'2024-12-25 02:06:03','2024-12-25 15:48:07');
/*!40000 ALTER TABLE `user_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','123456','2024-12-25 01:09:07'),(2,'root','pbkdf2:sha256:600000$X1HwVUSadvksCGea$cf6f32fb193b6a4afedc6a1229d88a5be685339ac349af5757db904a4ee917c6','2024-12-25 01:10:38');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-25 23:50:42
