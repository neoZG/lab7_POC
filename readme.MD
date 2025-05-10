# Offline-First Content Delivery POC – README

This repository contains a proof-of-concept implementation of an offline-first educational content delivery system for rural areas. The system enables local access to educational materials via an edge server that can function with little or no internet connectivity, and synchronizes with a central server when possible.

---

## Architecture

The solution comprises a **central server** (central hub) and an **edge server** (deployed in the rural site). Clients (e.g., student laptops) connect to the local edge server over a LAN or Wi-Fi. The edge server provides authentication and content access using locally cached data. Periodically, the edge server syncs with the central server to fetch new content (videos, PDFs) and update user credentials.

Syncing is done in **chunks** to handle large files over unstable connections, and would typically be scheduled (e.g., via cron jobs) and use message queues for reliability. This POC simulates the entire flow with dummy data.

---

## Code Structure

- `central_server/app.py`: Flask app for the central server. It stores the master user database and content library. Provides endpoints for login, listing content, downloading content, and serving chunks and user data for sync.
- `edge_server/app.py`: Flask app for the edge server. It caches users and content locally (initially a subset of central’s data). Provides endpoints for local login, content listing, and downloading content.
- `edge_server/sync_client.py`: A script that simulates the edge’s periodic synchronization job. It calls the central server’s APIs to update the edge’s users and content. In a real deployment, this might be run by a cron scheduler or a background service.
- `tests/test_fitness.py`: Test suite defining fitness functions to evaluate system **Availability**, **Performance**, and **Content Update Time**.
- `.github/workflows/ci.yml`: Configuration for GitHub Actions to automatically run the tests on each commit.
- `requirements.txt`: Python dependencies (Flask, requests, pytest).

---

## Running the POC

### Prerequisites

Python 3.x  
Install required libraries:

```bash
pip install -r requirements.txt
```

---

### 1. Start the Servers

Open **two terminals**.

**Terminal 1 (central server):**

```bash
python central_server/app.py
```

Runs on `localhost:5000`.

**Terminal 2 (edge server):**

```bash
python edge_server/app.py
```

Runs on `localhost:5001`.

---

### 2. Simulate Client Requests (Manual Testing)

With both servers running, you can simulate a client using `curl` or browser:

* **List content on edge:**

  ```bash
  curl http://localhost:5001/content
  ```
* **Download content:**

  ```bash
  curl http://localhost:5001/download/1 --output video1.dat
  ```
* **Attempt login:**

  ```bash
  curl -X POST http://localhost:5001/login -H "Content-Type: application/json" -d '{"username":"user1","password":"pass1"}'
  ```
* **List content on central (for comparison):**

  ```bash
  curl http://localhost:5000/content
  ```

---

### 3. Run Sync (Edge -> Central)

Simulate the cron job by running the sync script in a **third terminal**:

```bash
python edge_server/sync_client.py
```

This syncs new users and content in chunks to the edge. Output logs will show progress and sync time.

---

### 4. Verify Post-Sync State

After syncing:

* **Edge content should include content ID 3:**

  ```bash
  curl http://localhost:5001/content
  ```
* **Download synced content:**

  ```bash
  curl http://localhost:5001/download/3 --output video3.dat
  ```
* **Login as synced user:**

  ```bash
  curl -X POST http://localhost:5001/login -H "Content-Type: application/json" -d '{"username":"user2","password":"pass2"}'
  ```

---

## 🧪 Ejecución Local de Pruebas

Para facilitar las pruebas en sistemas Windows, se ha incluido un archivo de ejecución automática:

### 📄 `run_tests.bat`

Este script:

1. Establece el `PYTHONPATH` correctamente para el entorno local.
2. Ejecuta los tests definidos en `tests/test_fitness.py` usando `pytest`.
3. Muestra en consola el resultado de las funciones de *fitness* (disponibilidad, rendimiento y sincronización).

Para ejecutarlo:

```bash
.\run_tests.bat
```

---

## ✅ Resultados de Prueba Reales

Los siguientes son los resultados reales obtenidos al ejecutar `run_tests.bat` en un entorno Windows con hardware estándar (laptop de gama media, Python 3.10).

| Fitness Function             | Resultado Obtenido                                        | Estado              | Justificación                                                                                                                                            |
| ---------------------------- | --------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Disponibilidad**           | 100% de éxito en 100 intentos                             | ✅ Excelente         | Supera el umbral mínimo del 90% definido en la arquitectura.                                                                                             |
| **Rendimiento (QPS)**        | 4.88 QPS                                                  | ⚠️ Ligeramente Bajo | Por debajo del umbral (>5 QPS), atribuible al uso de Flask en modo desarrollo sin multithreading ni WSGI server. Justificable para un entorno POC local. |
| **Tiempo de sincronización** | 44.9 segundos para sincronizar nuevo contenido y usuarios | ✅ Excelente         | Muy por debajo del máximo aceptable de 1 hora definido.                                                                                                  |

**Nota:** Se decidió no ajustar el umbral mínimo del test de rendimiento para reflejar fielmente las capacidades reales del entorno de prueba.

---

## Fitness Function Tests

We use automated tests to validate system behavior:

### Availability (≥ 90%)

* Simulates 100 sequential requests (login/content).
* Asserts ≥ 90% success rate.

### Performance (QPS measurement)

* Simulates 10 concurrent users, each making 10 requests.
* Measures average Queries Per Second (QPS).
* Expects QPS > 5 to pass.

### Content Update Time

* Measures time from sync start to content/user availability at edge.
* Validates presence of newly synced content and user post-sync.

---

### Run All Tests Manually (Linux/macOS)

If you're not using the `.bat`, run this from the root directory:

```bash
PYTHONPATH=. pytest -s -q tests/test_fitness.py
```

---

## CI Integration

Tests automatically run on each push or pull request via GitHub Actions using the workflow at:

```plaintext
.github/workflows/ci.yml
```

This ensures that all fitness functions are continuously validated in an automated pipeline.

---
