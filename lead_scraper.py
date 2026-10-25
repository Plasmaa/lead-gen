"""
AI-Powered Lead Scraper using ScrapeGraphAI
Extracts structured company leads, key executives, contact info, emails, and social profiles.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import ScrapeGraphAI
try:
    from scrapegraphai.graphs import SmartScraperGraph
except ImportError:
    print("Error: scrapegraphai is not installed in the current environment.")
    print("Run '.\\.venv\\Scripts\\python.exe -m pip install scrapegraphai' or use the project virtual environment.")
    sys.exit(1)


# ==========================================
# Lead Generation Schemas
# ==========================================

class ContactPerson(BaseModel):
    name: Optional[str] = Field(default=None, description="Full name of founder, executive, or key team member")
    role: Optional[str] = Field(default=None, description="Job title, role, or position (e.g. CEO, CTO, Head of Sales)")
    email: Optional[str] = Field(default=None, description="Personal or work email address of the person")
    phone: Optional[str] = Field(default=None, description="Direct phone or mobile number if listed")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    twitter: Optional[str] = Field(default=None, description="Twitter / X profile URL")


class CompanyLead(BaseModel):
    company_name: Optional[str] = Field(default=None, description="Legal or trade name of the company / business")
    website: Optional[str] = Field(default=None, description="Official website URL")
    industry: Optional[str] = Field(default=None, description="Industry, niche, or business domain")
    tagline_or_summary: Optional[str] = Field(default=None, description="Brief description of what the company does or solves")
    headquarters: Optional[str] = Field(default=None, description="HQ physical address, city, or country")
    general_emails: List[str] = Field(default_factory=list, description="General contact emails (e.g., info@, sales@, contact@, support@)")
    phone_numbers: List[str] = Field(default_factory=list, description="Company phone or support numbers")
    social_links: List[str] = Field(default_factory=list, description="Company social profile links (LinkedIn, Twitter, GitHub, Facebook, etc.)")
    key_contacts: List[ContactPerson] = Field(default_factory=list, description="List of key executives, founders, or team members found")


class ScrapeResult(BaseModel):
    leads: List[CompanyLead] = Field(default_factory=list, description="List of company lead details extracted from the page")


# ==========================================
# LLM Configuration Helpers
# ==========================================

def get_graph_config(provider: str = "auto", model: Optional[str] = None, headless: bool = True):
    """
    Builds the graph configuration dictionary for ScrapeGraphAI based on provider.
    """
    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if provider == "auto":
        if gemini_key:
            provider = "gemini"
        elif openai_key:
            provider = "openai"
        elif groq_key:
            provider = "groq"
        else:
            provider = "ollama"

    if provider == "gemini":
        selected_model = model or "gemini-flash-latest"
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is not set in environment or .env file.")
        model_str = selected_model if "/" in selected_model else f"google_genai/{selected_model}"
        llm_config = {
            "api_key": gemini_key,
            "model": model_str,
        }
    elif provider == "openai":
        selected_model = model or "gpt-4o-mini"
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env file.")
        llm_config = {
            "api_key": openai_key,
            "model": f"openai/{selected_model}" if not selected_model.startswith("openai/") else selected_model,
        }
    elif provider == "groq":
        selected_model = model or "llama-3.3-70b-versatile"
        if not groq_key:
            raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
        llm_config = {
            "api_key": groq_key,
            "model": f"groq/{selected_model}" if not selected_model.startswith("groq/") else selected_model,
        }
    elif provider == "ollama":
        selected_model = model or "llama3.2"
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        llm_config = {
            "model": f"ollama/{selected_model}" if not selected_model.startswith("ollama/") else selected_model,
            "base_url": ollama_url,
        }
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    return {
        "llm": llm_config,
        "verbose": False,
        "headless": headless,
    }


# ==========================================
# Lead Scraper Pipeline Execution
# ==========================================

LEAD_EXTRACTION_PROMPT = (
    "Extract detailed lead generation data from this webpage for B2B outreach. "
    "Identify the company name, website, industry, description/value proposition, headquarters location, "
    "all general contact emails (e.g. info@, contact@, sales@), phone numbers, company social media links, "
    "and any key personnel, founders, executives, or team members with their names, titles/roles, emails, and LinkedIn profiles."
)

def scrape_leads_from_url(url: str, config: dict) -> dict:
    """
    Runs SmartScraperGraph with the lead extraction prompt and schema.
    """
    print(f"\n[Scraping] Fetching and analyzing: {url}")
    scraper = SmartScraperGraph(
        prompt=LEAD_EXTRACTION_PROMPT,
        source=url,
        schema=ScrapeResult,
        config=config,
    )
    result = scraper.run()
    return result


def export_leads(all_leads: list, output_dir: str = "outputs"):
    """
    Saves extracted leads into JSON and CSV files.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = out_path / f"leads_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)
    print(f"[Export] Saved JSON leads report: {json_file}")

    # Prepare flat records for CSV
    flat_rows = []
    for item in all_leads:
        source_url = item.get("source_url", "")
        lead_data = item.get("data", {})
        leads_list = lead_data.get("leads", [])
        if not leads_list and isinstance(lead_data, dict):
            # Fallback if returned directly as single lead dictionary
            if "company_name" in lead_data:
                leads_list = [lead_data]

        for company in leads_list:
            comp_name = company.get("company_name", "")
            comp_site = company.get("website", "")
            industry = company.get("industry", "")
            desc = company.get("tagline_or_summary", "")
            hq = company.get("headquarters", "")
            emails = ", ".join(company.get("general_emails", []))
            phones = ", ".join(company.get("phone_numbers", []))
            socials = ", ".join(company.get("social_links", []))
            contacts = company.get("key_contacts", [])

            if contacts:
                for c in contacts:
                    flat_rows.append({
                        "Source URL": source_url,
                        "Company Name": comp_name,
                        "Website": comp_site,
                        "Industry": industry,
                        "Headquarters": hq,
                        "General Emails": emails,
                        "General Phones": phones,
                        "Contact Name": c.get("name", ""),
                        "Contact Role": c.get("role", ""),
                        "Contact Email": c.get("email", ""),
                        "Contact Phone": c.get("phone", ""),
                        "Contact LinkedIn": c.get("linkedin", ""),
                        "Social Profiles": socials,
                        "Description": desc,
                    })
            else:
                flat_rows.append({
                    "Source URL": source_url,
                    "Company Name": comp_name,
                    "Website": comp_site,
                    "Industry": industry,
                    "Headquarters": hq,
                    "General Emails": emails,
                    "General Phones": phones,
                    "Contact Name": "",
                    "Contact Role": "",
                    "Contact Email": "",
                    "Contact Phone": "",
                    "Contact LinkedIn": "",
                    "Social Profiles": socials,
                    "Description": desc,
                })

    if flat_rows:
        try:
            import pandas as pd
            df = pd.DataFrame(flat_rows)
            csv_file = out_path / f"leads_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding="utf-8-sig")
            print(f"[Export] Saved CSV leads spreadsheet: {csv_file}")
            
            # Print table summary
            try:
                from tabulate import tabulate
                display_cols = ["Company Name", "Contact Name", "Contact Role", "Contact Email", "General Emails"]
                existing_cols = [c for c in display_cols if c in df.columns]
                print("\n" + "="*80)
                print("EXTRACTED LEADS SUMMARY")
                print("="*80)
                print(tabulate(df[existing_cols].head(15), headers="keys", tablefmt="grid", showindex=False))
                print("="*80 + "\n")
            except Exception:
                pass
        except Exception as e:
            print(f"[Notice] Could not create CSV (pandas error: {e})")


