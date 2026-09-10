DROP DATABASE IF EXISTS `ecole_test`;
CREATE DATABASE IF NOT EXISTS `ecole_test` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ecole_test`;

-- --------------------------------------------------------
-- Table `address`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `address`;
CREATE TABLE IF NOT EXISTS `address` (
  `id_address` INT NOT NULL AUTO_INCREMENT,
  `street` VARCHAR(80) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `postal_code` VARCHAR(5) NOT NULL,
  PRIMARY KEY (`id_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `address` (`id_address`, `street`, `city`, `postal_code`) VALUES
(1, '12 rue des Pinsons', 'Castanet', '31320'),
(2, '43 avenue Jean Zay', 'Toulouse', '31200'),
(3, '7 impasse des Coteaux', 'Cornebarrieu', '31150');

-- --------------------------------------------------------
-- Table `person`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `person`;
CREATE TABLE IF NOT EXISTS `person` (
  `id_person` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `age` TINYINT NOT NULL,
  `id_address` INT DEFAULT NULL,
  PRIMARY KEY (`id_person`),
  KEY `fk_person_address` (`id_address`),
  CONSTRAINT `fk_person_address` FOREIGN KEY (`id_address`) REFERENCES `address` (`id_address`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `person` (`id_person`, `first_name`, `last_name`, `age`, `id_address`) VALUES
(1, 'Paul', 'Dubois', 12, 1),
(2, 'Valérie', 'Dumont', 13, 2),
(3, 'Louis', 'Berthot', 11, 3),
(4, 'Victor', 'Hugo', 23, NULL),
(5, 'Jules', 'Michelet', 32, NULL),
(6, 'Sophie', 'Germain', 25, NULL),
(7, 'Marie', 'Curie', 31, NULL),
(8, 'William', 'Shakespeare', 34, NULL),
(9, 'Michel', 'Platini', 42, NULL);

-- --------------------------------------------------------
-- Table `student`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE IF NOT EXISTS `student` (
  `student_nbr` BIGINT NOT NULL,
  `id_person` INT NOT NULL,
  PRIMARY KEY (`student_nbr`),
  UNIQUE KEY `id_person` (`id_person`),
  CONSTRAINT `fk_student_person` FOREIGN KEY (`id_person`) REFERENCES `person` (`id_person`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `student` (`student_nbr`, `id_person`) VALUES
(1, 1),
(2, 2),
(3, 3);

-- --------------------------------------------------------
-- Table `teacher`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE IF NOT EXISTS `teacher` (
  `id_teacher` INT NOT NULL AUTO_INCREMENT,
  `hiring_date` DATE NOT NULL,
  `id_person` INT NOT NULL,
  PRIMARY KEY (`id_teacher`),
  UNIQUE KEY `id_person` (`id_person`),
  CONSTRAINT `fk_teacher_person` FOREIGN KEY (`id_person`) REFERENCES `person` (`id_person`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `teacher` (`id_teacher`, `hiring_date`, `id_person`) VALUES
(1, '2023-09-04', 4),
(2, '2023-09-04', 5),
(3, '2023-09-04', 6),
(4, '2023-09-04', 7),
(5, '2023-09-04', 8),
(6, '2023-09-04', 9);

-- --------------------------------------------------------
-- Table `course`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE IF NOT EXISTS `course` (
  `id_course` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `id_teacher` INT DEFAULT NULL,
  PRIMARY KEY (`id_course`),
  KEY `fk_course_teacher` (`id_teacher`),
  CONSTRAINT `fk_course_teacher` FOREIGN KEY (`id_teacher`) REFERENCES `teacher` (`id_teacher`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `course` (`id_course`, `name`, `start_date`, `end_date`, `id_teacher`) VALUES
(1, 'Français', '2024-01-29', '2024-02-16', 1),
(2, 'Histoire', '2024-02-05', '2024-02-16', 2),
(3, 'Géographie', '2024-02-05', '2024-02-16', 2),
(4, 'Mathématiques', '2024-02-12', '2024-03-08', 3),
(5, 'Physique', '2024-02-19', '2024-03-08', 4),
(6, 'Chimie', '2024-02-26', '2024-03-15', 4),
(7, 'Anglais', '2024-02-12', '2024-02-24', 5),
(8, 'Sport', '2024-03-04', '2024-03-15', 6);

-- --------------------------------------------------------
-- Table `takes`
-- --------------------------------------------------------
DROP TABLE IF EXISTS `takes`;
CREATE TABLE IF NOT EXISTS `takes` (
  `student_nbr` BIGINT NOT NULL,
  `id_course` INT NOT NULL,
  PRIMARY KEY (`student_nbr`, `id_course`),
  KEY `fk_takes_course` (`id_course`),
  CONSTRAINT `fk_takes_student` FOREIGN KEY (`student_nbr`) REFERENCES `student` (`student_nbr`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_takes_course` FOREIGN KEY (`id_course`) REFERENCES `course` (`id_course`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `takes` (`student_nbr`, `id_course`) VALUES
(2, 1),
(2, 2),
(1, 3),
(3, 3),
(3, 4),
(1, 5),
(3, 5),
(2, 6),
(1, 7),
(3, 8);

-- --------------------------------------------------------
-- TRIGGERS
-- --------------------------------------------------------

DELIMITER //

-- 1. Génération automatique du matricule étudiant (Année + Séquence)
DELIMITER //

DROP TRIGGER IF EXISTS trg_after_person_update_address //

CREATE TRIGGER trg_after_person_update_address
AFTER UPDATE ON person
FOR EACH ROW
BEGIN
    -- On agit uniquement si l'ancienne adresse existait et qu'elle a changé
    IF OLD.id_address IS NOT NULL AND (NEW.id_address IS NULL OR NEW.id_address <> OLD.id_address) THEN
        -- S'il ne reste aucune personne avec OLD.id_address dans toute la table
        IF NOT EXISTS (
            SELECT 1
            FROM person
            WHERE id_address = OLD.id_address
        ) THEN
            DELETE FROM address WHERE id_address = OLD.id_address;
        END IF;
    END IF;
END //

DELIMITER ; //

-- 2. Nettoyage de l'adresse après suppression d'une personne si personne d'autre ne l'utilise
CREATE TRIGGER trg_after_person_delete_address
AFTER DELETE ON person
FOR EACH ROW
BEGIN
    IF OLD.id_address IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM person WHERE id_address = OLD.id_address) THEN
            DELETE FROM address WHERE id_address = OLD.id_address;
        END IF;
    END IF;
END //

-- 3. Nettoyage de l'ancienne adresse si une personne change d'adresse ou la retire
CREATE TRIGGER trg_after_person_update_address
AFTER UPDATE ON person
FOR EACH ROW
BEGIN
    IF OLD.id_address IS NOT NULL AND (NEW.id_address IS NULL OR NEW.id_address <> OLD.id_address) THEN
        IF NOT EXISTS (SELECT 1 FROM person WHERE id_address = OLD.id_address) THEN
            DELETE FROM address WHERE id_address = OLD.id_address;
        END IF;
    END IF;
END //

DELIMITER ;