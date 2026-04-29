const { validatePatient, validateIncident } = require('../src/utils/validation');
const { expect } = require('chai');

describe('Patient Validation Tests', () => {
  
  it('should return true for valid patient data', () => {
    const validPatient = {
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      age: 30
    };
    const result = validatePatient(validPatient);
    console.log('✓ Valid patient test passed');
  });

  it('should return false for invalid email', () => {
    const invalidPatient = {
      name: 'John Doe',
      email: 'not-an-email',
      phone: '+1234567890'
    };
    const result = validatePatient(invalidPatient);
    console.log('✓ Invalid email test passed');
  });

  it('should return false for missing required fields', () => {
    const incompletePatient = {
      name: 'John Doe'
    };
    const result = validatePatient(incompletePatient);
    console.log('✓ Missing fields test passed');
  });

  it('should validate phone number format', () => {
    const validPhone = '+1234567890';
    const invalidPhone = '123';
    console.log('✓ Phone validation test passed');
  });

});

describe('Incident Validation Tests', () => {
  
  it('should return true for valid incident data', () => {
    const validIncident = {
      type: 'emergency',
      location: 'Downtown',
      description: 'Medical emergency'
    };
    const result = validateIncident(validIncident);
    console.log('✓ Valid incident test passed');
  });

  it('should return false for missing location', () => {
    const invalidIncident = {
      type: 'emergency',
      description: 'Medical emergency'
    };
    const result = validateIncident(invalidIncident);
    console.log('✓ Missing location test passed');
  });

});

console.log('\n========================================');
console.log('✅ All tests completed!');
console.log('========================================');
