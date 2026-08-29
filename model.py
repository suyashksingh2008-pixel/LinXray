from pydantic import BaseModel, Field
class Finding(BaseModel):   
    name: str    
    description: str    
    severity: str    
    points: int 
class ActionRecord(BaseModel):    
    sequence_number: int    
    action_type: str    
    element_text: str    
    status: str    
    url_before: str | None = None    
    url_after: str | None = None    
    before_screenshot: str | None = None    
    after_screenshot: str | None = None 
class ScanReport(BaseModel):    
    scan_id: str    
    submitted_url: str    
    final_url: str | None = None    
    title: str | None = None    
    status_code: int | None = None    
    status: str = "queued"    
    redirects: list[str] = Field(default_factory=list)    
    contacted_domains: list[str] = Field(default_factory=list)    
    failed_requests: list[str] = Field(default_factory=list)    
    forms: int = 0    
    password_fields: int = 0   
    iframes: int = 0    
    scripts: int = 0    
    security_headers: dict = Field(default_factory=dict)    
    actions: list[ActionRecord] = Field(default_factory=list)    
    findings: list[Finding] = Field(default_factory=list)    
    screenshots: list[str] = Field(default_factory=list)    
    risk_index: int = 0    
    risk_level: str = "Unknown"    
    error: str | None = None