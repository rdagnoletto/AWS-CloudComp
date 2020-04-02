-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ece1779_A1
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ece1779_A1
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ece1779_A1` DEFAULT CHARACTER SET utf8 ;
USE `ece1779_A1` ;

-- -----------------------------------------------------
-- Table `ece1779_A1`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ece1779_A1`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(16) NOT NULL,
  `password` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id`, `username`));


-- -----------------------------------------------------
-- Table `ece1779_A1`.`category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ece1779_A1`.`images` (
  `user_id` INT NOT NULL,
  `img_name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `id`
    FOREIGN KEY (`user_id`)
    REFERENCES `ece1779_A1`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
