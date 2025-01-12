from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from playwright.async_api import async_playwright
from fastapi.middleware.cors import CORSMiddleware
from database import supabase

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BusinessRequest(BaseModel):
    business_name: str


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/getdata")
async def get_business_data():
    response = supabase.table("businesses").select("*").execute()
    return response.data


@app.post("/crawl/")
async def crawl_business_details(request: BusinessRequest):
    business_name = request.business_name
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto("https://search.sunbiz.org/Inquiry/CorporationSearch/ByName/")

        # Search for business
        await page.fill("input[name='SearchTerm']", business_name)
        await page.click("input[type='submit'][value='Search Now']")
        await page.wait_for_load_state("networkidle")

        # Extract results
        results = []
        rows = await page.query_selector_all("#search-results tbody tr")
        for row in rows:
            columns = await row.query_selector_all("td")
            if len(columns) >= 3:
                detail_link = await columns[0].query_selector("a")
                detail_url = await detail_link.get_attribute("href")
                detail_page = await browser.new_page()
                await detail_page.goto(f"https://search.sunbiz.org{detail_url}")

                # Extract detailed information
                business_info = {}
                try:
                    business_info["corporate_name"] = await detail_page.inner_text(
                        ".corporationName p:nth-child(2)"
                    )
                except:
                    business_info["corporate_name"] = None

                try:
                    business_info["document_number"] = await detail_page.inner_text(
                        "label[for='Detail_DocumentId'] + span"
                    )
                except:
                    business_info["document_number"] = None

                try:
                    business_info["fein_number"] = await detail_page.inner_text(
                        "label[for='Detail_FeiEinNumber'] + span"
                    )
                except:
                    business_info["fein_number"] = None

                try:
                    business_info["date_filed"] = await detail_page.inner_text(
                        "label[for='Detail_FileDate'] + span"
                    )
                except:
                    business_info["date_filed"] = None

                try:
                    business_info["state"] = await detail_page.inner_text(
                        "label[for='Detail_EntityStateCountry'] + span"
                    )
                except:
                    business_info["state"] = None

                try:
                    business_info["status"] = await detail_page.inner_text(
                        "label[for='Detail_Status'] + span"
                    )
                except:
                    business_info["status"] = None

                try:
                    business_info["principal_address"] = await detail_page.inner_html(
                        ".detailSection:nth-of-type(3) div"
                    )
                except:
                    business_info["principal_address"] = None

                try:
                    business_info["mailing_address"] = await detail_page.inner_html(
                        ".detailSection:nth-of-type(4) div"
                    )
                except:
                    business_info["mailing_address"] = None

                try:
                    business_info["registered_agent"] = await detail_page.inner_html(
                        ".detailSection:nth-of-type(5) div"
                    )
                except:
                    business_info["registered_agent"] = None

                try:
                    business_info["officer_director_detail"] = (
                        await detail_page.inner_html(
                            ".detailSection:nth-of-type(6) div"
                        )
                    )
                except:
                    business_info["officer_director_detail"] = None

                try:
                    annual_report_links = await detail_page.query_selector_all(
                        ".detailSection:nth-of-type(7) table a"
                    )
                    business_info["annual_reports"] = [
                        f"https://search.sunbiz.org{await link.get_attribute('href')}"
                        for link in annual_report_links
                    ]
                except:
                    business_info["annual_reports"] = []

                try:
                    document_image_links = await detail_page.query_selector_all(
                        ".detailSection:nth-of-type(8) table a"
                    )
                    business_info["document_images"] = (
                        [
                            f"https://search.sunbiz.org{await link.get_attribute('href')}"
                            for link in document_image_links
                        ]
                        if document_image_links
                        else []
                    )
                except:
                    business_info["document_images"] = []

                results.append(business_info)
                await detail_page.close()

        await browser.close()

        # Insert data into Supabase
        for business in results:
            # Cast document_images to JSONB array explicitly
            document_images = business.get("document_images", [])
            # print(document_images)

            data = {
                "corporate_name": business.get("corporate_name"),
                "document_number": business.get("document_number"),
                "fein_number": business.get("fein_number"),
                "date_filed": business.get("date_filed"),
                "state": business.get("state"),
                "status": business.get("status"),
                "principal_address": business.get("principal_address"),
                "mailing_address": business.get("mailing_address"),
                "registered_agent": business.get("registered_agent"),
                "officer_director_detail": business.get("officer_director_detail"),
                "document_images": document_images,  # Make sure this is a list/array
            }

            # Insert into Supabase 'businesses' table with JSONB casting
            result = supabase.table("businesses").insert(data).execute()

        return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
