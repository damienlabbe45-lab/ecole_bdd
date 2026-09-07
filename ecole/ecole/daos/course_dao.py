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
        ...
        id_course: int
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO course (name, start_date, end_date) VALUES (%s)",
                    (course.name, course.start_date, course.end_date))
                id_course = cursor.lastrowid()
        except Exception as e:
            print(e)
            id_course = 0

        return id_course

    def read(self, id_course: int) -> Optional[Course]:
        """Renvoit le cours correspondant à l'entité dont l'id est id_course
           (ou None s'il n'a pu être trouvé)"""
        course: Optional[Course]
        
        with Dao.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course WHERE id_course=%s", (id_course,))
            record = cursor.fetchone()
        if record is not None:
            course = Course(record['name'], record['start_date'], record['end_date'])
            course.id = record['id_course']
        else:
            course = None

        return course

    def update(self, course: Course) -> bool:
        """Met à jour en BD l'entité Course correspondant à course, pour y correspondre

        :param course: cours déjà mis à jour en mémoire
        :return: True si la mise à jour a pu être réalisée
        """
        ...
        try:
            with Dao.connection.cursor() as cursor:
                if course.teacher is not None:
                    cursor.execute(
                        "UPDATE course SET name=%s, start_date=%s, end_date=%s, id_teacher= %s WHERE id_course=%s",
                        course.name, course.start_date, course.end_date, course.teacher.id)
                else:
                    cursor.execute(
                        "UPDATE course SET name=%s, start_date=%s, end_date=%s WHERE id_course=%s",
                        course.name, course.start_date, course.end_date)
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
