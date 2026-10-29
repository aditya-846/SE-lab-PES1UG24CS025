| **SQL Injection Risk** | Security (Bandit) | 11 | Potential SQL injection vector via string formatting (`B608`)[cite: 3]. | Use parameterized queries with tuples (e.g., `conn.execute("INSERT INTO towers ... VALUES (?, ?, ?)", (site, last_service, faults))`). |

| **Insecure Deserialization** | Security (Bandit) | 1, 43 | Unsafe use of the `pickle` module for handling data states (`B403`, `B301`)[cite: 3]. | Refactor snapshot logic to avoid pickle or use safer serialization alternatives like JSON if applicable. |

| **Line Too Long** | Style (Flake8/Pylint) | 5, 11, 18, 35, 43 | Lines exceed maximum character limits (exceeding 79/100 chars)[cite: 3]. | Break long lines into multi-line statements or use parentheses to comply with PEP 8. |

| **Invalid Naming Convention** | Style (Pylint) | 10, 15, 34 | Function names use camelCase (`addTower`, `serviceTower`, `riskLevel`) instead of snake_case[cite: 3]. | Rename functions to use snake_case (`add_tower`, `service_tower`, `risk_level`)[cite: 3]. |
