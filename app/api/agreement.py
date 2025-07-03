from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from fpdf import FPDF
import os

from app.db.models import AgentAgreement
from app.db.schemas import AgentAgreementCreate
from app.db.db_setup import get_db

router = APIRouter()


class AgreementPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=30)  # Increased bottom margin
        # More generous margins
        self.set_margins(left=25, top=15, right=25)
        self.set_font("Arial", size=10)  # Set default font
    
    def header(self):
        self.image("uploads/indus.png", x=25, y=10, w=25)  # Smaller image, adjusted position
        self.set_font("Arial", "B", 14)  # Slightly smaller title
        self.cell(0, 8, "AGENT TO AGENT AGREEMENT", ln=1, align="C")
        self.set_font("Arial", "", 9)  # Smaller subtitle
        self.cell(0, 5, "As per the Real Estate Brokers By-Law No. (85) of 2006", ln=1, align="C")
        self.ln(8)  # Reduced spacing
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 7)  # Smaller footer text
        self.cell(0, 4, "203 Al Sharafi Building | Bur Dubai, Dubai UAE | P.O Box 118163", ln=1, align="C")
        self.cell(0, 4, "Phone: +971 4 3519995 | Fax: +971 43515611 | www.indus-re.com", ln=1, align="C")
    
    def section_title(self, title):
        if self.get_y() > self.h - 40:  # More conservative page break check
            self.add_page()
        self.set_font("Arial", "B", 11)  # Smaller section titles
        self.cell(0, 6, title, ln=1)
        self.ln(3)  # Reduced spacing
        
    def bordered_section(self, title, data):
        # More conservative height estimation
        estimated_height = (len(data) * 7) + 15
        if self.get_y() + estimated_height > self.h - 40:
            self.add_page()
            
        x_start = self.get_x()
        y_start = self.get_y()
    
        # Narrower section to fit within margins
        section_width = 160
        self.rect(x_start, y_start, section_width, estimated_height)
    
        self.set_font("Arial", "B", 10)  # Smaller title font
        self.cell(0, 6, title, ln=1)
        self.ln(2)
    
        self.set_xy(x_start + 5, self.get_y())
    
        for label, value in data.items():
            self.set_font("Arial", "B", 9)  # Smaller label font
            self.cell(60, 6, f"{label}:", 0, 0, "L")  # Narrower label column
        
            line_x = self.get_x()
            line_y = self.get_y()
            self.line(line_x, line_y, line_x, line_y + 6)  # Shorter divider
            self.cell(3, 6, "", 0, 0)  # Smaller spacer
        
            self.set_font("Arial", "", 9)  # Smaller value font
            value_str = str(value) if value is not None else ""
        
            # Calculate width with new dimensions
            text_width = section_width - 60 - 3 - 10
            self.set_xy(line_x + 3, line_y)
            self.multi_cell(text_width, 6, value_str, 0, "L")  # Smaller line height
        
            self.set_xy(x_start + 5, self.get_y())
            self.line(x_start, self.get_y(), x_start + section_width, self.get_y())
    
        self.set_xy(x_start, y_start + estimated_height)
        self.ln(4)  # Reduced spacing

def generate_agreement(data: dict) -> str:
    pdf = AgreementPDF()
    pdf.add_page()
    
    # Header with date
    pdf.set_font("Arial", "", 9)  # Smaller date font
    pdf.cell(0, 5, f"Date: {data['dated']}", ln=1, align="R")
    pdf.ln(8)  # Reduced spacing
    
    # PART 1: THE PARTIES
    pdf.section_title("PART 1 - THE PARTIES")
    
    # Agent A Section (simplified)
    agent_a_data = {
        "Establishment": data['agent_a_establishment'],
        "Address": data['agent_a_address'],
        "Contact": f"{data['agent_a_phone']} | {data['agent_a_email']}",
        "License": data['agent_a_license'],
        "Agent": data['agent_a_name'],
        "BRN": data['agent_a_brn'],
        "Mobile": data['agent_a_mobile']
    }
    pdf.bordered_section("A) THE AGENT (LANDLORD'S AGENT)", agent_a_data)
    
    # Agent B Section (simplified)
    agent_b_data = {
        "Establishment": data['agent_b_establishment'],
        "Address": data['agent_b_address'],
        "Contact": f"{data['agent_b_phone']} | {data['agent_b_email']}",
        "License": data['agent_b_license'],
        "Agent": data['agent_b_name'],
        "BRN": data['agent_b_brn'],
        "Mobile": data['agent_b_mobile']
    }
    pdf.bordered_section("B) THE AGENT (TENANT'S AGENT)", agent_b_data)
    pdf.ln(8)  # Reduced spacing
    
    # PART 2: THE PROPERTY
    pdf.section_title("PART 2 - THE PROPERTY")
    
    property_data = {
        "Address": data['property_address'],
        "Building": data['building_name'],
        "Price": data['listed_price'],
        "Description": data['property_description']
    }
    pdf.bordered_section("PROPERTY DETAILS", property_data)
    pdf.ln(8)  # Reduced spacing
    
    # PART 3: THE COMMISSION
    pdf.section_title("PART 3 - THE COMMISSION")
    
    commission_data = {
        "Landlord %": data['landlord_agent_percent'],
        "Tenant %": f"{data['tenant_agent_percent']} %",
        "Tenant": data['tenant_name'],
        "Passport": data['tenant_passport'],
        "Budget": data['tenant_budget'],
        "Contacted Agent": "Yes" if data['tenant_contacted_agent'] else "No"
    }
    pdf.bordered_section("COMMISSION DETAILS", commission_data)
    pdf.ln(8)  # Reduced spacing
    
    # PART 4: SIGNATURES
    pdf.section_title("PART 4 - SIGNATURES")
    
    # Notice text with better formatting
    pdf.set_font("Arial", "", 9)
    notice_text = [
        "Both Agents are required to co-operate fully, complete this FORM & BOTH retain",
        "a fully signed & stamped copy on file. RERA DRS is available to both parties.",
        "(Office Stamps 'X' above).",
        "",
        "IN THE EVENT AGENT A DOES NOT RESPOND WITHIN 24 HOURS,",
        "AGENT B MUST CONTACT RERA"
    ]
    
    for line in notice_text:
        if line:  # Skip empty lines (spacing)
            pdf.cell(0, 5, line, ln=1)
        else:
            pdf.ln(3)  # Small space for empty lines
    
    pdf.ln(10)
    
    # Signature lines with actual signatures
    pdf.set_font("Arial", "", 10)
    pdf.cell(90, 20, f"Agent A: {data['agent_a_signature']}", 0, 0, "C")
    pdf.cell(90, 20, f"Agent B: {data['agent_b_signature']}", 0, 1, "C")
    
    # Save PDF
    os.makedirs("pdf_output", exist_ok=True)
    filename = f"pdf_output/agreement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    
    return filename

