import re
import os
import asyncio
from contextlib import contextmanager

import dotenv

import psycopg2
from playwright.async_api import async_playwright, Page


dotenv.load_dotenv()

DB_ENV_VARS = {
    "ENGINE": os.getenv("DATABASE_ENGINE", "postgresql"),
    "NAME": os.getenv("DATABASE_NAME"),
    "USER": os.getenv("DATABASE_USER"),
    "PASSWORD": os.getenv("DATABASE_PASSWORD"),
    "HOST": os.getenv("DATABASE_HOST", "localhost"),
    "PORT": os.getenv("DATABASE_PORT", "5432"),
}


@contextmanager
def db_cursor():
    dsn = (
        f"dbname={DB_ENV_VARS['NAME']} "
        f"user={DB_ENV_VARS['USER']} "
        f"password={DB_ENV_VARS['PASSWORD']} "
        f"host={DB_ENV_VARS['HOST']} "
        f"port={DB_ENV_VARS['PORT']}"
    )
    conn = psycopg2.connect(dsn)
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def upsert_teacher(record: dict) -> None:
    with db_cursor() as cur:
        cur.execute(
            "CALL upsert_teacher(%s, %s, %s, %s, %s)",
            (
                record.get("isu"),
                record.get("name"),
                record.get("photo_url"),
                record.get("phone"),
                record.get("url"),
            ),
        )

        for contact in record.get("contacts", []) or []:
            cur.execute(
                "CALL ensure_contact(%s, %s, %s)",
                (
                    record.get("isu"),
                    contact.get("type"),
                    contact.get("url"),
                ),
            )


def ensure_procedures() -> None:
        sql_upsert_teacher = """
        CREATE OR REPLACE PROCEDURE upsert_teacher(
            p_isu INTEGER,
            p_name TEXT,
            p_photo_url TEXT DEFAULT NULL,
            p_phone TEXT DEFAULT NULL,
            p_url TEXT DEFAULT NULL
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO teachers (isu, name, photo_url, phone, url, updated_at)
            VALUES (p_isu, p_name, p_photo_url, p_phone, p_url, now())
            ON CONFLICT (isu) DO UPDATE
                SET name = EXCLUDED.name,
                        photo_url = COALESCE(EXCLUDED.photo_url, teachers.photo_url),
                        phone = COALESCE(EXCLUDED.phone, teachers.phone),
                        url = COALESCE(EXCLUDED.url, teachers.url),
                        updated_at = now();
        END;
        $$;
        """

        sql_ensure_contact = """
        CREATE OR REPLACE PROCEDURE ensure_contact(
            p_teacher_isu INTEGER,
            p_contact_type TEXT,
            p_url TEXT
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_teacher_id BIGINT;
            v_exists BOOLEAN;
        BEGIN
            SELECT id INTO v_teacher_id FROM teachers WHERE isu = p_teacher_isu;
            IF v_teacher_id IS NULL THEN
                RAISE EXCEPTION 'Teacher with ISU % not found', p_teacher_isu;
            END IF;

            SELECT EXISTS(
                SELECT 1 FROM contacts
                WHERE teacher_id = v_teacher_id AND contact_type = p_contact_type AND url = p_url
            ) INTO v_exists;

            IF NOT v_exists THEN
                INSERT INTO contacts (contact_type, teacher_id, url)
                VALUES (p_contact_type, v_teacher_id, p_url);
            END IF;
        END;
        $$;
        """

        with db_cursor() as cur:
            cur.execute(sql_upsert_teacher)
            cur.execute(sql_ensure_contact)


async def login(page):
    await page.goto("https://my.itmo.ru/login")
    await page.wait_for_timeout(1000)
    await page.fill("input[id='username']", os.getenv("SCRAPER_LOGIN", ""))
    await page.fill("input[id='password']", os.getenv("SCRAPER_PASSWORD", ""))
    await page.click("input[id='kc-login']")
    await page.wait_for_timeout(2000)


async def collect_teacher_pages(page):
    isu_list = [
        105395, 208064, 126287, 115442, 146060, 
        142415, 157150, 111848, 129448, 106013,
        142291, 100043, 173960, 269255, 165275,
        267649, 106026, 165442, 279132, 100537,
        175390, 285578, 138626, 152625, 126471,
        100054
    ]
    return [f"https://my.itmo.ru/persons/{isu}" for isu in isu_list]


async def parse_teacher_page(page: Page, url: str) -> dict:
    await page.goto(url)
    await page.wait_for_timeout(500)
    
    isu = await page.text_content("xpath=//div[contains(@class, 'card-body')]/div[contains(@class, 'row')]/div[contains(@class, 'text-big')]")
    name = await page.text_content("xpath=//div[contains(@class, 'card-body')]/div[contains(@class, 'row')]/div[contains(@class, 'w-xl-auto')]")
    photo_style = await page.get_attribute("xpath=//div[@class='personalities__photo']", "style")
    photo_url = None
    if photo_style:
        match = re.search(r"url\((?:'|\")?(.*?)(?:'|\")?\)", photo_style)
        if match:
            photo_url = match.group(1)
    
    try:
        phone_raw = await page.text_content("xpath=//a[contains(@href, 'tel:')]", timeout=100)
        phone = phone_raw.strip() if phone_raw else None
    except Exception:
        phone = None
    
    profile_url = page.url
    
    # deprecated
    contacts = []

    return {
        "isu": int(isu) if isu else None,
        "name": name.strip() if name else None,
        "photo_url": photo_url,
        "phone": phone,
        "url": profile_url,
        "contacts": contacts,
    }


async def scrape():
    ensure_procedures()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page)
        teacher_links = await collect_teacher_pages(page)

        for link in teacher_links:
            data = await parse_teacher_page(page, link)
            if not data.get("isu") or not data.get("name"):
                print(f"Skipped: {data}")
                continue
            upsert_teacher(data)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape())
