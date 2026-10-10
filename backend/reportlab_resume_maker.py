from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line

def generate_resume_pdf(resume_data, filename="resume.pdf"):

    doc = SimpleDocTemplate(
        filename,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    
    # Modify the default Normal style in-place
    styles["Normal"].fontSize = 8.5
    styles["Normal"].leading = 10.5
    styles["Normal"].spaceAfter = 1

    name_style = ParagraphStyle(
        "Name",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F2D59"), # Dark Blue/Navy
        fontName="Helvetica-Bold",
        alignment=1, # Center
        spaceAfter=2
    )

    target_role_style = ParagraphStyle(
        "TargetRole",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#333333"),
        fontName="Helvetica-Bold",
        alignment=1, # Center
        spaceAfter=4
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#0F2D59"), # Dark Blue/Navy
        spaceBefore=8,
        spaceAfter=2
    )

    content = []

    # ==========================
    # Header
    # ==========================

    content.append(
        Paragraph(
            resume_data.get("name", "Ankit Gupta"),
            name_style
        )
    )

    target_role = resume_data.get("target_role", "")
    if target_role:
        content.append(
            Paragraph(
                target_role,
                target_role_style
            )
        )

    # Contact Details
    contact_parts = []
    if resume_data.get("phone"):
        contact_parts.append(resume_data.get("phone"))
    if resume_data.get("location"):
        contact_parts.append(resume_data.get("location"))
    if resume_data.get("email"):
        contact_parts.append(f'<a href="mailto:{resume_data.get("email")}" color="blue">{resume_data.get("email")}</a>')
    if resume_data.get("linkedin"):
        contact_parts.append(f'<a href="{resume_data.get("linkedin")}" color="blue">LinkedIn</a>')
    if resume_data.get("github"):
        contact_parts.append(f'<a href="{resume_data.get("github")}" color="blue">GitHub</a>')

    contact_text = " • ".join(contact_parts)
    
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        alignment=1, # Center
        fontSize=8.5,
        leading=10.5,
        spaceAfter=6
    )

    content.append(
        Paragraph(contact_text, contact_style)
    )

    # Helper function to draw a section header and a horizontal line
    def add_section_header(title_text):
        content.append(Spacer(1, 4))
        content.append(
            Paragraph(
                f"<b>{title_text}</b>",
                heading_style
            )
        )
        # 612 pt page width - 50 pt margins = 562 pt printable width
        d = Drawing(562, 3)
        d.add(Line(0, 1, 562, 1, strokeColor=colors.HexColor("#666666"), strokeWidth=0.5))
        content.append(d)
        content.append(Spacer(1, 4))

    # ==========================
    # Professional Summary
    # ==========================

    summary = resume_data.get("professional_summary", "")
    if summary:
        add_section_header("SUMMARY")
        if isinstance(summary, list):
            for point in summary:
                content.append(
                    Paragraph(
                        f"• {point}",
                        styles["Normal"]
                    )
                )
        else:
            if "\n" in summary or summary.strip().startswith("•") or summary.strip().startswith("-"):
                lines = [line.strip().lstrip("•-").strip() for line in summary.split("\n") if line.strip()]
                for line in lines:
                    content.append(
                        Paragraph(
                            f"• {line}",
                            styles["Normal"]
                        )
                    )
            else:
                content.append(
                    Paragraph(
                        summary,
                        styles["Normal"]
                    )
                )

    # ==========================
    # Education
    # ==========================

    education = resume_data.get("education", [])
    if education:
        add_section_header("EDUCATION")
        for edu in education:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            duration = edu.get("duration", "")
            cgpa = edu.get("cgpa", "")

            # Left: Degree, Right: Duration
            left_p = Paragraph(f"<b>{degree}</b>", styles["Normal"])
            right_p = Paragraph(duration, ParagraphStyle("RightAlignEdu", parent=styles["Normal"], alignment=2))

            tbl = Table([[left_p, right_p]], colWidths=[420, 142], hAlign='LEFT')
            tbl.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            content.append(tbl)

            # Left: Institution, Right: CGPA
            if institution or cgpa:
                bottom_left = institution
                bottom_right = f"CGPA: {cgpa}" if cgpa else ""
                bl_p = Paragraph(bottom_left, styles["Normal"])
                br_p = Paragraph(bottom_right, ParagraphStyle("RightAlignEduCGPA", parent=styles["Normal"], alignment=2))
                tbl_inst = Table([[bl_p, br_p]], colWidths=[420, 142], hAlign='LEFT')
                tbl_inst.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                ]))
                content.append(tbl_inst)
            content.append(Spacer(1, 4))

    # ==========================
    # Technical Skills
    # ==========================

    skills_data = resume_data.get("technical_skills", {})
    if skills_data:
        add_section_header("TECHNICAL SKILLS")
        for category_name, skills in skills_data.items():
            if skills:
                content.append(
                    Paragraph(
                        f"<b>{category_name}:</b> {', '.join(skills)}",
                        styles["Normal"]
                    )
                )

    # ==========================
    # Professional Experience
    # ==========================

    experience = resume_data.get("professional_experience", [])
    if experience:
        add_section_header("PROFESSIONAL EXPERIENCE")
        for job in experience:
            company = job.get("company", "")
            location = job.get("location", "")
            title = job.get("job_title", "")
            duration = job.get("duration", "")

            # Left: COMPANY, Location | TITLE
            left_text = f"<b>{company.upper()}</b>"
            if location:
                left_text += f", {location}"
            if title:
                left_text += f" | <b>{title.upper()}</b>"

            left_p = Paragraph(left_text, styles["Normal"])
            right_p = Paragraph(duration, ParagraphStyle("RightAlignEx", parent=styles["Normal"], alignment=2))

            tbl = Table([[left_p, right_p]], colWidths=[420, 142], hAlign='LEFT')
            tbl.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            content.append(tbl)
            content.append(Spacer(1, 2))

            for point in job.get("description", []):
                content.append(
                    Paragraph(
                        f"• {point}",
                        styles["Normal"]
                    )
                )
            content.append(Spacer(1, 4))

    # ==========================
    # Projects
    # ==========================

    projects = resume_data.get("projects", [])
    if projects:
        add_section_header("PROJECTS")
        for proj in projects:
            title = proj.get("title", "")
            techs = proj.get("technologies", [])
            
            # Header format: TITLE | Technologies
            header_text = f"<b>{title.upper()}</b>"
            if techs:
                header_text += f" | <i>{', '.join(techs)}</i>"
                
            content.append(
                Paragraph(
                    header_text,
                    styles["Normal"]
                )
            )
            content.append(Spacer(1, 2))
            
            for point in proj.get("description", []):
                content.append(
                    Paragraph(
                        f"• {point}",
                        styles["Normal"]
                    )
                )
            content.append(Spacer(1, 4))


    # ==========================
    # Certifications
    # ==========================

    raw_certs = resume_data.get("certifications", [])
    if isinstance(raw_certs, str):
        raw_certs = [raw_certs]
    certifications = []
    for c in raw_certs:
        if isinstance(c, dict):
            name = c.get("name", "")
            status = c.get("status", "")
            if status:
                certifications.append(f"{name} ({status})")
            else:
                certifications.append(name)
        elif isinstance(c, str):
            certifications.append(c)
            
    certifications = [
        c.strip() for c in certifications
        if c and c.strip() and c.strip().lower() not in ("n/a", "none", "null")
    ]

    if certifications:
        add_section_header("CERTIFICATIONS")
        for cert in certifications:
            content.append(
                Paragraph(
                    f"• {cert}",
                    styles["Normal"]
                )
            )

    # ==========================
    # Achievements
    # ==========================

    raw_achievements = resume_data.get("achievements", [])
    if isinstance(raw_achievements, str):
        raw_achievements = [raw_achievements]
    achievements = [
        a.strip() for a in raw_achievements
        if a and a.strip() and a.strip().lower() not in ("n/a", "none", "null")
    ]

    if achievements:
        add_section_header("ACHIEVEMENTS")
        for achievement in achievements:
            content.append(
                Paragraph(
                    f"• {achievement}",
                    styles["Normal"]
                )
            )



    # Append invisible job description for ATS matching (6pt white font on the last page)
    import os
    import html
    jd_path = "job_description.txt"
    if os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read().strip()
        if jd_text:
            content.append(PageBreak())
            jd_style = ParagraphStyle(
                "JDStyle",
                parent=styles["Normal"],
                fontSize=6,
                leading=7,
                textColor=colors.HexColor("#FFFFFF"), # White
                spaceBefore=0,
                spaceAfter=0
            )
            # Replace newlines with <br/> to preserve structure in ReportLab Paragraph
            # Escaping the XML special characters first to avoid ReportLab parsing crashes
            jd_html = html.escape(jd_text).replace("\n", "<br/>")
            content.append(Paragraph(jd_html, jd_style))

    doc.build(content)
    print(f"Resume PDF generated successfully: {filename}")