from sqlalchemy import Column, Integer, String, Boolean, Date, Text, DateTime, func
from app.db.db_setup import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)


class AgentAgreement(TimestampMixin, Base):
    __tablename__ = "agent_agreements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Agreement Info
    dated = Column(Date)
    
    # Agent A (Landlord's Agent)
    agent_a_establishment = Column(String(255))
    agent_a_address = Column(String(255))
    agent_a_phone = Column(String(50))
    agent_a_fax = Column(String(50))
    agent_a_email = Column(String(100))
    agent_a_orn = Column(String(50))
    agent_a_license = Column(String(50))
    agent_a_po_box = Column(String(50))
    agent_a_emirates = Column(String(50))
    agent_a_name = Column(String(100))
    agent_a_brn = Column(String(50))
    agent_a_date_issued = Column(Date)
    agent_a_mobile = Column(String(20))
    agent_a_email_personal = Column(String(100))
    
    # Agent B (Tenant's Agent)
    agent_b_establishment = Column(String(255))
    agent_b_address = Column(String(255))
    agent_b_phone = Column(String(50))
    agent_b_fax = Column(String(50))
    agent_b_email = Column(String(100))
    agent_b_orn = Column(String(50))
    agent_b_license = Column(String(50))
    agent_b_po_box = Column(String(50))
    agent_b_emirates = Column(String(50))
    agent_b_name = Column(String(100))
    agent_b_brn = Column(String(50))
    agent_b_date_issued = Column(Date)
    agent_b_mobile = Column(String(20))
    agent_b_email_personal = Column(String(100))
    
    # Property Details
    property_address = Column(String(255))
    master_developer = Column(String(100))
    master_project = Column(String(100))
    building_name = Column(String(100))
    listed_price = Column(String(50))
    property_description = Column(Text)
    
    # Commission
    landlord_agent_percent = Column(String(10))
    tenant_agent_percent = Column(String(10))
    tenant_name = Column(String(100))
    tenant_passport = Column(String(50))
    tenant_budget = Column(String(50))
    tenant_contacted_agent = Column(Boolean)

    # Agent A Signature
    agent_a_signature = Column(String(255))
    agent_b_signature = Column(String(255))
