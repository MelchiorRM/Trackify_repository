-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: trackifydb
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `book_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `genre` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `language` varchar(100) DEFAULT NULL,
  `publisher` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  `reviews` text,
  `coverart` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`book_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cinema`
--

DROP TABLE IF EXISTS `cinema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cinema` (
  `cinema_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `genre` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `director` varchar(255) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `language` varchar(100) DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  `reviews` text,
  `description` text,
  `coverart` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`cinema_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_media_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  KEY `user_id` (`user_id`),
  KEY `user_media_id` (`user_media_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_media_id`) REFERENCES `user_media` (`user_media_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `diary_entries`
--

DROP TABLE IF EXISTS `diary_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diary_entries` (
  `entry_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `media_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`entry_id`),
  KEY `idx_diary_user_id` (`user_id`),
  KEY `idx_diary_media_id` (`media_id`),
  KEY `idx_diary_created_at` (`created_at`),
  CONSTRAINT `diary_entries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `diary_entries_ibfk_2` FOREIGN KEY (`media_id`) REFERENCES `user_media` (`user_media_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `follows`
--

DROP TABLE IF EXISTS `follows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `follows` (
  `follow_id` int NOT NULL AUTO_INCREMENT,
  `follower_id` int NOT NULL,
  `followed_id` int NOT NULL,
  PRIMARY KEY (`follow_id`),
  UNIQUE KEY `follower_id` (`follower_id`,`followed_id`),
  KEY `followed_id` (`followed_id`),
  CONSTRAINT `follows_ibfk_1` FOREIGN KEY (`follower_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `follows_ibfk_2` FOREIGN KEY (`followed_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `likes` (
  `like_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_media_id` int NOT NULL,
  PRIMARY KEY (`like_id`),
  UNIQUE KEY `user_id` (`user_id`,`user_media_id`),
  KEY `user_media_id` (`user_media_id`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`user_media_id`) REFERENCES `user_media` (`user_media_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `list_items`
--

DROP TABLE IF EXISTS `list_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `list_items` (
  `list_item_id` int NOT NULL AUTO_INCREMENT,
  `list_id` int NOT NULL,
  `cinema_id` int DEFAULT NULL,
  `book_id` int DEFAULT NULL,
  `music_id` int DEFAULT NULL,
  `notes` text,
  `added_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`list_item_id`),
  KEY `list_id` (`list_id`),
  KEY `cinema_id` (`cinema_id`),
  KEY `book_id` (`book_id`),
  KEY `music_id` (`music_id`),
  CONSTRAINT `list_items_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `lists` (`list_id`) ON DELETE CASCADE,
  CONSTRAINT `list_items_ibfk_2` FOREIGN KEY (`cinema_id`) REFERENCES `cinema` (`cinema_id`) ON DELETE CASCADE,
  CONSTRAINT `list_items_ibfk_3` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE,
  CONSTRAINT `list_items_ibfk_4` FOREIGN KEY (`music_id`) REFERENCES `music` (`music_id`) ON DELETE CASCADE,
  CONSTRAINT `check_media_type` CHECK ((((`cinema_id` is not null) and (`book_id` is null) and (`music_id` is null)) or ((`cinema_id` is null) and (`book_id` is not null) and (`music_id` is null)) or ((`cinema_id` is null) and (`book_id` is null) and (`music_id` is not null))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lists`
--

DROP TABLE IF EXISTS `lists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lists` (
  `list_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text,
  `is_private` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`list_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `lists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `message_id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `recipient_id` int NOT NULL,
  `content` text NOT NULL,
  `user_media_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`message_id`),
  KEY `sender_id` (`sender_id`),
  KEY `recipient_id` (`recipient_id`),
  KEY `user_media_id` (`user_media_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`user_media_id`) REFERENCES `user_media` (`user_media_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `music`
--

DROP TABLE IF EXISTS `music`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `music` (
  `music_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `artist` varchar(255) DEFAULT NULL,
  `genre` varchar(100) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `language` varchar(100) DEFAULT NULL,
  `label` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  `reviews` text,
  `coverart` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`music_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `message` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `read` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`notification_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ratings` (
  `rating_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_media_id` int NOT NULL,
  `rating` int NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rating_id`),
  UNIQUE KEY `unique_rating` (`user_id`,`user_media_id`),
  KEY `user_media_id` (`user_media_id`),
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `ratings_ibfk_2` FOREIGN KEY (`user_media_id`) REFERENCES `user_media` (`user_media_id`) ON DELETE CASCADE,
  CONSTRAINT `rating_value` CHECK (((`rating` >= 1) and (`rating` <= 5)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_media_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`review_id`),
  KEY `user_id` (`user_id`),
  KEY `user_media_id` (`user_media_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_media_id`) REFERENCES `user_media` (`user_media_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_media`
--

DROP TABLE IF EXISTS `user_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_media` (
  `user_media_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `cinema_id` int DEFAULT NULL,
  `music_id` int DEFAULT NULL,
  `book_id` int DEFAULT NULL,
  `media_type` enum('cinema','music','book') NOT NULL,
  `done` tinyint(1) DEFAULT '0',
  `planned` tinyint(1) DEFAULT '0',
  `date_consumed` datetime DEFAULT NULL,
  `review` text,
  `rating` decimal(2,1) DEFAULT NULL,
  `tags` json DEFAULT NULL,
  PRIMARY KEY (`user_media_id`),
  KEY `user_id` (`user_id`),
  KEY `cinema_id` (`cinema_id`),
  KEY `music_id` (`music_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `user_media_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `user_media_ibfk_2` FOREIGN KEY (`cinema_id`) REFERENCES `cinema` (`cinema_id`) ON DELETE CASCADE,
  CONSTRAINT `user_media_ibfk_3` FOREIGN KEY (`music_id`) REFERENCES `music` (`music_id`) ON DELETE CASCADE,
  CONSTRAINT `user_media_ibfk_4` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `join_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `profile_picture` varchar(256) DEFAULT NULL,
  `bio` text,
  `theme` varchar(20) DEFAULT 'light',
  `notifications_enabled` tinyint(1) DEFAULT '1',
  `email_notifications` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-18 17:31:55
