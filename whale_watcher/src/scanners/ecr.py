# AWS ECR specific data models and implementations
from dataclasses import dataclass

@dataclass
class ECR_Findings:
    name: str
    description: str
    