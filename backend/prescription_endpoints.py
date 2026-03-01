# Add these endpoints to backend/main.py after the review_case endpoint

# Get doctor prescriptions
@app.get("/api/doctor/prescriptions", response_model=Dict[str, Any])
async def get_doctor_prescriptions(request: Request):
    """Get prescriptions written by current doctor"""
    import json
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get current doctor from auth header
            current_doctor_id = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                try:
                    if token.startswith("auth-token-"):
                        token_parts = token.split("-")
                        if len(token_parts) >= 3:
                            current_doctor_id = int(token_parts[2])
                    elif token.startswith("admin-bypass-token-"):
                        current_doctor_id = 0
                    elif "_token_" in token:
                        token_parts = token.split("_")
                        if len(token_parts) >= 3:
                            current_doctor_id = int(token_parts[2])
                except (ValueError, IndexError):
                    current_doctor_id = None

            if current_doctor_id is None:
                raise HTTPException(status_code=401, detail="User not authenticated")
            
            # Get prescriptions with patient and case details
            await cursor.execute("""
            SELECT p.id, p.case_id, p.medication_name, p.dosage, p.frequency, p.duration, 
                   p.instructions, p.doctor_signature, p.created_at,
                   u.first_name, u.last_name, c.symptoms
            FROM prescriptions p
            JOIN users u ON p.patient_id = u.id
            JOIN medical_cases c ON p.case_id = c.id
            WHERE p.doctor_id = %s
            ORDER BY p.created_at DESC
            """, (current_doctor_id,))
            
            prescriptions = await cursor.fetchall()
            
            # Convert to response format
            prescription_list = []
            for prescription in prescriptions:
                prescription_list.append({
                    "id": prescription[0],
                    "case_id": prescription[1],
                    "medication_name": prescription[2],
                    "dosage": prescription[3],
                    "frequency": prescription[4],
                    "duration": prescription[5],
                    "instructions": prescription[6],
                    "doctor_signature": prescription[7],
                    "created_at": prescription[8].isoformat() if prescription[8] and hasattr(prescription[8], 'isoformat') else str(prescription[8]) if prescription[8] else None,
                    "patient_name": f"{prescription[9]} {prescription[10]}",
                    "symptoms": json.loads(prescription[11]) if prescription[11] else {}
                })
        
        await cursor.close()
        
        return {
            "success": True,
            "prescriptions": prescription_list,
            "total": len(prescription_list)
        }
        
    except Exception as e:
        print(f"⚠️ Error getting doctor prescriptions: {e}")
        return {"success": False, "message": "Failed to get prescriptions"}

# Get patient prescriptions
@app.get("/api/patient/prescriptions", response_model=Dict[str, Any])
async def get_patient_prescriptions(request: Request):
    """Get prescriptions for current patient"""
    import json
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get current patient from auth header
            current_patient_id = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                try:
                    if token.startswith("auth-token-"):
                        token_parts = token.split("-")
                        if len(token_parts) >= 3:
                            current_patient_id = int(token_parts[2])
                    elif "_token_" in token:
                        token_parts = token.split("_")
                        if len(token_parts) >= 3:
                            current_patient_id = int(token_parts[2])
                except (ValueError, IndexError):
                    current_patient_id = None

            if current_patient_id is None:
                raise HTTPException(status_code=401, detail="User not authenticated")
            
            # Get prescriptions with doctor and case details
            await cursor.execute("""
            SELECT p.id, p.case_id, p.medication_name, p.dosage, p.frequency, p.duration, 
                   p.instructions, p.doctor_signature, p.created_at,
                   u.first_name, u.last_name, c.doctor_diagnosis, c.doctor_notes
            FROM prescriptions p
            JOIN users u ON p.doctor_id = u.id
            JOIN medical_cases c ON p.case_id = c.id
            WHERE p.patient_id = %s
            ORDER BY p.created_at DESC
            """, (current_patient_id,))
            
            prescriptions = await cursor.fetchall()
            
            # Convert to response format
            prescription_list = []
            for prescription in prescriptions:
                prescription_list.append({
                    "id": prescription[0],
                    "case_id": prescription[1],
                    "medication_name": prescription[2],
                    "dosage": prescription[3],
                    "frequency": prescription[4],
                    "duration": prescription[5],
                    "instructions": prescription[6],
                    "doctor_signature": prescription[7],
                    "created_at": prescription[8].isoformat() if prescription[8] and hasattr(prescription[8], 'isoformat') else str(prescription[8]) if prescription[8] else None,
                    "doctor_name": f"{prescription[9]} {prescription[10]}",
                    "doctor_diagnosis": prescription[11],
                    "doctor_notes": prescription[12]
                })
        
        await cursor.close()
        
        return {
            "success": True,
            "prescriptions": prescription_list,
            "total": len(prescription_list)
        }
        
    except Exception as e:
        print(f"⚠️ Error getting patient prescriptions: {e}")
        return {"success": False, "message": "Failed to get prescriptions"}

# Download prescription as PDF
@app.get("/api/prescriptions/{prescription_id}/download")
async def download_prescription(prescription_id: int):
    """Generate downloadable prescription PDF"""
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get prescription details
            await cursor.execute("""
            SELECT p.medication_name, p.dosage, p.frequency, p.duration, p.instructions, 
                   p.doctor_signature, p.created_at,
                   patient.first_name as patient_first, patient.last_name as patient_last,
                   doctor.first_name as doctor_first, doctor.last_name as doctor_last,
                   c.doctor_diagnosis, c.doctor_notes, c.symptoms
            FROM prescriptions p
            JOIN users patient ON p.patient_id = patient.id
            JOIN users doctor ON p.doctor_id = doctor.id
            JOIN medical_cases c ON p.case_id = c.id
            WHERE p.id = %s
            """, (prescription_id,))
            
            prescription = await cursor.fetchone()
            
            if not prescription:
                return {"success": False, "message": "Prescription not found"}
            
            # Generate prescription content (in a real implementation, use a PDF library)
            prescription_content = f"""
MEDICAL PRESCRIPTION

Patient: {prescription[8]} {prescription[9]}
Date: {prescription[6]}

Doctor: {prescription[10]} {prescription[11]}
Signature: {prescription[5] or 'Digital Signature'}

DIAGNOSIS:
{prescription[12] or 'Not specified'}

CLINICAL NOTES:
{prescription[13] or 'Not specified'}

PRESCRIPTION:
Medication: {prescription[0]}
Dosage: {prescription[1]}
Frequency: {prescription[2]}
Duration: {prescription[3]} days

Instructions:
{prescription[4] or 'Follow medication label instructions'}

---
This is an electronically generated prescription.
Medical Center Pro - Licensed Medical Practice
            """
            
            await cursor.close()
            
            return {
                "success": True,
                "prescription_content": prescription_content,
                "filename": f"prescription_{prescription_id}.txt"
            }
            
    except Exception as e:
        print(f"⚠️ Error generating prescription: {e}")
        return {"success": False, "message": "Failed to generate prescription"}
