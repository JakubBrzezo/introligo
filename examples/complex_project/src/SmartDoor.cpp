/**
 * @file SmartDoor.cpp
 * @brief Implementation of SmartDoor class
 */

#include "SmartDoor.h"
#include <iostream>
#include <sstream>

SmartDoor::SmartDoor(const std::string& id)
    : doorId(id), currentState(CLOSED_LOCKED), isSystemReady(false), openAttempts(0) {
    std::cout << "[SmartDoor] Creating smart door system: " << doorId << std::endl;

    // Create servo for lock mechanism
    lockServo = new Servo("LockServo_" + doorId);

    // Create contractor for door movement
    doorActuator = new Contractor("DoorActuator_" + doorId, 250);

    std::cout << "[SmartDoor] Components created" << std::endl;
}

SmartDoor::~SmartDoor() {
    std::cout << "[SmartDoor] Shutting down smart door: " << doorId << std::endl;

    // Ensure door is closed before shutdown
    if (currentState != CLOSED_LOCKED) {
        close();
    }

    delete lockServo;
    delete doorActuator;
}

bool SmartDoor::initialize() {
    std::cout << "[SmartDoor] Initializing system..." << std::endl;

    // Calibrate servo
    if (!lockServo->calibrate()) {
        std::cerr << "[SmartDoor] Error: Servo calibration failed" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    // Initialize contractor
    if (!doorActuator->initialize()) {
        std::cerr << "[SmartDoor] Error: Contractor initialization failed" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    // Lock the door by default
    if (!lockDoor()) {
        std::cerr << "[SmartDoor] Error: Initial lock failed" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    isSystemReady = true;
    currentState = CLOSED_LOCKED;
    openAttempts = 0;

    std::cout << "[SmartDoor] Initialization complete - System ready" << std::endl;
    return true;
}

bool SmartDoor::lockDoor() {
    std::cout << "[SmartDoor] Locking door..." << std::endl;

    // Move servo to locked position (0 degrees)
    if (!lockServo->setAngle(0)) {
        std::cerr << "[SmartDoor] Error: Failed to lock" << std::endl;
        return false;
    }

    std::cout << "[SmartDoor] Door locked" << std::endl;
    return true;
}

bool SmartDoor::unlockDoor() {
    std::cout << "[SmartDoor] Unlocking door..." << std::endl;

    // Move servo to unlocked position (90 degrees)
    if (!lockServo->setAngle(90)) {
        std::cerr << "[SmartDoor] Error: Failed to unlock" << std::endl;
        return false;
    }

    std::cout << "[SmartDoor] Door unlocked" << std::endl;
    return true;
}

bool SmartDoor::isSafeToOperate() const {
    if (!isSystemReady) {
        std::cerr << "[SmartDoor] System not ready" << std::endl;
        return false;
    }

    if (currentState == ERROR_STATE) {
        std::cerr << "[SmartDoor] System in error state" << std::endl;
        return false;
    }

    if (!lockServo->isCalibratedStatus()) {
        std::cerr << "[SmartDoor] Servo not calibrated" << std::endl;
        return false;
    }

    if (!doorActuator->isReady()) {
        std::cerr << "[SmartDoor] Contractor not ready" << std::endl;
        return false;
    }

    return true;
}

bool SmartDoor::open() {
    std::cout << "[SmartDoor] === Opening door ===" << std::endl;

    if (!isSafeToOperate()) {
        std::cerr << "[SmartDoor] Error: Not safe to operate" << std::endl;
        openAttempts++;
        if (openAttempts >= MAX_ATTEMPTS) {
            currentState = ERROR_STATE;
        }
        return false;
    }

    if (currentState == OPEN) {
        std::cout << "[SmartDoor] Door already open" << std::endl;
        return true;
    }

    currentState = OPENING;

    // Step 1: Unlock the door
    if (!unlockDoor()) {
        std::cerr << "[SmartDoor] Error: Failed to unlock" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    currentState = CLOSED_UNLOCKED;

    // Step 2: Extend contractor to push door open
    if (!doorActuator->extend()) {
        std::cerr << "[SmartDoor] Error: Failed to extend actuator" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    currentState = OPEN;
    openAttempts = 0;

    std::cout << "[SmartDoor] === Door successfully opened ===" << std::endl;
    return true;
}

bool SmartDoor::close() {
    std::cout << "[SmartDoor] === Closing door ===" << std::endl;

    if (!isSafeToOperate()) {
        std::cerr << "[SmartDoor] Error: Not safe to operate" << std::endl;
        return false;
    }

    if (currentState == CLOSED_LOCKED) {
        std::cout << "[SmartDoor] Door already closed and locked" << std::endl;
        return true;
    }

    currentState = CLOSING;

    // Step 1: Retract contractor to close door
    if (!doorActuator->retract()) {
        std::cerr << "[SmartDoor] Error: Failed to retract actuator" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    currentState = CLOSED_UNLOCKED;

    // Step 2: Lock the door
    if (!lockDoor()) {
        std::cerr << "[SmartDoor] Error: Failed to lock" << std::endl;
        currentState = ERROR_STATE;
        return false;
    }

    currentState = CLOSED_LOCKED;

    std::cout << "[SmartDoor] === Door successfully closed and locked ===" << std::endl;
    return true;
}

void SmartDoor::emergencyStop() {
    std::cout << "[SmartDoor] !!! EMERGENCY STOP ACTIVATED !!!" << std::endl;

    // Stop all movement
    doorActuator->stop();

    // Set safe state
    if (doorActuator->getPosition() > 50) {
        // Door is mostly open
        currentState = OPEN;
    } else {
        // Door is mostly closed
        currentState = CLOSED_UNLOCKED;
    }

    std::cout << "[SmartDoor] System halted in state: " << getStateString() << std::endl;
}

SmartDoor::DoorState SmartDoor::getState() const {
    return currentState;
}

std::string SmartDoor::getStateString() const {
    switch (currentState) {
        case CLOSED_LOCKED:   return "CLOSED_LOCKED";
        case CLOSED_UNLOCKED: return "CLOSED_UNLOCKED";
        case OPENING:         return "OPENING";
        case OPEN:            return "OPEN";
        case CLOSING:         return "CLOSING";
        case ERROR_STATE:     return "ERROR_STATE";
        default:              return "UNKNOWN";
    }
}

std::string SmartDoor::getDoorId() const {
    return doorId;
}

bool SmartDoor::isReady() const {
    return isSystemReady && currentState != ERROR_STATE;
}

std::string SmartDoor::getStatusReport() const {
    std::ostringstream report;

    report << "=== Smart Door Status Report ===" << std::endl;
    report << "Door ID: " << doorId << std::endl;
    report << "System Ready: " << (isSystemReady ? "Yes" : "No") << std::endl;
    report << "Current State: " << getStateString() << std::endl;
    report << std::endl;

    report << "--- Servo Lock ---" << std::endl;
    report << "Name: " << lockServo->getName() << std::endl;
    report << "Angle: " << lockServo->getAngle() << " degrees" << std::endl;
    report << "Calibrated: " << (lockServo->isCalibratedStatus() ? "Yes" : "No") << std::endl;
    report << std::endl;

    report << "--- Door Actuator ---" << std::endl;
    report << "Name: " << doorActuator->getName() << std::endl;
    report << "State: " << doorActuator->getStateString() << std::endl;
    report << "Position: " << doorActuator->getPosition() << "%" << std::endl;
    report << "Ready: " << (doorActuator->isReady() ? "Yes" : "No") << std::endl;

    report << "=============================" << std::endl;

    return report.str();
}

bool SmartDoor::reset() {
    std::cout << "[SmartDoor] Resetting system..." << std::endl;

    // Close door if not already closed
    if (currentState != CLOSED_LOCKED) {
        if (!close()) {
            std::cerr << "[SmartDoor] Error: Failed to close during reset" << std::endl;
            return false;
        }
    }

    // Reinitialize
    isSystemReady = false;
    return initialize();
}
