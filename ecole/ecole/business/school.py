# -*- coding: utf-8 -*-

"""
Classe School
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from daos.address_dao import AddressDao
from daos.course_dao import CourseDao
from daos.student_dao import StudentDao
from daos.teacher_dao import TeacherDao
from models.address import Address
from models.course import Course
from models.student import Student
from models.teacher import Teacher


@dataclass
class School:
    """Couche métier de l'application de gestion d'une école,
    interagissant directement avec la base de données via les DAO."""

    def add_course(self, course: Course) -> int:
        """Ajout du cours en base de données."""
        return CourseDao().create(course)

    def add_teacher(self, teacher: Teacher) -> int:
        """Ajout de l'enseignant en base de données (et de son adresse si présente)."""
        if teacher.address and teacher.address.id is None:
            AddressDao().create(teacher.address)
        return TeacherDao().create(teacher)

    def add_student(self, student: Student) -> int:
        """Ajout de l'élève en base de données (et de son adresse si présente)."""
        if student.address and student.address.id is None:
            AddressDao().create(student.address)
        return StudentDao().create(student)

    def display_courses_list(self) -> None:
        """Affichage de la liste des cours depuis la BD avec :
        - leur enseignant
        - la liste des élèves le suivant"""
        courses = CourseDao().read_all()
        for course in courses:
            print(f"cours de {course}")
            for student in course.students_taking_it:
                print(f"- {student}")
            print()

    @staticmethod
    def get_course_by_id(id_course: int) -> Optional[Course]:
        """Récupère un cours par son identifiant depuis la BD."""
        return CourseDao().read(id_course)

    def init_db(self) -> None:
        """Initialisation et persistance du jeu de données de test en base de données."""
        address_dao = AddressDao()
        student_dao = StudentDao()
        teacher_dao = TeacherDao()
        course_dao = CourseDao()

        # 1. Création des étudiants et persistance des adresses
        paul = Student('Paul', 'Dubois', 12)
        valerie = Student('Valérie', 'Dumont', 13)
        louis = Student('Louis', 'Berthot', 11)

        paul.address = Address('12 rue des Pinsons', 'Castanet', 31320)
        valerie.address = Address('43 avenue Jean Zay', 'Toulouse', 31200)
        louis.address = Address('7 impasse des Coteaux', 'Cornebarrieu', 31150)

        for student in [paul, valerie, louis]:
            address_dao.create(student.address)
            student_dao.create(student)

        # 2. Création des cours en BD
        francais = Course("Français", date(2024, 1, 29), date(2024, 2, 16))
        histoire = Course("Histoire", date(2024, 2, 5), date(2024, 2, 16))
        geographie = Course("Géographie", date(2024, 2, 5), date(2024, 2, 16))
        mathematiques = Course("Mathématiques", date(2024, 2, 12), date(2024, 3, 8))
        physique = Course("Physique", date(2024, 2, 19), date(2024, 3, 8))
        chimie = Course("Chimie", date(2024, 2, 26), date(2024, 3, 15))
        anglais = Course("Anglais", date(2024, 2, 12), date(2024, 2, 24))
        sport = Course("Sport", date(2024, 3, 4), date(2024, 3, 15))

        for course in [francais, histoire, geographie, mathematiques, physique, chimie, anglais, sport]:
            course_dao.create(course)

        # 3. Création des enseignants en BD
        victor = Teacher('Victor', 'Hugo', 23, date(2023, 9, 4))
        jules = Teacher('Jules', 'Michelet', 32, date(2023, 9, 4))
        sophie = Teacher('Sophie', 'Germain', 25, date(2023, 9, 4))
        marie = Teacher('Marie', 'Curie', 31, date(2023, 9, 4))
        william = Teacher('William', 'Shakespeare', 34, date(2023, 9, 4))
        michel = Teacher('Michel', 'Platini', 42, date(2023, 9, 4))

        for teacher in [victor, jules, sophie, marie, william, michel]:
            teacher_dao.create(teacher)

        # 4. Association des enseignants aux cours (via TeacherDao)
        teacher_dao.add_course(victor, francais)
        teacher_dao.add_course(jules, histoire)
        teacher_dao.add_course(jules, geographie)
        teacher_dao.add_course(sophie, mathematiques)
        teacher_dao.add_course(marie, physique)
        teacher_dao.add_course(marie, chimie)
        teacher_dao.add_course(william, anglais)
        teacher_dao.add_course(michel, sport)

        # 5. Association des élèves aux cours (mise à jour de la table `takes` via StudentDao)
        for course in [geographie, physique, anglais]:
            paul.add_course(course)
        student_dao.update(paul)

        for course in [francais, histoire, chimie]:
            valerie.add_course(course)
        student_dao.update(valerie)

        for course in [mathematiques, physique, geographie, sport]:
            louis.add_course(course)
        student_dao.update(louis)
