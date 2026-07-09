# =====================================================================
# FILE: generate_architecture.py
# DESCRIPTION: Generates a premium PDF document of the AgriCore AI
#              system architecture using ReportLab.
# =====================================================================

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render the total page count
    along with running headers, footers, and a corporate accent border.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # --- Page 1: Cover Page Layout ---
        if self._pageNumber == 1:
            # Decorative Top Bar
            self.setFillColor(colors.HexColor("#064e3b")) # Deep Emerald
            self.rect(0, 770, 612, 22, fill=True, stroke=False)
            
            # Bottom Bar
            self.setFillColor(colors.HexColor("#047857")) # Medium Emerald
            self.rect(0, 0, 612, 15, fill=True, stroke=False)
            self.restoreState()
            return

        # --- Pages 2+: Running Header & Footer ---
        # Header text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#065f46")) # Emerald Green
        self.drawString(54, 755, "AGRICORE AI SYSTEM ARCHITECTURE SPECIFICATION")
        
        # Header rule
        self.setStrokeColor(colors.HexColor("#e2e8f0")) # Slate Light
        self.setLineWidth(0.5)
        self.line(54, 747, 558, 747)
        
        # Footer rule
        self.line(54, 60, 558, 60)
        
        # Footer text
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b")) # Slate Gray
        self.drawString(54, 45, "AgriCore AI - Engineering Reference Blueprint")
        self.drawRightString(558, 45, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def create_pdf(filename="AgriCore_Architecture.pdf"):
    # Target page width = 612pt (8.5"), margins = 54pt (0.75") on each side.
    # Printable width = 504pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # --- Custom Colors ---
    PRIMARY_COLOR = colors.HexColor("#064e3b")      # Deep Emerald
    SECONDARY_COLOR = colors.HexColor("#0f766e")    # Teal Accent
    TEXT_COLOR = colors.HexColor("#1e293b")         # Slate Black
    LIGHT_BG = colors.HexColor("#f8fafc")           # Soft Light gray
    BORDER_COLOR = colors.HexColor("#e2e8f0")       # Border gray
    
    # --- Custom Styles ---
    # Base modifications
    styles['Normal'].textColor = TEXT_COLOR
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=PRIMARY_COLOR,
        alignment=0,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#475569"),
        alignment=0,
        spaceAfter=30
    )
    
    metadata_style = ParagraphStyle(
        'CoverMetadata',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#475569")
    )
    
    h1_style = ParagraphStyle(
        'H1_Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceBefore=22,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2_Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocumentBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeBlockText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    flowables = []

    # ==========================================
    # COVER PAGE
    # ==========================================
    flowables.append(Spacer(1, 100))
    flowables.append(Paragraph("AgriCore AI", title_style))
    flowables.append(Paragraph("System Architecture Specification Blueprint", ParagraphStyle(
        'SubtitleBold', parent=title_style, fontSize=20, leading=24, textColor=SECONDARY_COLOR, spaceAfter=20
    )))
    
    # Accent Line
    line_table = Table([[""]], colWidths=[504], rowHeights=[3])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SECONDARY_COLOR),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    flowables.append(line_table)
    flowables.append(Spacer(1, 20))
    
    desc_text = (
        "A detailed blueprint detailing the architectural layers, data flows, geolocation integration, "
        "and Model Context Protocol (MCP) coordination within the AgriCore AI platform. "
        "Built on React, Flask, NVIDIA Nemotron, FastMCP, Open-Meteo, and OpenStreetMap Nominatim APIs."
    )
    flowables.append(Paragraph(desc_text, subtitle_style))
    flowables.append(Spacer(1, 140))
    
    metadata_text = (
        "<b>Document Classification:</b> Confidential - Internal Engineering Reference<br/>"
        "<b>Version:</b> 1.3.0<br/>"
        "<b>Date:</b> June 2026<br/>"
        "<b>Author:</b> Senior Full-Stack Engineer<br/>"
        "<b>System Baseline:</b> React (Vite) + Flask RESTful + NVIDIA Nemotron Planning + Stdio Client Sessions"
    )
    flowables.append(Paragraph(metadata_text, metadata_style))
    flowables.append(PageBreak())

    # ==========================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==========================================
    flowables.append(Paragraph("1. Executive Summary & Overview", h1_style))
    flowables.append(Paragraph(
        "AgriCore AI is an intelligent agricultural assistant designed to provide localized, real-time "
        "weather advisory and crop crop disease diagnosis directly to farmers. The platform operates on a "
        "hybrid AI architecture, combining cloud-based language models (NVIDIA Nemotron 3 Nano) with cloud-based vision systems (Google Gemini).",
        body_style
    ))
    flowables.append(Paragraph(
        "A critical feature of AgriCore AI is its <b>zero-keyword background geolocation orchestration</b>. "
        "Upon application startup, the browser queries the client's geographic coordinates. If GPS permission "
        "is denied, it falls back to an IP Geolocation API. These coordinates are stored globally and sent automatically "
        "in the payload of every message. The backend routes coordinates directly into specialized tool sets powered by the "
        "<b>Model Context Protocol (MCP)</b>, retrieving metrics and geocoded locations seamlessly without requiring the user "
        "to specify their location in the chat.",
        body_style
    ))

    # ==========================================
    # SECTION 2: SYSTEM COMPONENT TOPOLOGY
    # ==========================================
    flowables.append(Paragraph("2. System Component Topology", h1_style))
    flowables.append(Paragraph(
        "The architecture is organized into four distinct runtime layers: the Client Presentation Layer, the API Gateway & "
        "Route Control Layer, the AI Orchestration Layer, and the Model Context Protocol (MCP) Tools Layer.",
        body_style
    ))

    # Architecture Table
    topo_data = [
        [Paragraph("<b>Component Layer</b>", ParagraphStyle('TableHeader', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white)),
         Paragraph("<b>Tech Stack / Files</b>", ParagraphStyle('TableHeader', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white)),
         Paragraph("<b>Architectural Responsibility</b>", ParagraphStyle('TableHeader', parent=body_style, fontName='Helvetica-Bold', textColor=colors.white))],
        
        [Paragraph("<b>Presentation Layer</b>", body_style),
         Paragraph("React 19, Vite, Tailwind v4<br/>• LocationContext.jsx<br/>• useLocation.js<br/>• LocationIndicator.jsx", body_style),
         Paragraph("Handles startup geolocation prompt, fallback IP fetches, coordinates state persistence, and running header dashboard display.", body_style)],
        
        [Paragraph("<b>Gateway & Routes</b>", body_style),
         Paragraph("Flask Web Service<br/>• routes/chat.py<br/>• api/router.py<br/>• main.py", body_style),
         Paragraph("Handles multi-origin CORS, exposes file upload API, routes SSE streaming chat lines, and handles geocoding proxies.", body_style)],
        
        [Paragraph("<b>AI Orchestration</b>", body_style),
         Paragraph("NVIDIA Nemotron, Gemini<br/>• coordinator_agent.py<br/>• services/planner.py<br/>• intent_router.py", body_style),
         Paragraph("Parses query intent via NVIDIA Nemotron Planner, triggers parallel agents (weather, disease, location, general), and aggregates advisory outputs.", body_style)],
        
        [Paragraph("<b>MCP Services</b>", body_style),
         Paragraph("FastMCP Stdio Server<br/>• weather_mcp.py<br/>• location_mcp.py", body_style),
         Paragraph("Exposes Python tools (get_weather, reverse_geocode) and interfaces with Open-Meteo & OpenStreetMap Nominatim APIs.", body_style)]
    ]

    t_topo = Table(topo_data, colWidths=[100, 154, 250])
    t_topo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    flowables.append(t_topo)
    flowables.append(Spacer(1, 15))

    # ==========================================
    # SECTION 3: DATA FLOWS & SEQUENCE
    # ==========================================
    flowables.append(PageBreak())
    flowables.append(Paragraph("3. Detailed Data Flows & Sequences", h1_style))
    
    flowables.append(Paragraph("3.1 Geolocation Capture & Verification Sequence", h2_style))
    flowables.append(Paragraph(
        "On startup, the client application executes a background geolocation capture cascade. "
        "The following diagram represents the decision pipeline:",
        body_style
    ))

    # Flow Diagram Table
    flow_data = [
        [Paragraph("<b>Step</b>", ParagraphStyle('Th', parent=body_style, fontName='Helvetica-Bold')),
         Paragraph("<b>Runtime Operation</b>", ParagraphStyle('Th', parent=body_style, fontName='Helvetica-Bold')),
         Paragraph("<b>Failure Handling & Cache Mitigation</b>", ParagraphStyle('Th', parent=body_style, fontName='Helvetica-Bold'))],
        
        [Paragraph("1", body_style),
         Paragraph("App Mount ➔ Read session storage cache.", body_style),
         Paragraph("If cache exists, immediately load coordinates in UI to prevent layout shift.", body_style)],
        
        [Paragraph("2", body_style),
         Paragraph("Query Browser Geolocation API (enableHighAccuracy=true).", body_style),
         Paragraph("Timeout set to 10s. If timeout triggers or permission is denied, proceed to step 3.", body_style)],
        
        [Paragraph("3", body_style),
         Paragraph("Query fallback IP Geolocation: <code>https://ipapi.co/json/</code>", body_style),
         Paragraph("Fetch network coordinates. If offline/fails, set state to <i>Location access unavailable.</i>", body_style)],
        
        [Paragraph("4", body_style),
         Paragraph("Submit coordinates to backend <code>/api/geocode</code> endpoint.", body_style),
         Paragraph("Invokes Location MCP's Nominatim tool to resolve town/district names. Caches values in LocalStorage & SessionStorage.", body_style)]
    ]
    
    t_flow = Table(flow_data, colWidths=[30, 237, 237])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    flowables.append(t_flow)
    flowables.append(Spacer(1, 10))

    flowables.append(Paragraph("3.2 SSE Weather Advisory Stream Flow", h2_style))
    flowables.append(Paragraph(
        "When the farmer sends a message (e.g. <i>'What is the temperature today?'</i>):",
        body_style
    ))
    
    # List block
    flowables.append(Paragraph(
        "1. <b>Client Injection:</b> The React client reads the active coordinates from `LocationContext` and appends "
        "them as `latitude` and `longitude` fields in the JSON payload sent to `/api/chat`.<br/>"
        "2. <b>Planning & Orchestration:</b> The Flask backend receives the payload and passes the variables to the Coordinator Agent, "
        "which queries the NVIDIA Nemotron planner to construct an execution plan.<br/>"
        "3. <b>MCP Subprocess Invocation:</b> The Coordinator Agent starts stdio client communication with the <b>Weather MCP</b> "
        "subprocess, passing coordinates. The MCP queries the Open-Meteo REST API.<br/>"
        "4. <b>Consolidation & Advisory Generation:</b> Real-time soil moisture and wind speeds are returned. The Coordinator Agent passes "
        "the metrics to the NVIDIA Nemotron LLM to synthesize a natural-language advisory.<br/>"
        "5. <b>Streaming Delivery:</b> Advisory tokens are streamed back via Server-Sent Events (SSE) in real-time, showing coordinates and localized advisories instantly.",
        ParagraphStyle('ListStyle', parent=body_style, leftIndent=15, firstLineIndent=-10)
    ))

    # ==========================================
    # SECTION 4: ERROR ROBUSTNESS
    # ==========================================
    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("4. Robustness & Error Mitigation Controls", h1_style))
    
    flowables.append(Paragraph(
        "The architecture specifies clear safety checks to ensure the application remains stable under "
        "limited client permissions or offline states:",
        body_style
    ))

    robust_data = [
        [Paragraph("<b>Scenario Encountered</b>", ParagraphStyle('Th2', parent=body_style, fontName='Helvetica-Bold')),
         Paragraph("<b>System Resilience Response</b>", ParagraphStyle('Th2', parent=body_style, fontName='Helvetica-Bold'))],
        
        [Paragraph("GPS Denied / Timeout", body_style),
         Paragraph("The system immediately catches the exception and launches the IP Geolocation fallback, updating the connection status indicator to IP Location fallback.", body_style)],
        
        [Paragraph("Full Geolocation Failure (No GPS & IP)", body_style),
         Paragraph("On startup, coordinates remain null. If the user submits a weather or location query, the coordinator agent intercepts the null values and immediately returns the formatted error card: <i>Location access unavailable. Please enable location permission...</i>", body_style)],
        
        [Paragraph("Nominatim API Rate-Limits / Offline", body_style),
         Paragraph("If Nominatim returns a 429/500 code, the Location MCP handles the exception gracefully, returning standard coordinate structures and showing coordinates in place of name formats in the header.", body_style)],
        
        [Paragraph("NVIDIA API Unreachable / Authentication Error", body_style),
         Paragraph("The backend performs request timeout, retry configurations, and key verification prior to dispatching requests. If the API is offline or key validation fails, the system returns a premium fallback card instantly to prevent runtime freezes.", body_style)]
    ]

    t_robust = Table(robust_data, colWidths=[180, 324])
    t_robust.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    flowables.append(t_robust)
    
    # Build Document
    doc.build(flowables, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    create_pdf()
    print("Success: Generated AgriCore_Architecture.pdf")
