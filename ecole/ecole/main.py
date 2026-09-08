#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application de gestion d'une école
"""

from business.school import School
from daos.student_dao import StudentDao


def main() -> None:
    """Programme principal."""
    print("""\
--------------------------
Bienvenue dans notre école
--------------------------""")

    school: School = School()

    # Initialisation et insertion en base de données
    #school.init_db()

    # Affichage de la liste des cours (lus directement depuis la BD)
    school.display_courses_list()

    # Lecture ponctuelle par id depuis la BD
    print(school.get_course_by_id(1))
    print(school.get_course_by_id(2))
    print(school.get_course_by_id(9))
    # --- Test StudentDao ---
    print("\n--- Test récupération des élèves ---")
    student_dao = StudentDao()

    # Lecture d'un élève par son ID (ex: 1)
    student = student_dao.read(1)

    if student:
        print(f"Élève trouvé : {student.first_name} {student.last_name} ({student.age} ans)")
        if student.address:
            print(f"Adresse : {student.address.street}, {student.address.postal_code} {student.address.city}")
        else:
            print("Aucune adresse rattachée.")

        print("Cours suivis :")
        courses = getattr(student, 'courses_taken', getattr(student, 'courses', []))
        if courses:
            for course in courses:
                print(f" - {course.name}")
        else:
            print(" - Aucun cours inscrit.")
    else:
        print("Élève non trouvé.")


if __name__ == '__main__':
    main()
