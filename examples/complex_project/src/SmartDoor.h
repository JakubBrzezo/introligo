/**
 * @file SmartDoor.h
 * @brief Smart door driver that coordinates servo and contractor mechanisms
 *
 * This file contains the SmartDoor class which is the main driver that
 * coordinates the servo locking mechanism and the linear actuator (contractor)
 * to provide secure and reliable door operation.
 */

#ifndef SMARTDOOR_H
#define SMARTDOOR_H

#include "Servo.h"
#include "Contractor.h"
#include <string>

/**
 * @brief Main smart door controller class
 *
 * The SmartDoor class coordinates the servo lock and contractor actuator
 * to provide a complete door control system. It implements safety checks
 * and proper sequencing of operations.
 */
class SmartDoor {
public:
    /**
     * @brief Door state enumeration
     */
    enum DoorState {
        CLOSED_LOCKED,    ///< Door is closed and locked
        CLOSED_UNLOCKED,  ///< Door is closed but unlocked
        OPENING,          ///< Door is in the process of opening
        OPEN,             ///< Door is fully open
        CLOSING,          ///< Door is in the process of closing
        ERROR_STATE       ///< Error condition
    };

private:
    Servo* lockServo;              ///< Servo controlling the lock mechanism
    Contractor* doorActuator;      ///< Linear actuator for door movement
    DoorState currentState;        ///< Current state of the door
    bool isSystemReady;            ///< System initialization status
    std::string doorId;            ///< Identifier for this door
    int openAttempts;              ///< Counter for failed open attempts
    static const int MAX_ATTEMPTS = 3;  ///< Maximum retry attempts

    /**
     * @brief Lock the door using servo
     * @return true if locking succeeded, false otherwise
     */
    bool lockDoor();

    /**
     * @brief Unlock the door using servo
     * @return true if unlocking succeeded, false otherwise
     */
    bool unlockDoor();

    /**
     * @brief Check if it's safe to operate the door
     * @return true if safe, false otherwise
     */
    bool isSafeToOperate() const;

public:
    /**
     * @brief Constructor for SmartDoor
     * @param id Identifier for the door
     */
    SmartDoor(const std::string& id);

    /**
     * @brief Destructor for SmartDoor
     */
    ~SmartDoor();

    /**
     * @brief Initialize the smart door system
     *
     * This method calibrates the servo and initializes the contractor.
     * Must be called before any door operations.
     *
     * @return true if initialization succeeded, false otherwise
     */
    bool initialize();

    /**
     * @brief Open the door
     *
     * Sequence: unlock servo -> extend contractor -> update state
     *
     * @return true if door opened successfully, false otherwise
     */
    bool open();

    /**
     * @brief Close the door
     *
     * Sequence: retract contractor -> lock servo -> update state
     *
     * @return true if door closed successfully, false otherwise
     */
    bool close();

    /**
     * @brief Emergency stop - halt all operations immediately
     *
     * This method stops all movement and puts the system in a safe state.
     */
    void emergencyStop();

    /**
     * @brief Get the current door state
     * @return Current DoorState enum value
     */
    DoorState getState() const;

    /**
     * @brief Get string representation of current state
     * @return State name as string
     */
    std::string getStateString() const;

    /**
     * @brief Get door identifier
     * @return Door ID string
     */
    std::string getDoorId() const;

    /**
     * @brief Check if system is ready for operation
     * @return true if ready, false otherwise
     */
    bool isReady() const;

    /**
     * @brief Get system status report
     *
     * Provides detailed status information about all components.
     *
     * @return Status report as string
     */
    std::string getStatusReport() const;

    /**
     * @brief Reset the door system
     *
     * Closes the door and reinitializes all components.
     *
     * @return true if reset succeeded, false otherwise
     */
    bool reset();
};

#endif // SMARTDOOR_H