def main():
    parser = argparse.ArgumentParser(description="ScrapeGraphAI Lead Scraper - Extract B2B contacts, emails, and executives.")
    parser.add_argument("urls", nargs="*", help="One or more URLs to scrape for leads.")
    parser.add_argument("--file", "-f", help="Text file containing URLs (one per line).")
    parser.add_argument("--provider", "-p", choices=["auto", "gemini", "openai", "groq", "ollama"], default="auto",
                        help="LLM provider to use (default: auto detects based on environment variables).")
    parser.add_argument("--model", "-m", help="Specific model name (e.g. gpt-4o-mini, gemini-2.0-flash, llama3.2).")
    parser.add_argument("--headful", action="store_true", help="Launch visible browser window (default is headless).")
    parser.add_argument("--output-dir", "-o", default="outputs", help="Output directory for CSV and JSON files.")

    args = parser.parse_args()

    # Collect target URLs
    targets = list(args.urls)
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                targets.extend(lines)
        else:
            print(f"Error: Targets file not found: {args.file}")
            sys.exit(1)

    if not targets:
        print("\n" + "="*70)
        print("  AI LEAD SCRAPPER (Powered by ScrapeGraphAI)")
        print("="*70)
        print("Usage Examples:")
        print("  .\\.venv\\Scripts\\python.exe lead_scraper.py https://example.com")
        print("  .\\.venv\\Scripts\\python.exe lead_scraper.py --file targets_example.txt")
        print("  .\\.venv\\Scripts\\python.exe lead_scraper.py https://example.com --provider gemini")
        print("  .\\.venv\\Scripts\\python.exe lead_scraper.py https://example.com --provider openai --model gpt-4o-mini")
        print("  .\\.venv\\Scripts\\python.exe lead_scraper.py https://example.com --provider ollama --model llama3.2")
        print("\nTip: Configure your API keys in .env (copy from .env.example).")
        print("="*70 + "\n")
        return

    try:
        config = get_graph_config(provider=args.provider, model=args.model, headless=not args.headful)
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("Please check your .env file or supply the required API key.")
        return

    all_results = []
    print(f"Starting lead scraping for {len(targets)} target(s)...")

    for url in targets:
        try:
            result = scrape_leads_from_url(url, config)
            all_results.append({
                "source_url": url,
                "scraped_at": datetime.now().isoformat(),
                "data": result
            })
        except Exception as e:
            print(f"[Error] Failed scraping {url}: {e}")

    if all_results:
        export_leads(all_results, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
