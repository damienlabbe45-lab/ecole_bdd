# -*- coding: utf-8 -*-

"""
Classe Dao[Student]
"""

from models.student import Student
from models.address import Address
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentDao(Dao[Student]):
    def create(self, student: Student) -> int:
        id_student: int = 0
        address_id = student.address.id if student.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Insertion dans person
                cursor.execute(
                    "INSERT IGNORE INTO person (first_name, last_name, age, id_address) VALUES (%s, %s, %s, %s)",
                    (student.first_name, student.last_name, student.age, address_id)
                )
                id_person = cursor.lastrowid

                # 2. Insertion dans student
                cursor.execute(
                    "INSERT IGNORE INTO student (student_nbr, id_person) VALUES (%s, %s)",
                    (id_person, id_person)
                )
                id_student = id_person
                student.student_nbr = id_student
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_student = 0

        return id_student

    def read(self, student_nbr: int) -> str | None:
        query = """
                    SELECT CONCAT(
                        c.name, ' (', c.start_date, ' – ', c.end_date, '), enseigné par ',
                        COALESCE(CONCAT(p_t.first_name, ' ', p_t.last_name), "pas d'enseignant affecté"),
                        IF(COUNT(p_s.id_person) > 0, CONCAT('\nÉlèves :\n  - ', GROUP_CONCAT(CONCAT(p_s.first_name, 
                        ' ', p_s.last_name) SEPARATOR '\n  - ')), '\n  pas d\'étudiant')
                    )
                    FROM course c
                    LEFT JOIN teacher t ON c.id_teacher = t.id_teacher
                    LEFT JOIN person p_t ON t.id_person = p_t.id_person
                    LEFT JOIN takes tk ON c.id_course = tk.id_course
                    LEFT JOIN student s ON tk.student_nbr = s.student_nbr
                    LEFT JOIN person p_s ON s.id_person = p_s.id_person
                    where s.student_nbr = %s
                """
        with self.connection.cursor() as cursor:
            cursor.execute(query, student_nbr)
            record = cursor.fetchone()
            return record[0] if record is not None else None

    def update(self, student: Student) -> bool:
        """Met à jour en BD l'entité Student correspondant à student"""
        address_id = student.address.id if student.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Mise à jour des informations personnelles
                cursor.execute(
                    """
                    UPDATE person p
                    JOIN student s ON p.id_person = s.id_person
                    SET p.first_name = %s, p.last_name = %s, p.age = %s, p.id_address = %s
                    WHERE s.student_nbr = %s
                    """,
                    (student.first_name, student.last_name, student.age, address_id, student.student_nbr)
                )

                # 2. Resynchronisation des cours suivis (takes)
                cursor.execute("DELETE FROM takes WHERE student_nbr = %s", (student.student_nbr,))
                for course in student.courses_taken:
                    if course.id is not None:
                        cursor.execute(
                            "INSERT INTO takes (student_nbr, id_course) VALUES (%s, %s)",
                            (student.student_nbr, course.id)
                        )

                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, student: Student) -> bool:
        """Supprime en BD l'entité Student correspondant à student"""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id_person, p.id_address 
                    FROM person p 
                    JOIN student s ON p.id_person = s.id_person 
                    WHERE s.student_nbr = %s
                    """,
                    (student.student_nbr,)
                )
                record = cursor.fetchone()

                cursor.execute("DELETE FROM takes WHERE student_nbr=%s", (student.student_nbr,))
                cursor.execute("DELETE FROM student WHERE student_nbr=%s", (student.student_nbr,))
                cursor.execute("DELETE FROM person WHERE id_person=%s", (record[0],))
                cursor.execute("DELETE FROM address WHERE id_address=%s", (record[1],))
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[str]:
        """Récupère chaque cours sous forme d'une chaîne texte unique formatée par la BD."""
        query = """
            SELECT CONCAT(
                c.name, ' (', c.start_date, ' – ', c.end_date, '), enseigné par ',
                COALESCE(CONCAT(p_t.first_name, ' ', p_t.last_name), "pas d'enseignant affecté"),
                IF(COUNT(p_s.id_person) > 0, CONCAT('\nÉlèves :\n  - ', GROUP_CONCAT(CONCAT(p_s.first_name, 
                ' ', p_s.last_name) SEPARATOR '\n  - ')), '\n  pas d\'étudiant')
            )
            FROM course c
            LEFT JOIN teacher t ON c.id_teacher = t.id_teacher
            LEFT JOIN person p_t ON t.id_person = p_t.id_person
            LEFT JOIN takes tk ON c.id_course = tk.id_course
            LEFT JOIN student s ON tk.student_nbr = s.student_nbr
            LEFT JOIN person p_s ON s.id_person = p_s.id_person
            GROUP BY c.id_course;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
