-- ------------------------------------------- Create the Books Database Schema -------------------------------------------------
CREATE DATABASE Library;            
-- ------------------------------------------- Create the Tables / Collections --------------------------------------------------
-- ------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE `Library`.`LibraryUser` (
  `LibraryUserID` varchar(45) NOT NULL,
  `LibraryUserName` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  PRIMARY KEY (`LibraryUserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`AdminUser` (
  `AdminUserID` varchar(45) NOT NULL,
  `AdminUserName` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  PRIMARY KEY (`AdminUserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`Book` (
  `BookID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(500) DEFAULT NULL,
  `ISBN` varchar(45) DEFAULT NULL,
  `PageCount` int NOT NULL DEFAULT '0',
  `PublishedDate` datetime DEFAULT NULL,
  `Status` varchar(45) DEFAULT NULL,
  `Authors` varchar(500) DEFAULT NULL,
  `Categories` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`BookID`)
) ENGINE=InnoDB AUTO_INCREMENT=797 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`Borrow` (
  `BookID` int NOT NULL AUTO_INCREMENT,
  `LibraryUserID` varchar(45) NOT NULL,
  `DueDate` datetime DEFAULT NULL,
  PRIMARY KEY (`BookID`),
  FOREIGN KEY (`BookID`) REFERENCES `Book`(`BookID`),
  FOREIGN KEY (`LibraryUserID`) REFERENCES `LibraryUser`(`LibraryUserID`)
) ENGINE=InnoDB AUTO_INCREMENT=797 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`Reserve` (
  `BookID` int NOT NULL AUTO_INCREMENT,
  `LibraryUserID` varchar(45) NOT NULL,
  PRIMARY KEY (`BookID`),
  FOREIGN KEY (`BookID`) REFERENCES `Book`(`BookID`),
  FOREIGN KEY (`LibraryUserID`) REFERENCES `LibraryUser`(`LibraryUserID`)
) ENGINE=InnoDB AUTO_INCREMENT=797 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`Fine` (
  `LibraryUserID` varchar(45) NOT NULL,
  `AmountCharged` double NOT NULL DEFAULT '0',
  PRIMARY KEY (`LibraryUserID`),
  FOREIGN KEY (`LibraryUserID`) REFERENCES `LibraryUser`(`LibraryUserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Library`.`Payment` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `LibraryUserID` varchar(45) NOT NULL,
  `AmountPaid` double NOT NULL DEFAULT '0',
  `DateOfPayment` datetime DEFAULT NULL,
  `PaymentType` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`PaymentID`),
  FOREIGN KEY (`LibraryUserID`) REFERENCES `LibraryUser`(`LibraryUserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
