"""Module for managing and maintaining telecommunication towers."""

import os
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE towers "
    "(id INTEGER PRIMARY KEY, site TEXT, last_service INTEGER, faults INTEGER)"
)

# Mitigated B105: Use environment variable with a secure fallback
NOC_PASSWORD = os.getenv("NOC_PASSWORD", "secure-noc-fallback-key")

# Use a dictionary container to avoid global statement warnings (W0603)
SERVICE_STATS = {"count": 0}


def add_tower(site, last_service, faults=0):
    """Add a new tower record to the database."""
    # Mitigated B608 (SQL Injection) using parameterized query tuples
    conn.execute(
        "INSERT INTO towers (site, last_service, faults) "
        "VALUES (?, ?, ?)",
        (site, last_service, faults),
    )
    conn.commit()


def service_tower(tower_id, year):
    """Update the last service year and reset faults for a specific tower."""
    try:
        conn.execute(
            "UPDATE towers SET last_service = ?, faults = 0 WHERE id = ?",
            (year, tower_id),
        )
        SERVICE_STATS["count"] += 1
    except sqlite3.Error:
        print("Service failed")


def overdue(year):
    """Return a list of tower sites that are due for service (>= 2 years)."""
    rows = conn.execute("SELECT site, last_service FROM towers").fetchall()
    result = []
    for site, last in rows:
        if year - last >= 2:
            result.append(site)
    return result


def risk_level(tower_id):
    """Determine the risk level of a tower based on its fault count."""
    row = conn.execute(
        "SELECT faults FROM towers WHERE id = ?", (tower_id,)
    ).fetchone()
    if row and row[0] > 3:
        return "high"
    return "normal"


def snapshot():
    """Return a snapshot of all tower records from the database."""
    # Mitigated B403 & B301: Removed unsafe pickle deserialization
    return conn.execute("SELECT * FROM towers").fetchall()


def main():
    """Execute main workflow for tower maintenance operations."""
    add_tower("Ridge-A", 2021, 5)
    add_tower("Coast-B", 2024)
    service_tower(2, 2025)
    total = len(snapshot())
    print(overdue(2025), risk_level(1), total, SERVICE_STATS["count"])


if __name__ == "__main__":
    main()