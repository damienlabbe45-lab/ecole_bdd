# -*- coding: utf-8 -*-

"""
Classe Dao[Course]
"""

from models.course import Course
from daos.dao import Dao
from dataclasses import dataclass
from typing import Optional


@dataclass
class CourseDao(Dao[Course]):
    def create(self, course: Course) -> int:
        """Crée en BD l'entité Course correspondant au cours course

        :param course: à créer sous forme d'entité Course en BD
        :return: l'id de l'entité insérée en BD (0 si la création a échoué)
        """
        id_course: int
        teacher_id = course.teacher.id if course.teacher is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO course (name, start_date, end_date, id_teacher) VALUES (%s, %s, %s, %s)",
                    (course.name, course.start_date, course.end_date, teacher_id))
                id_course = cursor.lastrowid()
                course.id = id_course
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_course = 0

        return id_course

    def read(self, id_course: int) -> Optional[Course]:
        """Renvoit le cours correspondant à l'entité dont l'id est id_course
           (ou None s'il n'a pu être trouvé)"""
        course: Optional[Course] = None

        with Dao.connection.cursor() as cursor:
            # 1. Lecture des informations principales du cours
            cursor.execute("SELECT * FROM course WHERE id_course=%s", (id_course,))
            record = cursor.fetchone()

            if record is not None:
                course = Course(record['name'], record['start_date'], record['end_date'])
                course.id = record['id_course']

                # 2. Chargement du prof (si présent)
                if record['id_teacher'] is not None:
                    from daos.teacher_dao import TeacherDao
                    teacher = TeacherDao().read(record['id_teacher'])
                    if teacher is not None:
                        course.set_teacher(teacher)

                # 3. Chargement de la liste des élèves inscrits
                # Dans course_dao.py (méthode read)
                from models.student import Student
                from models.address import Address
                cursor.execute(
                    """
                    SELECT s.student_nbr, p.first_name, p.last_name, p.age,
                           a.id_address, a.street, a.city, a.postal_code
                    FROM student s
                    JOIN person p ON s.id_person = p.id_person
                    JOIN takes t ON s.student_nbr = t.student_nbr
                    LEFT JOIN address a ON p.id_address = a.id_address
                    WHERE t.id_course = %s
                    """,
                    (id_course,)
                )
                student_records = cursor.fetchall()
                for s_rec in student_records:
                    student = Student(
                        s_rec['first_name'],
                        s_rec['last_name'],
                        s_rec['age']
                    )
                    student.student_nbr = s_rec['student_nbr']

                    if s_rec['street'] is not None:
                        address = Address(
                            s_rec['street'],
                            s_rec['city'],
                            s_rec['postal_code']
                        )
                        address.id = s_rec['id_address']
                        student.address = address

                    course.add_student(student)
        return course

    def update(self, course: Course) -> bool:
        """Met à jour en BD l'entité Course correspondant à course, pour y correspondre

        :param course: cours déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        ...
        teacher_id = course.teacher.id if course.teacher is not None else None
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                        "UPDATE course SET name=%s, start_date=%s, end_date=%s, id_teacher= %s WHERE id_course=%s",
                        (course.name, course.start_date, course.end_date, teacher_id, course.id))
                Dao.connection.commit()
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
                cursor.execute("DELETE FROM takes WHERE id_course=%s", (course.id,))
                cursor.execute("DELETE FROM course WHERE id_course=%s", (course.id,))
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[Course]:
        """Renvoie tous les cours enregistrés en base de données avec leurs professeurs et étudiants."""
        courses: list[Course] = []
        with Dao.connection.cursor() as cursor:
            cursor.execute("SELECT id_course FROM course")
            records = cursor.fetchall()
            for record in records:
                course = self.read(record['id_course'])
                if course is not None:
                    courses.append(course)
        return courses
