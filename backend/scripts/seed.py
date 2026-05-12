# ============================================================
# Script de Seed - Données Initiales MobiTranz
# Fichier : backend/scripts/seed.py
# Description : Crée les utilisateurs admin, ministère et tests
# Exécution : python backend/scripts/seed.py
# ============================================================

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import async_session, init_db
from backend.services.auth_service import auth_service
from backend.models.user import User, UserRole, UserStatus
from backend.models.driver import Driver, DriverStatus
from backend.models.zone import Zone

ADMIN_USERS = [
    {
        "phone": "+24101020304",
        "email": "admin@mobitranz.ga",
        "password": "AdminMobitranz2026!",
        "first_name": "Admin",
        "last_name": "Mobitranz",
        "role": UserRole.ADMIN,
    },
    {
        "phone": "+24102030405",
        "email": "super@mobitranz.ga",
        "password": "SuperAdmin2026!",
        "first_name": "Super",
        "last_name": "Admin",
        "role": UserRole.ADMIN,
    },
    {
        "phone": "+24103040506",
        "email": "ministere@mobitranz.ga",
        "password": "Ministere2026!",
        "first_name": "Ministere",
        "last_name": "Transports",
        "role": UserRole.MINISTRY,
    },
]

DRIVER_USERS = [
    {
        "phone": "+24106010203",
        "email": "jean@mobitranz.ga",
        "password": "DriverJean2026!",
        "first_name": "Jean",
        "last_name": "Okonga",
    },
    {
        "phone": "+24106102030",
        "email": "marie@mobitranz.ga",
        "password": "DriverMarie2026!",
        "first_name": "Marie",
        "last_name": "Bongolo",
    },
    {
        "phone": "+24106203040",
        "email": "paul@mobitranz.ga",
        "password": "DriverPaul2026!",
        "first_name": "Paul",
        "last_name": "Nze",
    },
]

CLIENT_USERS = [
    {
        "phone": "+24107010203",
        "email": "client1@mobitranz.ga",
        "password": "ClientTest2026!",
        "first_name": "Test",
        "last_name": "Client",
    },
]

ZONES = [
    {
        "name": "centre-ville",
        "display_name": "Centre-Ville",
        "base_price": 350,
        "keywords": "centre,plateau,haut de gue-gue,lgbt",
        "lat_min": 0.385,
        "lat_max": 0.400,
        "lon_min": 9.440,
        "lon_max": 9.465,
        "priority": 10,
    },
    {
        "name": "owendo",
        "display_name": "Owendo",
        "base_price": 500,
        "keywords": "owendo,ouen",
        "lat_min": 0.275,
        "lat_max": 0.305,
        "lon_min": 9.450,
        "lon_max": 9.485,
        "priority": 8,
    },
    {
        "name": "akanda",
        "display_name": "Akanda",
        "base_price": 600,
        "keywords": "akanda,mondah",
        "lat_min": 0.515,
        "lat_max": 0.540,
        "lon_min": 9.420,
        "lon_max": 9.460,
        "priority": 7,
    },
    {
        "name": "libreville",
        "display_name": "Libreville",
        "base_price": 300,
        "keywords": "libreville,lbv",
        "lat_min": 0.240,
        "lat_max": 0.560,
        "lon_min": 9.200,
        "lon_max": 9.580,
        "priority": 5,
    },
    {
        "name": "port-gentil",
        "display_name": "Port-Gentil",
        "base_price": 750,
        "keywords": "port,gentil,pg",
        "lat_min": -0.720,
        "lat_max": -0.680,
        "lon_min": 8.780,
        "lon_max": 8.830,
        "priority": 6,
    },
    {
        "name": "pk5",
        "display_name": "PK5",
        "base_price": 400,
        "keywords": "pk5,p-k-5",
        "lat_min": 0.420,
        "lat_max": 0.435,
        "lon_min": 9.450,
        "lon_max": 9.470,
        "priority": 9,
    },
    {
        "name": "pk8",
        "display_name": "PK8",
        "base_price": 450,
        "keywords": "pk8,p-k-8",
        "lat_min": 0.405,
        "lat_max": 0.420,
        "lon_min": 9.445,
        "lon_max": 9.465,
        "priority": 9,
    },
]


async def get_user_by_phone(session, phone: str):
    from sqlalchemy import select

    result = await session.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def create_user(session, data: dict, role: UserRole) -> User:
    phone = data["phone"]
    existing = await get_user_by_phone(session, phone)
    if existing:
        print(f"  [SKIP] {phone} existe")
        return existing
    user = User(
        phone=phone,
        email=data["email"],
        password_hash=auth_service.hash_password(data["password"]),
        role=role,
        status=UserStatus.ACTIVE,
        first_name=data["first_name"],
        last_name=data["last_name"],
    )
    session.add(user)
    await session.flush()
    print(f"  [OK] {phone}")
    return user


async def create_driver(session, user_data: dict) -> tuple:
    user = await create_user(session, user_data, UserRole.DRIVER)
    from sqlalchemy import select

    result = await session.execute(select(Driver).where(Driver.user_id == user.id))
    existing = result.scalar_one_or_none()
    if existing:
        print(f"  [SKIP] Driver {user.id}")
        return user, existing
    phone_suffix = user.phone[-4:]
    driver = Driver(
        user_id=user.id,
        license_number="LIC-" + user.phone[-6:],
        status=DriverStatus.VALIDATED,
        current_lat=0.3921,
        current_lon=9.4543,
        is_available=True,
        rating=4.5,
    )
    session.add(driver)
    await session.flush()
    print(f"  [DRIVER] {user.id}")
    return user, driver


async def get_zone_by_name(session, name: str):
    from sqlalchemy import select

    result = await session.execute(select(Zone).where(Zone.name == name))
    return result.scalar_one_or_none()


async def create_zone(session, data: dict) -> Zone:
    zone = await get_zone_by_name(session, data["name"])
    if zone:
        print(f"  [SKIP] Zone {data['name']}")
        return zone
    zone = Zone(**data)
    session.add(zone)
    await session.flush()
    print(f"  [ZONE] {data['name']} = {data['base_price']} XAF")
    return zone


async def seed():
    print("\n=== MobiTranz Seed ===")
    print("Initialisation DB...")
    await init_db()
    async with async_session() as session:
        print("\n--- Admins & Ministere ---")
        for data in ADMIN_USERS:
            role = data.pop("role")
            await create_user(session, data, role)
        print("\n--- Conducteurs ---")
        for data in DRIVER_USERS:
            await create_driver(session, data)
        print("\n--- Clients ---")
        for data in CLIENT_USERS:
            await create_user(session, data, UserRole.CLIENT)
        print("\n--- Zones Tarifaires ---")
        for data in ZONES:
            await create_zone(session, data)
        await session.commit()
    print("\n=== Seed termine ===")


if __name__ == "__main__":
    asyncio.run(seed())
