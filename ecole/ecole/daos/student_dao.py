# -*- coding: utf-8 -*-

"""
Classe Dao[Student]
"""

from models.student import Student
from models.course import Course
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
                    "INSERT INTO person (first_name, last_name, age, id_adress) VALUES (%s, %s, %s, %s)",
                    (student.first_name, student.last_name, student.age, address_id)
                )
                id_person = cursor.lastrowid()

                # 2. Insertion dans student
                cursor.execute(
                    "INSERT INTO student (id_person) VALUES (%s)",
                    (id_person,)
                )
                id_student = cursor.lastrowid() or id_person
                student.student_nbr = id_student
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_student = 0

        return id_student

    def read(self, id_student: int) -> Optional[Student]:
        student: Optional[Student] = None

        with Dao.connection.cursor() as cursor:
            # Requête unique avec JOIN pour récupérer l'étudiant et son adresse
            cursor.execute(
                """
                SELECT p.*, a.street, a.city, a.postal_code
                FROM student s
                JOIN person p ON s.id_person = p.id_person
                LEFT JOIN adress a ON p.id_adress = a.id_adress
                WHERE s.id_person = %s
                """,
                (id_student,)
            )
            record_person = cursor.fetchone()

            if record_person is not None:
                # Instanciation (address est en init=False)
                student = Student(
                    record_person['first_name'],
                    record_person['last_name'],
                    record_person['age']
                )
                student.student_nbr = id_student

                if record_person['street'] is not None:
                    student.address = Address(
                        record_person['street'],
                        record_person['city'],
                        record_person['postal_code']
                    )

                # Chargement des cours suivis
                cursor.execute(
                    "SELECT id_course FROM takes WHERE id_student=%s",
                    (id_student,)
                )
                takes_records = cursor.fetchall()
                if takes_records:
                    from daos.course_dao import CourseDao
                    course_dao = CourseDao()
                    for take in takes_records:
                        course = course_dao.read(take['id_course'])
                        if course is not None:
                            student.add_course(course)

        return student

    def update(self, course: Student) -> bool:
        """Met à jour en BD l'entité Course correspondant à course, pour y correspondre

        :param course: cours déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        ...
        try:
            with Dao.connection.cursor() as cursor:
                if Course.teacher is not None:
                    cursor.execute(
                        "UPDATE course SET name=%s, start_date=%s, end_date=%s, id_teacher= %s WHERE id_course=%s",
                        Course.name, Course.start_date, Course.end_date, Course.teacher.id)
                else:
                    cursor.execute(
                        "UPDATE course SET name=%s, start_date=%s, end_date=%s WHERE id_course=%s",
                        Course.name, Course.start_date, Course.end_date)
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, course: Course) -> bool:
        """Supprime en BD l'entité Course correspondant à course

        :param course: cours dont l'entité Course correspondante est à supprimer
        :return: True si la suppression a pu être réalisée
        """
        ...
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute("DELETE FROM course WHERE id_course=%s", (course.id,))
            return True
        except Exception as e:
            print(e)
            return False