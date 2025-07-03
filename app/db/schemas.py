from pydantic import BaseModel
from datetime import date
from typing import Optional

class AgentAgreementBase(BaseModel):
    # Agreement Info
    dated: date
    
    # Agent A
    agent_a_establishment: str
    agent_a_address: str
    agent_a_phone: str
    agent_a_fax: str
    agent_a_email: str
    agent_a_orn: str
    agent_a_license: str
    agent_a_po_box: str
    agent_a_emirates: str
    agent_a_name: str
    agent_a_brn: str
    agent_a_date_issued: date
    agent_a_mobile: str
    agent_a_email_personal: str
    
    # Agent B
    agent_b_establishment: str
    agent_b_address: str
    agent_b_phone: str
    agent_b_fax: str
    agent_b_email: str
    agent_b_orn: str
    agent_b_license: str
    agent_b_po_box: str
    agent_b_emirates: str
    agent_b_name: str
    agent_b_brn: str
    agent_b_date_issued: date
    agent_b_mobile: str
    agent_b_email_personal: str
    
    # Property
    property_address: str
    master_developer: str
    master_project: str
    building_name: str
    listed_price: str
    property_description: str
    
    # Commission
    landlord_agent_percent: str
    tenant_agent_percent: str
    tenant_name: str
    tenant_passport: str
    tenant_budget: str
    tenant_contacted_agent: bool

    # Signature
    agent_a_signature: str
    agent_b_signature: str

class AgentAgreementCreate(AgentAgreementBase):
    pass

class AgentAgreement(AgentAgreementBase):
    id: int
    created_at: date
    
    class Config:
        orm_mode = True