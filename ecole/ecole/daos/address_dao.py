# -*- coding: utf-8 -*-

"""
Classe Dao[Address]
"""

from dataclasses import dataclass
from typing import Optional
from daos.dao import Dao
from models.address import Address


@dataclass
class AddressDao(Dao[Address]):
    def create(self, address: Address) -> int:
        """Crée en BD l'entité Address correspondant à l'adresse"""
        id_address: int = 0
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT IGNORE INTO address (street, city, postal_code) VALUES (%s, %s, %s)",
                    (address.street, address.city, address.postal_code)
                )
                id_address = cursor.lastrowid
                address.id = id_address
                Dao.connection.commit()
        except Exception as e:
            print(e)
            id_address = 0

        return id_address

    def read(self, id_address: int) -> Optional[Address]:
        """Renvoie l'adresse correspondant à id_address (ou None)"""
        address: Optional[Address] = None

        with Dao.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM address WHERE id_address = %s",
                (id_address,)
            )
            record = cursor.fetchone()

            if record is not None:
                address = Address(
                    record['street'],
                    record['city'],
                    record['postal_code']
                )
                address.id = record['id_address']

        return address

    def update(self, address: Address) -> bool:
        """Met à jour l'entité Address en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE address 
                    SET street = %s, city = %s, postal_code = %s 
                    WHERE id_address = %s
                    """,
                    (address.street, address.city, address.postal_code, address.id)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self, address: Address) -> bool:
        """Supprime l'entité Address en BD"""
        try:
            with Dao.connection.cursor() as cursor:
                # 1. Libérer la référence dans person pour éviter le conflit de clé étrangère
                cursor.execute(
                    "UPDATE person SET id_address = NULL WHERE id_address = %s",
                    (address.id,)
                )
                # 2. Supprimer l'adresse
                cursor.execute(
                    "DELETE FROM address WHERE id_address = %s",
                    (address.id,)
                )
                Dao.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def read_all(self) -> list[Address]:
        """Renvoie toutes les adresses enregistrées en base de données."""
        addresss: list[Address] = []
        with Dao.connection.cursor() as cursor:
            cursor.execute("SELECT id_address FROM address")
            records = cursor.fetchall()
            for record in records:
                address = self.read(record['id_address'])
                if address is not None:
                    addresss.append(address)
        return addresss