-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema Project
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema Project
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Project` DEFAULT CHARACTER SET utf8 ;
USE `Project` ;

-- -----------------------------------------------------
-- Table `Project`.`Sensors`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`Sensors` (
  `idSensors` INT NOT NULL AUTO_INCREMENT,
  `SensorName` VARCHAR(45) NULL,
  PRIMARY KEY (`idSensors`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Project`.`SensorSettings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`SensorSettings` (
  `idSensorSettings` INT NOT NULL AUTO_INCREMENT,
  `SensorID` INT NULL,
  `UpperLimit` VARCHAR(45) NULL,
  `LowerLimit` VARCHAR(45) NULL,
  `Active` TINYINT NULL,
  `ActuatorPin` INT NULL,
  PRIMARY KEY (`idSensorSettings`),
  INDEX `fk_SensorSettings_Sensors_idx` (`SensorID` ASC),
  CONSTRAINT `fk_SensorSettings_Sensors`
    FOREIGN KEY (`SensorID`)
    REFERENCES `Project`.`Sensors` (`idSensors`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Project`.`SensorData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`SensorData` (
  `idSensorData` INT NOT NULL AUTO_INCREMENT,
  `DateTime` DATETIME(4) NULL,
  `Value` VARCHAR(45) NULL,
  `SensorID` INT NULL,
  PRIMARY KEY (`idSensorData`),
  INDEX `fk_SensorData_Sensors1_idx` (`SensorID` ASC),
  CONSTRAINT `fk_SensorData_Sensors1`
    FOREIGN KEY (`SensorID`)
    REFERENCES `Project`.`Sensors` (`idSensors`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Project`.`Users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`Users` (
  `idUsers` INT NOT NULL,
  `UserName` VARCHAR(45) NULL,
  `Password` VARCHAR(45) NULL,
  PRIMARY KEY (`idUsers`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Project`.`TimeLimit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`TimeLimit` (
  `idTimeLimit` INT NOT NULL,
  `startTime` TIME NULL,
  `stopTime` TIME NULL,
  PRIMARY KEY (`idTimeLimit`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Project`.`TimeLimit_has_Sensors`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Project`.`TimeLimit_has_Sensors` (
  `TimeLimit_idTimeLimit` INT NOT NULL,
  `Sensors_idSensors` INT NOT NULL,
  PRIMARY KEY (`TimeLimit_idTimeLimit`, `Sensors_idSensors`),
  INDEX `fk_TimeLimit_has_Sensors_Sensors1_idx` (`Sensors_idSensors` ASC),
  INDEX `fk_TimeLimit_has_Sensors_TimeLimit1_idx` (`TimeLimit_idTimeLimit` ASC),
  CONSTRAINT `fk_TimeLimit_has_Sensors_TimeLimit1`
    FOREIGN KEY (`TimeLimit_idTimeLimit`)
    REFERENCES `Project`.`TimeLimit` (`idTimeLimit`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_TimeLimit_has_Sensors_Sensors1`
    FOREIGN KEY (`Sensors_idSensors`)
    REFERENCES `Project`.`Sensors` (`idSensors`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
