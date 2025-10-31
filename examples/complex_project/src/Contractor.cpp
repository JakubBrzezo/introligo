/**
 * @file Contractor.cpp
 * @brief Implementation of Contractor class
 */

#include "Contractor.h"
#include <iostream>

Contractor::Contractor(const std::string& contractorName, int maxExt)
    : name(contractorName), maxExtension(maxExt), currentPosition(0),
      currentState(RETRACTED), isInitialized(false), speed(5) {
    std::cout << "[Contractor] " << name << " created with max extension "
              << maxExtension << "mm" << std::endl;
}

Contractor::~Contractor() {
    std::cout << "[Contractor] " << name << " shutting down" << std::endl;
    if (currentState != RETRACTED) {
        retract();
    }
}

bool Contractor::initialize() {
    std::cout << "[Contractor] Initializing " << name << "..." << std::endl;

    // Simulate homing procedure
    currentState = RETRACTING;
    currentPosition = 0;
    currentState = RETRACTED;
    isInitialized = true;

    std::cout << "[Contractor] Initialization complete" << std::endl;
    return true;
}

bool Contractor::extend() {
    if (!isInitialized) {
        std::cerr << "[Contractor] Error: Not initialized" << std::endl;
        return false;
    }

    if (currentState == EXTENDED) {
        std::cout << "[Contractor] Already fully extended" << std::endl;
        return true;
    }

    std::cout << "[Contractor] Extending " << name << "..." << std::endl;
    currentState = EXTENDING;

    // Simulate extension
    currentPosition = 100;
    currentState = EXTENDED;

    std::cout << "[Contractor] Extension complete" << std::endl;
    return true;
}

bool Contractor::retract() {
    if (!isInitialized) {
        std::cerr << "[Contractor] Error: Not initialized" << std::endl;
        return false;
    }

    if (currentState == RETRACTED) {
        std::cout << "[Contractor] Already fully retracted" << std::endl;
        return true;
    }

    std::cout << "[Contractor] Retracting " << name << "..." << std::endl;
    currentState = RETRACTING;

    // Simulate retraction
    currentPosition = 0;
    currentState = RETRACTED;

    std::cout << "[Contractor] Retraction complete" << std::endl;
    return true;
}

void Contractor::stop() {
    std::cout << "[Contractor] Stopping " << name << " at position "
              << currentPosition << "%" << std::endl;

    if (currentState == EXTENDING || currentState == RETRACTING) {
        // Stop at current position
        currentState = (currentPosition > 50) ? EXTENDED : RETRACTED;
    }
}

Contractor::State Contractor::getState() const {
    return currentState;
}

int Contractor::getPosition() const {
    return currentPosition;
}

bool Contractor::setSpeed(int newSpeed) {
    if (newSpeed < 1 || newSpeed > 10) {
        std::cerr << "[Contractor] Error: Speed must be between 1 and 10" << std::endl;
        return false;
    }

    speed = newSpeed;
    std::cout << "[Contractor] Speed set to " << speed << std::endl;
    return true;
}

bool Contractor::isReady() const {
    return isInitialized && currentState != ERROR;
}

std::string Contractor::getStateString() const {
    switch (currentState) {
        case RETRACTED:  return "RETRACTED";
        case EXTENDING:  return "EXTENDING";
        case EXTENDED:   return "EXTENDED";
        case RETRACTING: return "RETRACTING";
        case ERROR:      return "ERROR";
        default:         return "UNKNOWN";
    }
}

std::string Contractor::getName() const {
    return name;
}
