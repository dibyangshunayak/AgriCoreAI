from app.tools.registry import registry
from app.tools.implementations import (
    WeatherApiTool,
    ReverseGeocodeTool,
    McpTool,
    OcrTool,
    VisionTool,
    SearchTool,
    CalculatorTool,
    TranslationTool,
    GovSchemesTool,
    CropDatabaseTool,
    LatLonSchema,
    CropDatabaseSchema,
    GovSchemesSchema,
    SearchSchema
)

# Instantiate and register tools
registry.register(WeatherApiTool())
registry.register(ReverseGeocodeTool())
registry.register(OcrTool())
registry.register(VisionTool())
registry.register(SearchTool())
registry.register(CalculatorTool())
registry.register(TranslationTool())
registry.register(GovSchemesTool())
registry.register(CropDatabaseTool())

# Dynamic MCP Tool registrations
registry.register(McpTool(
    name="weather_mcp",
    description="Invoke the Weather MCP Server get_weather tool over stdio protocol.",
    module_name="weather_mcp",
    tool_name="get_weather",
    args_schema=LatLonSchema
))
registry.register(McpTool(
    name="location_mcp",
    description="Invoke the Location MCP Server reverse_geocode tool over stdio protocol.",
    module_name="location_mcp",
    tool_name="reverse_geocode",
    args_schema=LatLonSchema
))
registry.register(McpTool(
    name="crop_db_mcp",
    description="Invoke Crop Database MCP server over stdio protocol to query crop guidelines.",
    module_name="crop_db_mcp",
    tool_name="query_crop",
    args_schema=CropDatabaseSchema
))
registry.register(McpTool(
    name="gov_scheme_mcp",
    description="Invoke Government Scheme MCP server over stdio protocol to query subsidies.",
    module_name="gov_scheme_mcp",
    tool_name="query_schemes",
    args_schema=GovSchemesSchema
))
registry.register(McpTool(
    name="search_mcp",
    description="Invoke Search MCP server over stdio protocol to perform agricultural web search.",
    module_name="search_mcp",
    tool_name="search_web",
    args_schema=SearchSchema
))


