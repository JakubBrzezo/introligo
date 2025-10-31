/**
 * @file Servo.h
 * @brief Servo mechanism controller for smart door actuator
 *
 * This file contains the Servo class which controls the servo motor
 * that operates the door locking mechanism.
 */

#ifndef SERVO_H
#define SERVO_H

#include <string>

/**
 * @brief Servo motor controller class
 *
 * The Servo class controls a servo motor that can rotate between
 * 0 and 180 degrees. It is used to control the locking mechanism
 * of the smart door.
 */
class Servo {
private:
    int currentAngle;      ///< Current angle of the servo (0-180 degrees)
    int minAngle;          ///< Minimum angle limit (default 0)
    int maxAngle;          ///< Maximum angle limit (default 180)
    bool isCalibrated;     ///< Calibration status flag
    std::string name;      ///< Name/identifier of the servo

public:
    /**
     * @brief Constructor for Servo
     * @param servoName Name identifier for the servo
     */
    Servo(const std::string& servoName);

    /**
     * @brief Destructor for Servo
     */
    ~Servo();

    /**
     * @brief Calibrate the servo to its home position
     * @return true if calibration succeeded, false otherwise
     */
    bool calibrate();

    /**
     * @brief Set the servo angle
     * @param angle Target angle in degrees (0-180)
     * @return true if angle was set successfully, false if out of range
     */
    bool setAngle(int angle);

    /**
     * @brief Get the current servo angle
     * @return Current angle in degrees
     */
    int getAngle() const;

    /**
     * @brief Check if servo is calibrated
     * @return true if calibrated, false otherwise
     */
    bool isCalibratedStatus() const;

    /**
     * @brief Reset servo to default position (90 degrees)
     */
    void reset();

    /**
     * @brief Get the servo name
     * @return Name of the servo
     */
    std::string getName() const;
};

#endif // SERVO_H
