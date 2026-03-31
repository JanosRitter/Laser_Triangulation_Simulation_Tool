from src_laser_sim.trajectory import generate_trajectory
from src_laser_sim.run_pipeline import (
    run_single_simulation,
    run_trajectory_simulation
)


def main():
    print("🔧 Lasertriangulation Simulation gestartet")

    positions = generate_trajectory()

    if len(positions) == 1:
        run_single_simulation(positions[0])
    else:
        run_trajectory_simulation(positions)


if __name__ == "__main__":
    main()