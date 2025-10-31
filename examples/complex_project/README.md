# Smart Door Driver - Complex Example

This is a comprehensive example demonstrating the use of Introligo to document a complex C++ project. The project implements a smart door driver system that coordinates a servo-based locking mechanism with a linear actuator (contractron) to provide automated door control.

## Project Overview

The Smart Door Driver is a C++ control system that manages:

- **Servo Lock Mechanism**: A servo motor that rotates to lock/unlock the door
- **Linear Actuator (Contractron)**: A contractron device that extends and retracts to physically open and close the door
- **Safety & State Management**: Comprehensive state tracking and safety checks
- **Error Handling**: Robust error detection and recovery mechanisms

## Architecture

The system consists of three main components:

### 1. Servo Class (`src/Servo.h`, `src/Servo.cpp`)
Controls the servo motor for the locking mechanism:
- Angle control (0-180 degrees)
- Calibration procedures
- Position tracking
- Safety limits

### 2. Contractor Class (`src/Contractor.h`, `src/Contractor.cpp`)
Manages the linear actuator (contractron):
- Extension and retraction control
- Position feedback (0-100%)
- Speed adjustment
- State machine implementation

### 3. SmartDoor Class (`src/SmartDoor.h`, `src/SmartDoor.cpp`)
Main controller that orchestrates both components:
- Coordinated door opening/closing sequences
- Safety checks and interlocks
- State management
- Emergency stop functionality
- Status reporting

## Features

- **Safe Operation Sequences**: The system ensures proper sequencing - unlock before opening, close before locking
- **State Machine**: Comprehensive state tracking (CLOSED_LOCKED, CLOSED_UNLOCKED, OPENING, OPEN, CLOSING, ERROR_STATE)
- **Error Handling**: Retry logic and error state management
- **Emergency Stop**: Immediate halt of all operations
- **Status Reporting**: Detailed system status information
- **Calibration**: Automatic calibration and homing procedures

## Operating Sequence

### Opening the Door
1. Check if system is initialized and safe to operate
2. Unlock the door (servo moves to 90°)
3. Extend the contractor to push the door open
4. Update state to OPEN

### Closing the Door
1. Check if system is initialized and safe to operate
2. Retract the contractor to close the door
3. Lock the door (servo moves to 0°)
4. Update state to CLOSED_LOCKED

## Documentation Structure

This example demonstrates:

1. **C++ Code Documentation**: Using Doxygen comments in header and source files
2. **Class Diagrams**: PlantUML diagram showing class relationships and structure
3. **Algorithm Workflows**: Mermaid flowcharts showing:
   - System initialization algorithm
   - Door opening algorithm
   - Door closing algorithm
4. **Markdown Documentation**: This README file
5. **Introligo Integration**: Complete configuration showing how to combine all documentation types

## Building Documentation

### Prerequisites

Install required dependencies:
```bash
pip install sphinx furo sphinxcontrib-plantuml sphinxcontrib-mermaid breathe
sudo apt-get install doxygen graphviz  # On Ubuntu/Debian
```

### Method 1: Using build script (Easiest)

The project includes a build script that handles everything automatically:

```bash
cd examples/complex_project
./build_docs.sh
```

This will:
1. Run Doxygen to generate C++ API documentation
2. Generate RST files from the Introligo configuration
3. Build Sphinx HTML documentation
4. Serve the docs at http://localhost:8000

To build without serving, use:
```bash
./build_docs.sh --no-serve
```

### Method 2: Using preview.py

**Important:** You must run Doxygen first, then use preview.py:

```bash
# Step 1: Generate Doxygen XML files
cd examples/complex_project
doxygen Doxyfile

# Step 2: Build and serve with preview.py
cd ../../docs
python3 preview.py --example complex_project
```

### Method 3: Manual Build

1. Generate Doxygen XML output:
   ```bash
   cd examples/complex_project
   doxygen Doxyfile
   ```

2. Generate Introligo documentation:
   ```bash
   python -m introligo examples/complex_project/introligo_config.yaml -o examples/complex_project/docs
   ```

3. Build Sphinx documentation:
   ```bash
   cd examples/complex_project/docs
   sphinx-build -b html . _build/html
   ```

4. View the documentation:
   ```bash
   # Open examples/complex_project/docs/_build/html/index.html in your browser
   ```

## Code Example

```cpp
#include "SmartDoor.h"
#include <iostream>

int main() {
    // Create a smart door instance
    SmartDoor door("MainEntrance");

    // Initialize the system
    if (!door.initialize()) {
        std::cerr << "Failed to initialize door!" << std::endl;
        return 1;
    }

    // Display status
    std::cout << door.getStatusReport() << std::endl;

    // Open the door
    if (door.open()) {
        std::cout << "Door opened successfully!" << std::endl;
        std::cout << "Current state: " << door.getStateString() << std::endl;
    }

    // Wait or perform other operations...

    // Close the door
    if (door.close()) {
        std::cout << "Door closed and locked successfully!" << std::endl;
        std::cout << "Current state: " << door.getStateString() << std::endl;
    }

    return 0;
}
```

## Diagrams Included

- **Class Diagram** (`diagrams/class_diagram.puml`): Shows the relationship between SmartDoor, Servo, and Contractor classes
- **Initialization Algorithm** (`diagrams/initialization.mmd`): Flowchart of the system initialization process
- **Open Algorithm** (`diagrams/open_algorithm.mmd`): Flowchart of the door opening sequence
- **Close Algorithm** (`diagrams/close_algorithm.mmd`): Flowchart of the door closing sequence

## Safety Features

- **Calibration Checks**: System verifies servo calibration before operation
- **State Validation**: Ensures valid state transitions
- **Retry Logic**: Automatic retry with maximum attempt limits
- **Emergency Stop**: Immediate shutdown capability
- **Error States**: Clear error reporting and handling

## What This Example Demonstrates

This complex example showcases Introligo's ability to:

1. **Integrate C++ documentation** using Doxygen/Breathe
2. **Include UML diagrams** (PlantUML class diagrams)
3. **Include workflow diagrams** (Mermaid flowcharts)
4. **Combine markdown documentation** with generated API docs
5. **Handle multiple source files** with proper organization
6. **Create comprehensive documentation** from a single YAML configuration

## License

This is an example project for demonstration purposes.
