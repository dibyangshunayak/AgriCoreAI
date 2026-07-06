import sys
from pathlib import Path

file_path = Path(r"c:\Users\dibya\OneDrive\Desktop\New project\backend\app\agents\coordinator_agent.py")

if not file_path.exists():
    print(f"File not found: {file_path}")
    sys.exit(1)

content = file_path.read_text(encoding="utf-8")

start_marker = """    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.location_mcp"],
        env=env
    )"""

end_marker = "def resolve_target_language(detected_language: str, preferred_language: str) -> str:"

if start_marker not in content:
    print("Start marker not found!")
    sys.exit(1)

if end_marker not in content:
    print("End marker not found!")
    sys.exit(1)

start_idx = content.find(start_marker) + len(start_marker)
end_idx = content.find(end_marker)

replacement = """

    logger.info("Connecting to Location MCP server via stdio transport...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            logger.info("Location MCP session initialized. Invoking reverse_geocode tool...")
            
            result = await session.call_tool(
                "reverse_geocode",
                {"latitude": latitude, "longitude": longitude}
            )
            
            if not result or not result.content:
                raise ValueError("Location MCP server tool returned an empty response.")
            
            raw_text = result.content[0].text
            logger.info(f"Location MCP raw tool response: {raw_text}")
            return json.loads(raw_text)

def parse_disease_report(report_text: str) -> Dict[str, Any]:
    \"\"\"Parses the Disease Agent's report to extract specific fields.\"\"\"
    import re
    name_match = re.search(r"🌿\\s*Disease\\s*:\\s*\\n?\\s*(.*)", report_text, re.IGNORECASE)
    symptoms_match = re.search(r"🔍\\s*Symptoms\\s*:\\s*\\n?\\s*(.*)", report_text, re.IGNORECASE)
    treatment_match = re.search(r"💊\\s*Treatment\\s*:\\s*\\n?\\s*(.*)", report_text, re.IGNORECASE)
    prevention_match = re.search(r"🛡\\s*Prevention\\s*:\\s*\\n?\\s*(.*)", report_text, re.IGNORECASE)
    confidence_match = re.search(r"📊\\s*Confidence\\s*:\\s*\\n?\\s*(.*)", report_text, re.IGNORECASE)
    
    name = name_match.group(1).strip() if name_match else "Unknown"
    confidence = confidence_match.group(1).strip() if confidence_match else "High"
    
    return {
        "name": name,
        "symptoms": symptoms_match.group(1).strip() if symptoms_match else "",
        "treatment": treatment_match.group(1).strip() if treatment_match else "",
        "prevention": prevention_match.group(1).strip() if prevention_match else "",
        "confidence": confidence,
        "raw_report": report_text
    }

def is_general_query(query: str) -> bool:
    clean = query.strip().lower().rstrip(".?!,")
    general_queries = {
        "hi", "hello", "hellow", "hey", "hola", "greetings", "good morning", "good evening",
        "who are you", "what can you do", "thanks", "thank you", "bye"
    }
    return clean in general_queries

def get_predefined_response(query: str) -> str:
    clean = query.strip().lower().rstrip(".?!,")
    if clean in ["hi", "hello", "hellow", "hey", "hola", "greetings", "good morning", "good evening"]:
        return (
            "👋 Welcome to AgriCore AI.\\n\\n"
            "I am ready to help you with expert agricultural guidance. I can assist you with:\\n"
            "- 🌿 Crop Disease Diagnostics (please upload a crop leaf image)\\n"
            "- 🌦 Localized Weather Advisories & irrigation advice\\n"
            "- 📍 Soil Suitability & crop selection recommendations\\n\\n"
            "What agricultural topic would you like to discuss today?"
        )
    elif clean in ["who are you", "what can you do"]:
        return (
            "I am 🌾 **AgriCore AI**, your expert agricultural assistant.\\n\\n"
            "You can ask me about crop cultivation, soil health, fertilizer ratios, weather advisories, "
            "irrigation requirements, and plant disease diagnostics. How can I help you today?"
        )
    elif clean in ["thanks", "thank you"]:
        return "You are very welcome! Happy to assist you. Let me know if you need any other agricultural advice."
    elif clean in ["bye", "goodbye"]:
        return "Goodbye! Have a great day and happy farming!"
    return "How can I help you today?"

# Localized status strings for translation lookup to avoid external translation API calls in tests
LOCALIZED_STATUS = {
    "or": {
        "Thinking...": "ଚିନ୍ତା କରୁଛି...",
        "Checking weather...": "ପାଣିପାଗ ଯାଞ୍ଚ କରୁଛି...",
        "Analyzing image...": "ଫଟୋ ବିଶ୍ଳେଷଣ କରୁଛି...",
        "Consulting disease expert...": "ରୋଗ ବିଶେଷଜ୍ଞଙ୍କ ସହ ପରାମର୍ଶ କରୁଛି...",
        "Consulting crop expert...": "ଫସଲ ବିଶେଷଜ୍ଞଙ୍କ ସହ ପରାମର୍ଶ କରୁଛି...",
        "Resolving location...": "ସ୍ଥାନ ନିର୍ଣ୍ଣୟ କରୁଛି...",
        "Generating recommendation...": "ପରାମର୍ଶ ପ୍ରସ୍ତୁତ କରୁଛି..."
    },
    "hi": {
        "Thinking...": "सोच रहा हूँ...",
        "Checking weather...": "मौसम की जाँच की जा रही है...",
        "Analyzing image...": "छवि का विश्लेषण किया जा रहा है...",
        "Consulting disease expert...": "रोग विशेषज्ञ से परामर्श किया जा रहा है...",
        "Consulting crop expert...": "फसल विशेषज्ञ से परामर्श किया जा रहा है...",
        "Resolving location...": "स्थान का निर्धारण किया जा रहा है...",
        "Generating recommendation...": "सिफारिश तैयार की जा रही है..."
    }
}

"""

new_content = content[:start_idx] + replacement + content[end_idx:]
file_path.write_text(new_content, encoding="utf-8")
print("Repair completed successfully!")
