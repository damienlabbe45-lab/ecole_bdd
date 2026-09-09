# -*- coding: utf-8 -*-

"""
Classe Dao[Teacher]
"""

from dataclasses import dataclass
from typing import Optional
from daos.dao import Dao
from models.teacher import Teacher
from models.address import Address
from models.course import Course


@dataclass
class TeacherDao(Dao[Teacher]):
    def create(self, teacher: Teacher) -> int:
        """Crée en BD l'entité Teacher correspondant à teacher"""
        id_teacher: int = 0
        address_id = teacher.address.id if teacher.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Insertion dans person
                cursor.execute(
                    "INSERT IGNORE INTO person (first_name, last_name, age, id_address) VALUES (%s, %s, %s, %s)",
                    (teacher.first_name, teacher.last_name, teacher.age, address_id)
                )
                id_person = cursor.lastrowid

                # 2. Insertion dans teacher
                cursor.execute(
                    "INSERT IGNORE INTO teacher (hiring_date, id_person) VALUES (%s, %s)",
                    (teacher.hiring_date, id_person)
                )
                id_teacher = cursor.lastrowid
                teacher.id = id_teacher
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_teacher = 0

        return id_teacher

    def read(self, id_teacher: int) -> Optional[Teacher]:
        """Renvoie le professeur correspondant à id_teacher (ou None)"""
        teacher: Optional[Teacher] = None

        with Dao.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT t.hiring_date, p.first_name, p.last_name, p.age,
                       a.id_address, a.street, a.city, a.postal_code
                FROM teacher t
                JOIN person p ON t.id_person = p.id_person
                LEFT JOIN address a ON p.id_address = a.id_address
                WHERE t.id_teacher = %s
                """,
                (id_teacher,)
            )
            record = cursor.fetchone()

            if record is not None:
                teacher = Teacher(
                    record[1],
                    record[2],
                    record[3],
                    record[0]
                )
                teacher.id = record[id_teacher]

                if record[5] is not None:
                    address = Address(
                        record[5],
                        record[6],
                        record[7]
                    )
                    address.id = record[4]
                    teacher.address = address

                # Chargement des cours (instanciation avec 3 arguments)
                cursor.execute(
                    "SELECT id_course, name, start_date, end_date FROM course WHERE id_teacher = %s",
                    (id_teacher,)
                )
                course_records = cursor.fetchall()
                for c_rec in course_records:
                    course = Course(
                        c_rec[1],
                        c_rec[2],
                        c_rec[3]
                    )
                    course.id = c_rec[0]
                    teacher.add_course(course)

        return teacher

    def add_course(self, teacher: Teacher, course: Course) -> bool:
        """Associe un cours à un enseignant dans la table course."""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE course SET id_teacher = %s WHERE id_course = %s",
                    (teacher.id, course.id)
                )
                Dao.connection.commit()
                teacher.add_course(course)
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, teacher: Teacher) -> bool:
        """Met à jour l'entité Teacher en BD"""
        address_id = teacher.address.id if teacher.address is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE person p
                    JOIN teacher t ON p.id_person = t.id_person
                    SET p.first_name = %s, p.last_name = %s, p.age = %s, p.id_address = %s
                    WHERE t.id_teacher = %s
                    """,
                    (teacher.first_name, teacher.last_name, teacher.age, address_id, teacher.id)
                )

                cursor.execute(
                    "UPDATE teacher SET hiring_date = %s WHERE id_teacher = %s",
                    (teacher.hiring_date, teacher.id)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, teacher: Teacher) -> bool:
        """Supprime l'entité Teacher en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id_person 
                    FROM person p 
                    JOIN teacher t ON p.id_person = t.id_person 
                    WHERE t.id_teacher = %s
                    """,
                    (teacher.id,)
                )
                record = cursor.fetchone()

                if record:
                    cursor.execute("DELETE FROM teacher WHERE id_teacher = %s", (teacher.id,))
                    cursor.execute("DELETE FROM person WHERE id_person = %s", (record[0],))
                    Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[Teacher]:
        """Renvoie tous les profs enregistrés en base de données avec leurs cours."""
        teachers: list[Teacher] = []
        with Dao.connection.cursor() as cursor:
            cursor.execute("SELECT id_teacher FROM teacher")
            records = cursor.fetchall()
            for record in records:
                teacher = self.read(record[0])
                if teacher is not None:
                    teachers.append(teacher)
        return teachers
