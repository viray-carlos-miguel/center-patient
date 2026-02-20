"""
Doctor Verification and Digital Signature System
For prescription validation and medical oversight
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import json
from pydantic import BaseModel, EmailStr
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PrescriptionRequest(BaseModel):
    id: str
    patient_id: int
    patient_name: str
    patient_age: int
    patient_weight: float
    symptoms: List[str]
    recommended_medicines: List[Dict]
    ai_confidence: float
    risk_level: str
    created_at: datetime
    expires_at: datetime
    status: VerificationStatus = VerificationStatus.PENDING

class DoctorSignature(BaseModel):
    doctor_id: int
    doctor_name: str
    doctor_license: str
    signature_hash: str
    timestamp: datetime
    ip_address: str
    verification_method: str  # "digital_signature", "otp", "biometric"

class VerificationRecord(BaseModel):
    request_id: str
    doctor_id: int
    signature: DoctorSignature
    decision: str  # "approve", "reject"
    notes: Optional[str] = None
    verified_at: datetime
    prescription_modifications: Optional[List[Dict]] = None

class DoctorVerificationSystem:
    def __init__(self):
        self.pending_requests: Dict[str, PrescriptionRequest] = {}
        self.verification_records: Dict[str, VerificationRecord] = {}
        self.doctor_credentials: Dict[int, Dict] = self._initialize_doctors()
        self.digital_signatures: Dict[int, str] = {}
        
    def _initialize_doctors(self) -> Dict[int, Dict]:
        """Initialize verified doctors for Sta. Ana, Pampanga"""
        return {
            1: {
                "id": 1,
                "name": "Dr. Maria Santos",
                "license": "PRC-MED-12345",
                "specialization": "General Practice",
                "email": "maria.santos@medical.com",
                "phone": "+639123456789",
                "clinic": "Sta. Ana Health Center",
                "verified": True,
                "active": True
            },
            2: {
                "id": 2,
                "name": "Dr. Jose Reyes",
                "license": "PRC-MED-67890",
                "specialization": "Internal Medicine",
                "email": "jose.reyes@medical.com",
                "phone": "+639987654321",
                "clinic": "Holy Cross Medical Clinic",
                "verified": True,
                "active": True
            },
            3: {
                "id": 3,
                "name": "Dr. Ana Cruz",
                "license": "PRC-MED-54321",
                "specialization": "Pediatrics",
                "email": "ana.cruz@medical.com",
                "phone": "+639112233445",
                "clinic": "Pampanga Pediatric Care",
                "verified": True,
                "active": True
            }
        }
    
    def create_prescription_request(self, patient_data: Dict, ai_recommendations: Dict) -> PrescriptionRequest:
        """Create a new prescription request for doctor verification"""
        request_id = self._generate_request_id()
        
        # Calculate expiration (24 hours from creation)
        expires_at = datetime.now() + timedelta(hours=24)
        
        request = PrescriptionRequest(
            id=request_id,
            patient_id=patient_data["id"],
            patient_name=patient_data["name"],
            patient_age=patient_data["age"],
            patient_weight=patient_data.get("weight", 70),
            symptoms=patient_data["symptoms"],
            recommended_medicines=ai_recommendations.get("recommendations", []),
            ai_confidence=ai_recommendations.get("confidence", 0.0),
            risk_level=ai_recommendations.get("risk_level", "low"),
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        self.pending_requests[request_id] = request
        return request
    
    def _generate_request_id(self) -> str:
        """Generate unique prescription request ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(hash(timestamp))[:6]
        return f"RX{timestamp}{random_suffix}"
    
    def get_pending_requests(self, doctor_id: Optional[int] = None) -> List[PrescriptionRequest]:
        """Get pending prescription requests"""
        pending = []
        current_time = datetime.now()
        
        for request in self.pending_requests.values():
            # Check if expired
            if current_time > request.expires_at:
                request.status = VerificationStatus.EXPIRED
                continue
            
            # Filter by doctor if specified
            if doctor_id is None or self._is_assigned_doctor(request, doctor_id):
                pending.append(request)
        
        return sorted(pending, key=lambda x: x.created_at, reverse=True)
    
    def _is_assigned_doctor(self, request: PrescriptionRequest, doctor_id: int) -> bool:
        """Check if doctor is assigned to this request (simplified - all doctors can review)"""
        return True  # In real implementation, would have assignment logic
    
    def verify_doctor_credentials(self, doctor_id: int, license_number: str, password: str) -> bool:
        """Verify doctor credentials"""
        doctor = self.doctor_credentials.get(doctor_id)
        if not doctor:
            return False
        
        return (
            doctor["license"] == license_number and
            doctor["verified"] and
            doctor["active"]
        )
    
    def generate_otp(self, doctor_id: int) -> str:
        """Generate one-time password for doctor verification"""
        import random
        otp = str(random.randint(100000, 999999))
        
        # Store OTP (in real system, would use secure storage)
        doctor = self.doctor_credentials.get(doctor_id, {})
        doctor["otp"] = otp
        doctor["otp_expires"] = datetime.now() + timedelta(minutes=5)
        
        return otp
    
    def verify_otp(self, doctor_id: int, otp: str) -> bool:
        """Verify OTP for doctor"""
        doctor = self.doctor_credentials.get(doctor_id, {})
        stored_otp = doctor.get("otp")
        expires = doctor.get("otp_expires")
        
        if not stored_otp or not expires:
            return False
        
        if datetime.now() > expires:
            return False
        
        return stored_otp == otp
    
    def create_digital_signature(self, doctor_id: int, request_data: str, verification_method: str = "digital_signature") -> DoctorSignature:
        """Create digital signature for doctor"""
        doctor = self.doctor_credentials.get(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        # Create signature hash
        signature_data = f"{doctor_id}{request_data}{datetime.now().isoformat()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        signature = DoctorSignature(
            doctor_id=doctor_id,
            doctor_name=doctor["name"],
            doctor_license=doctor["license"],
            signature_hash=signature_hash,
            timestamp=datetime.now(),
            ip_address="127.0.0.1",  # In real system, would get actual IP
            verification_method=verification_method
        )
        
        # Store signature
        self.digital_signatures[doctor_id] = signature_hash
        return signature
    
    def approve_prescription(self, request_id: str, doctor_id: int, notes: Optional[str] = None, modifications: Optional[List[Dict]] = None) -> VerificationRecord:
        """Approve prescription request"""
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError("Prescription request not found")
        
        if request.status != VerificationStatus.PENDING:
            raise ValueError("Request is not pending")
        
        # Create digital signature
        signature = self.create_digital_signature(doctor_id, json.dumps(request.dict()))
        
        # Create verification record
        record = VerificationRecord(
            request_id=request_id,
            doctor_id=doctor_id,
            signature=signature,
            decision="approve",
            notes=notes,
            verified_at=datetime.now(),
            prescription_modifications=modifications
        )
        
        # Update request status
        request.status = VerificationStatus.APPROVED
        
        # Store verification record
        self.verification_records[request_id] = record
        
        # Remove from pending
        del self.pending_requests[request_id]
        
        return record
    
    def reject_prescription(self, request_id: str, doctor_id: int, reason: str) -> VerificationRecord:
        """Reject prescription request"""
        request = self.pending_requests.get(request_id)
        if not request:
            raise ValueError("Prescription request not found")
        
        # Create digital signature
        signature = self.create_digital_signature(doctor_id, json.dumps(request.dict()))
        
        # Create verification record
        record = VerificationRecord(
            request_id=request_id,
            doctor_id=doctor_id,
            signature=signature,
            decision="reject",
            notes=reason,
            verified_at=datetime.now()
        )
        
        # Update request status
        request.status = VerificationStatus.REJECTED
        
        # Store verification record
        self.verification_records[request_id] = record
        
        # Remove from pending
        del self.pending_requests[request_id]
        
        return record
    
    def get_verification_record(self, request_id: str) -> Optional[VerificationRecord]:
        """Get verification record for a prescription"""
        return self.verification_records.get(request_id)
    
    def verify_signature(self, request_id: str, signature_hash: str) -> bool:
        """Verify digital signature"""
        record = self.verification_records.get(request_id)
        if not record:
            return False
        
        return record.signature.signature_hash == signature_hash
    
    def get_doctor_workload(self, doctor_id: int, days: int = 7) -> Dict:
        """Get doctor workload statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        workload = {
            "total_verified": 0,
            "approved": 0,
            "rejected": 0,
            "pending": 0,
            "average_time": 0
        }
        
        verified_times = []
        
        for record in self.verification_records.values():
            if record.doctor_id == doctor_id and record.verified_at >= cutoff_date:
                workload["total_verified"] += 1
                if record.decision == "approve":
                    workload["approved"] += 1
                else:
                    workload["rejected"] += 1
                
                # Calculate processing time (from request creation to verification)
                # This is simplified - in real system would track request creation time
                verified_times.append(0)  # Placeholder
        
        # Count pending requests
        for request in self.pending_requests.values():
            if self._is_assigned_doctor(request, doctor_id):
                workload["pending"] += 1
        
        # Calculate average time
        if verified_times:
            workload["average_time"] = sum(verified_times) / len(verified_times)
        
        return workload
    
    def get_prescription_statistics(self, days: int = 30) -> Dict:
        """Get overall prescription verification statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stats = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "expired": 0,
            "pending": 0,
            "average_processing_time": 0,
            "top_medicines": {},
            "risk_distribution": {"low": 0, "moderate": 0, "high": 0}
        }
        
        processing_times = []
        medicine_counts = {}
        
        # Count verification records
        for record in self.verification_records.values():
            if record.verified_at >= cutoff_date:
                stats["total_requests"] += 1
                if record.decision == "approve":
                    stats["approved"] += 1
                else:
                    stats["rejected"] += 1
        
        # Count pending and expired requests
        for request in self.pending_requests.values():
            if request.created_at >= cutoff_date:
                stats["total_requests"] += 1
                if request.status == VerificationStatus.EXPIRED:
                    stats["expired"] += 1
                elif request.status == VerificationStatus.PENDING:
                    stats["pending"] += 1
                    stats["risk_distribution"][request.risk_level] += 1
                    
                    # Count medicines
                    for med in request.recommended_medicines:
                        med_name = med.get("drug_name", "unknown")
                        medicine_counts[med_name] = medicine_counts.get(med_name, 0) + 1
        
        # Get top medicines
        stats["top_medicines"] = dict(sorted(medicine_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return stats
    
    def export_verification_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Export verification data for analysis"""
        export_data = []
        
        for record in self.verification_records.values():
            if start_date <= record.verified_at <= end_date:
                export_data.append({
                    "request_id": record.request_id,
                    "doctor_id": record.doctor_id,
                    "doctor_name": record.signature.doctor_name,
                    "decision": record.decision,
                    "verified_at": record.verified_at.isoformat(),
                    "notes": record.notes,
                    "verification_method": record.signature.verification_method
                })
        
        return export_data

# Global instance
doctor_verification = DoctorVerificationSystem()
