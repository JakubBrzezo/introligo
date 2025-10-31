/**
 * @file Servo.cpp
 * @brief Implementation of Servo class
 */

#include "Servo.h"
#include <iostream>

Servo::Servo(const std::string& servoName)
    : name(servoName), currentAngle(90), minAngle(0), maxAngle(180), isCalibrated(false) {
    std::cout << "[Servo] " << name << " initialized at angle " << currentAngle << std::endl;
}

Servo::~Servo() {
    std::cout << "[Servo] " << name << " shutting down" << std::endl;
}

bool Servo::calibrate() {
    std::cout << "[Servo] Calibrating " << name << "..." << std::endl;
    currentAngle = 0;
    isCalibrated = true;
    std::cout << "[Servo] Calibration complete" << std::endl;
    return true;
}

bool Servo::setAngle(int angle) {
    if (angle < minAngle || angle > maxAngle) {
        std::cerr << "[Servo] Error: Angle " << angle << " out of range ["
                  << minAngle << ", " << maxAngle << "]" << std::endl;
        return false;
    }

    if (!isCalibrated) {
        std::cerr << "[Servo] Warning: Servo not calibrated" << std::endl;
    }

    std::cout << "[Servo] Moving " << name << " from " << currentAngle
              << " to " << angle << " degrees" << std::endl;
    currentAngle = angle;
    return true;
}

int Servo::getAngle() const {
    return currentAngle;
}

bool Servo::isCalibratedStatus() const {
    return isCalibrated;
}

void Servo::reset() {
    std::cout << "[Servo] Resetting " << name << " to default position" << std::endl;
    currentAngle = 90;
}

std::string Servo::getName() const {
    return name;
}
