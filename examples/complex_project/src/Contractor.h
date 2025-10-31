/**
 * @file Contractor.h
 * @brief Linear actuator (contractron) controller for smart door mechanism
 *
 * This file contains the Contractor class which controls a linear actuator
 * that extends and retracts to physically move the door.
 */

#ifndef CONTRACTOR_H
#define CONTRACTOR_H

#include <string>

/**
 * @brief Linear actuator controller class
 *
 * The Contractor (contractron) class controls a linear actuator that can
 * extend and retract. It is used to physically push or pull the door open
 * and closed in coordination with the servo locking mechanism.
 */
class Contractor {
public:
    /**
     * @brief State of the contractor
     */
    enum State {
        RETRACTED,    ///< Fully retracted position (door closed)
        EXTENDING,    ///< Currently extending
        EXTENDED,     ///< Fully extended position (door open)
        RETRACTING,   ///< Currently retracting
        ERROR         ///< Error state
    };

private:
    State currentState;           ///< Current state of the contractor
    int currentPosition;          ///< Current position (0=retracted, 100=extended)
    int maxExtension;             ///< Maximum extension in mm
    bool isInitialized;           ///< Initialization status
    std::string name;             ///< Name/identifier of the contractor
    int speed;                    ///< Speed of extension/retraction (1-10)

public:
    /**
     * @brief Constructor for Contractor
     * @param contractorName Name identifier for the contractor
     * @param maxExt Maximum extension in millimeters (default 200mm)
     */
    Contractor(const std::string& contractorName, int maxExt = 200);

    /**
     * @brief Destructor for Contractor
     */
    ~Contractor();

    /**
     * @brief Initialize the contractor and home it to retracted position
     * @return true if initialization succeeded, false otherwise
     */
    bool initialize();

    /**
     * @brief Extend the contractor to open the door
     * @return true if extension started successfully, false otherwise
     */
    bool extend();

    /**
     * @brief Retract the contractor to close the door
     * @return true if retraction started successfully, false otherwise
     */
    bool retract();

    /**
     * @brief Stop the contractor at current position
     */
    void stop();

    /**
     * @brief Get the current state of the contractor
     * @return Current State enum value
     */
    State getState() const;

    /**
     * @brief Get the current position as percentage (0-100)
     * @return Current position percentage
     */
    int getPosition() const;

    /**
     * @brief Set the speed of the contractor
     * @param newSpeed Speed value (1-10, where 10 is fastest)
     * @return true if speed was set successfully, false if out of range
     */
    bool setSpeed(int newSpeed);

    /**
     * @brief Check if contractor is initialized
     * @return true if initialized, false otherwise
     */
    bool isReady() const;

    /**
     * @brief Get string representation of current state
     * @return State name as string
     */
    std::string getStateString() const;

    /**
     * @brief Get the contractor name
     * @return Name of the contractor
     */
    std::string getName() const;
};

#endif // CONTRACTOR_H
