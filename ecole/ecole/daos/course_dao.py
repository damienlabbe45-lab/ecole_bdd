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
                cursor.execute("SELECT student_nbr FROM takes WHERE id_course=%s", (id_course,))
                takes_records = cursor.fetchall()
                if takes_records is not None:
                    from daos.student_dao import StudentDao
                    student_dao = StudentDao()
                    for take in takes_records:
                        student = student_dao.read(take['student_nbr'])
                        if student is not None:
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
                cursor.execute("DELETE FROM course WHERE id_course=%s", (course.id,))
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False
