"""
Database Schemas for DeepTrace

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisFrameScore(BaseModel):
    frame_index: int = Field(..., description="Frame number in sequence")
    confidence: float = Field(..., ge=0, le=1, description="Deepfake confidence score 0-1")

class AnalysisJob(BaseModel):
    filename: str
    filesize: int
    filehash: str
    status: Literal["queued", "processing", "completed", "failed"] = "completed"
    accuracy: float = Field(..., ge=0, le=1)
    deepfake_likelihood: float = Field(..., ge=0, le=1)
    model: str = Field("CNN+LSTM v1", description="Model identifier used for analysis")
    frame_scores: List[AnalysisFrameScore] = []
    analyzed_at: Optional[datetime] = None

class VerificationRecord(BaseModel):
    filehash: str
    contract_address: str
    tx_hash: str
    network: str = "ethereum"
    verified: bool = True
    timestamp: datetime

class SubscriptionPlan(BaseModel):
    name: Literal["Free", "Pro", "Enterprise"]
    price_monthly: float
    features: List[str]

class Subscription(BaseModel):
    user_email: str
    plan: Literal["Free", "Pro", "Enterprise"]
    started_at: datetime
    status: Literal["active", "canceled", "past_due"] = "active"

class UserActivity(BaseModel):
    user_email: Optional[str] = None
    action: Literal["upload", "analyze", "verify", "login"]
    metadata: dict = {}
    created_at: Optional[datetime] = None
