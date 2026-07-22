# Portal-zur-Exmatrikulation
Portal-Roboter mit Bilderkennung

Hier wird mieß gehusselt.

## Installation

### Systemvoraussetzungen

Stelle sicher, dass dein System folgende Voraussetzungen erfüllt:

- Du hast Zugriff auf eine Kamera an deinem System.
- Du hast Python 3 global installiert, inklusive des Pakets `cv2` (z. B. über pip oder einen anderen Python-Paketmanager).
- Du hast ROS2 Humble installiert.

### Schritte

1. Klone das GitHub-Repository in einen Ordner deiner Wahl.
2. Wechsle in folgendes Verzeichnis und installiere das Python-Paket:
   ```bash
   cd Portal-zur-Exmatrikulation/ros2_logic
   pip install -e .
   ```
3. Lade alle Submodule herunter:
   ```bash
   git submodule update --recursive --init
   ```
4. Wechsle in folgendes Verzeichnis und führe `colcon build` aus:
   ```bash
   cd Portal-zur-Exmatrikulation/ros2_ws/
   colcon build
   ```
5. Source den ROS-Workspace:
   ```bash
   source install/setup.bash
   ```

## Starten

Wechsle in das ROS-Workspace-Verzeichnis:

```bash
cd Portal-zur-Exmatrikulation/ros2_ws/
```

Starte anschließend den gewünschten Node:

```bash
ros2 run chaos_nodes <node_name>
```

Verfügbare Nodes (`<node_name>`): `motion`, `camera`, `coord_pred`, `machine_learning`, `mainy`, `planner`, `test_planner`.