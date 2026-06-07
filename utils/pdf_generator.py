
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os

def create_resume_pdf(resume_data, output_path):
    """Creates a professional PDF from resume data"""
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Name
        name = str(resume_data.get('name', 'Candidate Name'))
        story.append(Paragraph(name, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Contact Information
        email = str(resume_data.get('email', 'N/A'))
        phone = str(resume_data.get('phone', 'N/A'))
        contact_info = f"<b>Email:</b> {email} | <b>Phone:</b> {phone}"
        story.append(Paragraph(contact_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if resume_data.get('summary'):
            story.append(Paragraph('Professional Summary', heading_style))
            summary = str(resume_data.get('summary', ''))
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Skills
        if resume_data.get('skills'):
            story.append(Paragraph('Skills', heading_style))
            skills = resume_data['skills']
            skills_text = ', '.join(skills) if isinstance(skills, list) else str(skills)
            story.append(Paragraph(skills_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Experience
        if resume_data.get('experience') or resume_data.get('experience_years'):
            story.append(Paragraph('Experience', heading_style))
            exp_text = str(resume_data.get('experience', f"{resume_data.get('experience_years', 0)}+ years of experience"))
            story.append(Paragraph(exp_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Education
        if resume_data.get('education'):
            story.append(Paragraph('Education', heading_style))
            education = resume_data['education']
            if isinstance(education, dict):
                edu_text = f"{education.get('degree', 'N/A')} - {education.get('university', 'N/A')}"
            else:
                edu_text = str(education)
            story.append(Paragraph(edu_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_path
    except Exception as e:
        raise Exception(f"Failed to create PDF: {str(e)}")

def create_multiple_resume_pdfs(resumes_data, output_dir):
    """Creates multiple PDFs"""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, data in enumerate(resumes_data):
        path = os.path.join(output_dir, f"resume_{i}.pdf")
        create_resume_pdf(data, path)
        paths.append(path)
    return paths

def generate_resume_buffer(resume_data):
    """Generates PDF in memory and returns bytes"""
    buffer = io.BytesIO()
    
    try:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Name
        name = str(resume_data.get('name', 'Candidate Name'))
        story.append(Paragraph(name, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Contact Information
        email = str(resume_data.get('email', 'N/A'))
        phone = str(resume_data.get('phone', 'N/A'))
        contact_info = f"<b>Email:</b> {email} | <b>Phone:</b> {phone}"
        story.append(Paragraph(contact_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if resume_data.get('summary'):
            story.append(Paragraph('Professional Summary', heading_style))
            summary = str(resume_data.get('summary', ''))
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Skills
        if resume_data.get('skills'):
            story.append(Paragraph('Skills', heading_style))
            skills = resume_data['skills']
            skills_text = ', '.join(skills) if isinstance(skills, list) else str(skills)
            story.append(Paragraph(skills_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Experience
        if resume_data.get('experience') or resume_data.get('experience_years'):
            story.append(Paragraph('Experience', heading_style))
            exp_text = str(resume_data.get('experience', f"{resume_data.get('experience_years', 0)}+ years of experience"))
            story.append(Paragraph(exp_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Education
        if resume_data.get('education'):
            story.append(Paragraph('Education', heading_style))
            education = resume_data['education']
            if isinstance(education, dict):
                edu_text = f"{education.get('degree', 'N/A')} - {education.get('university', 'N/A')}"
            else:
                edu_text = str(education)
            story.append(Paragraph(edu_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    except Exception as e:
        buffer.close()
        raise Exception(f"Failed to generate PDF: {str(e)}")
