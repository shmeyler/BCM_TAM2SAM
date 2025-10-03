"""
PDF Generator for BCM Market Intelligence Reports
Matches the web-based report design with proper formatting and text wrapping
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io


def create_market_report_pdf(market_map, market_input):
    """Create a professional PDF report matching the web design"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Define custom styles matching web design
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=6,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=10,
        alignment=TA_LEFT,
        leading=14,
        fontName='Helvetica'
    )
    
    small_text_style = ParagraphStyle(
        'SmallText',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=6,
        leading=12,
        fontName='Helvetica'
    )
    
    # === COVER PAGE ===
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>BCM</b>", title_style))
    story.append(Paragraph("Market Intelligence Report", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Product Title
    story.append(Paragraph(f"<b>{market_input['product_name']}</b>", 
                          ParagraphStyle('ProductTitle', parent=title_style, fontSize=24)))
    story.append(Paragraph(f"{market_input['geography']} • {market_input['industry']}", subtitle_style))
    
    # Key Metrics - Similar to web cards
    story.append(Spacer(1, 0.4*inch))
    metrics_data = [
        [
            Paragraph('<b>Total Market Size</b><br/><font size="18" color="#FF6B35">${:.1f}B</font>'.format(
                market_map['total_market_size']/1000000000), body_style),
            Paragraph('<b>Annual Growth Rate</b><br/><font size="18" color="#10B981">{:.1f}%</font>'.format(
                market_map['market_growth_rate']*100), body_style),
            Paragraph('<b>Confidence Level</b><br/><font size="14" color="#1E40AF">{}</font>'.format(
                market_map.get('confidence_level', 'medium').upper()), body_style)
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    metrics_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(metrics_table)
    
    # Page Break
    story.append(PageBreak())
    
    # === EXECUTIVE SUMMARY ===
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph("Strategic Overview and Key Insights", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Executive Summary Cards - 3 columns like web
    summary_cards = []
    
    # Card 1: Market Opportunity
    card1_content = f'''
    <b>Market Opportunity</b><br/>
    <br/>
    <font size="9">Total Market Size: <b>${market_map['total_market_size']/1000000000:.1f}B</b></font><br/>
    <font size="9">Growth Rate: <b>{market_map['market_growth_rate']*100:.1f}% CAGR</b></font><br/>
    <font size="9">Serviceable Market: <b>${market_map['total_market_size']*0.3/1000000000:.1f}B</b></font><br/>
    <font size="9">Target Revenue: <b>${market_map['total_market_size']*0.03/1000000000:.2f}B</b></font>
    '''
    
    # Card 2: Competitive Dynamics
    competitors_text = '<b>Competitive Dynamics</b><br/><br/>'
    for comp in market_map.get('competitors', [])[:4]:
        share = f"{comp.get('market_share', 0)*100:.0f}%" if comp.get('market_share') else 'N/A'
        competitors_text += f'<font size="9">{comp["name"]}: {share}</font><br/>'
    competitors_text += f'<br/><font size="8">{len(market_map.get("competitors", []))} key players identified</font>'
    
    # Card 3: Key Drivers
    drivers_text = '<b>Key Drivers & Trends</b><br/><br/>'
    for driver in market_map.get('key_drivers', [])[:4]:
        drivers_text += f'<font size="9">• {driver[:60]}</font><br/>'
    
    cards_data = [[
        Paragraph(card1_content, body_style),
        Paragraph(competitors_text, body_style),
        Paragraph(drivers_text, body_style)
    ]]
    
    cards_table = Table(cards_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    cards_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#FEF3C7')),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#D1FAE5')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(cards_table)
    
    # Detailed Executive Summary Text
    story.append(Spacer(1, 0.3*inch))
    exec_summary = market_map.get('executive_summary', 'Executive summary not available')
    if exec_summary and exec_summary != 'Executive summary not available':
        story.append(Paragraph("<b>Detailed Analysis:</b>", subheading_style))
        for para in exec_summary.split('\n\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
    
    # Page Break
    story.append(PageBreak())
    
    # === MARKET SEGMENTATION ===
    story.append(Paragraph("Market Segmentation Analysis", heading_style))
    story.append(Paragraph("Comprehensive breakdown across multiple dimensions", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Helper function to create segmentation section matching web design
    def create_segmentation_section(title, segments, color, icon, subtitle):
        elements = []
        
        # Section header with icon and subtitle (like web)
        header_content = f'''
        <para alignment="center">
        <font size="24">{icon}</font><br/>
        <font size="14"><b>{title}</b></font><br/>
        <font size="9" color="#6B7280">{subtitle}</font>
        </para>
        '''
        elements.append(Paragraph(header_content, body_style))
        elements.append(Spacer(1, 0.15*inch))
        
        if not segments:
            elements.append(Paragraph("<i>No segmentation data available</i>", small_text_style))
            return elements
        
        for seg in segments[:3]:
            # Get key players
            key_players = seg.get("key_players", [])
            players_text = ""
            if key_players:
                players_text = f'<br/><font size="8" color="#6B7280"><b>Key Players:</b> {", ".join(key_players[:3])}</font>'
            
            # Create detailed segment card matching web layout
            seg_content = f'''
            <font size="10"><b>{seg["name"]}</b></font><br/>
            <font size="9" color="#6B7280">{seg["description"]}</font><br/>
            <font size="9"><b>Market Size:</b> <font color="{color}">${seg["size_estimate"]/1000000:.0f}M</font> | <b>Growth:</b> <font color="#10B981">{seg["growth_rate"]*100:.1f}%</font></font>
            {players_text}
            '''
            
            seg_data = [[Paragraph(seg_content, body_style)]]
            
            seg_table = Table(seg_data, colWidths=[6.5*inch])
            seg_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor(color)),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(seg_table)
            elements.append(Spacer(1, 0.12*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    # Geographic Segmentation
    for element in create_segmentation_section(
        "Geographic Segmentation",
        market_map.get('segmentation_by_geographics', []),
        '#3B82F6',
        '🌍',
        'Country, City, Density, Language, Climate, Area, Population'
    ):
        story.append(element)
    
    # Demographic Segmentation
    for element in create_segmentation_section(
        "Demographic Segmentation",
        market_map.get('segmentation_by_demographics', []),
        '#F97316',
        '👥',
        'Age, Gender, Income, Education, Social Status, Family, Life Stage, Occupation'
    ):
        story.append(element)
    
    # Page Break
    story.append(PageBreak())
    
    # Psychographic Segmentation
    for element in create_segmentation_section(
        "Psychographic Segmentation",
        market_map.get('segmentation_by_psychographics', []),
        '#EAB308',
        '🧠',
        'Lifestyle, AIO (Activity/Interest/Opinion), Concerns, Personality, Values, Attitudes'
    ):
        story.append(element)
    
    # Behavioral Segmentation
    for element in create_segmentation_section(
        "Behavioral Segmentation",
        market_map.get('segmentation_by_behavioral', []),
        '#8B5CF6',
        '🛒',
        'Behavior, Benefits, Perks, User Status, Usage Rate, Loyalty, Buyer Stage'
    ):
        story.append(element)
    
    # === COMPETITIVE ANALYSIS ===
    story.append(Paragraph("Competitive Analysis", heading_style))
    story.append(Paragraph("Key competitors and market positioning", subtitle_style))
    story.append(Spacer(1, 0.15*inch))
    
    for comp in market_map.get('competitors', [])[:5]:
        # Competitor card
        comp_header = [[
            Paragraph(f'<b>{comp["name"]}</b>', body_style),
            Paragraph(f'<b>Market Share: {comp.get("market_share", 0)*100:.1f}%</b>', body_style) if comp.get('market_share') else Paragraph('Market Share: N/A', body_style)
        ]]
        
        comp_table = Table(comp_header, colWidths=[4*inch, 2.5*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF7ED')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FF6B35')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(comp_table)
        
        # Strengths and Weaknesses
        strengths_text = '<b>Strengths:</b> ' + ', '.join(comp.get('strengths', [])[:3])
        weaknesses_text = '<b>Weaknesses:</b> ' + ', '.join(comp.get('weaknesses', [])[:3])
        
        story.append(Paragraph(strengths_text, small_text_style))
        story.append(Paragraph(weaknesses_text, small_text_style))
        story.append(Spacer(1, 0.15*inch))
    
    # === STRATEGIC RECOMMENDATIONS ===
    story.append(PageBreak())
    story.append(Paragraph("Strategic Recommendations", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    for i, rec in enumerate(market_map.get('strategic_recommendations', [])[:5], 1):
        story.append(Paragraph(f'<b>{i}.</b> {rec}', body_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Opportunities & Threats
    story.append(Paragraph("Market Opportunities", subheading_style))
    for opp in market_map.get('opportunities', [])[:4]:
        story.append(Paragraph(f'• {opp}', body_style))
    
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Market Threats", subheading_style))
    for threat in market_map.get('threats', [])[:4]:
        story.append(Paragraph(f'• {threat}', body_style))
    
    # Data Sources Section with Hyperlinks
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Data Sources & References", subheading_style))
    
    data_sources = market_map.get('data_sources', [])
    if data_sources:
        for i, source in enumerate(data_sources[:6], 1):
            if isinstance(source, dict) and 'url' in source:
                # Clickable link
                source_text = f'<font size="9">[{i}] <link href="{source["url"]}" color="blue">{source.get("name", source["url"])}</link></font>'
            elif isinstance(source, str):
                # Plain text, try to make it clickable if it looks like a known source
                source_name = source
                source_url = None
                
                # Map common sources to URLs
                source_mapping = {
                    "Gartner Market Research": "https://www.gartner.com/en/research",
                    "McKinsey Industry Reports": "https://www.mckinsey.com/industries",
                    "IBISWorld Market Analysis": "https://www.ibisworld.com",
                    "Forrester Research": "https://www.forrester.com/research",
                    "PwC Industry Insights": "https://www.pwc.com/us/en/industries.html",
                    "Statista": "https://www.statista.com",
                    "CB Insights": "https://www.cbinsights.com",
                    "Crunchbase": "https://www.crunchbase.com"
                }
                
                for key, url in source_mapping.items():
                    if key.lower() in source_name.lower():
                        source_url = url
                        break
                
                if source_url:
                    source_text = f'<font size="9">[{i}] <link href="{source_url}" color="blue">{source_name}</link></font>'
                else:
                    source_text = f'<font size="9">[{i}] {source_name}</font>'
            else:
                source_text = f'<font size="9">[{i}] {str(source)}</font>'
            
            story.append(Paragraph(source_text, small_text_style))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_text = f'<i>Report generated by BCM Market Intelligence Platform • Powered by Kimi K2 • {str(market_map["timestamp"])[:10]}</i>'
    story.append(Paragraph(footer_text, 
                          ParagraphStyle('Footer', parent=small_text_style, 
                                       textColor=colors.HexColor('#9CA3AF'), 
                                       alignment=TA_CENTER,
                                       fontSize=8)))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()