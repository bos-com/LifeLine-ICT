# 📡 API Documentation

This document provides details of all backend API endpoints.

---

## 📌 Overview

The API allows interaction with the system through HTTP requests.  
All responses are returned in a structured format.

Base URL:
`/api`

---

## 🔐 Authentication

Some endpoints require authentication using a token.

**Header Format:**
Authorization: Bearer <token>

If authentication is required, it will be specified per endpoint.

---

## 📍 Endpoints

### 1. Get All Resources

**Endpoint:** GET /api/resources  
**Authentication:** Optional  

**Description:**  
Fetch all resources from the system.

**Request Example:**
- Method: GET  
- URL: /api/resources  

**Response Example:**
- Status: Success  
- Data:
  - id: 1  
    name: Resource One  
  - id: 2  
    name: Resource Two  

---

### 2. Get Resource by ID

**Endpoint:** GET /api/resources/{id}  
**Authentication:** Optional  

**Description:**  
Fetch a single resource by its ID.

**Request Example:**
- Method: GET  
- URL: /api/resources/1  

**Response Example:**
- Status: Success  
- Data:
  - id: 1  
  - name: Resource One  

---

### 3. Create Resource

**Endpoint:** POST /api/resources  
**Authentication:** Required  

**Description:**  
Create a new resource.

**Request Example:**
- Method: POST  
- URL: /api/resources  
- Body:
  - name: New Resource  

**Response Example:**
- Status: Success  
- Message: Resource created successfully  

---

### 4. Update Resource

**Endpoint:** PUT /api/resources/{id}  
**Authentication:** Required  

**Description:**  
Update an existing resource.

**Request Example:**
- Method: PUT  
- URL: /api/resources/1  
- Body:
  - name: Updated Resource  

**Response Example:**
- Status: Success  
- Message: Resource updated successfully  

---

### 5. Delete Resource

**Endpoint:** DELETE /api/resources/{id}  
**Authentication:** Required  

**Description:**  
Delete a resource by ID.

**Request Example:**
- Method: DELETE  
- URL: /api/resources/1  

**Response Example:**
- Status: Success  
- Message: Resource deleted successfully  

---

## 🧪 Testing the API

You can test the API using:
- Postman  
- cURL  
- Browser (for GET endpoints)  

---

## 📌 Notes

- Ensure correct HTTP methods are used  
- Include authentication token where required  
- Follow endpoint structure carefully  

---

## 📎 Summary

- All endpoints are documented  
- Request/response examples provided  
- Authentication clearly defined  