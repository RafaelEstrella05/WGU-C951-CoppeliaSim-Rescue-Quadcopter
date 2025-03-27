# Autonomous Disaster Recovery Quadcopter – CoppeliaSim Simulation

## Overview

This project simulates an autonomous quadcopter used for post-disaster search and rescue operations. Developed using [CoppeliaSim](https://www.coppeliarobotics.com/) and scripted in Python and Lua, the robot autonomously explores a flooded or tornado-impacted urban environment to detect survivors and map obstacles. This simulation fulfills the requirements for a virtual disaster recovery prototype using goal-seeking behavior and sensor integration.

## Scenario

A tornado has impacted a small urban area, flooding streets and knocking down buildings. The quadcopter is deployed to autonomously:
- Survey the environment
- Avoid debris and impassable buildings
- Detect trapped individuals (represented by red-colored dummies)
- Record and report survivor coordinates

## Features

- **Autonomous Exploration:** Implements a grid-based search strategy with pathfinding and backtracking.
- **Survivor Detection:** Uses vision sensors to detect red-colored figures representing survivors.
- **Obstacle Avoidance:** Uses four proximity sensors to avoid buildings and debris.
- **Data Visualization:** Real-time RGB color data and proximity sensor data are streamed to visual graphs for analysis.
- **Map Tracking:** Maintains a live internal map of visited, unvisited, and obstacle areas.

## Sensors and Architecture

- **Vision Sensors (x4):** Positioned at 45° angles to cover front, back, left, and right.
- **Proximity Sensors (x4):** Placed in cardinal directions to avoid collisions.
- **Grid Mapping:** The quadcopter maps its path and keeps track of visited cells using a hash map.


## Robot Intelligence & Reasoning

- **Reasoning:** Based on a directional search algorithm that prioritizes unvisited, reachable grid cells.
- **Knowledge Representation:** Grid map with status (visited, unvisited, obstacle) and survivor locations.
- **Uncertainty Handling:** Survivor detection confirmed using vision and proximity over multiple cycles to reduce false positives.
- **Intelligence:** Combines sensor input, movement planning, and obstacle detection to autonomously adapt its path.

## Improvements & Future Work

- **Reinforcement Learning:** Could be implemented to optimize search strategies based on success in survivor detection.
- **Advanced Search Algorithms:** A* or D* Lite could improve path planning.
- **Multi-Drone Coordination:** Simulate multiple drones working in coordination for faster area coverage.
- **Heatmaps & Dynamic Obstacles:** Implement survivor heat signatures and simulate collapsing debris.

## How to Run

To run project, install and Open CoppeliaSim Edu 4.7.0 and open the search_rescure_drone.ttt scene file.

1. Open the CoppeliaSim environment and load your scene.
2. Press **Play** to start the simulation.
3. Use the keyboard if manual mode is activated (`manual_movement.py`).

## Credits

Developed as part of a school project focused on AI in disaster recovery robotics using CoppeliaSim.
