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

    def read(self, student_nbr: int) -> Optional[Student]:
        student: Optional[Student] = None

        with Dao.connection.cursor() as cursor:
            # 1. Récupération des infos de l'étudiant, sa personne et son adresse
            cursor.execute(
                """
                SELECT s.student_nbr, p.first_name, p.last_name, p.age,
                       a.id_address, a.street, a.city, a.postal_code
                FROM student s
                JOIN person p ON s.id_person = p.id_person
                LEFT JOIN address a ON p.id_address = a.id_address
                WHERE s.student_nbr = %s
                """,
                (student_nbr,)
            )
            record = cursor.fetchone()

            if record is not None:
                student = Student(
                    record['first_name'],
                    record['last_name'],
                    record['age']
                )
                student.student_nbr = record['student_nbr']

                if record['street'] is not None:
                    address = Address(
                        record['street'],
                        record['city'],
                        record['postal_code']
                    )
                    address.id = record['id_address']
                    student.address = address
                cursor.execute(
                    """
                    SELECT c.id_course, c.name, c.start_date, c.end_date
                    FROM course c
                    JOIN takes t ON c.id_course = t.id_course
                    WHERE t.student_nbr = %s
                    """,
                    (student_nbr,)
                )
                from models.course import Course
                course_records = cursor.fetchall()
                for c_rec in course_records:
                    course = Course(
                        c_rec['name'],
                        c_rec['start_date'],
                        c_rec['end_date']
                    )
                    course.id = c_rec['id_course']
                    student.add_course(course)

        return student

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
                cursor.execute("DELETE FROM person WHERE id_person=%s", (record["id_person"],))
                cursor.execute("DELETE FROM address WHERE id_address=%s", (record["id_address"],))
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[tuple]:
        """Récupère tous les étudiants avec leur adresse et leurs cours sous forme de données brutes."""
        with self.connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                s.student_nbr,
                CONCAT(p.first_name, ' ', p.last_name) AS etudiant,
                CONCAT(a.street, ', ', a.postal_code, ' ', a.city) AS adresse,
                GROUP_CONCAT(c.name SEPARATOR ', ') AS cours_suivis
            FROM student s
            JOIN person p ON s.id_person = p.id_person
            LEFT JOIN address a ON p.id_address = a.id_address
            LEFT JOIN takes t ON s.student_nbr = t.student_nbr
            LEFT JOIN course c ON t.id_course = c.id_course
            GROUP BY s.student_nbr;
        """)
            return cursor.fetchall()
