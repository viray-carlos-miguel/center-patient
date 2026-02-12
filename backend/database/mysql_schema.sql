-- MySQL XAMPP Schema for Medical Center Pro
-- Educational Medical Management System

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS medical_center;
USE medical_center;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- Medical cases table
CREATE TABLE IF NOT EXISTS medical_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NULL,
    title VARCHAR(200) NOT NULL,
    symptoms TEXT NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    status ENUM('pending', 'under_review', 'diagnosed', 'treated', 'closed') DEFAULT 'pending',
    ai_assessment JSON NULL,
    doctor_diagnosis TEXT NULL,
    doctor_notes TEXT NULL,
    prescription JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_patient (patient_id),
    INDEX idx_doctor (doctor_id),
    INDEX idx_status (status),
    INDEX idx_severity (severity),
    INDEX idx_created (created_at)
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    medication_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(200) NOT NULL,
    duration_days INT NOT NULL,
    instructions TEXT NOT NULL,
    doctor_signature VARCHAR(255) NULL,
    is_educational BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_case (case_id),
    INDEX idx_doctor (doctor_id),
    INDEX idx_patient (patient_id)
);

-- Insert demo data
INSERT IGNORE INTO users (email, password_hash, role, first_name, last_name, is_active) VALUES
('admin@medical.com', 'admin123', 'admin', 'System', 'Admin', TRUE),
('dr.smith@medical.com', 'doctor123', 'doctor', 'John', 'Smith', TRUE),
('dr.jones@medical.com', 'neurology123', 'doctor', 'Sarah', 'Jones', TRUE),
('patient.demo@medical.com', 'patient123', 'patient', 'Demo', 'Patient', TRUE),
('john.doe@example.com', 'password123', 'patient', 'John', 'Doe', TRUE);

-- Insert demo cases
INSERT IGNORE INTO medical_cases (patient_id, title, symptoms, severity, status, ai_assessment) VALUES
((SELECT id FROM users WHERE email = 'patient.demo@medical.com'), 
 'Persistent Headache with Fever', 
 'Headache for 3 days, fever 38.5°C, fatigue, mild dizziness', 
 'medium', 'pending',
 JSON_OBJECT(
   'possible_conditions', JSON_ARRAY('Tension Headache', 'Viral Infection'),
   'confidence_score', 0.75,
   'recommended_tests', JSON_ARRAY('Physical Examination', 'Temperature Check'),
   'urgency_level', 'medium',
   'educational_note', 'Educational AI assessment based on symptoms'
 )),
 
((SELECT id FROM users WHERE email = 'john.doe@example.com'), 
 'Seasonal Allergy Symptoms', 
 'Sneezing, runny nose, itchy eyes, congestion for 2 weeks', 
 'low', 'pending',
 JSON_OBJECT(
   'possible_conditions', JSON_ARRAY('Allergic Rhinitis', 'Seasonal Allergies'),
   'confidence_score', 0.85,
   'recommended_tests', JSON_ARRAY('Allergy Test', 'Physical Examination'),
   'urgency_level', 'low',
   'educational_note', 'Educational AI assessment based on symptoms'
 ));

-- Insert demo prescriptions
INSERT IGNORE INTO prescriptions (case_id, doctor_id, patient_id, medication_name, dosage, frequency, duration_days, instructions, doctor_signature) VALUES
((SELECT id FROM medical_cases WHERE title = 'Persistent Headache with Fever'), 
 (SELECT id FROM users WHERE email = 'dr.smith@medical.com'),
 (SELECT id FROM users WHERE email = 'patient.demo@medical.com'),
 'Acetaminophen', '500mg', 'Every 6 hours as needed', 3, 
 'Take with food. Do not exceed 4,000mg per day.',
 'Dr. John Smith'),
 
((SELECT id FROM medical_cases WHERE title = 'Seasonal Allergy Symptoms'), 
 (SELECT id FROM users WHERE email = 'dr.jones@medical.com'),
 (SELECT id FROM users WHERE email = 'john.doe@example.com'),
 'Loratadine', '10mg', 'Once daily', 7, 
 'Take in the morning. May cause drowsiness.',
 'Dr. Sarah Jones');

-- Show database status
SELECT 'Database setup completed!' as status;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_cases FROM medical_cases;
SELECT COUNT(*) as total_prescriptions FROM prescriptions;
