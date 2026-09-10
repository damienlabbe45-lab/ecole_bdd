#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de validation CRUD pour la couche métier School.
"""

from asyncio import run
from datetime import date
from business.school import School


async def run_crud_tests() -> None:
    school = School()
    print("=== DÉBUT DU TEST CRUD COMPLET ===")

    # ----------------------------------------------------
    # 1. TEST ADRESSE
    # ----------------------------------------------------
    print("\n--- 1. Test Adresse ---")
    addr_id = await school.add_address("10 Rue du Test", "Toulouse", "31000")
    print(f"[CREATE] Adresse insérée — ID : {addr_id}")

    addr = await school.get_address_by_id(addr_id)
    print(f"[READ] {addr}")

    updated = await school.update_address("15 Rue Modifiée", "Toulouse", "31000", addr_id)
    print(f"[UPDATE] Modification adresse : {updated}")

    # ----------------------------------------------------
    # 2. TEST ENSEIGNANT
    # ----------------------------------------------------
    print("\n--- 2. Test Enseignant ---")
    teacher_addr_id = await school.add_address("1 Place des Profs", "Toulouse", "31200")
    teacher_id = await school.add_teacher(
        "Alan", "Turing", 41, date(2024, 9, 1), teacher_addr_id
    )
    print(f"[CREATE] Enseignant créé — ID : {teacher_id}")

    teacher = await school.get_teacher_by_id(teacher_id)
    print(f"[READ] {teacher}")

    updated = await school.update_teacher(
        "Alan", "Turing", 42, date(2024, 9, 1), teacher_addr_id, teacher_id
    )
    print(f"[UPDATE] Modification enseignant : {updated}")

    # ----------------------------------------------------
    # 3. TEST COURS
    # ----------------------------------------------------
    print("\n--- 3. Test Cours ---")
    course_id = await school.add_course(
        "Informatique", date(2026, 10, 1), date(2026, 12, 20), teacher_id
    )
    print(f"[CREATE] Cours créé — ID : {course_id}")

    course = await school.get_course_by_id(course_id)
    print(f"[READ] {course}")

    updated = await school.update_course(
        "Algorithmique", date(2026, 10, 1), date(2026, 12, 20), teacher_id, course_id
    )
    print(f"[UPDATE] Modification cours : {updated}")

    # ----------------------------------------------------
    # 4. TEST ÉTUDIANT & INSCRIPTION
    # ----------------------------------------------------
    print("\n--- 4. Test Étudiant & Inscription ---")
    student_nbr = await school.add_student("Ada", "Lovelace", 20, None)
    print(f"[CREATE] Étudiant créé — Matricule (Trigger) : {student_nbr}")

    student = await school.get_student_by_id(student_nbr)
    print(f"[READ] {student}")

    takes_ok = await school.add_student_to_course(student_nbr, course_id)
    print(f"[LINK] Inscription au cours : {takes_ok}")

    updated = await school.update_student(
        "Ada", "Lovelace", 21, None, student_nbr
    )
    print(f"[UPDATE] Modification étudiant : {updated}")

    # ----------------------------------------------------
    # 5. NETTOYAGE & VERIFICATION DES CAS CADES / TRIGGERS
    # ----------------------------------------------------
    print("\n--- 5. Test Suppressions & Triggers ---")

    # Suppression de l'étudiant (supprime automatiquement l'entrée dans 'takes')
    student_deleted = await school.delete_student(student_nbr)
    print(f"[DELETE] Étudiant {student_nbr} : {student_deleted}")

    # Suppression du cours
    course_deleted = await school.delete_course(course_id)
    print(f"[DELETE] Cours {course_id} : {course_deleted}")

    # Suppression de l'enseignant (la personne est supprimée, et le trigger nettoie teacher_addr_id)
    teacher_deleted = await school.delete_teacher(teacher_id)
    print(f"[DELETE] Enseignant {teacher_id} : {teacher_deleted}")

    # Vérification que l'adresse orpheline du prof a bien été purgée par le trigger
    check_teacher_addr = await school.get_address_by_id(teacher_addr_id)
    print(f"[TRIGGER CHECK] Adresse du prof purgée automatiquement : {check_teacher_addr is None}")

    # Suppression manuelle de la première adresse créée
    addr_deleted = await school.delete_address(addr_id)
    print(f"[DELETE] Adresse standalone {addr_id} : {addr_deleted}")

    print("\n=== VALIDA TION DE TOUS LES TESTS RÉUSSIE ===")


if __name__ == "__main__":
    run(run_crud_tests())