@router.post("/v1/submit-agreement")
async def create_agreement(
    request: Request,
    dated: str = Form(...),
    agent_a_establishment: str = Form(...),
    agent_a_address: str = Form(...),
    agent_a_phone: str = Form(...),
    agent_a_fax: str = Form(...),
    agent_a_email: str = Form(...),
    agent_a_orn: str = Form(...),
    agent_a_license: str = Form(...),
    agent_a_po_box: str = Form(...),
    agent_a_emirates: str = Form(...),
    agent_a_name: str = Form(None),
    agent_a_brn: str = Form(...),
    agent_a_date_issued: str = Form(...),
    agent_a_mobile: str = Form(...),
    agent_a_email_personal: str = Form(...),
    agent_b_establishment: str = Form(...),
    agent_b_address: str = Form(...),
    agent_b_phone: str = Form(...),
    agent_b_fax: str = Form(...),
    agent_b_email: str = Form(...),
    agent_b_orn: str = Form(...),
    agent_b_license: str = Form(...),
    agent_b_po_box: str = Form(...),
    agent_b_emirates: str = Form(...),
    agent_b_name: str = Form(...),
    agent_b_brn: str = Form(...),
    agent_b_date_issued: str = Form(...),
    agent_b_mobile: str = Form(...),
    agent_b_email_personal: str = Form(...),
    property_address: str = Form(...),
    master_developer: str = Form(...),
    master_project: str = Form(...),
    building_name: str = Form(...),
    listed_price: str = Form(...),
    property_description: str = Form(...),
    landlord_agent_percent: str = Form(...),
    tenant_agent_percent: str = Form(...),
    tenant_name: str = Form(...),
    tenant_passport: str = Form(...),
    tenant_budget: str = Form(...),
    tenant_contacted_agent: str = Form(...),
    agent_a_signature: str = Form(...),
    agent_b_signature: str = Form(...),
    db: Session = Depends(get_db)
):
    # Convert form data to dict
    agreement_data = {
        "dated": dated,
        "agent_a_establishment": agent_a_establishment,
        "agent_a_address": agent_a_address,
        "agent_a_phone":agent_a_phone,
        "agent_a_fax":agent_a_fax,
        "agent_a_email":agent_a_email,
        "agent_a_orn":agent_a_orn,
        "agent_a_license":agent_a_license,
        "agent_a_po_box":agent_a_po_box,
        "agent_a_emirates":agent_a_emirates,
        "agent_a_name":agent_a_name,
        "agent_a_brn":agent_a_brn,
        "agent_a_date_issued":agent_a_date_issued,
        "agent_a_mobile":agent_a_mobile,
        "agent_a_email_personal":agent_a_email_personal,
        "agent_b_establishment":agent_b_establishment,
        "agent_b_address":agent_b_address,
        "agent_b_phone":agent_b_phone,
        "agent_b_fax":agent_b_fax,
        "agent_b_email":agent_b_email,
        "agent_b_orn":agent_b_orn,
        "agent_b_license":agent_b_license,
        "agent_b_license":agent_b_license,
        "agent_b_po_box":agent_b_po_box,
        "agent_b_emirates":agent_b_emirates,
        "agent_b_name":agent_b_name,
        "agent_b_brn":agent_b_brn,
        "agent_b_date_issued":agent_b_date_issued,
        "agent_b_mobile":agent_b_mobile,
        "agent_b_email_personal":agent_b_email_personal,
        "property_address":property_address,
        "master_developer":master_developer,
        "master_project":master_project,
        "building_name":building_name,
        "listed_price":listed_price,
        "property_description":property_description,
        "landlord_agent_percent":landlord_agent_percent,
        "tenant_agent_percent":tenant_agent_percent,
        "tenant_name":tenant_name,
        "tenant_passport":tenant_passport,
        "tenant_budget": tenant_budget,
        "tenant_contacted_agent": tenant_contacted_agent.lower() == "yes",
        "agent_a_signature": agent_a_signature,
        "agent_b_signature": agent_b_signature
    }

    # Create database record
    db_agreement = AgentAgreement(**agreement_data)
    db.add(db_agreement)
    db.commit()
    db.refresh(db_agreement)

    # Generate PDF
    pdf_path = generate_agreement(agreement_data)

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename="agent_agreement.pdf"
    )