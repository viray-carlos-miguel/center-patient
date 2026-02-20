"""
User Evaluation Study System
For collecting and analyzing user feedback on the AI system
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, EmailStr
from enum import Enum
import json
import statistics

class UserType(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
    IT_EXPERT = "it_expert"

class EvaluationType(str, Enum):
    PRE_TEST = "pre_test"
    POST_TEST = "post_test"
    LIKERT_SCALE = "likert_scale"
    CASE_EVALUATION = "case_evaluation"

class LikertResponse(BaseModel):
    question_id: str
    response: int  # 1-4 scale
    timestamp: datetime

class CaseEvaluation(BaseModel):
    case_id: str
    appropriateness_score: int  # 1-5 scale
    accuracy_score: int  # 1-5 scale
    clarity_score: int  # 1-5 scale
    notes: Optional[str] = None
    timestamp: datetime

class UserEvaluation(BaseModel):
    user_id: int
    user_type: UserType
    user_name: str
    email: EmailStr
    age: int
    gender: str
    location: str  # Sta. Ana, Pampanga
    profession: Optional[str] = None
    years_experience: Optional[int] = None
    digital_literacy: int  # 1-5 scale
    evaluation_type: EvaluationType
    responses: List[Dict]
    case_evaluations: Optional[List[CaseEvaluation]] = None
    completed_at: datetime
    session_duration: int  # minutes

class EvaluationQuestion(BaseModel):
    id: str
    question: str
    category: str
    evaluation_type: EvaluationType
    target_user_type: Optional[UserType] = None

class UserEvaluationSystem:
    def __init__(self):
        self.evaluations: List[UserEvaluation] = []
        self.questions: Dict[str, EvaluationQuestion] = self._initialize_questions()
        self.case_studies: Dict[str, Dict] = self._initialize_case_studies()
        self.participant_demographics = self._initialize_demographics()
        
    def _initialize_questions(self) -> Dict[str, EvaluationQuestion]:
        """Initialize evaluation questions based on research paper"""
        return {
            # Pre-test questions
            "pre_1": EvaluationQuestion(
                id="pre_1",
                question="I feel confident managing my health without professional help",
                category="confidence",
                evaluation_type=EvaluationType.PRE_TEST,
                target_user_type=UserType.PATIENT
            ),
            "pre_2": EvaluationQuestion(
                id="pre_2",
                question="I understand which medicines to take for common symptoms",
                category="knowledge",
                evaluation_type=EvaluationType.PRE_TEST,
                target_user_type=UserType.PATIENT
            ),
            "pre_3": EvaluationQuestion(
                id="pre_3",
                question="I trust online health information for medical decisions",
                category="trust",
                evaluation_type=EvaluationType.PRE_TEST
            ),
            
            # Post-test questions
            "post_1": EvaluationQuestion(
                id="post_1",
                question="The AI system helped me better understand my health condition",
                category="understanding",
                evaluation_type=EvaluationType.POST_TEST,
                target_user_type=UserType.PATIENT
            ),
            "post_2": EvaluationQuestion(
                id="post_2",
                question="The medicine recommendations were appropriate for my symptoms",
                category="appropriateness",
                evaluation_type=EvaluationType.POST_TEST,
                target_user_type=UserType.PATIENT
            ),
            "post_3": EvaluationQuestion(
                id="post_3",
                question="I feel more confident using this system than self-medicating",
                category="confidence",
                evaluation_type=EvaluationType.POST_TEST,
                target_user_type=UserType.PATIENT
            ),
            
            # Likert scale questions for all users
            "likert_1": EvaluationQuestion(
                id="likert_1",
                question="The system interface is easy to use",
                category="usability",
                evaluation_type=EvaluationType.LIKERT_SCALE
            ),
            "likert_2": EvaluationQuestion(
                id="likert_2",
                question="The system provides accurate medicine recommendations",
                category="accuracy",
                evaluation_type=EvaluationType.LIKERT_SCALE
            ),
            "likert_3": EvaluationQuestion(
                id="likert_3",
                question="The treatment analysis is clear and understandable",
                category="clarity",
                evaluation_type=EvaluationType.LIKERT_SCALE
            ),
            "likert_4": EvaluationQuestion(
                id="likert_4",
                question="The system is reliable for healthcare guidance",
                category="reliability",
                evaluation_type=EvaluationType.LIKERT_SCALE
            ),
            "likert_5": EvaluationQuestion(
                id="likert_5",
                question="I would recommend this system to others",
                category="recommendation",
                evaluation_type=EvaluationType.LIKERT_SCALE
            ),
            
            # Doctor-specific questions
            "doc_1": EvaluationQuestion(
                id="doc_1",
                question="The AI recommendations align with medical standards",
                category="medical_standards",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.DOCTOR
            ),
            "doc_2": EvaluationQuestion(
                id="doc_2",
                question="The doctor verification feature enhances patient safety",
                category="safety",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.DOCTOR
            ),
            "doc_3": EvaluationQuestion(
                id="doc_3",
                question="This system could improve healthcare accessibility in rural areas",
                category="accessibility",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.DOCTOR
            ),
            
            # IT expert questions
            "it_1": EvaluationQuestion(
                id="it_1",
                question="The system architecture is technically robust",
                category="technical",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.IT_EXPERT
            ),
            "it_2": EvaluationQuestion(
                id="it_2",
                question="The AI algorithms perform as expected",
                category="algorithm_performance",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.IT_EXPERT
            ),
            "it_3": EvaluationQuestion(
                id="it_3",
                question="The system is scalable for larger deployments",
                category="scalability",
                evaluation_type=EvaluationType.LIKERT_SCALE,
                target_user_type=UserType.IT_EXPERT
            )
        }
    
    def _initialize_case_studies(self) -> Dict[str, Dict]:
        """Initialize case studies for evaluation"""
        return {
            "case_1": {
                "id": "case_1",
                "title": "Adult with Fever and Headache",
                "patient_profile": {
                    "age": 35,
                    "weight": 70,
                    "symptoms": ["fever", "headache", "muscle_pain"],
                    "medical_conditions": []
                },
                "ai_recommendations": {
                    "primary": "paracetamol",
                    "alternatives": ["ibuprofen"],
                    "confidence": 0.85
                },
                "expected_evaluation": {
                    "appropriateness": 5,  # Very appropriate
                    "accuracy": 5,        # Very accurate
                    "clarity": 5           # Very clear
                }
            },
            "case_2": {
                "id": "case_2",
                "title": "Child with Allergic Symptoms",
                "patient_profile": {
                    "age": 8,
                    "weight": 25,
                    "symptoms": ["runny_nose", "sneezing", "itchy_eyes"],
                    "medical_conditions": ["asthma"]
                },
                "ai_recommendations": {
                    "primary": "cetirizine",
                    "alternatives": ["loratadine"],
                    "confidence": 0.92
                },
                "expected_evaluation": {
                    "appropriateness": 5,
                    "accuracy": 5,
                    "clarity": 5
                }
            },
            "case_3": {
                "id": "case_3",
                "title": "Elderly with Joint Pain",
                "patient_profile": {
                    "age": 68,
                    "weight": 65,
                    "symptoms": ["joint_pain", "stiffness"],
                    "medical_conditions": ["high_blood_pressure"]
                },
                "ai_recommendations": {
                    "primary": "acetaminophen",
                    "alternatives": ["topical_nsaid"],
                    "confidence": 0.78
                },
                "expected_evaluation": {
                    "appropriateness": 4,
                    "accuracy": 4,
                    "clarity": 5
                }
            }
        }
    
    def _initialize_demographics(self) -> Dict:
        """Initialize target demographics for Sta. Ana, Pampanga study"""
        return {
            "total_participants": 20,
            "distribution": {
                UserType.DOCTOR: 5,
                UserType.PATIENT: 10,
                UserType.IT_EXPERT: 5
            },
            "location_focus": "Sta. Ana, Pampanga",
            "age_ranges": {
                "18-25": 4,
                "26-35": 6,
                "36-45": 5,
                "46-55": 3,
                "56+": 2
            }
        }
    
    def get_questions_for_user_type(self, user_type: UserType, evaluation_type: EvaluationType) -> List[EvaluationQuestion]:
        """Get questions appropriate for user type and evaluation type"""
        questions = []
        
        for question in self.questions.values():
            if question.evaluation_type == evaluation_type:
                if question.target_user_type is None or question.target_user_type == user_type:
                    questions.append(question)
        
        return questions
    
    def create_evaluation_session(self, user_data: Dict, evaluation_type: EvaluationType) -> Dict:
        """Create a new evaluation session"""
        session_id = f"eval_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_data['id']}"
        
        questions = self.get_questions_for_user_type(
            UserType(user_data["user_type"]), 
            evaluation_type
        )
        
        return {
            "session_id": session_id,
            "user_data": user_data,
            "evaluation_type": evaluation_type,
            "questions": [q.dict() for q in questions],
            "case_studies": list(self.case_studies.values()) if evaluation_type == EvaluationType.CASE_EVALUATION else [],
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=2)  # 2-hour session timeout
        }
    
    def submit_evaluation(self, session_data: Dict, responses: List[Dict], case_evaluations: Optional[List[Dict]] = None) -> UserEvaluation:
        """Submit completed evaluation"""
        user_data = session_data["user_data"]
        
        # Convert responses
        likert_responses = []
        for resp in responses:
            likert_responses.append(LikertResponse(
                question_id=resp["question_id"],
                response=resp["response"],
                timestamp=datetime.now()
            ))
        
        # Convert case evaluations
        case_evals = None
        if case_evaluations:
            case_evals = []
            for case_eval in case_evaluations:
                case_evals.append(CaseEvaluation(
                    case_id=case_eval["case_id"],
                    appropriateness_score=case_eval["appropriateness_score"],
                    accuracy_score=case_eval["accuracy_score"],
                    clarity_score=case_eval["clarity_score"],
                    notes=case_eval.get("notes"),
                    timestamp=datetime.now()
                ))
        
        # Calculate session duration
        session_duration = int((datetime.now() - session_data["created_at"]).total_seconds() / 60)
        
        evaluation = UserEvaluation(
            user_id=user_data["id"],
            user_type=UserType(user_data["user_type"]),
            user_name=user_data["name"],
            email=user_data["email"],
            age=user_data["age"],
            gender=user_data["gender"],
            location=user_data["location"],
            profession=user_data.get("profession"),
            years_experience=user_data.get("years_experience"),
            digital_literacy=user_data.get("digital_literacy", 3),
            evaluation_type=session_data["evaluation_type"],
            responses=responses,
            case_evaluations=case_evals,
            completed_at=datetime.now(),
            session_duration=session_duration
        )
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def calculate_weighted_mean(self, responses: List[Dict]) -> float:
        """Calculate weighted mean for Likert scale responses"""
        if not responses:
            return 0.0
        
        # Weighted mean formula: x̄ = Σ(f·x)/N
        total_weighted_score = 0
        total_responses = 0
        
        for response in responses:
            score = response.get("response", 0)
            frequency = 1  # Each response counts as one
            total_weighted_score += score * frequency
            total_responses += frequency
        
        return total_weighted_score / total_responses if total_responses > 0 else 0.0
    
    def calculate_standard_deviation(self, responses: List[Dict]) -> float:
        """Calculate standard deviation for responses"""
        if len(responses) < 2:
            return 0.0
        
        scores = [r.get("response", 0) for r in responses]
        mean = statistics.mean(scores)
        
        variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
        return statistics.sqrt(variance)
    
    def analyze_question_responses(self, question_id: str, user_type: Optional[UserType] = None) -> Dict:
        """Analyze responses for a specific question"""
        relevant_evaluations = []
        
        for eval in self.evaluations:
            if user_type is None or eval.user_type == user_type:
                for response in eval.responses:
                    if response.get("question_id") == question_id:
                        relevant_evaluations.append({
                            "response": response.get("response", 0),
                            "user_type": eval.user_type,
                            "user_id": eval.user_id
                        })
        
        if not relevant_evaluations:
            return {"error": "No responses found"}
        
        responses_only = [r["response"] for r in relevant_evaluations]
        
        # Calculate statistics
        weighted_mean = self.calculate_weighted_mean(relevant_evaluations)
        std_dev = self.calculate_standard_deviation(relevant_evaluations)
        
        # Frequency distribution
        frequency = {1: 0, 2: 0, 3: 0, 4: 0}
        for response in responses_only:
            if 1 <= response <= 4:
                frequency[response] += 1
        
        return {
            "question_id": question_id,
            "total_responses": len(responses_only),
            "weighted_mean": round(weighted_mean, 2),
            "standard_deviation": round(std_dev, 2),
            "frequency_distribution": frequency,
            "interpretation": self._interpret_score(weighted_mean)
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret weighted mean score according to research paper scale"""
        if score >= 3.25:
            return "Strongly Agree"
        elif score >= 2.50:
            return "Agree"
        elif score >= 1.75:
            return "Disagree"
        else:
            return "Strongly Disagree"
    
    def generate_evaluation_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        if not self.evaluations:
            return {"error": "No evaluations completed"}
        
        report = {
            "study_metadata": {
                "title": "AI-Powered Decision Support System Evaluation",
                "location": "Sta. Ana, Pampanga",
                "evaluation_period": {
                    "start": min(e.completed_at for e in self.evaluations).isoformat(),
                    "end": max(e.completed_at for e in self.evaluations).isoformat()
                },
                "total_participants": len(self.evaluations)
            },
            "participant_demographics": self._analyze_demographics(),
            "overall_statistics": self._calculate_overall_statistics(),
            "question_analysis": self._analyze_all_questions(),
            "case_study_analysis": self._analyze_case_studies(),
            "conclusions": self._generate_conclusions()
        }
        
        return report
    
    def _analyze_demographics(self) -> Dict:
        """Analyze participant demographics"""
        demographics = {
            "user_types": {},
            "age_distribution": {},
            "gender_distribution": {},
            "digital_literacy": {},
            "experience_levels": {}
        }
        
        for eval in self.evaluations:
            # User types
            user_type = eval.user_type.value
            demographics["user_types"][user_type] = demographics["user_types"].get(user_type, 0) + 1
            
            # Age groups
            age_group = self._get_age_group(eval.age)
            demographics["age_distribution"][age_group] = demographics["age_distribution"].get(age_group, 0) + 1
            
            # Gender
            demographics["gender_distribution"][eval.gender] = demographics["gender_distribution"].get(eval.gender, 0) + 1
            
            # Digital literacy
            literacy = eval.digital_literacy
            demographics["digital_literacy"][literacy] = demographics["digital_literacy"].get(literacy, 0) + 1
            
            # Experience (for professionals)
            if eval.years_experience:
                exp_group = self._get_experience_group(eval.years_experience)
                demographics["experience_levels"][exp_group] = demographics["experience_levels"].get(exp_group, 0) + 1
        
        return demographics
    
    def _get_age_group(self, age: int) -> str:
        """Get age group category"""
        if age <= 25:
            return "18-25"
        elif age <= 35:
            return "26-35"
        elif age <= 45:
            return "36-45"
        elif age <= 55:
            return "46-55"
        else:
            return "56+"
    
    def _get_experience_group(self, years: int) -> str:
        """Get experience group category"""
        if years <= 2:
            return "0-2 years"
        elif years <= 5:
            return "3-5 years"
        elif years <= 10:
            return "6-10 years"
        else:
            return "10+ years"
    
    def _calculate_overall_statistics(self) -> Dict:
        """Calculate overall evaluation statistics"""
        all_responses = []
        for eval in self.evaluations:
            all_responses.extend(eval.responses)
        
        if not all_responses:
            return {"error": "No responses found"}
        
        overall_mean = self.calculate_weighted_mean(all_responses)
        overall_std = self.calculate_standard_deviation(all_responses)
        
        return {
            "total_responses": len(all_responses),
            "overall_weighted_mean": round(overall_mean, 2),
            "overall_standard_deviation": round(overall_std, 2),
            "overall_interpretation": self._interpret_score(overall_mean),
            "average_session_duration": round(statistics.mean([e.session_duration for e in self.evaluations]), 2)
        }
    
    def _analyze_all_questions(self) -> Dict:
        """Analyze all questions"""
        question_analysis = {}
        
        for question_id in self.questions.keys():
            analysis = self.analyze_question_responses(question_id)
            if "error" not in analysis:
                question_analysis[question_id] = analysis
        
        return question_analysis
    
    def _analyze_case_studies(self) -> Dict:
        """Analyze case study evaluations"""
        case_analysis = {}
        
        for eval in self.evaluations:
            if eval.case_evaluations:
                for case_eval in eval.case_evaluations:
                    case_id = case_eval.case_id
                    if case_id not in case_analysis:
                        case_analysis[case_id] = {
                            "total_evaluations": 0,
                            "appropriateness_scores": [],
                            "accuracy_scores": [],
                            "clarity_scores": []
                        }
                    
                    case_analysis[case_id]["total_evaluations"] += 1
                    case_analysis[case_id]["appropriateness_scores"].append(case_eval.appropriateness_score)
                    case_analysis[case_id]["accuracy_scores"].append(case_eval.accuracy_score)
                    case_analysis[case_id]["clarity_scores"].append(case_eval.clarity_score)
        
        # Calculate averages for each case
        for case_id, data in case_analysis.items():
            if data["appropriateness_scores"]:
                data["average_appropriateness"] = round(statistics.mean(data["appropriateness_scores"]), 2)
                data["average_accuracy"] = round(statistics.mean(data["accuracy_scores"]), 2)
                data["average_clarity"] = round(statistics.mean(data["clarity_scores"]), 2)
        
        return case_analysis
    
    def _generate_conclusions(self) -> List[str]:
        """Generate study conclusions based on analysis"""
        conclusions = []
        
        overall_stats = self._calculate_overall_statistics()
        if "error" not in overall_stats:
            mean_score = overall_stats["overall_weighted_mean"]
            interpretation = overall_stats["overall_interpretation"]
            
            conclusions.append(f"Overall, participants {interpretation} with the system's performance (mean: {mean_score})")
            
            if mean_score >= 3.25:
                conclusions.append("The system successfully meets its objectives and is ready for implementation")
            elif mean_score >= 2.50:
                conclusions.append("The system shows promise but requires minor improvements before full implementation")
            else:
                conclusions.append("The system requires significant improvements before implementation")
        
        # Check specific objectives
        usability_analysis = self.analyze_question_responses("likert_1")
        if "error" not in usability_analysis:
            conclusions.append(f"System usability: {usability_analysis['interpretation']} (mean: {usability_analysis['weighted_mean']})")
        
        accuracy_analysis = self.analyze_question_responses("likert_2")
        if "error" not in accuracy_analysis:
            conclusions.append(f"System accuracy: {accuracy_analysis['interpretation']} (mean: {accuracy_analysis['weighted_mean']})")
        
        return conclusions
    
    def export_data_for_analysis(self) -> Dict:
        """Export all data for statistical analysis"""
        return {
            "evaluations": [eval.dict() for eval in self.evaluations],
            "questions": {qid: q.dict() for qid, q in self.questions.items()},
            "case_studies": self.case_studies,
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_evaluations": len(self.evaluations),
                "study_location": "Sta. Ana, Pampanga"
            }
        }

# Global instance
user_evaluation = UserEvaluationSystem()
