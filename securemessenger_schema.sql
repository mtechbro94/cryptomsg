/*
SQLyog Community v8.71 
MySQL - 5.5.30 : Database - mpns04_2023
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`mpns04_2023` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `mpns04_2023`;

/*Table structure for table `feedback` */

DROP TABLE IF EXISTS `feedback`;

CREATE TABLE `feedback` (
  `fid` int(10) NOT NULL AUTO_INCREMENT,
  `uname` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`fid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `feedback` */

/*Table structure for table `message` */

DROP TABLE IF EXISTS `message`;

CREATE TABLE `message` (
  `mid` int(255) NOT NULL AUTO_INCREMENT,
  `sid` int(255) NOT NULL,
  `sname` varchar(255) NOT NULL,
  `sender` varchar(255) NOT NULL,
  `receiver` varchar(255) NOT NULL,
  `router` varchar(255) NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `pkey` varchar(255) NOT NULL DEFAULT '',
  `message` longblob NOT NULL,
  `certificate` longblob NOT NULL,
  `ce` longblob NOT NULL,
  `status` varchar(255) NOT NULL,
  PRIMARY KEY (`mid`),
  KEY `sid` (`sid`),
  CONSTRAINT `message_ibfk_1` FOREIGN KEY (`sid`) REFERENCES `userdetails` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `message` */

insert  into `message`(`mid`,`sid`,`sname`,`sender`,`receiver`,`router`,`date`,`pkey`,`message`,`certificate`,`ce`,`status`) values (2,1,'User1','user1@gmail.com','user2@gmail.com','router@gmail.com','2023-09-29 13:52:24','CSEuz35o-oxmmFlRoEsj9IVXnan_OY9j4K_BeVvI1ek=','gAAAAABlFojT_fmJehPVKPC7EbVSkJHQwO_7RnKe9vVbOA1nokeSTZdUkpdEr6tizpZCIcPpjRv17Tk9ppn1PYubjFLKcyXpThnKb3LygVtMkPlg21s7JrV64sNtdGVG5y98gaxBj-m51JAxksh2yBgORjwTInztdFAvQv12A_08OLFqw4NGLWGr3MhmChxRo-ZymrinoUuJUYm0-JTIY7cCfIGSwxgeGhCVKQkZGpJZUfiKeZ3kwOdlHPpt865jjDI7_IzjGFexHmAeN0ExDv7F6fok1qhip3lh9-tZfIV0-sJV8NRGGuCoGmuD0cqdMdmpkFb79QAD70Uu3RtB2sQ0VU6qbwxqfh7v0JbcK_2yrUqIq9Uvv_wuXjv5ThoZaRqVxFpuD0DbZWJ9smXfL2mEtizmYLEMlw==','1695975635','','Received'),(3,1,'User1','user1@gmail.com','user3@gmail.com','router@gmail.com','2023-09-29 15:01:26','0KkvrG1SF5Qh0oeM7LbQN3vFqUIBI1rqH7LCV2Zjdu8=','gAAAAABlFpk-YVH06h6V4ZeePqaVBQSaE_eIobm4Gq3zDdOyssqEQO6ubhziwyw8s92nNUPHF7w31jpMyZTbG94zpLAS2Z1q7ETJsC8hrtSuu1galKfT5qaq2TftIjNoGeC5S9JTzkkZ9IQCXPcVY-vGGM6JCaNk869yai13ckm_ex8v5w1ApcxLZoHHFGTg1F_o_ZPNR1Qr4owt_pAlnPFbyY7n1aVZ99ExZrw2CgT2FVSgBqlKUIajCu2i0ibX-RvTHHzhBBWe5NcBQHRwbnEGaHvKcsNBe0wxP8zdXfeBN3GB0z86F_2Ut5uhjpYczxh0op_Vujl359i9SOHYwnrCBvlismEIAiQql14vJ-MjL4XXFzxbA4LAUOqv-ALRIu80SQtLaDUrVpBF4bDaVj5wau5_u7H4-w==','1695979838','','Received');

/*Table structure for table `userdetails` */

DROP TABLE IF EXISTS `userdetails`;

CREATE TABLE `userdetails` (
  `uid` int(10) NOT NULL AUTO_INCREMENT,
  `uname` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `mobile` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `userdetails` */

insert  into `userdetails`(`uid`,`uname`,`email`,`password`,`dob`,`mobile`,`status`) values (1,'User1','user1@gmail.com','User1@123','2000-01-01','7891234560','Accepted'),(2,'User2','user2@gmail.com','User2@123','1999-09-09','1234567890','Accepted'),(3,'User3','user3@gmail.com','User3@123','1998-03-03','7531597410','Accepted');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
