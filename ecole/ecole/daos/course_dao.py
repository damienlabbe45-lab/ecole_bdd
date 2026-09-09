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
                    "INSERT IGNORE INTO course (name, start_date, end_date, id_teacher) VALUES (%s, %s, %s, %s)",
                    (course.name, course.start_date, course.end_date, teacher_id))
                id_course = cursor.lastrowid
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
            cursor.execute("SELECT name, start_date, end_date, id_teacher FROM course WHERE id_course=%s", (id_course,))
            record = cursor.fetchone()

            if record is not None:
                course = Course(record[0], record[1], record[2])
                course.id = id_course

                # 2. Chargement du prof (si présent)
                if record[3] is not None:
                    from daos.teacher_dao import TeacherDao
                    teacher = TeacherDao().read(record[3])
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
                        s_rec[1],
                        s_rec[2],
                        s_rec[3]
                    )
                    student.student_nbr = s_rec[0]

                    if s_rec[5] is not None:
                        address = Address(
                            s_rec[5],
                            s_rec[6],
                            s_rec[7]
                        )
                        address.id = s_rec[4]
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

    # daos/course_dao.py

    def read_all(self) -> list[str]:
        """Récupère chaque cours sous forme d'une chaîne texte unique formatée par la BD."""
        query = """
            SELECT CONCAT(
                c.name, ' (', c.start_date, ' – ', c.end_date, '), enseigné par ',
                COALESCE(CONCAT(p_t.first_name, ' ', p_t.last_name), "pas d'enseignant affecté"),
                IF(COUNT(p_s.id_person) > 0, CONCAT('\nÉlèves :\n  - ', GROUP_CONCAT(CONCAT(p_s.first_name, ' ',
                 p_s.last_name) SEPARATOR '\n  - ')),  '\n  pas d\'étudiant'
                )
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
